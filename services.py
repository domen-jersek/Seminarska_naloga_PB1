"""
Bančne storitve - vmesna plast med Flask aplikacijo in bazo podatkov
"""
from model import get_connection, Kazalec, Stranka, Racun, Paket, Transakcija, Uporabnik
from datetime import datetime
import hashlib
import os


def hash_geslo(geslo, sol=None):
    """
    Hashira geslo s SHA-256 in soljo.
    Vrne 'sol:hash' string.
    """
    if sol is None:
        sol = os.urandom(16).hex()
    h = hashlib.sha256((sol + geslo).encode('utf-8')).hexdigest()
    return f"{sol}:{h}"


def preveri_geslo(geslo, geslo_hash):
    """
    Preveri, če se geslo ujema s hashiranim geslom.
    """
    sol = geslo_hash.split(':')[0]
    return hash_geslo(geslo, sol) == geslo_hash


class BankService:
    """Glavna razred za bančne storitve"""

    # ==================== AVTENTIKACIJA ====================
    
    def authenticate(self, uporabnisko_ime, geslo):
        """
        Preveri uporabniško ime in geslo.
        
        Returns: (success: bool, user_data: dict or None, message: str)
        """
        with Kazalec() as cur:
            cur.execute("""
                SELECT u.id_uporabnika, u.uporabnisko_ime, u.geslo_hash, 
                       u.id_stranke, u.vloga
                FROM uporabnik u
                WHERE u.uporabnisko_ime = ?
            """, (uporabnisko_ime,))
            row = cur.fetchone()
            
            if not row:
                return False, None, "Napačno uporabniško ime ali geslo"
            
            if not preveri_geslo(geslo, row[2]):
                return False, None, "Napačno uporabniško ime ali geslo"
            
            user_data = {
                'id_uporabnika': row[0],
                'uporabnisko_ime': row[1],
                'id_stranke': row[3],
                'vloga': row[4]
            }
            
            return True, user_data, "Uspešna prijava"
    
    def create_uporabnik(self, uporabnisko_ime, geslo, id_stranke=None, vloga='stranka'):
        """
        Ustvari novega uporabnika.
        
        Returns: (success: bool, message: str)
        """
        if not uporabnisko_ime or len(uporabnisko_ime.strip()) < 3:
            return False, "Uporabniško ime mora imeti vsaj 3 znake"
        if not geslo or len(geslo) < 4:
            return False, "Geslo mora imeti vsaj 4 znake"
        
        geslo_hash = hash_geslo(geslo)
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, če uporabniško ime že obstaja
                    cur.execute("SELECT id_uporabnika FROM uporabnik WHERE uporabnisko_ime = ?", 
                               (uporabnisko_ime.strip(),))
                    if cur.fetchone():
                        return False, "Uporabniško ime je že zasedeno"
                    
                    cur.execute("""
                        INSERT INTO uporabnik (uporabnisko_ime, geslo_hash, id_stranke, vloga)
                        VALUES (?, ?, ?, ?)
                    """, (uporabnisko_ime.strip(), geslo_hash, id_stranke, vloga))
                    
                    return True, "Uporabnik uspešno ustvarjen"
        except Exception as e:
            return False, f"Napaka pri ustvarjanju uporabnika: {str(e)}"
    
    def change_password(self, id_uporabnika, staro_geslo, novo_geslo):
        """
        Spremeni geslo uporabnika.
        
        Returns: (success: bool, message: str)
        """
        if not novo_geslo or len(novo_geslo) < 4:
            return False, "Novo geslo mora imeti vsaj 4 znake"
        
        with Kazalec() as cur:
            cur.execute("SELECT geslo_hash FROM uporabnik WHERE id_uporabnika = ?", (id_uporabnika,))
            row = cur.fetchone()
            if not row:
                return False, "Uporabnik ne obstaja"
            
            if not preveri_geslo(staro_geslo, row[0]):
                return False, "Napačno staro geslo"
        
        novo_hash = hash_geslo(novo_geslo)
        try:
            with get_connection():
                with Kazalec() as cur:
                    cur.execute("UPDATE uporabnik SET geslo_hash = ? WHERE id_uporabnika = ?",
                               (novo_hash, id_uporabnika))
                    return True, "Geslo uspešno spremenjeno"
        except Exception as e:
            return False, f"Napaka: {str(e)}"
    
    def delete_uporabnik_za_stranko(self, id_stranke):
        """Izbriši uporabnika, ki pripada stranki"""
        try:
            with get_connection():
                with Kazalec() as cur:
                    cur.execute("DELETE FROM uporabnik WHERE id_stranke = ?", (id_stranke,))
                    return True, "Uporabnik izbrisan"
        except Exception as e:
            return False, f"Napaka: {str(e)}"

    # ==================== STRANKE ====================
    
    def get_stranka(self, id_stranke):
        """Pridobi podatke o stranki"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT id_stranke, ime, priimek, naslov, datum_rojstva
                FROM stranka
                WHERE id_stranke = ?
            """, (id_stranke,))
            row = cur.fetchone()
            if row:
                return Stranka(
                    id_stranke=row[0],
                    ime=row[1],
                    priimek=row[2],
                    naslov=row[3],
                    datum_rojstva=row[4]
                )
            return None
    
    def get_racuni_stranke(self, id_stranke):
        """Pridobi vse račune stranke"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT IBAN, id_lastnik, stanje
                FROM racun
                WHERE id_lastnik = ?
                ORDER BY IBAN
            """, (id_stranke,))
            rows = cur.fetchall()
            return [
                {
                    'IBAN': row[0],
                    'id_lastnik': row[1],
                    'stanje': row[2]
                }
                for row in rows
            ]
    
    def get_racun(self, iban):
        """Pridobi podatke o računu"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT IBAN, id_lastnik, stanje
                FROM racun
                WHERE IBAN = ?
            """, (iban,))
            row = cur.fetchone()
            if row:
                return {
                    'IBAN': row[0],
                    'id_lastnik': row[1],
                    'stanje': row[2]
                }
            return None
    
    def get_paket_za_racun(self, iban):
        """Pridobi paket za račun"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT p.id_paket, p.tip, p.cena, p.osnovni_limit, p.dnevni_limit
                FROM paket p
                JOIN racun r ON r.id_paket = p.id_paket
                WHERE r.IBAN = ?
            """, (iban,))
            row = cur.fetchone()
            if row:
                return {
                    'id_paket': row[0],
                    'tip': row[1],
                    'cena': row[2],
                    'osnovni_limit': row[3],
                    'dnevni_limit': row[4]
                }
            return None
    
    def get_recent_transactions(self, id_stranke, limit=10):
        """Pridobi zadnje transakcije za stranko"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT t.id_transakcije, t.posilja, t.prejema, t.tip, t.znesek, t.cas
                FROM transakcija t
                LEFT JOIN racun r1 ON t.posilja = r1.IBAN
                LEFT JOIN racun r2 ON t.prejema = r2.IBAN
                WHERE r1.id_lastnik = ? OR r2.id_lastnik = ?
                ORDER BY t.cas DESC
                LIMIT ?
            """, (id_stranke, id_stranke, limit))
            rows = cur.fetchall()
            return [
                {
                    'id_transakcije': row[0],
                    'posilja': row[1],
                    'prejema': row[2],
                    'tip': row[3],
                    'znesek': row[4],
                    'cas': row[5]
                }
                for row in rows
            ]
    
    def get_transactions_for_account(self, iban, limit=50):
        """Pridobi transakcije za določen račun"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT id_transakcije, posilja, prejema, tip, znesek, cas
                FROM transakcija
                WHERE posilja = ? OR prejema = ?
                ORDER BY cas DESC
                LIMIT ?
            """, (iban, iban, limit))
            rows = cur.fetchall()
            return [
                {
                    'id_transakcije': row[0],
                    'posilja': row[1],
                    'prejema': row[2],
                    'tip': row[3],
                    'znesek': row[4],
                    'cas': row[5]
                }
                for row in rows
            ]
    
    def create_transfer(self, from_iban, to_iban, amount_cents):
        """
        Ustvari nakazilo med računi
        
        Returns: (success: bool, message: str)
        """
        if amount_cents <= 0:
            return False, "Znesek mora biti pozitiven"
        
        if from_iban == to_iban:
            return False, "Ne morete nakazati na isti račun"
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri stanje pošiljatelja
                    cur.execute("SELECT stanje FROM racun WHERE IBAN = ?", (from_iban,))
                    row = cur.fetchone()
                    if not row:
                        return False, "Račun pošiljatelja ne obstaja"
                    
                    if row[0] < amount_cents:
                        return False, "Nezadostna sredstva"
                    
                    # Preveri, da prejemnik obstaja
                    cur.execute("SELECT IBAN FROM racun WHERE IBAN = ?", (to_iban,))
                    if not cur.fetchone():
                        return False, "Račun prejemnika ne obstaja"
                    
                    # Preveri dnevni limit
                    paket = self.get_paket_za_racun(from_iban)
                    if paket and paket['dnevni_limit']:
                        # Preveri koliko je bilo že poslano danes
                        cur.execute("""
                            SELECT COALESCE(SUM(znesek), 0)
                            FROM transakcija
                            WHERE posilja = ? 
                            AND tip = 'nakazilo'
                            AND DATE(cas) = DATE('now')
                        """, (from_iban,))
                        daily_total = cur.fetchone()[0]
                        
                        if daily_total + amount_cents > paket['dnevni_limit']:
                            return False, f"Presežen dnevni limit ({paket['dnevni_limit']/100:.2f} EUR)"
                    
                    # Izvedi transakcijo
                    cur.execute("""
                        INSERT INTO transakcija (posilja, prejema, tip, znesek)
                        VALUES (?, ?, 'nakazilo', ?)
                    """, (from_iban, to_iban, amount_cents))
                    
                    # Posodobi stanja
                    cur.execute("""
                        UPDATE racun SET stanje = stanje - ? WHERE IBAN = ?
                    """, (amount_cents, from_iban))
                    
                    cur.execute("""
                        UPDATE racun SET stanje = stanje + ? WHERE IBAN = ?
                    """, (amount_cents, to_iban))
                    
                    return True, f"Nakazilo {amount_cents/100:.2f} EUR uspešno!"
                    
        except Exception as e:
            return False, f"Napaka: {str(e)}"
    
    def create_deposit(self, iban, amount_cents):
        """
        Ustvari polog na račun
        
        Returns: (success: bool, message: str)
        """
        if amount_cents <= 0:
            return False, "Znesek mora biti pozitiven"
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, da račun obstaja
                    cur.execute("SELECT IBAN FROM racun WHERE IBAN = ?", (iban,))
                    if not cur.fetchone():
                        return False, "Račun ne obstaja"
                    
                    # Izvedi polog
                    cur.execute("""
                        INSERT INTO transakcija (posilja, prejema, tip, znesek)
                        VALUES (NULL, ?, 'polog', ?)
                    """, (iban, amount_cents))
                    
                    # Posodobi stanje
                    cur.execute("""
                        UPDATE racun SET stanje = stanje + ? WHERE IBAN = ?
                    """, (amount_cents, iban))
                    
                    return True, f"Polog {amount_cents/100:.2f} EUR uspešen!"
                    
        except Exception as e:
            return False, f"Napaka: {str(e)}"
    
    def create_withdrawal(self, iban, amount_cents):
        """
        Ustvari dvig z računa
        
        Returns: (success: bool, message: str)
        """
        if amount_cents <= 0:
            return False, "Znesek mora biti pozitiven"
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri stanje
                    cur.execute("SELECT stanje FROM racun WHERE IBAN = ?", (iban,))
                    row = cur.fetchone()
                    if not row:
                        return False, "Račun ne obstaja"
                    
                    if row[0] < amount_cents:
                        return False, "Nezadostna sredstva"
                    
                    # Preveri dnevni limit
                    paket = self.get_paket_za_racun(iban)
                    if paket and paket['dnevni_limit']:
                        cur.execute("""
                            SELECT COALESCE(SUM(znesek), 0)
                            FROM transakcija
                            WHERE posilja = ? 
                            AND tip = 'dvig'
                            AND DATE(cas) = DATE('now')
                        """, (iban,))
                        daily_total = cur.fetchone()[0]
                        
                        if daily_total + amount_cents > paket['dnevni_limit']:
                            return False, f"Presežen dnevni limit ({paket['dnevni_limit']/100:.2f} EUR)"
                    
                    # Izvedi dvig
                    cur.execute("""
                        INSERT INTO transakcija (posilja, prejema, tip, znesek)
                        VALUES (?, NULL, 'dvig', ?)
                    """, (iban, amount_cents))
                    
                    # Posodobi stanje
                    cur.execute("""
                        UPDATE racun SET stanje = stanje - ? WHERE IBAN = ?
                    """, (amount_cents, iban))
                    
                    return True, f"Dvig {amount_cents/100:.2f} EUR uspešen!"
                    
        except Exception as e:
            return False, f"Napaka: {str(e)}"
    
    # Admin funkcije
    
    def get_all_stranke(self):
        """Pridobi vse stranke (admin)"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT s.id_stranke, s.ime, s.priimek, s.naslov, s.datum_rojstva,
                       COUNT(r.IBAN) as stevilo_racunov,
                       COALESCE(SUM(r.stanje), 0) as skupno_stanje
                FROM stranka s
                LEFT JOIN racun r ON s.id_stranke = r.id_lastnik
                GROUP BY s.id_stranke
                ORDER BY s.priimek, s.ime
            """)
            rows = cur.fetchall()
            return [
                {
                    'id_stranke': row[0],
                    'ime': row[1],
                    'priimek': row[2],
                    'naslov': row[3],
                    'datum_rojstva': row[4],
                    'stevilo_racunov': row[5],
                    'skupno_stanje': row[6]
                }
                for row in rows
            ]
    
    def get_all_transactions(self, limit=100):
        """Pridobi vse transakcije (admin)"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT id_transakcije, posilja, prejema, tip, znesek, cas
                FROM transakcija
                ORDER BY cas DESC
                LIMIT ?
            """, (limit,))
            rows = cur.fetchall()
            return [
                {
                    'id_transakcije': row[0],
                    'posilja': row[1],
                    'prejema': row[2],
                    'tip': row[3],
                    'znesek': row[4],
                    'cas': row[5]
                }
                for row in rows
            ]
    
    def get_statistics(self):
        """Pridobi statistiko (admin)"""
        with Kazalec() as cur:
            # Število strank
            cur.execute("SELECT COUNT(*) FROM stranka")
            total_customers = cur.fetchone()[0]
            
            # Število računov
            cur.execute("SELECT COUNT(*) FROM racun")
            total_accounts = cur.fetchone()[0]
            
            # Skupna vrednost vseh računov
            cur.execute("SELECT COALESCE(SUM(stanje), 0) FROM racun")
            total_balance = cur.fetchone()[0]
            
            # Število transakcij danes
            cur.execute("""
                SELECT COUNT(*) FROM transakcija 
                WHERE DATE(cas) = DATE('now')
            """)
            transactions_today = cur.fetchone()[0]
            
            # Število transakcij vse skupaj
            cur.execute("SELECT COUNT(*) FROM transakcija")
            total_transactions = cur.fetchone()[0]
            
            # Povprečno stanje na računu
            avg_balance = total_balance / total_accounts if total_accounts > 0 else 0
            
            return {
                'total_customers': total_customers,
                'total_accounts': total_accounts,
                'total_balance': total_balance,
                'transactions_today': transactions_today,
                'total_transactions': total_transactions,
                'avg_balance': avg_balance
            }
    
    def add_stranka(self, ime, priimek, naslov, datum_rojstva):
        """
        Dodaj novo stranko
        
        Returns: (success: bool, message: str, id_stranke: int or None)
        """
        if not ime or len(ime.strip()) == 0:
            return False, "Ime je obvezno", None
        if not priimek or len(priimek.strip()) == 0:
            return False, "Priimek je obvezen", None
        if not naslov or len(naslov.strip()) == 0:
            return False, "Naslov je obvezen", None
        if not datum_rojstva:
            return False, "Datum rojstva je obvezen", None
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    cur.execute("""
                        INSERT INTO stranka (ime, priimek, naslov, datum_rojstva)
                        VALUES (?, ?, ?, ?)
                    """, (ime.strip(), priimek.strip(), naslov.strip(), datum_rojstva))
                    
                    id_stranke = cur.lastrowid
                    return True, "Stranka uspešno dodana", id_stranke
        except Exception as e:
            return False, f"Napaka pri dodajanju stranke: {str(e)}", None

    # ==================== RAČUNI (Admin) ====================

    def get_all_racuni(self):
        """Pridobi vse račune z informacijami o lastniku in paketu (admin)"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT r.IBAN, r.id_lastnik, r.id_paket, r.stanje,
                       s.ime, s.priimek,
                       p.tip as paket_tip
                FROM racun r
                JOIN stranka s ON r.id_lastnik = s.id_stranke
                JOIN paket p ON r.id_paket = p.id_paket
                ORDER BY s.priimek, s.ime, r.IBAN
            """)
            rows = cur.fetchall()
            return [
                {
                    'IBAN': row[0],
                    'id_lastnik': row[1],
                    'id_paket': row[2],
                    'stanje': row[3],
                    'ime_lastnika': row[4],
                    'priimek_lastnika': row[5],
                    'paket_tip': row[6]
                }
                for row in rows
            ]

    def get_all_paketi(self):
        """Pridobi vse pakete"""
        with Kazalec() as cur:
            cur.execute("""
                SELECT id_paket, tip, cena, osnovni_limit, dnevni_limit
                FROM paket
                ORDER BY id_paket
            """)
            rows = cur.fetchall()
            return [
                {
                    'id_paket': row[0],
                    'tip': row[1],
                    'cena': row[2],
                    'osnovni_limit': row[3],
                    'dnevni_limit': row[4]
                }
                for row in rows
            ]

    def add_racun(self, iban, id_lastnik, id_paket, stanje=0):
        """
        Ustvari nov račun za stranko.
        
        Returns: (success: bool, message: str)
        """
        if not iban or len(iban.strip()) != 19:
            return False, "IBAN mora imeti točno 19 znakov"
        if not id_lastnik:
            return False, "Lastnik je obvezen"
        if not id_paket:
            return False, "Paket je obvezen"
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, da stranka obstaja
                    cur.execute("SELECT id_stranke FROM stranka WHERE id_stranke = ?", (id_lastnik,))
                    if not cur.fetchone():
                        return False, "Stranka ne obstaja"
                    
                    # Preveri, da paket obstaja
                    cur.execute("SELECT id_paket FROM paket WHERE id_paket = ?", (id_paket,))
                    if not cur.fetchone():
                        return False, "Paket ne obstaja"
                    
                    # Preveri, da IBAN še ni zaseden
                    cur.execute("SELECT IBAN FROM racun WHERE IBAN = ?", (iban.strip(),))
                    if cur.fetchone():
                        return False, "IBAN je že zaseden"
                    
                    cur.execute("""
                        INSERT INTO racun (IBAN, id_lastnik, id_paket, stanje)
                        VALUES (?, ?, ?, ?)
                    """, (iban.strip(), id_lastnik, id_paket, stanje))
                    
                    return True, f"Račun {iban} uspešno ustvarjen"
        except Exception as e:
            return False, f"Napaka pri ustvarjanju računa: {str(e)}"

    def generate_iban(self):
        """Generiraj naključen edinstven IBAN (19 znakov, SI56...)"""
        import random
        with Kazalec() as cur:
            for _ in range(100):  # max 100 poskusov
                account_num = f"{random.randint(100000000000000, 999999999999999):015d}"
                iban = f"SI56{account_num}"
                cur.execute("SELECT IBAN FROM racun WHERE IBAN = ?", (iban,))
                if not cur.fetchone():
                    return iban
        return None

    def delete_racun(self, iban):
        """
        Izbriši račun in vse povezane transakcije.
        
        Returns: (success: bool, message: str)
        """
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, da račun obstaja
                    cur.execute("SELECT IBAN, stanje FROM racun WHERE IBAN = ?", (iban,))
                    row = cur.fetchone()
                    if not row:
                        return False, "Račun ne obstaja"
                    
                    # Izbriši povezane transakcije
                    cur.execute("DELETE FROM transakcija WHERE posilja = ? OR prejema = ?", (iban, iban))
                    
                    # Izbriši račun
                    cur.execute("DELETE FROM racun WHERE IBAN = ?", (iban,))
                    
                    return True, f"Račun {iban} uspešno izbrisan"
        except Exception as e:
            return False, f"Napaka pri brisanju računa: {str(e)}"

    def update_racun_paket(self, iban, id_paket):
        """
        Spremeni paket za račun.
        
        Returns: (success: bool, message: str)
        """
        try:
            with get_connection():
                with Kazalec() as cur:
                    cur.execute("SELECT IBAN FROM racun WHERE IBAN = ?", (iban,))
                    if not cur.fetchone():
                        return False, "Račun ne obstaja"
                    
                    cur.execute("SELECT id_paket FROM paket WHERE id_paket = ?", (id_paket,))
                    if not cur.fetchone():
                        return False, "Paket ne obstaja"
                    
                    cur.execute("UPDATE racun SET id_paket = ? WHERE IBAN = ?", (id_paket, iban))
                    return True, "Paket uspešno spremenjen"
        except Exception as e:
            return False, f"Napaka: {str(e)}"

    # ==================== PAKETI (Admin) ====================

    def add_paket(self, tip, cena, osnovni_limit, dnevni_limit):
        """
        Dodaj nov paket.
        
        Returns: (success: bool, message: str, id_paket: int or None)
        """
        if not tip or len(tip.strip()) == 0:
            return False, "Tip paketa je obvezen", None
        if dnevni_limit is None:
            return False, "Dnevni limit je obvezen", None
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, da tip še ne obstaja
                    cur.execute("SELECT id_paket FROM paket WHERE tip = ?", (tip.strip(),))
                    if cur.fetchone():
                        return False, "Paket s tem tipom že obstaja", None
                    
                    cur.execute("""
                        INSERT INTO paket (tip, cena, osnovni_limit, dnevni_limit)
                        VALUES (?, ?, ?, ?)
                    """, (tip.strip(), cena, osnovni_limit, dnevni_limit))
                    
                    id_paket = cur.lastrowid
                    return True, f"Paket '{tip}' uspešno dodan", id_paket
        except Exception as e:
            return False, f"Napaka pri dodajanju paketa: {str(e)}", None

    def update_paket(self, id_paket, tip, cena, osnovni_limit, dnevni_limit):
        """
        Posodobi obstoječ paket.
        
        Returns: (success: bool, message: str)
        """
        if not tip or len(tip.strip()) == 0:
            return False, "Tip paketa je obvezen"
        if dnevni_limit is None:
            return False, "Dnevni limit je obvezen"
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    cur.execute("SELECT id_paket FROM paket WHERE id_paket = ?", (id_paket,))
                    if not cur.fetchone():
                        return False, "Paket ne obstaja"
                    
                    # Preveri, da tip ni zaseden pri drugem paketu
                    cur.execute("SELECT id_paket FROM paket WHERE tip = ? AND id_paket != ?", 
                               (tip.strip(), id_paket))
                    if cur.fetchone():
                        return False, "Paket s tem tipom že obstaja"
                    
                    cur.execute("""
                        UPDATE paket SET tip = ?, cena = ?, osnovni_limit = ?, dnevni_limit = ?
                        WHERE id_paket = ?
                    """, (tip.strip(), cena, osnovni_limit, dnevni_limit, id_paket))
                    
                    return True, "Paket uspešno posodobljen"
        except Exception as e:
            return False, f"Napaka pri posodabljanju paketa: {str(e)}"

    def delete_paket(self, id_paket):
        """
        Izbriši paket (samo če ni v uporabi).
        
        Returns: (success: bool, message: str)
        """
        try:
            with get_connection():
                with Kazalec() as cur:
                    cur.execute("SELECT id_paket FROM paket WHERE id_paket = ?", (id_paket,))
                    if not cur.fetchone():
                        return False, "Paket ne obstaja"
                    
                    # Preveri, da ni v uporabi
                    cur.execute("SELECT COUNT(*) FROM racun WHERE id_paket = ?", (id_paket,))
                    count = cur.fetchone()[0]
                    if count > 0:
                        return False, f"Paketa ni mogoče izbrisati — uporablja ga {count} račun(ov)"
                    
                    cur.execute("DELETE FROM paket WHERE id_paket = ?", (id_paket,))
                    return True, "Paket uspešno izbrisan"
        except Exception as e:
            return False, f"Napaka pri brisanju paketa: {str(e)}"
    
    def delete_stranka(self, id_stranke):
        """
        Izbriši stranko in vse njene račune ter transakcije
        
        Returns: (success: bool, message: str)
        """
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, če stranka obstaja
                    cur.execute("SELECT id_stranke FROM stranka WHERE id_stranke = ?", (id_stranke,))
                    if not cur.fetchone():
                        return False, "Stranka ne obstaja"
                    
                    # Pridobi vse račune stranke
                    cur.execute("SELECT IBAN FROM racun WHERE id_lastnik = ?", (id_stranke,))
                    ibans = [row[0] for row in cur.fetchall()]
                    
                    # Izbriši vse transakcije povezane z računi
                    for iban in ibans:
                        cur.execute("DELETE FROM transakcija WHERE posilja = ? OR prejema = ?", (iban, iban))
                    
                    # Izbriši vse račune
                    cur.execute("DELETE FROM racun WHERE id_lastnik = ?", (id_stranke,))
                    
                    # Izbriši uporabnika
                    cur.execute("DELETE FROM uporabnik WHERE id_stranke = ?", (id_stranke,))
                    
                    # Izbriši stranko
                    cur.execute("DELETE FROM stranka WHERE id_stranke = ?", (id_stranke,))
                    
                    return True, "Stranka in vsi povezani podatki uspešno izbrisani"
        except Exception as e:
            return False, f"Napaka pri brisanju stranke: {str(e)}"
    
    def update_stranka(self, id_stranke, ime, priimek, naslov, datum_rojstva):
        """
        Posodobi podatke stranke
        
        Returns: (success: bool, message: str)
        """
        if not ime or len(ime.strip()) == 0:
            return False, "Ime je obvezno"
        if not priimek or len(priimek.strip()) == 0:
            return False, "Priimek je obvezen"
        if not naslov or len(naslov.strip()) == 0:
            return False, "Naslov je obvezen"
        if not datum_rojstva:
            return False, "Datum rojstva je obvezen"
        
        try:
            with get_connection():
                with Kazalec() as cur:
                    # Preveri, če stranka obstaja
                    cur.execute("SELECT id_stranke FROM stranka WHERE id_stranke = ?", (id_stranke,))
                    if not cur.fetchone():
                        return False, "Stranka ne obstaja"
                    
                    cur.execute("""
                        UPDATE stranka 
                        SET ime = ?, priimek = ?, naslov = ?, datum_rojstva = ?
                        WHERE id_stranke = ?
                    """, (ime.strip(), priimek.strip(), naslov.strip(), datum_rojstva, id_stranke))
                    
                    return True, "Podatki stranke uspešno posodobljeni"
        except Exception as e:
            return False, f"Napaka pri posodabljanju stranke: {str(e)}"
