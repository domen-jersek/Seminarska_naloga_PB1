# 🏦 Slovenia Bank - Bančni Sistem

Seminarska naloga za predmet Podatkovne Baze 1 (PB1).

Popolnoma funkcionalen bančni sistem z modernim spletnim vmesnikom (frontend) in zaledjem (backend) za upravljanje računov, transakcij, paketov in strank.

---

## 📋 Vsebina

- [Značilnosti](#-značilnosti)
- [Tehnologije](#-tehnologije)
- [Namestitev](#-namestitev)
- [Zagon aplikacije](#-zagon-aplikacije)
- [Uporaba](#-uporaba)
- [Struktura projekta](#-struktura-projekta)
- [API Endpoints](#-api-endpoints)
- [Podatkovni model](#-podatkovni-model)

---

## ✨ Značilnosti

### Uporabniške funkcionalnosti
- 🔐 **Prijava** - Enostavna prijava z uporabniškim imenom in geslom stranke
- 📊 **Nadzorna plošča** - Pregled vseh računov in stanja
- 💳 **Upravljanje računov** - Pregled detajlov računa in zgodovine transakcij
- 💸 **Nakazila** - Prenos denarja med računi
- 💰 **Pologi in dvigi** - Dodajanje ali dvig denarja
- 📦 **Bančni paketi** - Različni paketi z različnimi limiti
- 🔄 **Zgodovina transakcij** - Popoln pregled vseh transakcij

### Admin funkcionalnosti
- 📈 **Admin dashboard** - Statistika in pregled sistema
- 👥 **Upravljanje strank** - Pregled vseh strank in njihovih računov
- 📝 **Pregled transakcij** - Vse transakcije v sistemu
- 📊 **Statistika** - Številke in analitika poslovanja

### Varnostne funkcionalnosti
- ✅ Preverjanje lastništva računov
- ✅ Dnevni limiti transakcij
- ✅ Preverjanje zadostnih sredstev
- ✅ Validacija IBAN številk
- ✅ Session management

---

## 🛠 Tehnologije

### Backend
- **Python 3.8+**
- **Flask 3.0** - Web framework
- **SQLite3** - Relacijska baza podatkov
- **Werkzeug** - WSGI utilities

### Frontend
- **HTML5/CSS3**
- **Bootstrap 5.3** - Responsive design
- **Bootstrap Icons** - Ikone
- **JavaScript (Vanilla)** - Interaktivnost
- **Fetch API** - AJAX calls

---

## 📥 Namestitev

### 1. Klonirajte repozitorij ali prenesite datoteke


### 2. Namestite potrebne Python pakete

```powershell
pip install -r requirements.txt
```

### 3. Ustvarite bazo podatkov

Če baza `Banka.db` še ne obstaja, jo ustvarite:

```powershell
python model.py
```

To bo ustvarilo prazno bazo z vsemi tabelami.

### 4. Generirajte testne podatke (opcijsko)

Če želite generirati testne podatke strank, računov in transakcij:

```powershell
python generate_demo_data.py
```

---

## 🚀 Zagon aplikacije

### Zagon Flask strežnika

```powershell
python app.py
```

Aplikacija bo dostopna na: **http://localhost:5000**

### Alternativa - Debug način

Za development mode z avtomatskim reloadom:

```powershell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run
```

---

## 💻 Uporaba

### Prijava kot stranka

1. Odprite **http://localhost:5000** v brskalniku
2. Vnesite **ID stranke** (npr. `1`, `2`, `3`, ...)
3. Kliknite **Prijava**

### Prijava kot administrator

1. Odprite **http://localhost:5000**
2. Vnesite `admin` kot ID
3. Dostop do admin panela

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

## 📁 Struktura projekta

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
│   ├── transfer.html          # Nakazilo
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

## 🔌 API Endpoints

### Javni endpoints
- `GET /` - Domača stran (redirect)
- `GET/POST /login` - Prijava
- `GET /logout` - Odjava

### Uporabniški endpoints (zaščiteno)
- `GET /dashboard` - Nadzorna plošča
- `GET /accounts` - Seznam računov
- `GET /account/<iban>` - Detajli računa
- `GET/POST /transfer` - Nakazilo
- `POST /deposit` - Polog
- `POST /withdraw` - Dvig
- `GET /packages` - Bančni paketi

### Admin endpoints (admin zaščita)
- `GET /admin` - Admin dashboard
- `GET /admin/customers` - Seznam strank
- `GET /admin/transactions` - Seznam transakcij

### API endpoints
- `GET /api/account/<iban>/balance` - Stanje računa

---

## 🗄 Podatkovni model

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
- `osnovni_limit` (v centih)
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


## 🔒 Varnost

### Implementirane funkcije
- Session management s Flask sessions
- Login required decorators
- Admin required decorators
- Preverjanje lastništva računov
- Validacija vnosnih podatkov
- SQL injection zaščita (parametrizirane poizvedbe)
- CSRF zaščita (preko Flask session)


## 🧪 Testiranje

### Testni podatki

Če uporabljate `generacijaPodatkov.py`, dobite:
- Naključne stranke s slovenskimi imeni in priimki
- IBAN račune v slovenskem formatu
- Različna stanja računov (Pareto distribucija)
- Testne transakcije

### Primer testne prijave
```
ID stranke: 1
ID stranke: 2
ID stranke: 3
...
Admin: admin
```

---

## 📊 Funkcionalnosti po modulih

### `app.py` - Flask aplikacija
- Routing in view funkcije
- Session management
- Template rendering
- Error handling
- Template filters (centi_v_eure, format_iban, format_datum)

### `services.py` - Poslovna logika
- `BankService` class
- CRUD operacije za stranke, račune, pakete
- Transakcijske funkcije (transfer, deposit, withdrawal)
- Validacija in preverjanje limitov
- Admin statistika

### `model.py` - Podatkovni model
- Definicije tabel (dataclass)
- Ustvarjanje in brisanje tabel
- Uvoz podatkov iz CSV
- Kazalec (cursor) management
- Foreign keys omogočeni

---

## 🐛 Troubleshooting

### Baza se ne ustvari
```powershell
# Pobrišite staro bazo in ustvarite novo
Remove-Item Banka.db
python model.py
```

### Port 5000 je zaseden
```powershell
# Uporabite drug port
python app.py --port 5001
```

Ali v `app.py` spremenite:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Napaka pri importu modula
```powershell
# Preverite Python pot
$env:PYTHONPATH="."
python app.py
```

---

## 📝 Razvoj

### Dodajanje nove funkcionalnosti

1. **Backend** - Dodajte route v `app.py`
2. **Service** - Dodajte metodo v `services.py`
3. **Frontend** - Ustvarite/posodobite template
4. **Styling** - Dodajte CSS v `style.css`
5. **JavaScript** - Dodajte logiko v `main.js`


## 📄 Licenca

Projekt je namenjen za izobraževalne namene v okviru predmeta PB1.

---

**Uživajte v uporabi Slovenia Bank sistema! 🏦**
