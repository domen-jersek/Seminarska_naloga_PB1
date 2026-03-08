"""
CLI - Tekstovni vmesnik za Slovenia Bank
Omogoča interakcijo z banko preko ukazov v terminalu
"""

import sys
from services import BankService
from datetime import datetime

bank = BankService()

# Globalna spremenljivka za prijavljenega uporabnika
current_user = None
is_admin = False


def clear_screen():
    """Počisti terminal"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Izpiši glavo aplikacije"""
    print("=" * 60)
    print("🏦  SLOVENIA BANK - Tekstovni vmesnik  🏦".center(60))
    print("=" * 60)
    if current_user:
        role = "Administrator" if is_admin else "Stranka"
        if is_admin:
            print(f"Prijavljen: {role}")
        else:
            print(f"Prijavljen: {current_user.ime} {current_user.priimek} ({role})")
    print("=" * 60)
    print()


def print_menu():
    """Izpiši meni"""
    if not current_user:
        print("1. Prijava")
        print("2. Izhod")
    elif is_admin:
        print("1. Pregled vseh strank")
        print("2. Dodaj stranko")
        print("3. Izbriši stranko")
        print("4. Pregled vseh transakcij")
        print("5. Statistika sistema")
        print("6. Odjava")
        print("7. Izhod")
    else:
        print("1. Pregled računov")
        print("2. Pregled stanja računa")
        print("3. Nakazilo med računi")
        print("4. Polog na račun")
        print("5. Dvig z računa")
        print("6. Zgodovina transakcij")
        print("7. Odjava")
        print("8. Izhod")
    print()


def login():
    """Prijava uporabnika z uporabniškim imenom in geslom"""
    global current_user, is_admin
    
    print("\n--- PRIJAVA ---")
    uporabnisko_ime = input("Uporabniško ime: ").strip()
    geslo = input("Geslo: ").strip()
    
    success, user_data, message = bank.authenticate(uporabnisko_ime, geslo)
    
    if success:
        if user_data['vloga'] == 'admin':
            is_admin = True
            class Admin:
                id_stranke = 'admin'
            current_user = Admin()
            print("✅ Prijavljeni kot administrator!")
        else:
            stranka = bank.get_stranka(user_data['id_stranke'])
            if stranka:
                current_user = stranka
                is_admin = False
                print(f"✅ Prijavljeni kot {stranka.ime} {stranka.priimek}!")
            else:
                print("❌ Napaka: Stranka ne obstaja!")
    else:
        print(f"❌ {message}")
    
    input("\nPritisnite Enter za nadaljevanje...")


def logout():
    """Odjava uporabnika"""
    global current_user, is_admin
    current_user = None
    is_admin = False
    print("✅ Uspešno odjavljeni!")
    input("\nPritisnite Enter za nadaljevanje...")


# ==================== FUNKCIJE ZA STRANKE ====================

def view_accounts():
    """Pregled računov stranke"""
    print("\n--- MOJI RAČUNI ---")
    racuni = bank.get_racuni_stranke(current_user.id_stranke)
    
    if not racuni:
        print("Nimate računov.")
    else:
        print(f"\n{'IBAN':<40} {'Stanje':>15}")
        print("-" * 55)
        for racun in racuni:
            stanje_eur = racun['stanje'] / 100
            print(f"{racun['IBAN']:<40} {stanje_eur:>14.2f} €")
    
    input("\nPritisnite Enter za nadaljevanje...")


