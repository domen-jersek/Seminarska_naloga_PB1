"""
CLI - Tekstovni vmesnik za Slovenia Bank
Omogoča interakcijo z banko preko ukazov v terminalu
"""

import sys
import os
from datetime import date, datetime
from services import BankService

bank = BankService()

# Globalna spremenljivka za prijavljenega uporabnika
current_user = None
is_admin = False


def clear_screen():
    """Počisti terminal"""
    os.system("cls" if os.name == "nt" else "clear")


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
        print("── STRANKE ──────────────")
        print("1. Pregled vseh strank")
        print("2. Dodaj stranko")
        print("3. Izbriši stranko")
        print("── RAČUNI ───────────────")
        print("4. Pregled vseh računov")
        print("5. Dodaj račun stranki")
        print("6. Izbriši račun")
        print("7. Spremeni paket računa")
        print("── PAKETI ───────────────")
        print("8. Pregled vseh paketov")
        print("9. Dodaj paket")
        print("10. Uredi paket")
        print("11. Izbriši paket")
        print("── OSTALO ───────────────")
        print("12. Pregled vseh transakcij")
        print("13. Statistika sistema")
        print("14. Odjava")
        print("15. Izhod")
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
        if user_data["vloga"] == "admin":
            is_admin = True

            class Admin:
                id_stranke = "admin"

            current_user = Admin()
            print("✅ Prijavljeni kot administrator!")
        else:
            stranka = bank.get_stranka(user_data["id_stranke"])
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


