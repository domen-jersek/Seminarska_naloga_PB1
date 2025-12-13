# pip install bcrypt
import csv
import random
import string
from datetime import datetime, timedelta
import bcrypt

imena = ['Franc', ' Janez', 'Ana', ' Marko', 'Maja', ' Andrej', 'Irena', ' Ivan', 'Mojca', ' Luka', 'Nina', ' Anton', 'Mateja', ' Jože', 'Nataša', ' Matej', 'Eva', ' Peter', 'Andreja', ' Jožef', 'Sara', ' Tomaž', 'Barbara', ' Marjan', 'Petra', ' Milan', 'Anja', ' Aleš', 'Jožica', ' Rok', 'Katja', ' Bojan', 'Nika', ' Robert', 'Tina', ' Boštjan', 'Tanja', ' Branko', 'Tatjana', ' Miha', 'Vesna', ' Matjaž', 'Katarina', ' Gregor', 'Sonja', ' David', 'Alenka', ' Jan', 'Milena', ' Dejan', 'Urška', ' Martin', 'Martina', ' Igor', 'Majda', ' Nejc', 'Špela', ' Žiga', 'Tjaša', ' Boris', 'Ema', ' Žan', 'Lara', ' Jure', 'Darja', ' Dušan', 'Jožefa', ' Stanislav', 'Anica', ' Uroš', 'Helena', ' Blaž', 'Dragica', ' Matic', 'Neža', ' Mitja', 'Simona', ' Simon', 'Ivana', ' Jakob', 'Zala', ' Nik', 'Nada', ' Jaka', 'Kristina', ' Klemen', 'Suzana', ' Darko', 'Maša', ' Anže', 'Zdenka', ' Alojz', 'Lidija', ' Primož', 'Danica', ' Gašper', 'Marjeta', ' Jernej', 'Sabina', ' Aljaž', 'Olga', ' Filip', 'Janja', ' Aleksander', 'Lana', ' Denis', 'Frančiška', ' Tadej', 'Marta', ' Drago', 'Terezija', ' Miran', 'Karmen', ' Roman', 'Klara', ' Mark', 'Kaja', ' Matija', 'Vida', ' Tim', 'Hana', ' Damjan', 'Aleksandra', ' Tilen', 'Julija', ' Vid', 'Ivanka', ' Zoran', 'Silva', ' Borut', 'Darinka', ' Alen', 'Anita', ' Štefan', 'Veronika', 
' Vladimir', 'Lucija', ' Domen', 'Jana', ' Srečko', 'Lea', ' Goran', 'Brigita', ' Slavko', 'Metka', ' Janko', 'Antonija', ' Leon', 'Monika', ' Danijel', 'Ajda', ' Mirko', 'Natalija', ' Miroslav', 'Angela', ' Matevž', 'Jasmina', ' Lovro', 'Tamara', ' Urban', 'Cvetka', ' Maks', 'Manca', ' Andraž', 'Nevenka', ' Gal', 'Mia', ' Stanko', 'Renata', ' Jurij', 'Branka', ' Sašo', 'Marjana', ' Mihael', 'Saša', ' Dragan', 'Slavica', ' Iztok', 'Ljudmila', ' Benjamin', 'Stanislava', ' Erik', 'Zoja', ' Maj', 'Klavdija', ' Lan', 'Laura', ' Samo', 'Bojana', ' Viktor', 'Teja', ' Patrik', 'Ela', ' Anej', 'Alojzija', ' Vinko', 'Elizabeta', ' Marijan', 'Valentina'] 

