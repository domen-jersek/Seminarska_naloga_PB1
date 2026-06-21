# Slovenia Bank - Bančni Sistem

Seminarska naloga za predmet Podatkovne Baze 1 (PB1).

Popolnoma funkcionalen bančni sistem z modernim spletnim vmesnikom (frontend) in zaledjem (backend) za upravljanje računov, transakcij, paketov in strank.

---

## Vsebina

- [Značilnosti](#-značilnosti)
- [Tehnologije](#-tehnologije)
- [Namestitev](#-namestitev)
- [Zagon aplikacije](#-zagon-aplikacije)
- [Uporaba](#-uporaba)
- [Struktura projekta](#-struktura-projekta)
- [Končne točke API-ja](#-končne-točke-api-ja)
- [Podatkovni model](#-podatkovni-model)

---

## Značilnosti

**Uporabnik**
- Prijava z ID ali uporabniškim imenom + geslom
- Nadzorna plošča s stanjem računov
- Upravljanje računov + zgodovina transakcij
- Nakazila, pologi, dvigi
- Bančni paketi z različnimi limiti

**Administrator**
- Admin nadzorna plošča s statistiko
- Upravljanje strank in pregled vseh transakcij

**Varnost**
- Preverjanje lastništva računov
- Dnevni limiti transakcij
- Preverjanje zadostnih sredstev
- Validacija IBAN
- Upravljanje sej

---

## Tehnologije

Python 3.8+, Flask 3.0, SQLite3, Bootstrap 5.3, JavaScript (Fetch API)

---

## Namestitev

1. Klonirajte repozitorij:
   git clone https://github.com/domen-jersek/Seminarska_naloga_PB1

2. Namestite potrebne pakete:
   pip install -r requirements.txt

3. Ustvarite bazo:
   python model.py

4. (Opcijsko) Generirajte testne podatke:
   python generate_demo_data.py

---

## Zagon

```powershell
python app.py
```

Aplikacija na: **http://localhost:5000**

---

## Uporaba

### Prijava

**Stranka**
1. Odprite http://localhost:5000
2. Vnesite uporabniško ime (npr. `marko.novak`) ali ID stranke
3. Vnesite geslo (`geslo123`)
4. Kliknite Prijava

**Administrator**
1. Odprite http://localhost:5000
2. Uporabniško ime: `admin`, geslo: `admin123`
3. Kliknite Prijava

### Testni podatki

| Vrsta | Uporabniško ime | Geslo |
|-------|----------------|-------|
| Stranka | `marko.novak` | `geslo123` |
| Administrator | `admin` | `admin123` |

### Primeri uporabe

#### Prenos denarja
1. Pojdite na **Nakazilo**
2. Izberite račun pošiljatelja
3. Vnesite IBAN prejemnika
4. Vnesite znesek
5. Kliknite **Izvedi nakazilo**

#### Polog ali dvig
1. Na **Nadzorni plošči** kliknite **Polog** ali **Dvig**
2. Izberite račun
3. Vnesite znesek
4. Potrdite

---

## Struktura projekta

```
SN/
│
├── app.py                      # Glavna Flask aplikacija
├── model.py                    # Podatkovni model in ORM
├── services.py                 # Poslovna logika in storitve
├── generacijaPodatkov.py       # Generator testnih podatkov
├── requirements.txt            # Python odvisnosti
├── README.md                   # Ta dokument
│
├── Banka.db                    # SQLite baza podatkov
│
├── templates/                  # HTML predloge (Jinja2)
│   ├── base.html              # Osnovna predloga
│   ├── login.html             # Prijava
│   ├── dashboard.html         # Nadzorna plošča
│   ├── accounts.html          # Seznam računov
│   ├── account_detail.html    # Detajli računa
│   ├── transfer.html          # Nakazila
│   ├── packages.html          # Bančni paketi
│   │
│   └── admin/                 # Admin predloge
│       ├── dashboard.html     # Admin nadzorna plošča
│       ├── customers.html     # Seznam strank
│       └── transactions.html  # Seznam transakcij
│
└── static/                     # Statične datoteke
    ├── css/
    │   └── style.css          # CSS stili
    └── js/
        └── main.js            # JavaScript
```

---

## Končne točke API-ja

- `GET /` – Domača stran (preusmeritev)
- `GET/POST /login` – Prijava
- `GET /logout` – Odjava

**Uporabniške (zaščitene)**
- `GET /dashboard` – Nadzorna plošča
- `GET /accounts` – Seznam računov
- `GET /account/<iban>` – Detajli računa
- `GET/POST /transfer` – Nakazilo
- `POST /deposit` – Polog
- `POST /withdraw` – Dvig
- `GET /packages` – Bančni paketi

**Administratorske (zaščitene)**
- `GET /admin` – Admin nadzorna plošča
- `GET /admin/customers` – Seznam strank
- `GET /admin/transactions` – Seznam transakcij

**API**
- `GET /api/account/<iban>/balance` – Stanje računa

---

## Podatkovni model

### Tabele

#### `stranka`
- `id_stranke` (PRIMARY KEY)
- `ime`
- `priimek`
- `naslov`
- `datum_rojstva`

#### `racun`
- `IBAN` (PRIMARY KEY, 34 znakov)
- `id_lastnik` (FOREIGN KEY → stranka)
- `stanje` (v centih)

#### `paket`
- `id_paket` (PRIMARY KEY)
- `id_racuna` (FOREIGN KEY → racun)
- `tip` (Basic, Premium, Business)
- `cena` (v centih)
- `transakcijski_limit` (v centih)
- `dnevni_limit` (v centih)

#### `transkacija`
- `id_transakcije` (PRIMARY KEY)
- `posilja` (FOREIGN KEY → racun, NULL za polog)
- `prejema` (FOREIGN KEY → racun, NULL za dvig)
- `tip` (polog, dvig, nakazilo, obresti)
- `znesek` (v centih)
- `cas` (DATETIME)

### Omejitve (Constraints)
- IBAN mora biti natanko 34 znakov
- Ime, priimek, naslov ne smejo biti prazni
- Znesek mora biti pozitiven
- Tip transakcije mora biti veljaven
- Polog: `posilja = NULL`, `prejema ≠ NULL`
- Dvig: `posilja ≠ NULL`, `prejema = NULL`
- Nakazilo: `posilja ≠ NULL`, `prejema ≠ NULL`, `posilja ≠ prejema`

---


## Varnost

- Upravljanje sej s Flask sejami
- Dekoratorji za zahtevano prijavo in administratorske pravice
- Preverjanje lastništva računov
- Validacija vnosnih podatkov
- SQL injection zaščita (parametrizirane poizvedbe)
- CSRF zaščita (preko Flask seje)

---

## Odpravljanje težav

### Baza se ne ustvari
```powershell
Remove-Item Banka.db
python model.py
```

### vrata 5000 so zasedena
```powershell
python app.py --port 5001
```

Ali v `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Napaka pri uvozu modula
```powershell
$env:PYTHONPATH="."
python app.py
```

---

## Razvoj

Aplikacija sledi **tristopenjski arhitekturi**:

| Nivo | Datoteka | Vloga |
|------|----------|-------|
| Pogled | `app.py` | Flask poti (routes), upravljanje sej, renderiranje predlog |
| Storitev | `services.py` | Razred `BankService` – poslovna logika, validacija, transakcije |
| Podatki | `model.py` | Definicije tabel, ORM, upravljanje povezav z bazo |

**Dodajanje funkcionalnosti:**

1. **Nova stran** – Dodajte pot v `app.py` z zaščitnimi dekoratorji (`@login_required`, `@admin_required`). Uporabite obstoječe predloge iz `templates/` ali ustvarite novo.
2. **Nova poslovna operacija** – Implementirajte metodo v `services.py` (npr. avtomatsko polog obresti, mesečno poročilo). Preverite omejitve in pravice uporabnika.
3. **Sprememba podatkovnega modela** – Posodobite tabele v `model.py`, nato ponovno ustvarite bazo. Posodobite ustrezne metode v `services.py`.
4. **UI prilagoditve** – CSS v `static/css/style.css`, JavaScript interakcije v `static/js/main.js` (npr. dinamična validacija IBAN pred pošiljanjem).

---

## Licenca

Izobraževalni namen – predmet PB1.

---

**Uživajte v uporabi Slovenia Bank sistema!**
