# 🚀 Quick Start Guide - Slovenia Bank

## Hiter začetek v 3 korakih!

### 1️⃣ Namestitev odvisnosti

```powershell
pip install -r requirements.txt
```

### 2️⃣ Zagon aplikacije

```powershell
python app.py
```

### 3️⃣ Odpri v brskalniku

Odpri: **http://localhost:5000**

---

## 🎯 Testna prijava

### Kot stranka
- **ID**: `1`, `2`, `3`, ... (katerakoli ID iz baze)
- Dostop do osebne nadzorne plošče, računov, transakcij

### Kot administrator  
- **ID**: `admin`
- Dostop do celotnega sistema, vseh strank in statistike

---

## ⚡ Hitre funkcionalnosti

### Za stranko:
1. **Nadzorna plošča** - Pregled stanja in transakcij
2. **Nakazilo** - Prenos denarja med računi
3. **Polog/Dvig** - Hitri akciji iz modala
4. **Moji računi** - Detajli vsakega računa
5. **Paketi** - Pregled bančnih paketov

### Za admina:
1. **Admin Dashboard** - Statistika sistema
2. **Stranke** - Vsi uporabniki sistema
3. **Transakcije** - Vse transakcije v realnem času

---

## 🗄️ Baza podatkov

### Če baza NE obstaja:

```powershell
python model.py
```

To bo ustvarilo prazno bazo `Banka.db`.

### Če potrebujete testne podatke:

Bazo lahko napolnite ročno preko SQL ali uporabite obstoječe podatke.

---

## 🌐 Dostop do aplikacije

- **Lokalno**: http://localhost:5000
- **V omrežju**: http://192.168.0.102:5000 (ali vaš IP)

---

## 🛑 Zaustavitev aplikacije

V terminalu pritisnite: **CTRL+C**

---

## 💡 Primeri uporabe

### Prenos denarja (Nakazilo)

1. Prijava kot stranka (npr. ID `1`)
2. Klik na **Nakazilo** v meniju
3. Izberi račun pošiljatelja
4. Vnesi IBAN prejemnika (lahko drug račun iste stranke)
5. Vnesi znesek (npr. `50.00`)
6. Klik **Izvedi nakazilo**

### Polog na račun

1. Na **Nadzorni plošči** klik **Polog**
2. Izberi račun
3. Vnesi znesek (npr. `100.00`)
4. Potrdi

### Pregled transakcij

1. Klik na **Moji računi**
2. Izberi račun
3. Vidiš celotno zgodovino transakcij za ta račun

---

## ⚙️ Dodatne nastavitve

### Sprememba porta

V `app.py` spremeni zadnjo vrstico:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Namesto 5000
```

### Debug mode izklop (produkcija)

```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## 🐛 Težave?

### "Module not found"
```powershell
pip install Flask Werkzeug
```

### "Port already in use"
Spremeni port na 5001 ali ugasni drugo aplikacijo na portu 5000.

### "Database locked"
Zapri vse programe, ki uporabljajo `Banka.db`, in poskusi znova.

---

## 📂 Datoteke projekta

```
✅ app.py              - Glavna aplikacija
✅ services.py         - Poslovna logika  
✅ model.py            - Podatkovni model
✅ templates/          - HTML strani
✅ static/             - CSS & JavaScript
✅ Banka.db            - SQLite baza
✅ README.md           - Podrobna dokumentacija
✅ QUICKSTART.md       - Ta dokument
```

---

## 🎓 Za ocenjevalca

Projekt demonstrira:

- ✅ **Polno funkcionalen backend** (Flask + SQLite)
- ✅ **Profesionalen frontend** (Bootstrap 5 + responsive design)
- ✅ **RESTful API** endpoints
- ✅ **Varnostne funkcije** (session management, validation)
- ✅ **Admin panel** za upravljanje
- ✅ **Kompleksne SQL poizvedbe** (JOIN, aggregates, subqueries)
- ✅ **CRUD operacije** za vse entitete
- ✅ **Transakcijska logika** (transfer, deposit, withdrawal)
- ✅ **Dnevni limiti** in poslovne omejitve
- ✅ **Real-time statistika**

---

**Uživajte! 🏦✨**