priimki = ['Novak', 'Horvat', 'Kovačič', 'Krajnc', 'Zupančič', 'Kovač', 'Potočnik', 'Mlakar', 'Vidmar', 'Kos', 'Golob', 'Kralj', 'Turk', 'Božič', 'Korošec', 'Bizjak', 'Zupan', 'Kotnik', 'Hribar', 'Kavčič', 'Rozman', 'Kastelic', 'Oblak', 'Hočevar', 'Kolar', 'Petek', 'Žagar', 'Košir', 'Koren', 'Klemenčič', 'Zajc', 'Knez', 'Medved', 'Kovačević', 'Zupanc', 'Krasniqi', 'Petrič', 'Pirc', 'Hrovat', 'Lah', 'Kuhar', 'Pavlič', 'Petrović', 'Erjavec', 'Uršič', 'Zorko', 'Gashi', 'Hodžić', 'Tomažič', 'Babič', 'Rupnik', 'Jereb', 'Sever', 'Jerman', 'Kranjc', 'Pušnik', 'Dolenc', 'Breznik', 'Majcen', 'Perko', 'Močnik', 'Lesjak', 'Furlan', 'Jovanović', 'Vidic', 'Pavlin', 'Pečnik', 'Logar', 'Jenko', 'Ribič', 'Marolt', 'Žnidaršič', 'Jelen', 'Janežič', 'Pintar', 'Marković', 'Tomšič', 'Blatnik', 'Dolinar', 'Cerar', 'Černe', 'Hren', 'Mihelič', 'Maček', 'Fras', 'Kokalj', 'Gregorič', 'Ilić', 'Leban', 'Zadravec', 'Nikolić', 'Lešnik', 'Bezjak', 'Rus', 'Popović', 'Čeh', 'Vidovič', 'Bogataj', 'Kobal', 'Jug']

ulice = ['Bavdkova ulica', 'Dravska ulica', 'Kodrova ulica', 'Do proge', 'Borsetova ulica', 'Vogelna ulica', 'cesta XXVII', 'Miklavčeva ulica', 'Črnuška cesta', 'D', 'cesta XXII', 'Zvonarska ulica', 'Reška ulica', 'Pod vrbami', 'Černivčeva ulica', 'Cesta na Brod', 'Cesta Cirila Košmana', 'Vrhovci', 'Kikljeva ulica', 'Mivka', 'Mesarska cesta', 'Zgornje Gameljne', 'Gameljska cesta', 'Pod hrasti', 'Jurčkova cesta', 'Miklošičev park', 'Lampetova ulica', 'Cesta v Kleče', 'Ilešičeva ulica', 'cesta XXIV', 'O', 'Jarčeva ulica', 'Gradnikova ulica', 'Rozmanova ulica', 'Zgornja Besnica', 'Zabretova ulica', 'Krekov trg', 'Rožna dolina', 'Trg francoske revolucije', 'Stara Ježica', 'Nazorjeva ulica', 'Savinškova ulica', 'Hodoščkova ulica', 'Česnikova ulica', 'Ravnikova ulica', 'Triglavska ulica', 'Merosodna ulica', 'Nanoška ulica', 'Funtkova ulica', 'Toplarniška ulica', 'cesta XXX', 'Turnerjeva ulica', 'Skopska ulica', 'Parmska cesta', 'Peternelova ulica', 'Pot v mejah', 'Ulica bratov Miklič', 'Ložarjeva ulica', 'Veselova ulica', 'Pogačarjev trg', 'Strojeva ulica', 'Pilonova ulica', 'Trg Ajdovščina', 'Salkonecrova ulica', 'cesta XL', 'Bezenškova ulica', 'Hranilniška ulica', 'K reaktorju', 'Cesta v Zeleni log', 'Hladilniška pot', 'Cesta v Pesale', 'Livada', 'Bizovik', 'Apihova ulica', 'Vagajeva ulica', 'Švabićeva ulica', 'Ježa', 'U', 'Polje', 'Ulica Željka Tonija', 'Novo Polje', 'Medarska ulica', 'Rocenska ulica', 'Komacova ulica', 'Ribičičeva ulica', 'Dimičeva ulica', 'M', 'Osenjakova ulica', 'Kamniška ulica', 'Stanežiče', 'Za krajem', 'Kernova cesta', 'Gortanova ulica', 'Sostrska cesta', 'Tbilisijska ulica', 'Ajdovščina', 'Ulica bratov Komel', 'cesta V', 'Ulica Lili Novy', 'Obvozna cesta']

def random_ime(imena = imena):
    "vrne random ime"
    return random.choice(imena)

def random_priimek(priimek = priimki):
    "Vrne random priimek"
    return random.choice(priimek)

def random_naslov(ul = ulice):
    "Vrne random naslov"
    return random.choice(ul) + " " + str(random.randint(1, 100))

def random_datum(začetno=1950, končno=2007):
    """
    Vrne random pravilni datum oblike: 1985-12-03
    
    :param začetno: začetni datum
    :param končno: končni datum
    """
    return str(random.randint(začetno,končno)) + "-" + str(random.randint(1,12)) + "-" + str(random.randint(1,28))

