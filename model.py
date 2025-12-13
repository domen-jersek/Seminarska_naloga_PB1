#
#   Model za delo z bazo Banka.db
#
#   
#   Prirejeno po J. Vidali, nov. 2024, M. Pretnar, 2019, M. Lokar, dec. 2020
#

import csv
import sqlite3 as dbapi
from dataclasses import dataclass, field
import threading


# Thread-local storage za database povezave
_thread_local = threading.local()


def get_connection():
    """
    Dobi thread-safe database povezavo.
    Vsak thread ima svojo povezavo.
    """
    if not hasattr(_thread_local, 'conn'):
        _thread_local.conn = dbapi.connect('Banka.db', check_same_thread=False)
        _thread_local.conn.execute("PRAGMA foreign_keys = ON;")
    return _thread_local.conn


# Backwards compatibility - za obstojočo kodo
conn = get_connection()


class Kazalec:
    """
    Upravitelj konteksta za kazalce.
    """

    def __init__(self, cur=None):
        """
        Konstruktor upravitelja konteksta.

        Če kazalec ni podan, odpre novega, sicer uporabi podanega.
        """
        if cur is None:
            self.cur = get_connection().cursor()
            self.close = True
        else:
            self.cur = cur
            self.close = False

    def __enter__(self):
        """
        Vstop v kontekst z `with`.

        Vrne kazalec - ta se shrani v spremenljivko, podano z `as`.
        """
        return self.cur

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Izstop iz konteksta.

        Če je bil ustvarjen nov kazalec, se ta zapre.
        """
        if self.close:
            self.cur.close()


class Tabela:
    """
    Nadrazred za tabele.
    """

    TABELE = []

    def __init_subclass__(cls, /, **kwargs):
        """
        Inicializacija podrazreda.

        Doda podrazred v seznam tabel.
        """
        super().__init_subclass__(**kwargs)
        cls.TABELE.append(cls)

    @classmethod
    def uvozi_podatke(cls, cur=None):
        """
        Uvozi podatke v tabelo.

        Privzeto ne naredi ničesar, podrazredi naj povozijo definicijo.
        """
        pass

    @classmethod
    def preberi_vir(cls):
        """
        Preberi vir v obliki CSV in vračaj slovarje za vsako vrstico.
        """
        with open(f"podatki/{cls.VIR}") as f:
            rd = csv.reader(f)
            stolpci = next(rd)
            for vrstica in rd:
                yield dict(zip(stolpci, vrstica))


class Entiteta:
    """
    Nadrazred za posamezne entitetne tipe.
    """
    def __bool__(self):
        """
        Pretvorba v logično vrednost.
        Preveri, če je primarni ključ (prvi atribut) nastavljen.
        """
        # Dobi ime prvega polja iz dataclass
        if hasattr(self, '__dataclass_fields__'):
            first_field = next(iter(self.__dataclass_fields__))
            return getattr(self, first_field) is not None
        return True

    def __str__(self):
        """
        Znakovna predstavitev.
        """
        if hasattr(self, '__dataclass_fields__'):
            first_field = next(iter(self.__dataclass_fields__))
            value = getattr(self, first_field)
            return str(value) if value is not None else f"<entiteta tipa {self.__class__}>"
        return f"<entiteta tipa {self.__class__}>"

    def __init_subclass__(cls, /, **kwargs):
        """
        Inicializacija podrazreda.

        Pripravi prazen objekt.
        """
        super().__init_subclass__(**kwargs)
        cls.NULL = cls()


@dataclass
class Stranka(Tabela, Entiteta):
    """
    Razred za stranka.
    """

    id_stranke: int = field(default=None)
    ime: str = field(default=None)
    priimek: str = field(default=None)
    naslov: str = field(default=None)
    datum_rojstva: str = field(default=None)
    
    VIR = "stranka.csv"
    IME = 'stranka'

    @classmethod
    def ustvari_tabelo(cls, cur=None):
        """
        Ustvari tabelo "stranka".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stranka (
                        id_stranke      INTEGER  PRIMARY KEY AUTOINCREMENT,
                        ime             TEXT     NOT NULL CHECK(LENGTH(ime) > 0),
                        priimek         TEXT     NOT NULL CHECK(LENGTH(priimek) > 0),
                        naslov          TEXT     NOT NULL CHECK(LENGTH(naslov) > 0),
                        datum_rojstva   DATE     NOT NULL  
                );
            """)

    @classmethod
    def pobrisi_tabelo(cls, cur=None):
        """
        Pobriši tabelo "stranka".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                DROP TABLE IF EXISTS stranka;
            """)
    
    @classmethod
    def uvozi_podatke(cls, cur=None):
        """
        Uvozi podatke v tabelo "stranka".
        """
        with Kazalec(cur) as cur:
            cur.executemany("""
                INSERT INTO stranka (id_stranke, ime, priimek, naslov, datum_rojstva)
                VALUES (:id_stranke, :ime, :priimek, :naslov, :datum_rojstva);
            """, cls.preberi_vir())


@dataclass
class Racun(Tabela, Entiteta):
    """
    Razred za racun.
    """

    IBAN: str = field(default=None)
    id_lastnik: int = field(default=None)
    stanje: int = field(default=None)
    
    VIR = "racun.csv"
    IME = 'racun'

    @classmethod
    def ustvari_tabelo(cls, cur=None):
        """
        Ustvari tabelo "racun".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS racun (
                        IBAN            TEXT     PRIMARY KEY UNIQUE CHECK(LENGTH(IBAN) = 34), -- 34 je standart po Wiki
                        id_lastnik      INTEGER  NOT NULL REFERENCES stranka(id_stranke),
                        stanje          INTEGER  NOT NULL DEFAULT(0) -- centi
                );
            """)

    @classmethod
    def pobrisi_tabelo(cls, cur=None):
        """
        Pobriši tabelo "racun".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                DROP TABLE IF EXISTS racun;
            """)
    
    @classmethod
    def uvozi_podatke(cls, cur=None):
        """
        Uvozi podatke v tabelo "racun".
        """
        with Kazalec(cur) as cur:
            cur.executemany("""
                INSERT INTO racun (IBAN, id_lastnik, stanje)
                VALUES (:IBAN, :id_lastnik, :stanje);
            """, cls.preberi_vir())


@dataclass
class Paket(Tabela, Entiteta):
    """
    Razred za paket.
    """

    id_paket: int = field(default=None)
    id_racuna: str = field(default=None)
    tip: str = field(default=None)
    cena: int = field(default=None)
    osnovni_limit: int = field(default=None)
    dnevni_limit: int = field(default=None)

    VIR = "paket.csv"
    IME = 'paket'

    @classmethod
    def ustvari_tabelo(cls, cur=None):
        """
        Ustvari tabelo "paket".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS paket (
                    id_paket  INTEGER PRIMARY KEY,
                    id_racuna TEXT NOT NULL REFERENCES racun(IBAN),
                    tip       TEXT     NOT NULL,
                    cena      INTEGER  NOT NULL,
                    osnovni_limit  INTEGER,
                    dnevni_limit   INTEGER  NOT NULL
                    
                );
            """)

    @classmethod
    def pobrisi_tabelo(cls, cur=None):
        """
        Pobriši tabelo "paket".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                DROP TABLE IF EXISTS paket;
            """)

    @classmethod
    def uvozi_podatke(cls, cur=None):
        """
        Uvozi podatke v tabelo "paket".
        """
        with Kazalec(cur) as cur:
            cur.executemany("""
                INSERT INTO paket (id_paket, id_racuna, tip, cena, osnovni_limit, dnevni_limit)
                VALUES (:id_paket, :id_racuna, :tip, :cena, :osnovni_limit, :dnevni_limit);
            """, cls.preberi_vir())

@dataclass
class Transakcija(Tabela, Entiteta):
    """
    Razred za transakcija.
    """

    id_transakcije: int = field(default=None)
    posilja: str = field(default=None)
    prejema: str = field(default=None)
    tip: str = field(default=None)
    znesek: int = field(default=None)
    cas: str = field(default=None)
    
    VIR = "transakcija.csv"
    IME = 'transakcija'

    @classmethod
    def ustvari_tabelo(cls, cur=None):
        """
        Ustvari tabelo "transkacija".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transkacija (
                    id_transakcije  INTEGER  PRIMARY KEY AUTOINCREMENT,
                    posilja         TEXT     REFERENCES racun(IBAN), -- NULL za polog
                    prejema         TEXT     REFERENCES racun(IBAN), -- NULL za dvig
                    tip             TEXT     NOT NULL CHECK(tip IN ('polog', 'dvig', 'nakazilo', 'obresti')),
                    znesek          INTEGER  NOT NULL DEFAULT(0) CHECK(znesek > 0),    -- centi
                    cas             DATETIME DEFAULT(DATETIME('now'))

    
                CHECK (
                (tip = 'polog'   AND posilja IS NULL AND prejema IS NOT NULL) OR
                (tip = 'dvig'    AND posilja IS NOT NULL AND prejema IS NULL) OR
                (tip = 'nakazilo' AND posilja IS NOT NULL AND prejema IS NOT NULL AND posilja != prejema) OR
                (tip = 'obresti' AND posilja IS NULL AND prejema IS NOT NULL)
                )
            );
            """)

    @classmethod
    def pobrisi_tabelo(cls, cur=None):
        """
        Pobriši tabelo "transakcija".
        """
        with Kazalec(cur) as cur:
            cur.execute("""
                DROP TABLE IF EXISTS transakcija;
            """)
    
    @classmethod
    def uvozi_podatke(cls, cur=None):
        """
        Uvozi podatke v tabelo "transakcija".
        """
        with Kazalec(cur) as cur:
            cur.executemany("""
                INSERT INTO transakcija (id_transakcije, posilja, prejema, tip, znesek, cas)
                VALUES (:id_transakcije, :posilja, :prejema, :tip, :znesek, :cas);
            """, cls.preberi_vir())    
            

##########################################################################################################################################################

def ustvari_tabele(cur=None):
    """
    Ustvari vse tabele.
    """
    with Kazalec(cur) as cur:
        for t in Tabela.TABELE:
            t.ustvari_tabelo(cur=cur)


def pobrisi_tabele(cur=None):
    """
    Pobriši vse tabele.
    """
    with Kazalec(cur) as cur:
        for t in reversed(Tabela.TABELE):
            t.pobrisi_tabelo(cur=cur)


def uvozi_podatke(cur=None):
    """
    Uvozi vse podatke.
    """
    with Kazalec(cur) as cur:
        for t in Tabela.TABELE:
            t.uvozi_podatke(cur=cur)


def ustvari_bazo(pobrisi=False, cur=None):
    """
    Ustvari tabele in uvozi podatke.
    """
    with Kazalec(cur) as cur:
        try:
            with get_connection():
                cur.execute("PRAGMA foreign_keys = OFF;")
                if pobrisi:
                    pobrisi_tabele(cur=cur)
                ustvari_tabele(cur=cur)
                uvozi_podatke(cur=cur)
        finally:
            cur.execute("PRAGMA foreign_keys = ON;")

def ustvari_prazno_bazo():
    """
    Ustvari vse tabele v bazi 'Banka.db' — brez uvoza podatkov.
    """
    with get_connection():  # auto-commit
        ustvari_tabele()
    print("✅ Prazna baza 'Banka.db' z vsemi tabelami je ustvarjena.")

if __name__ == "__main__":
    # Samo ustvari prazno bazo (brez podatkov)
    ustvari_prazno_bazo()