def preveri_datum_rojstva(datum_str):
    """
    Preveri veljavnost datuma rojstva.
    Vrne (veljavno: bool, sporocilo: str).
    """
    try:
        dt = datetime.strptime(datum_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Neveljaven datum. Uporabite obliko LLLL-MM-DD (npr. 1990-05-20)."

    danes = date.today()
    if dt >= danes:
        return False, "Datum rojstva ne sme biti v prihodnosti."
    if dt.year < 1900:
        return False, "Datum rojstva je prezgodnji."

    return True, ""


def format_iban(iban):
    """Formatiraj IBAN v skupine po štiri znake."""
    cisti = "".join(c for c in str(iban) if c.isalnum()).upper()
    return " ".join(cisti[i : i + 4] for i in range(0, len(cisti), 4))


def format_datum(cas):
    """Formatiraj datum transakcije za izpis v CLI."""
    if not cas:
        return "N/A"
    try:
        return datetime.fromisoformat(cas.replace(" ", "T")).strftime("%d. %m. %Y %H:%M")
    except ValueError:
        return cas[:16]


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
            stanje_eur = racun["stanje"] / 100
            print(f"{format_iban(racun['IBAN']):<40} {stanje_eur:>14.2f} €")

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
        stanje_eur = racun["stanje"] / 100
        print(f"{i}. {format_iban(racun['IBAN'])} - {stanje_eur:.2f} €")

    try:
        izbira = int(input("\nIzberite račun (številka): ")) - 1
        if 0 <= izbira < len(racuni):
            racun = racuni[izbira]
            paket = bank.get_paket_za_racun(racun["IBAN"])

            print(f"\n{'='*55}")
            print(f"IBAN:   {format_iban(racun['IBAN'])}")
            print(f"Stanje: {racun['stanje'] / 100:.2f} €")
            if paket:
                print(f"Paket:  {paket['tip']}")
                if paket["osnovni_limit"]:
                    print(f"Limit posamezne transakcije: {paket['osnovni_limit'] / 100:.2f} €")
                else:
                    print("Limit posamezne transakcije: brez")
                if paket["dnevni_limit"]:
                    print(f"Dnevni limit:   {paket['dnevni_limit'] / 100:.2f} €")
                else:
                    print("Dnevni limit:   neomejen")
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
        stanje_eur = racun["stanje"] / 100
        print(f"{i}. {format_iban(racun['IBAN'])} - {stanje_eur:.2f} €")

    try:
        izbira = int(input("\nIzbira računa za plačilo (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        from_iban = racuni[izbira]["IBAN"]
        to_iban = input("IBAN prejemnika: ").strip()
        amount = float(input("Znesek (EUR): "))
        opis = input("Namen plačila (opcijsko): ").strip() or None

        amount_cents = int(amount * 100)

        success, message = bank.create_transfer(from_iban, to_iban, amount_cents, opis)

        if success:
            print(f"✅ {message}")
            racun_posodobljen = bank.get_racun(from_iban)
            if racun_posodobljen:
                novo_stanje = racun_posodobljen["stanje"] / 100
                print(f"   Novo stanje na vašem računu: {novo_stanje:.2f} €")
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
        stanje_eur = racun["stanje"] / 100
        print(f"{i}. {format_iban(racun['IBAN'])} - {stanje_eur:.2f} €")

    try:
        izbira = int(input("\nIzbira računa za polog (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        iban = racuni[izbira]["IBAN"]
        amount = float(input("Znesek pologa (EUR): "))
        amount_cents = int(amount * 100)
        opis = input("Opis pologa (opcijsko): ").strip() or None

        success, message = bank.create_deposit(iban, amount_cents, opis)

        if success:
            print(f"✅ {message}")
            # Prikaži novo stanje
            racun_posodobljen = bank.get_racun(iban)
            if racun_posodobljen:
                novo_stanje = racun_posodobljen["stanje"] / 100
                print(f"   Novo stanje: {novo_stanje:.2f} €")
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
        stanje_eur = racun["stanje"] / 100
        print(f"{i}. {format_iban(racun['IBAN'])} - {stanje_eur:.2f} €")

    try:
        izbira = int(input("\nIzbira računa za dvig (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        iban = racuni[izbira]["IBAN"]
        amount = float(input("Znesek dviga (EUR): "))
        amount_cents = int(amount * 100)
        opis = input("Opis dviga (opcijsko): ").strip() or None

        success, message = bank.create_withdrawal(iban, amount_cents, opis)

        if success:
            print(f"✅ {message}")
            # Prikaži novo stanje
            racun_posodobljen = bank.get_racun(iban)
            if racun_posodobljen:
                novo_stanje = racun_posodobljen["stanje"] / 100
                print(f"   Novo stanje: {novo_stanje:.2f} €")
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
        print(f"{i}. {format_iban(racun['IBAN'])}")

    try:
        izbira = int(input("\nIzbira računa (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        iban = racuni[izbira]["IBAN"]
        transakcije = bank.get_transactions_for_account(iban, limit=20)

        if not transakcije:
            print("\nNi transakcij.")
        else:
            print(f"\n{'Datum':<20} {'Tip':<12} {'Znesek':>12}  {'Opis':<30}")
            print("-" * 80)
            for tr in transakcije:
                datum = format_datum(tr["cas"])
                tip = tr["tip"].upper()
                znesek = tr["znesek"] / 100

                if tr["tip"] == "nakazilo":
                    if tr["posilja"] == iban:
                        znak = "-"
                        smer = f"→ {format_iban(tr['prejema'])}"
                    else:
                        znak = "+"
                        smer = f"← {format_iban(tr['posilja'])}"
                elif tr["tip"] == "polog":
                    znak = "+"
                    smer = "Polog na račun"
                else:
                    znak = "-"
                    smer = "Dvig z računa"

                # Prikaži namen plačila, če obstaja
                opis_prikaz = tr.get("opis") or smer

                print(f"{datum:<20} {tip:<12} {znak}{znesek:>11.2f} €  {opis_prikaz:<30}")

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
        print(
            f"\n{'ID':<6} {'Ime':<15} {'Priimek':<15} {'Naslov':<30} {'Računi':>8} {'Stanje':>12}"
        )
        print("-" * 95)
        for stranka in stranke:
            print(
                f"{stranka['id_stranke']:<6} {stranka['ime']:<15} {stranka['priimek']:<15} "
                f"{stranka['naslov']:<30} {stranka['stevilo_racunov']:>8} "
                f"{stranka['skupno_stanje']/100:>11.2f} €"
            )

    input("\nPritisnite Enter za nadaljevanje...")


def admin_add_customer():
    """Dodaj novo stranko"""
    print("\n--- DODAJ STRANKO ---")

    ime = input("Ime: ").strip()
    priimek = input("Priimek: ").strip()
    naslov = input("Naslov: ").strip()

    # Preverjanje datuma rojstva
    while True:
        datum_rojstva = input("Datum rojstva (LLLL-MM-DD, npr. 1990-05-20): ").strip()
        veljaven, napaka = preveri_datum_rojstva(datum_rojstva)
        if veljaven:
            break
        print(f"❌ {napaka}")

    # Avtomatično ustvari uporabniški račun
    uporabnisko_ime = input(
        "Uporabniško ime za dostop do spleta (opcijsko, Enter za preskočitev): "
    ).strip()
    geslo = None
    if uporabnisko_ime:
        geslo = input("Geslo (vsaj 4 znake): ").strip()

    success, message, id_stranke = bank.add_stranka(ime, priimek, naslov, datum_rojstva)

    if success:
        print(f"✅ {message} (ID: {id_stranke})")
        # Ustvari uporabniški račun, če je bilo podano
        if uporabnisko_ime and geslo:
            ok, msg = bank.create_uporabnik(uporabnisko_ime, geslo, id_stranke, "stranka")
            if ok:
                print(f"✅ Uporabniški račun '{uporabnisko_ime}' uspešno ustvarjen.")
            else:
                print(f"⚠️  Stranka dodana, a napaka pri ustvarjanju uporabniškega računa: {msg}")
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

        if potrditev == "da":
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
            print(
                f"\n{'ID':<8} {'Datum':<20} {'Tip':<12} {'Od':<22} {'Za':<22} {'Znesek':>12}"
            )
            print("-" * 103)
            for tr in transakcije:
                id_tr = tr["id_transakcije"]
                datum = format_datum(tr["cas"])
                tip = tr["tip"].upper()
                posilja = tr["posilja"] or "-"
                prejema = tr["prejema"] or "-"
                znesek = tr["znesek"] / 100

                print(
                    f"{id_tr:<8} {datum:<20} {tip:<12} {posilja:<22} {prejema:<22} {znesek:>11.2f} €"
                )

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_view_statistics():
    """Statistika sistema"""
    print("\n--- STATISTIKA SISTEMA ---")
    stats = bank.get_statistics()

    print(f"\n{'='*50}")
    print(f"Skupno strank:                {stats['total_customers']}")
    print(f"Skupno računov:               {stats['total_accounts']}")
    print(f"Skupno stanje vseh računov:   {stats['total_balance']/100:.2f} €")
    print(f"Povprečno stanje računa:      {stats['avg_balance']/100:.2f} €")
    print(f"Transakcij danes:             {stats['transactions_today']}")
    print(f"Skupno transakcij:            {stats['total_transactions']}")
    print(f"{'='*50}")

    input("\nPritisnite Enter za nadaljevanje...")


# ==================== ADMIN - RAČUNI ====================


def admin_view_accounts():
    """Pregled vseh računov"""
    print("\n--- VSI RAČUNI ---")
    racuni = bank.get_all_racuni()

    if not racuni:
        print("Ni računov.")
    else:
        print(f"\n{'IBAN':<22} {'Lastnik':<25} {'Paket':<12} {'Stanje':>12}")
        print("-" * 75)
        for r in racuni:
            lastnik = f"{r['ime_lastnika']} {r['priimek_lastnika']}"
            stanje_eur = r["stanje"] / 100
            print(f"{format_iban(r['IBAN']):<22} {lastnik:<25} {r['paket_tip']:<12} {stanje_eur:>11.2f} €")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_add_account():
    """Dodaj nov račun stranki"""
    print("\n--- DODAJ RAČUN ---")

    # Prikaži stranke
    stranke = bank.get_all_stranke()
    if not stranke:
        print("❌ Ni strank v sistemu.")
        input("\nPritisnite Enter za nadaljevanje...")
        return

    print("\nStranke:")
    for s in stranke:
        print(f"  {s['id_stranke']:>4}. {s['ime']} {s['priimek']}")

    # Prikaži pakete
    paketi = bank.get_all_paketi()
    print("\nPaketi:")
    for p in paketi:
        limit = f"{p['dnevni_limit']/100:.0f} €/dan" if p["dnevni_limit"] else "brez limita"
        cena = f"{p['cena']/100:.2f} €/mes" if p["cena"] else "brezplačen"
        print(f"  {p['id_paket']:>4}. {p['tip']:<12} {cena:<18} dnevni limit: {limit}")

    try:
        id_lastnik = int(input("\nID stranke: "))
        id_paket = int(input("ID paketa: "))
        stanje_vnos = input("Začetno stanje v EUR (privzeto 0): ").strip()
        stanje_eur = float(stanje_vnos) if stanje_vnos else 0.0
        stanje_cents = int(stanje_eur * 100)

        # Generiraj veljaven IBAN
        iban = bank.generate_iban()
        if not iban:
            print("❌ Ni mogoče generirati IBAN-a.")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        print(f"\nGeneriran IBAN: {format_iban(iban)}")
        potrditev = input("Ustvariti ta račun? (da/ne): ").strip().lower()

        if potrditev == "da":
            success, message = bank.add_racun(iban, id_lastnik, id_paket, stanje_cents)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("Ustvarjanje preklicano.")

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_delete_account():
    """Izbriši račun"""
    print("\n--- IZBRIŠI RAČUN ---")

    racuni = bank.get_all_racuni()
    if not racuni:
        print("Ni računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return

    print(f"\n{'#':<4} {'IBAN':<22} {'Lastnik':<25} {'Stanje':>12}")
    print("-" * 65)
    for i, r in enumerate(racuni, 1):
        lastnik = f"{r['ime_lastnika']} {r['priimek_lastnika']}"
        print(f"{i:<4} {format_iban(r['IBAN']):<22} {lastnik:<25} {r['stanje']/100:>11.2f} €")

    try:
        izbira = int(input("\nIzberite račun (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        racun = racuni[izbira]
        print(f"\n⚠️  POZOR: Izbrisali boste račun {format_iban(racun['IBAN'])}")
        print(f"   Lastnik: {racun['ime_lastnika']} {racun['priimek_lastnika']}")
        print(f"   Stanje: {racun['stanje']/100:.2f} €")
        print("   Izbrisane bodo tudi vse transakcije tega računa!")

        potrditev = input("\nSte prepričani? (da/ne): ").strip().lower()
        if potrditev == "da":
            success, message = bank.delete_racun(racun["IBAN"])
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("Brisanje preklicano.")

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_change_package():
    """Spremeni paket računa"""
    print("\n--- SPREMENI PAKET RAČUNA ---")

    racuni = bank.get_all_racuni()
    if not racuni:
        print("Ni računov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return

    print(f"\n{'#':<4} {'IBAN':<22} {'Lastnik':<25} {'Paket':<12}")
    print("-" * 65)
    for i, r in enumerate(racuni, 1):
        lastnik = f"{r['ime_lastnika']} {r['priimek_lastnika']}"
        print(f"{i:<4} {format_iban(r['IBAN']):<22} {lastnik:<25} {r['paket_tip']:<12}")

    paketi = bank.get_all_paketi()
    print("\nDostopni paketi:")
    for p in paketi:
        limit = f"{p['dnevni_limit']/100:.0f} €/dan" if p["dnevni_limit"] else "brez limita"
        cena = f"{p['cena']/100:.2f} €/mes" if p["cena"] else "brezplačen"
        print(f"  {p['id_paket']:>4}. {p['tip']:<12} {cena:<18} dnevni limit: {limit}")

    try:
        izbira = int(input("\nIzberite račun (številka): ")) - 1
        if not (0 <= izbira < len(racuni)):
            print("❌ Neveljavna izbira!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        id_paket = int(input("ID novega paketa: "))
        success, message = bank.update_racun_paket(racuni[izbira]["IBAN"], id_paket)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

    input("\nPritisnite Enter za nadaljevanje...")


# ==================== ADMIN - PAKETI ====================


def admin_view_packages():
    """Pregled vseh paketov"""
    print("\n--- VSI PAKETI ---")
    paketi = bank.get_all_paketi()

    if not paketi:
        print("Ni paketov.")
    else:
        print(f"\n{'ID':<6} {'Tip':<14} {'Cena/mes':>10} {'Dnevni limit':>14}")
        print("-" * 48)
        for p in paketi:
            cena = f"{p['cena']/100:.2f} €" if p["cena"] else "brezpl."
            dnevni = f"{p['dnevni_limit']/100:.2f} €" if p["dnevni_limit"] else "brez"
            print(f"{p['id_paket']:<6} {p['tip']:<14} {cena:>10} {dnevni:>14}")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_add_package():
    """Dodaj nov paket"""
    print("\n--- DODAJ PAKET ---")

    tip = input("Tip paketa (npr. Gold): ").strip()
    if not tip:
        print("❌ Tip je obvezen!")
        input("\nPritisnite Enter za nadaljevanje...")
        return

    try:
        cena_vnos = input("Mesečna cena v EUR (0 za brezplačen): ").strip()
        cena_cents = int(float(cena_vnos) * 100) if cena_vnos else 0

        osnov_vnos = input("Limit posamezne transakcije v EUR (prazno = brez limita): ").strip()
        osnov_cents = int(float(osnov_vnos) * 100) if osnov_vnos else None

        dnevni_vnos = input("Dnevni limit v EUR: ").strip()
        if not dnevni_vnos:
            print("❌ Dnevni limit je obvezen!")
            input("\nPritisnite Enter za nadaljevanje...")
            return
        dnevni_cents = int(float(dnevni_vnos) * 100)

        success, message, id_paket = bank.add_paket(tip, cena_cents, osnov_cents, dnevni_cents)
        if success:
            print(f"✅ {message} (ID: {id_paket})")
        else:
            print(f"❌ {message}")

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_edit_package():
    """Uredi obstoječ paket"""
    print("\n--- UREDI PAKET ---")

    paketi = bank.get_all_paketi()
    if not paketi:
        print("Ni paketov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return

    print(f"\n{'ID':<6} {'Tip':<14} {'Cena/mes':>10} {'Dnevni limit':>14}")
    print("-" * 48)
    for p in paketi:
        cena = f"{p['cena']/100:.2f} €" if p["cena"] else "brezpl."
        dnevni = f"{p['dnevni_limit']/100:.2f} €" if p["dnevni_limit"] else "brez"
        print(f"{p['id_paket']:<6} {p['tip']:<14} {cena:>10} {dnevni:>14}")

    try:
        id_paket = int(input("\nID paketa za urejanje: "))

        stari = next((p for p in paketi if p["id_paket"] == id_paket), None)
        if not stari:
            print("❌ Paket ne obstaja!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        print(f"\nUrejanje paketa '{stari['tip']}' (Enter = obdrži staro vrednost):")

        tip_vnos = input(f"Tip [{stari['tip']}]: ").strip()
        tip = tip_vnos if tip_vnos else stari["tip"]

        stara_cena_eur = stari["cena"] / 100 if stari["cena"] else 0
        cena_vnos = input(f"Cena v EUR [{stara_cena_eur:.2f}]: ").strip()
        cena_cents = int(float(cena_vnos) * 100) if cena_vnos else stari["cena"]

        stari_osnov = stari["osnovni_limit"] / 100 if stari["osnovni_limit"] else ""
        osnov_vnos = input(
            f"Limit posamezne transakcije v EUR [{stari_osnov if stari_osnov else 'brez'}]: "
        ).strip()
        if osnov_vnos == "":
            osnov_cents = stari["osnovni_limit"]
        elif osnov_vnos.lower() in ("brez", "0"):
            osnov_cents = None
        else:
            osnov_cents = int(float(osnov_vnos) * 100)

        stari_dnevni = stari["dnevni_limit"] / 100 if stari["dnevni_limit"] else 0
        dnevni_vnos = input(f"Dnevni limit v EUR [{stari_dnevni:.2f}]: ").strip()
        dnevni_cents = (
            int(float(dnevni_vnos) * 100) if dnevni_vnos else stari["dnevni_limit"]
        )

        success, message = bank.update_paket(id_paket, tip, cena_cents, osnov_cents, dnevni_cents)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

    input("\nPritisnite Enter za nadaljevanje...")


def admin_delete_package():
    """Izbriši paket"""
    print("\n--- IZBRIŠI PAKET ---")

    paketi = bank.get_all_paketi()
    if not paketi:
        print("Ni paketov.")
        input("\nPritisnite Enter za nadaljevanje...")
        return

    print(f"\n{'ID':<6} {'Tip':<14}")
    print("-" * 22)
    for p in paketi:
        print(f"{p['id_paket']:<6} {p['tip']:<14}")

    try:
        id_paket = int(input("\nID paketa za brisanje: "))
        paket = next((p for p in paketi if p["id_paket"] == id_paket), None)
        if not paket:
            print("❌ Paket ne obstaja!")
            input("\nPritisnite Enter za nadaljevanje...")
            return

        print(f"\n⚠️  POZOR: Izbrisali boste paket '{paket['tip']}'.")
        print("   Paket je mogoče izbrisati le, če ni v uporabi!")

        potrditev = input("Ste prepričani? (da/ne): ").strip().lower()
        if potrditev == "da":
            success, message = bank.delete_paket(id_paket)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("Brisanje preklicano.")

    except ValueError:
        print("❌ Napaka: Neveljaven vnos!")

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

                if izbira == "1":
                    login()
                elif izbira == "2":
                    print("\n👋 Nasvidenje!")
                    sys.exit(0)
                else:
                    print("❌ Neveljavna izbira!")
                    input("\nPritisnite Enter za nadaljevanje...")

            elif is_admin:
                izbira = input("Izbira: ").strip()

                if izbira == "1":
                    admin_view_customers()
                elif izbira == "2":
                    admin_add_customer()
                elif izbira == "3":
                    admin_delete_customer()
                elif izbira == "4":
                    admin_view_accounts()
                elif izbira == "5":
                    admin_add_account()
                elif izbira == "6":
                    admin_delete_account()
                elif izbira == "7":
                    admin_change_package()
                elif izbira == "8":
                    admin_view_packages()
                elif izbira == "9":
                    admin_add_package()
                elif izbira == "10":
                    admin_edit_package()
                elif izbira == "11":
                    admin_delete_package()
                elif izbira == "12":
                    admin_view_transactions()
                elif izbira == "13":
                    admin_view_statistics()
                elif izbira == "14":
                    logout()
                elif izbira == "15":
                    print("\n👋 Nasvidenje!")
                    sys.exit(0)
                else:
                    print("❌ Neveljavna izbira!")
                    input("\nPritisnite Enter za nadaljevanje...")

            else:
                izbira = input("Izbira: ").strip()

                if izbira == "1":
                    view_accounts()
                elif izbira == "2":
                    view_account_balance()
                elif izbira == "3":
                    make_transfer()
                elif izbira == "4":
                    make_deposit()
                elif izbira == "5":
                    make_withdrawal()
                elif izbira == "6":
                    view_transactions()
                elif izbira == "7":
                    logout()
                elif izbira == "8":
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