def random_stanje(koef = 0.69, skala = 10000):
    """
    Vrne naključno stanje v centih po paretovi distribuciji -> intiger
    
    :param mini: minimalno centov
    :param maxi: maksimalno centov
    
    output primer: 132467
    
    povprečje: 17'949.14 € 
    minimum: 100.0 €
    maksimum: 3'6220'249.71 €
    
    """
    return int(random.paretovariate(koef)*skala)

def random_IBAN():
    """
    Vrne naključni slovenski IBAN
    
    output type str: SI56 2104 1452 2906 738
    """
    št = "0123456789"
    IBAN = "SI56"  + "".join(random.sample(št,4))  + "".join(random.sample(št,4))  + "".join(random.sample(št,4))  + "".join(random.sample(št,3))
    return IBAN

def random_cas(začetek=datetime(1950, 1, 1), konec=datetime.now()):
    """Generira random datetime med `začetek` and `konec`."""
    razlika = konec - začetek
    random_seconds = random.randint(0, int(razlika.total_seconds()))
    return (začetek + timedelta(seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")

def random_geslo(dolžina = 8):
    """
    generira random geslo
    
    :param dolžina: dolžina gesla
    """
    
    nabor = string.ascii_letters + string.digits + string.punctuation
    
    return "".join(random.sample(nabor, dolžina))

# for _ in range(20): print(random_geslo())
N_STRANK = 200
N_RACUNOV = 300  
N_PAKETOV = 150  
N_TRANSAKCIJ = 1000

# 1. STRANKE
stranke = []
id_stranke_št = 1

with open("podatki/stranka.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id_stranke", "ime", "priimek", "naslov", "datum_rojstva"])
    writer.writeheader()
    for _ in range(N_STRANK):
        ime = random_ime().strip()
        priimek = random_priimek().strip()
        if not ime or not priimek:
            continue
        naslov = random_naslov()
        datum_rojstva = random_datum()
        row = {
            "id_stranke": id_stranke_št,
            "ime": ime,
            "priimek": priimek,
            "naslov": naslov,
            "datum_rojstva": datum_rojstva
        }
        writer.writerow(row)
        stranke.append(id_stranke_št)
        id_stranke_št += 1

print(f"Stranke so")

# 2. RAČUNI
racuni = []  # list of IBANs

with open("podatki/racun.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["IBAN", "id_lastnik", "id_paket", "stanje"])
    writer.writeheader()
    for _ in range(N_RACUNOV):
        iban = random_IBAN()
        id_lastnik = random.choice(stranke)
        id_paket = random.randint(1,5)
        stanje = random_stanje()
        row = {
            "IBAN": iban,
            "id_lastnik": id_lastnik,
            "id_paket": id_paket,
            "stanje": stanje
        }
        writer.writerow(row)
        racuni.append(iban)

print("Računi so")

# 3. PAKETI
with open("podatki/paket.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id_paket", "tip", "cena", "osnovni_limit", "dnevni_limit"])
    writer.writeheader()
    # tip: [cena, osnovni limit, dnevni limit]
    paketi = {"študentski": [0, 20000, 150000], "premium": [1540, 400000, 200000], "osnovni": [599, 70000, 150000], "aktivni": [999, 150000, 150000], "digitalni": [99, None, 150000]}
    for i, tip in enumerate(paketi.keys()):
        cena = paketi[tip][0]
        osnovni_limit = paketi[tip][1]
        dnevni_limit = paketi[tip][2]
        row = {
            "id_paket": i+1,
            "tip": tip,
            "cena": cena,
            "osnovni_limit": osnovni_limit if osnovni_limit is not None else "", # "" pomeni: ni limita
            "dnevni_limit": dnevni_limit
        }
        writer.writerow(row)

print("Paketi so")

# 4. TRANSAKCIJE
with open("podatki/transakcija.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id_transakcije", "posilja", "prejema", "tip", "znesek", "cas"])
    writer.writeheader()
    
    for tid in range(1, N_TRANSAKCIJ + 1):
        tip = "polog"  # nič še dvigov, da ni negativno stanje
        znesek = random.randint(100, 500000)  # €1 to €5000
        cas = random_cas()
        posilja = "None" # potrebno posebej pretvorit ker Python glup
        prejema = random.choice(racuni)
        

        row = {
            "id_transakcije": tid,
            "posilja": posilja,
            "prejema": prejema,
            "tip": tip,
            "znesek": znesek,
            "cas": cas
        }
        writer.writerow(row)

print(f"Transakcije so")

print("\n🎉 Vsi CSV generirani v 'podatki/' folder.")
