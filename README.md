# Slovenia Bank - bančni sistem

Seminarska naloga za predmet Podatkovne baze 1 (PB1).

Aplikacija omogoča delo z bančnimi strankami, računi, paketi in transakcijami prek spletnega vmesnika in tekstovnega vmesnika (CLI). Podatki so shranjeni v SQLite bazi `Banka.db`.

## Funkcionalnosti

**Stranka**
- prijava z uporabniškim imenom in geslom,
- pregled računov, stanja in zadnjih transakcij,
- nakazilo na drug račun,
- polog in dvig,
- pregled bančnih paketov.

**Administrator**
- pregled strank, računov, paketov in transakcij,
- dodajanje, urejanje in brisanje strank,
- dodajanje, brisanje in spreminjanje paketov računov,
- dodajanje in brisanje računov,
- urejanje paketov.

**Preverjanja in omejitve**
- preverjanje prijave in pravic dostopa,
- preverjanje lastništva računov pri uporabniških akcijah,
- preverjanje pozitivnih zneskov,
- preverjanje zadostnega stanja,
- dnevni limit za nakazila in dvige,
- limit posamezne transakcije glede na paket,
- preverjanje slovenskega IBAN-a po standardu ISO 7064 Mod 97-10,
- preverjanje datuma rojstva pri dodajanju ali urejanju stranke.

## Tehnologije

- Python 3
- Flask
- SQLite
- Bootstrap
- JavaScript

## Namestitev in zagon

```powershell
pip install -r requirements.txt
python model.py
python generate_demo_data.py
python app.py
```

Spletna aplikacija je dostopna na `http://localhost:5000`.

Tekstovni vmesnik zaženete z:

```powershell
python cli.py
```

## Prijava v demo okolje

Po zagonu `generate_demo_data.py` sta na voljo vsaj naslednja uporabnika:

| Vloga | Uporabniško ime | Geslo |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Stranka | `marko.novak` | `geslo123` |

Če bazo izbrišete ali ponovno ustvarite, je treba ponovno zagnati `python generate_demo_data.py`, da se ustvarijo demo stranke, računi, paketi, transakcije in uporabniški računi.

## Uporaba

**Nakazilo**
1. Prijavite se kot stranka.
2. Odprite stran **Nakazilo**.
3. Izberite račun pošiljatelja.
4. Vnesite IBAN prejemnika, znesek in po želji namen plačila.
5. Potrdite nakazilo.

**Polog ali dvig**
1. Na nadzorni plošči ali podrobnostih računa izberite polog oziroma dvig.
2. Izberite račun.
3. Vnesite znesek.
4. Potrdite transakcijo.

**Administracija**
1. Prijavite se kot `admin`.
2. V administratorskem delu urejate stranke, račune, pakete in pregledujete transakcije.
3. Pri dodajanju stranke lahko ustvarite tudi uporabniški račun za spletno prijavo.

## Struktura projekta

```text
SN/
├── app.py                 # Flask aplikacija in spletne poti
├── cli.py                 # Tekstovni vmesnik
├── model.py               # Ustvarjanje podatkovnega modela
├── services.py            # Poslovna logika za uporabnike, stranke, račune, pakete in transakcije
├── generate_demo_data.py  # Ustvari demo podatke
├── requirements.txt       # Python odvisnosti
├── templates/             # HTML predloge
├── static/                # CSS in JavaScript
└── Banka.db               # SQLite baza
```

Datoteka `generacijaPodatkov.py` ni več del projekta. Nadomešča jo `generate_demo_data.py`, ki ustvari demo podatke, skladne s trenutno shemo in validacijo IBAN-ov.

## Podatkovni model

Glavne tabele:

- `stranka`: osebni podatki stranke,
- `uporabnik`: podatki za prijavo in vloga,
- `racun`: IBAN, lastnik, paket in stanje,
- `paket`: cena, dnevni limit in limit posamezne transakcije,
- `transakcija`: pologi, dvigi, nakazila in opis transakcije.

Zneski so v bazi shranjeni v centih. IBAN je shranjen brez presledkov, v vmesnikih pa se prikaže v skupinah po štiri znake.

## Brisanje podatkov

Ob izbrisu stranke se izbrišejo tudi njen uporabniški račun, računi in transakcije, ki so povezane z njenimi računi. Enako se ob izbrisu posameznega računa izbrišejo transakcije tega računa. Ta pristop ohranja referenčno integriteto v trenutnem modelu, vendar izbriše tudi transakcije, kjer je sodeloval račun druge stranke.

## Odpravljanje težav

Če želite bazo ustvariti znova:

```powershell
Remove-Item Banka.db
python model.py
python generate_demo_data.py
```

Če so vrata 5000 zasedena, v zadnji vrstici `app.py` spremenite parameter `port`.

## Namen

Projekt je pripravljen za izobraževalni namen pri predmetu PB1.
