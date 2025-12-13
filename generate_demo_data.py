"""
Generiranje demo podatkov za testiranje bančnega sistema
"""
import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('Banka.db')
cur = conn.cursor()

def clear_data():
    """Pobriši vse obstoječe podatke"""
    print("🗑️  Brisanje starih podatkov...")
    cur.execute("DELETE FROM transkacija")
    cur.execute("DELETE FROM paket")
    cur.execute("DELETE FROM racun")
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
        cur.execute("""
            INSERT INTO stranka (ime, priimek, naslov, datum_rojstva)
            VALUES (?, ?, ?, ?)
        """, (ime, priimek, naslov, datum))
    
    conn.commit()
    print(f"   ✅ Ustvarjenih {len(stranke)} strank")

def generate_racuni():
    """Generiraj demo račune"""
    print("💳 Generiranje računov...")
    
    # Pridobi ID-je strank
    cur.execute("SELECT id_stranke FROM stranka")
    stranke_ids = [row[0] for row in cur.fetchall()]
    
    racuni = []
    for idx, id_stranke in enumerate(stranke_ids, start=1):
        # Vsaka stranka dobi 1-2 računa
        num_accounts = random.randint(1, 2)
        for i in range(num_accounts):
            # Generiraj IBAN - točno 34 znakov
            # Format: SI56 (4 znaki) + 30 številk = 34 znakov
            # Slovenski IBAN: SI56 + 5 številk banke + 8 številk računa + 3 kontrolne številke
            bank_code = f"{1000+idx:04d}{i:01d}"  # 5 številk
            account_num = f"{random.randint(10000000,99999999):08d}"  # 8 številk
            check_digits = f"{random.randint(100,999):03d}"  # 3 številke
            # Dodaj še 14 dodatnih številk da pridemo do 30 skupaj (5+8+3+14=30)
            additional = f"{random.randint(10000000000000,99999999999999):014d}"
            iban = f"SI56{bank_code}{account_num}{check_digits}{additional}"  # 4 + 30 = 34
            stanje = random.randint(10000, 500000)  # 100-5000 EUR v centih
            racuni.append((iban, id_stranke, stanje))
    
    cur.executemany("""
        INSERT INTO racun (IBAN, id_lastnik, stanje)
        VALUES (?, ?, ?)
    """, racuni)
    
    conn.commit()
    print(f"   ✅ Ustvarjenih {len(racuni)} računov")

def generate_paketi():
    """Generiraj demo pakete"""
    print("📦 Generiranje paketov...")
    
    # Pridobi vse IBAN-e
    cur.execute("SELECT IBAN FROM racun")
    ibans = [row[0] for row in cur.fetchall()]
    
    paketi_tipi = [
        ("Basic", 0, 50000, 10000),
        ("Premium", 599, 500000, 100000),
        ("Business", 1999, None, 1000000),
    ]
    
    paketi = []
    for idx, iban in enumerate(ibans, start=1):
        # Naključno izberi paket
        tip, cena, osnovni_limit, dnevni_limit = random.choice(paketi_tipi)
        paketi.append((idx, iban, tip, cena, osnovni_limit, dnevni_limit))
    
    cur.executemany("""
        INSERT INTO paket (id_paket, id_racuna, tip, cena, osnovni_limit, dnevni_limit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, paketi)
    
    conn.commit()
    print(f"   ✅ Ustvarjenih {len(paketi)} paketov")

def generate_transakcije():
    """Generiraj demo transakcije"""
    print("💸 Generiranje transakcij...")
    
    # Pridobi vse IBAN-e
    cur.execute("SELECT IBAN FROM racun")
    ibans = [row[0] for row in cur.fetchall()]
    
    transakcije = []
    
    # Pologi
    for _ in range(10):
        iban = random.choice(ibans)
        znesek = random.randint(5000, 50000)
        cas = datetime.now() - timedelta(days=random.randint(1, 30))
        transakcije.append((None, iban, 'polog', znesek, cas))
    
    # Dvigi
    for _ in range(8):
        iban = random.choice(ibans)
        znesek = random.randint(2000, 10000)
        cas = datetime.now() - timedelta(days=random.randint(1, 30))
        transakcije.append((iban, None, 'dvig', znesek, cas))
    
    # Nakazila
    for _ in range(15):
        from_iban = random.choice(ibans)
        to_iban = random.choice([i for i in ibans if i != from_iban])
        znesek = random.randint(1000, 20000)
        cas = datetime.now() - timedelta(days=random.randint(1, 30))
        transakcije.append((from_iban, to_iban, 'nakazilo', znesek, cas))
    
    cur.executemany("""
        INSERT INTO transkacija (posilja, prejema, tip, znesek, cas)
        VALUES (?, ?, ?, ?, ?)
    """, transakcije)
    
    # Posodobi stanja računov glede na transakcije
    cur.execute("""
        UPDATE racun SET stanje = (
            SELECT 
                r.stanje +
                COALESCE((SELECT SUM(znesek) FROM transkacija WHERE prejema = r.IBAN AND tip IN ('polog', 'nakazilo', 'obresti')), 0) -
                COALESCE((SELECT SUM(znesek) FROM transkacija WHERE posilja = r.IBAN AND tip IN ('dvig', 'nakazilo')), 0)
            FROM racun r
            WHERE r.IBAN = racun.IBAN
        )
    """)
    
    conn.commit()
    print(f"   ✅ Ustvarjenih {len(transakcije)} transakcij")

def show_summary():
    """Prikaži povzetek podatkov"""
    print("\n📊 Povzetek generiranih podatkov:")
    print("=" * 50)
    
    cur.execute("SELECT COUNT(*) FROM stranka")
    print(f"   Stranke: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM racun")
    print(f"   Računi: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM paket")
    print(f"   Paketi: {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM transkacija")
    print(f"   Transakcije: {cur.fetchone()[0]}")
    
    cur.execute("SELECT SUM(stanje) FROM racun")
    total = cur.fetchone()[0] or 0
    print(f"   Skupno stanje: {total/100:.2f} EUR")
    
    print("=" * 50)
    
    # Primer strank za prijavo
    cur.execute("SELECT id_stranke, ime, priimek FROM stranka LIMIT 3")
    print("\n🔐 Primer prijav:")
    for id_stranke, ime, priimek in cur.fetchall():
        print(f"   ID: {id_stranke} - {ime} {priimek}")
    print(f"   ID: admin - Administrator")

if __name__ == "__main__":
    print("🏦 Generiranje demo podatkov za Slovenia Bank\n")
    
    try:
        # Pobriši stare podatke
        clear_data()
        
        # Generiraj nove podatke
        generate_stranke()
        generate_racuni()
        generate_paketi()
        generate_transakcije()
        
        # Prikaži povzetek
        show_summary()
        
        print("\n✅ Demo podatki uspešno generirani!")
        print("\n🚀 Zdaj lahko zaženete: python app.py")
        
    except Exception as e:
        print(f"\n❌ Napaka: {e}")
        conn.rollback()
    finally:
        conn.close()
