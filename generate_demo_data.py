"""
Generiranje demo podatkov za testiranje bančnega sistema
"""

import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("Banka.db")
cur = conn.cursor()


def clear_data():
    """Pobriši vse obstoječe podatke"""
    print("Brisanje starih podatkov...")
    cur.execute("DELETE FROM transakcija")
    cur.execute("DELETE FROM racun")
    cur.execute("DELETE FROM paket")
    cur.execute("DELETE FROM uporabnik")
    cur.execute("DELETE FROM stranka")
    conn.commit()


def generate_stranke():
    """Generiraj demo stranke"""
    print("👥 Generiranje strank...")

    stranke = [
        ("Marko", "Novak", "Dunajska cesta 15", "1990-05-15"),
        ("Ana", "Kovač", "Slovenska cesta 28", "1985-08-22"),
        ("Peter", "Horvat", "Trubarjeva ulica 5", "1992-11-30"),
        ("Maja", "Krajnc", "Beethovnova ulica 12", "1988-03-17"),
        ("Luka", "Zupančič", "Njegoševa cesta 8", "1995-07-08"),
    ]

    for ime, priimek, naslov, datum in stranke:
        cur.execute(
            """
            INSERT INTO stranka (ime, priimek, naslov, datum_rojstva)
            VALUES (?, ?, ?, ?)
        """,
            (ime, priimek, naslov, datum),
        )

    conn.commit()
    print(f"Ustvarjenih {len(stranke)} strank")


def generate_racuni():
    """Generiraj demo račune"""
    print("Generiranje računov...")

    # Pridobi ID-je strank
    cur.execute("SELECT id_stranke FROM stranka")
    stranke_ids = [row[0] for row in cur.fetchall()]

    # Najprej ustvari pakete
    paketi_tipi = [
        (1, "Basic", 0, 50000, 10000),
        (2, "Premium", 599, 500000, 100000),
        (3, "Business", 1999, None, 1000000),
    ]

    # Preveri, če paketi že obstajajo
    cur.execute("SELECT COUNT(*) FROM paket")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            """
            INSERT INTO paket (id_paket, tip, cena, osnovni_limit, dnevni_limit)
            VALUES (?, ?, ?, ?, ?)
        """,
            paketi_tipi,
        )
        conn.commit()
        print(f"Ustvarjeni {len(paketi_tipi)} paketi")

    racuni = []
    for idx, id_stranke in enumerate(stranke_ids, start=1):
        # Vsaka stranka dobi 1-2 računa
        num_accounts = random.randint(1, 2)
        for i in range(num_accounts):
            # Generiraj IBAN - točno 19 znakov za SI standard
            # Format: SI56 (4 znaki) + 15 številk = 19 znakov
            account_num = f"{random.randint(100000000000000, 999999999999999):015d}"
            iban = f"SI56{account_num}"  # 4 + 15 = 19
            stanje = random.randint(10000, 500000)  # 100-5000 EUR v centih
            id_paket = random.choice([1, 2, 3])
            racuni.append((iban, id_stranke, id_paket, stanje))

    cur.executemany(
        """
        INSERT INTO racun (IBAN, id_lastnik, id_paket, stanje)
        VALUES (?, ?, ?, ?)
    """,
        racuni,
    )

    conn.commit()
    print(f"Ustvarjenih {len(racuni)} računov")


def generate_uporabniki():
    """Generiraj demo uporabnike (avtentikacija)"""
    print("Generiranje uporabnikov...")

    # Pridobi stranke
    cur.execute("SELECT id_stranke, ime, priimek FROM stranka")
    stranke = cur.fetchall()

    uporabniki = []
    for id_stranke, ime, priimek in stranke:
        # Uporabniško ime: ime.priimek (male črke, brez šumnikov)
        uporabnisko_ime = f"{ime.lower()}.{priimek.lower()}"
        # Zamenjaj šumnike
        for src, dst in [("č", "c"), ("š", "s"), ("ž", "z"), ("ć", "c"), ("đ", "d")]:
            uporabnisko_ime = uporabnisko_ime.replace(src, dst)

        geslo_hash = generate_password_hash("geslo123")
        uporabniki.append((uporabnisko_ime, geslo_hash, id_stranke, "stranka"))

    # Admin uporabnik
    admin_hash = generate_password_hash("admin123")
    uporabniki.append(("admin", admin_hash, None, "admin"))

    cur.executemany(
        """
        INSERT INTO uporabnik (uporabnisko_ime, geslo_hash, id_stranke, vloga)
        VALUES (?, ?, ?, ?)
    """,
        uporabniki,
    )

    conn.commit()
    print(f"Ustvarjenih {len(uporabniki)} uporabnikov")