def view_account_balance():
    """Pregled stanja računa"""
    print("\n--- STANJE RAČUNA ---")
    racuni = bank.get_racuni_stranke(current_user.id_stranke)
    
    if not racuni:
        print("Nimate računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return
    
    print("\nVaši računi:")
    for i, racun in enumerate(racuni, 1):
        stanje_eur = racun['stanje'] / 100
        print(f"{i}. {racun['IBAN']} - {stanje_eur:.2f} €")
    
    try:
        izbira = int(input("\nIzberite račun (številka): ")) - 1
        if 0 <= izbira < len(racuni):
            racun = racuni[izbira]
            paket = bank.get_paket_za_racun(racun['IBAN'])
            
            print(f"\n{'='*55}")
            print(f"IBAN: {racun['IBAN']}")
            print(f"Stanje: {racun['stanje'] / 100:.2f} €")
            if paket:
                print(f"Paket: {paket['tip']}")
                print(f"Osnovni limit: {paket['osnovni_limit'] / 100 if paket['osnovni_limit'] else 'Neomejen'}")
                print(f"Dnevni limit: {paket['dnevni_limit'] / 100 if paket['dnevni_limit'] else 'Neomejen'}")
            print(f"{'='*55}")
        else:
            print("❌ Neveljavna izbira!")
    except ValueError:
        print("❌ Napaka: Vnesite številko!")
    
    input("\nPritisnite Enter za nadaljevanje...")


def make_transfer():
    """Nakazilo med računi"""
    print("\n--- NAKAZILO ---")
    racuni = bank.get_racuni_stranke(current_user.id_stranke)
    
    if not racuni:
        print("Nimate računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return
    
    print("\nVaši računi:")
    for i, racun in enumerate(racuni, 1):
        stanje_eur = racun['stanje'] / 100
        print(f"{i}. {racun['IBAN']} - {stanje_eur:.2f} €")
    
    try:
        izbira = int(input("\nIzbira računa za plačilo (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return
        
        from_iban = racuni[izbira]['IBAN']
        to_iban = input("IBAN prejemnika: ").strip()
        amount = float(input("Znesek (EUR): "))
        opis = input("Opis (opcijsko): ").strip() or None
        
        amount_cents = int(amount * 100)
        
        success, message = bank.create_transfer(from_iban, to_iban, amount_cents, opis)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")
    
    input("\nPritisnite Enter za nadaljevanje...")


def make_deposit():
    """Polog na račun"""
    print("\n--- POLOG ---")
    racuni = bank.get_racuni_stranke(current_user.id_stranke)
    
    if not racuni:
        print("Nimate računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return
    
    print("\nVaši računi:")
    for i, racun in enumerate(racuni, 1):
        stanje_eur = racun['stanje'] / 100
        print(f"{i}. {racun['IBAN']} - {stanje_eur:.2f} €")
    
    try:
        izbira = int(input("\nIzbira računa za polog (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return
        
        iban = racuni[izbira]['IBAN']
        amount = float(input("Znesek pologa (EUR): "))
        amount_cents = int(amount * 100)
        
        success, message = bank.create_deposit(iban, amount_cents)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")
    
    input("\nPritisnite Enter za nadaljevanje...")


def make_withdrawal():
    """Dvig z računa"""
    print("\n--- DVIG ---")
    racuni = bank.get_racuni_stranke(current_user.id_stranke)
    
    if not racuni:
        print("Nimate računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return
    
    print("\nVaši računi:")
    for i, racun in enumerate(racuni, 1):
        stanje_eur = racun['stanje'] / 100
        print(f"{i}. {racun['IBAN']} - {stanje_eur:.2f} €")
    
    try:
        izbira = int(input("\nIzbira računa za dvig (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return
        
        iban = racuni[izbira]['IBAN']
        amount = float(input("Znesek dviga (EUR): "))
        amount_cents = int(amount * 100)
        
        success, message = bank.create_withdrawal(iban, amount_cents)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")
    
    input("\nPritisnite Enter za nadaljevanje...")


def view_transactions():
    """Zgodovina transakcij"""
    print("\n--- ZGODOVINA TRANSAKCIJ ---")
    racuni = bank.get_racuni_stranke(current_user.id_stranke)
    
    if not racuni:
        print("Nimate računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return
    
    print("\nVaši računi:")
    for i, racun in enumerate(racuni, 1):
        print(f"{i}. {racun['IBAN']}")
    
    try:
        izbira = int(input("\nIzbira računa (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return
        
        iban = racuni[izbira]['IBAN']
        transakcije = bank.get_transactions_for_account(iban, limit=20)
        
        if not transakcije:
            print("\nNi transakcij.")
        else:
            print(f"\n{'Datum':<20} {'Tip':<15} {'Znesek':>12} {'Opis':<30}")
            print("-" * 80)
            for tr in transakcije:
                datum = tr['cas'][:16] if tr['cas'] else 'N/A'
                tip = tr['tip'].upper()
                znesek = tr['znesek'] / 100
                
                # Določi opis glede na tip
                if tr['tip'] == 'nakazilo':
                    if tr['posilja'] == iban:
                        opis = f"Nakazilo → {tr['prejema'][:20]}"
                    else:
                        opis = f"Prejeto ← {tr['posilja'][:20]}"
                elif tr['tip'] == 'polog':
                    opis = "Polog na račun"
                else:
                    opis = "Dvig z računa"
                
                # Barva glede na tip
                if tr['tip'] == 'nakazilo':
                    if tr['posilja'] == iban:
                        znak = '-'
                    else:
                        znak = '+'
                else:
                    znak = '+' if tr['tip'] == 'polog' else '-'
                
                print(f"{datum:<20} {tip:<15} {znak}{znesek:>11.2f} € {opis:<30}")
        
    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")
    
    input("\nPritisnite Enter za nadaljevanje...")


# ==================== FUNKCIJE ZA ADMIN ====================

def admin_view_customers():
    """Pregled vseh strank"""
    print("\n--- VSE STRANKE ---")
    stranke = bank.get_all_stranke()
    
    if not stranke:
        print("Ni strank.")
    else:
        print(f"\n{'ID':<6} {'Ime':<15} {'Priimek':<15} {'Naslov':<30} {'Računi':>8} {'Stanje':>12}")
        print("-" * 95)
        for stranka in stranke:
            print(f"{stranka['id_stranke']:<6} {stranka['ime']:<15} {stranka['priimek']:<15} "
                  f"{stranka['naslov']:<30} {stranka['stevilo_racunov']:>8} "
                  f"{stranka['skupno_stanje']/100:>11.2f} €")
    
    input("\nPritisnite Enter za nadaljevanje...")


def admin_add_customer():
    """Dodaj novo stranko"""
    print("\n--- DODAJ STRANKO ---")
    
    ime = input("Ime: ").strip()
    priimek = input("Priimek: ").strip()
    naslov = input("Naslov: ").strip()
    datum_rojstva = input("Datum rojstva (YYYY-MM-DD): ").strip()
    
    success, message, id_stranke = bank.add_stranka(ime, priimek, naslov, datum_rojstva)
    
    if success:
        print(f"✅ {message} (ID: {id_stranke})")
    else:
        print(f"❌ {message}")
    
    input("\nPritisnite Enter za nadaljevanje...")


def admin_delete_customer():
    """Izbriši stranko"""
    print("\n--- IZBRIŠI STRANKO ---")
    
    try:
        id_stranke = int(input("ID stranke za brisanje: "))
        
        stranka = bank.get_stranka(id_stranke)
        if not stranka:
            print("❌ Stranka ne obstaja!")
            input("\nPritisnite Enter za nadaljevanje...")
            return
        
        print(f"\n⚠️  POZOR: Želite izbrisati stranko:")
        print(f"   {stranka.ime} {stranka.priimek} (ID: {id_stranke})")
        print("   Izbrisani bodo tudi vsi računi in transakcije!")
        
        potrditev = input("\nSte prepričani? (da/ne): ").strip().lower()
        
        if potrditev == 'da':
            success, message = bank.delete_stranka(id_stranke)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("Brisanje preklicano.")
    
    except ValueError:
        print("❌ Napaka: Neveljaven ID!")
    
    input("\nPritisnite Enter za nadaljevanje...")


def admin_view_transactions():
    """Pregled vseh transakcij"""
    print("\n--- VSE TRANSAKCIJE ---")
    
    try:
        limit = input("Število transakcij (privzeto 50): ").strip()
        limit = int(limit) if limit else 50
        
        transakcije = bank.get_all_transactions(limit=limit)
        
        if not transakcije:
            print("Ni transakcij.")
        else:
            print(f"\n{'ID':<8} {'Datum':<20} {'Tip':<12} {'Od':<36} {'Za':<36} {'Znesek':>12}")
            print("-" * 130)
            for tr in transakcije:
                id_tr = tr['id_transakcije']
                datum = tr['cas'][:16] if tr['cas'] else 'N/A'
                tip = tr['tip'].upper()
                posilja = (tr['posilja'][:34] + '..') if tr['posilja'] and len(tr['posilja']) > 36 else (tr['posilja'] or '-')
                prejema = (tr['prejema'][:34] + '..') if tr['prejema'] and len(tr['prejema']) > 36 else (tr['prejema'] or '-')
                znesek = tr['znesek'] / 100
                
                print(f"{id_tr:<8} {datum:<20} {tip:<12} {posilja:<36} {prejema:<36} {znesek:>11.2f} €")
    
    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")
    
    input("\nPritisnite Enter za nadaljevanje...")


def admin_view_statistics():
    """Statistika sistema"""
    print("\n--- STATISTIKA SISTEMA ---")
    stats = bank.get_statistics()
    
    print(f"\n{'='*50}")
    print(f"Skupno strank: {stats['total_customers']}")
    print(f"Skupno računov: {stats['total_accounts']}")
    print(f"Skupno stanje vseh računov: {stats['total_balance']/100:.2f} €")
    print(f"Povprečno stanje računa: {stats['avg_balance']/100:.2f} €")
    print(f"Transakcij danes: {stats['transactions_today']}")
    print(f"Skupno transakcij: {stats['total_transactions']}")
    print(f"{'='*50}")
    
    input("\nPritisnite Enter za nadaljevanje...")


# ==================== GLAVNA ZANKA ====================

def main():
    """Glavna funkcija programa"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        try:
            if not current_user:
                izbira = input("Izbira: ").strip()
                
                if izbira == '1':
                    login()
                elif izbira == '2':
                    print("\n👋 Nasvidenje!")
                    sys.exit(0)
                else:
                    print("❌ Neveljavna izbira!")
                    input("\nPritisnite Enter za nadaljevanje...")
            
            elif is_admin:
                izbira = input("Izbira: ").strip()
                
                if izbira == '1':
                    admin_view_customers()
                elif izbira == '2':
                    admin_add_customer()
                elif izbira == '3':
                    admin_delete_customer()
                elif izbira == '4':
                    admin_view_transactions()
                elif izbira == '5':
                    admin_view_statistics()
                elif izbira == '6':
                    logout()
                elif izbira == '7':
                    print("\n👋 Nasvidenje!")
                    sys.exit(0)
                else:
                    print("❌ Neveljavna izbira!")
                    input("\nPritisnite Enter za nadaljevanje...")
            
            else:
                izbira = input("Izbira: ").strip()
                
                if izbira == '1':
                    view_accounts()
                elif izbira == '2':
                    view_account_balance()
                elif izbira == '3':
                    make_transfer()
                elif izbira == '4':
                    make_deposit()
                elif izbira == '5':
                    make_withdrawal()
                elif izbira == '6':
                    view_transactions()
                elif izbira == '7':
                    logout()
                elif izbira == '8':
                    print("\n👋 Nasvidenje!")
                    sys.exit(0)
                else:
                    print("❌ Neveljavna izbira!")
                    input("\nPritisnite Enter za nadaljevanje...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Nasvidenje!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Napaka: {e}")
            input("\nPritisnite Enter za nadaljevanje...")


if __name__ == "__main__":
    print("\n🏦 Dobrodošli v Slovenia Bank CLI! 🏦\n")
    input("Pritisnite Enter za začetek...")
    main()
