"""
Bančne storitve - vmesna plast med Flask aplikacijo in bazo podatkov
"""
from model import get_connection, Kazalec, Stranka, Racun, Paket, Transakcija
from datetime import datetime


class BankService:
    """Glavna razred za bančne storitve"""
    
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
                SELECT id_paket, tip, cena, osnovni_limit, dnevni_limit
                FROM paket
                WHERE id_racuna = ?
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
                FROM transkacija t
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
                FROM transkacija
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
                            FROM transkacija
                            WHERE posilja = ? 
                            AND tip = 'nakazilo'
                            AND DATE(cas) = DATE('now')
                        """, (from_iban,))
                        daily_total = cur.fetchone()[0]
                        
                        if daily_total + amount_cents > paket['dnevni_limit']:
                            return False, f"Presežen dnevni limit ({paket['dnevni_limit']/100:.2f} EUR)"
                    
                    # Izvedi transakcijo
                    cur.execute("""
                        INSERT INTO transkacija (posilja, prejema, tip, znesek)
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
                        INSERT INTO transkacija (posilja, prejema, tip, znesek)
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
                            FROM transkacija
                            WHERE posilja = ? 
                            AND tip = 'dvig'
                            AND DATE(cas) = DATE('now')
                        """, (iban,))
                        daily_total = cur.fetchone()[0]
                        
                        if daily_total + amount_cents > paket['dnevni_limit']:
                            return False, f"Presežen dnevni limit ({paket['dnevni_limit']/100:.2f} EUR)"
                    
                    # Izvedi dvig
                    cur.execute("""
                        INSERT INTO transkacija (posilja, prejema, tip, znesek)
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
                FROM transkacija
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
                SELECT COUNT(*) FROM transkacija 
                WHERE DATE(cas) = DATE('now')
            """)
            transactions_today = cur.fetchone()[0]
            
            # Število transakcij vse skupaj
            cur.execute("SELECT COUNT(*) FROM transkacija")
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
                        cur.execute("DELETE FROM transkacija WHERE posilja = ? OR prejema = ?", (iban, iban))
                    
                    # Izbriši vse pakete
                    for iban in ibans:
                        cur.execute("DELETE FROM paket WHERE id_racuna = ?", (iban,))
                    
                    # Izbriši vse račune
                    cur.execute("DELETE FROM racun WHERE id_lastnik = ?", (id_stranke,))
                    
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