def generate_transakcije():
    """Generiraj demo transakcije"""
    print("Generiranje transakcij...")

    # Pridobi vse IBAN-e
    cur.execute("SELECT IBAN FROM racun")
    ibans = [row[0] for row in cur.fetchall()]

    transakcije = []

    # Pologi
    for _ in range(10):
        iban = random.choice(ibans)
        znesek = random.randint(5000, 50000)
        cas = datetime.now() - timedelta(days=random.randint(1, 30))
        transakcije.append((None, iban, "polog", znesek, cas))

    # Dvigi
    for _ in range(8):
        iban = random.choice(ibans)
        znesek = random.randint(2000, 10000)
        cas = datetime.now() - timedelta(days=random.randint(1, 30))
        transakcije.append((iban, None, "dvig", znesek, cas))

    # Nakazila
    for _ in range(15):
        from_iban = random.choice(ibans)
        to_iban = random.choice([i for i in ibans if i != from_iban])
        znesek = random.randint(1000, 20000)
        cas = datetime.now() - timedelta(days=random.randint(1, 30))
        transakcije.append((from_iban, to_iban, "nakazilo", znesek, cas))

    cur.executemany(
        """
        INSERT INTO transakcija (posilja, prejema, tip, znesek, cas)
        VALUES (?, ?, ?, ?, ?)
    """,
        transakcije,
    )

    # Posodobi stanja računov glede na transakcije
    cur.execute("""
        UPDATE racun SET stanje = (
            SELECT 
                r.stanje +
                COALESCE((SELECT SUM(znesek) FROM transakcija WHERE prejema = r.IBAN AND tip IN ('polog', 'nakazilo', 'obresti')), 0) -
                COALESCE((SELECT SUM(znesek) FROM transakcija WHERE posilja = r.IBAN AND tip IN ('dvig', 'nakazilo')), 0)
            FROM racun r
            WHERE r.IBAN = racun.IBAN
        )
    """)

    conn.commit()
    print(f"Ustvarjenih {len(transakcije)} transakcij")


def show_summary():
    """Prikaži povzetek podatkov"""
    print("\nPovzetek generiranih podatkov:")
    print("=" * 50)

    cur.execute("SELECT COUNT(*) FROM stranka")
    print(f"   Stranke: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM uporabnik")
    print(f"   Uporabniki: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM racun")
    print(f"   Računi: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM paket")
    print(f"   Paketi: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM transakcija")
    print(f"   Transakcije: {cur.fetchone()[0]}")

    cur.execute("SELECT SUM(stanje) FROM racun")
    total = cur.fetchone()[0] or 0
    print(f"   Skupno stanje: {total / 100:.2f} EUR")

    print("=" * 50)

    # Primer uporabnikov za prijavo
    cur.execute("""
        SELECT u.uporabnisko_ime, u.vloga, s.ime, s.priimek
        FROM uporabnik u
        LEFT JOIN stranka s ON u.id_stranke = s.id_stranke
    """)
    print("\nUporabniki za prijavo (geslo je 'geslo123' oz. 'admin123' za admina):")
    for uporabnisko_ime, vloga, ime, priimek in cur.fetchall():
        if vloga == "admin":
            print(f"{uporabnisko_ime} (Administrator) — geslo: admin123")
        else:
            print(f"  {uporabnisko_ime} ({ime} {priimek}) — geslo: geslo123")


if __name__ == "__main__":
    print("Generiranje demo podatkov za Slovenia Bank\n")

    try:
        # Pobriši stare podatke
        clear_data()

        # Generiraj nove podatke
        generate_stranke()
        generate_racuni()
        generate_uporabniki()
        generate_transakcije()

        # Prikaži povzetek
        show_summary()

        print("\nDemo podatki uspešno generirani!")
        print("\nZdaj lahko zaženete: python app.py")

    except Exception as e:
        print(f"\n❌ Napaka: {e}")
        import traceback

        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()
