# Leola broneerimine: veebilehelt Google Sheetsi

Klient täidab veebilehel vormi. Google Apps Script võtab broneeringu vastu ja kirjutab selle Google'i tabelisse.
Apps Script on tasuta ja töötab sinu Google'i konto all. Omanik näeb kõiki broneeringuid ühest tabelist, ka
telefonis Google Sheetsi äpis.

Vorm küsib samalt scriptilt ka vabu aegu. Kui aeg on juba võetud, ei näe teine klient seda enam ja kaks inimest ei
saa sama aega kinni panna. Arvesse lähevad ka käsitsi lisatud broneeringud, juuksurite tööpäevad ja puhkused.

Veebilehele ei lähe tabelist kunagi klientide nimesid ega numbreid, ainult juuksurite nimed ja vabad kellaajad.

Failid:

- `Code.gs`: script, mis kleebitakse Google'i tabeli juurde.
- `../veebileht/index.html`: veebileht, mille vorm saadab broneeringud scriptile.

## Paigaldamine (üks kord, umbes 15 minutit)

### 1. Tabel ja script

1. Ava brauseris **sheets.new**. See teeb uue tühja tabeli. Pane nimeks näiteks „Leola broneeringud”.

   Tee see salongi omaniku Google'i kontoga, sest tabel ja script jäävad selle konto alla. Kui teed oma kontoga,
   jaga tabel hiljem omanikuga: **Jaga** → tema e-post → **Toimetaja**.
2. Ava menüüst **Laiendused → Apps Script** (inglise keeles *Extensions → Apps Script*). Avaneb koodiaken.
3. Kustuta sealt olemasolev kood (`function myFunction() { … }`) ja kleebi asemele kogu faili `Code.gs` sisu.
   Salvesta: kettaikoon või Ctrl+S. Vasakul üleval saad projekti nimeks panna „Leola broneerimine”.
4. Mine tagasi tabeli kaardile ja laadi leht uuesti (F5). Mõne sekundi pärast tekib menüüribale **Broneerimine**.
5. Vali **Broneerimine → Seadista tabel**. Esimesel korral küsib Google luba:
   - **Continue** (Jätka), siis vali oma konto.
   - Kui tuleb hoiatus „Google hasn't verified this app”, vali **Advanced** (Täpsemalt), siis
     **Go to Leola broneerimine (unsafe)** ja lõpuks **Allow** (Luba).

   See hoiatus tuleb alati, kui script on sinu enda tehtud. Script pääseb ligi ainult sellele ühele tabelile.
   E-kirja saadab see ainult siis, kui netibroneerimine läheb spämmi tõttu pausile, ja ainult sulle.

   Pärast loa andmist vali uuesti **Broneerimine → Seadista tabel**. Tabelisse tekivad lehed
   **Ülevaade, Broneeringud, Juuksurid, Puudumised** ja **Blokeeritud**.
6. Ava leht **Juuksurid** ja vaata see üle:
   - Nimed on praegu Rita, Maire, Kaire, Laine, Hele ja Reelika. Kui on veel keegi, lisa uus rida.
   - Iga nädalapäeva all: `x` = töötab terve päeva, `8-12` = ainult need tunnid, tühi = ei tööta.
   - Mobiil võib esialgu tühjaks jääda. Seda läheb vaja järgmises etapis SMSide jaoks.

### 2. Avalda script veebis

1. Apps Scripti aknas paremal üleval: sinine nupp **Deploy → New deployment**.
2. „Select type” kõrval hammasratas → **Web app**.
3. Pane:
   - **Execute as: Me**
   - **Who has access: Anyone**

   „Anyone” tähendab, et veebilehe külastaja saab broneeringu saata ilma Google'isse sisse logimata. Tabelit ennast
   ei näe keegi peale sinu ja nende, kellega sa selle jagad.
4. Vajuta **Deploy** ja kopeeri **Web app URL**. See algab `https://script.google.com/macros/s/` ja lõpeb `/exec`.

Kontrolliks ava see aadress brauseris. Ekraanile peaks tulema tekst, mis algab nii:
`{"ok":true,"paused":false,"stylists":["Rita",…`

### 3. Ühenda veebileht

1. Ava veebilehe kaustas fail `index.html` tekstiredaktoriga (Notepad, TextEdit vms, mitte Wordiga).
2. Otsi (Ctrl+F): `const BOOKING_ENDPOINT = "";`
3. Kleebi aadress jutumärkide vahele:
   `const BOOKING_ENDPOINT = "https://script.google.com/macros/s/…/exec";`
4. Salvesta ja laadi kaust uuesti üles sinna, kus leht praegu on.

Kui tahad, saada aadress mulle ja panen selle ise sisse.

### 4. Proovi järele

Tee lehel broneering oma mobiilinumbriga. Lehele **Broneeringud** tekib uus rida. Kui avad vormi uuesti, ei pakuta
seda aega selle juuksuri juures enam. Pärast proovi muuda rea staatus **Tühistatud** peale või kustuta rida.

## Igapäevane kasutamine

| Mida teha | Kuidas |
|---|---|
| Näha kõiki tulevasi aegu | Leht **Ülevaade** näitab neid kuupäeva ja kellaaja järgi. Lahtrist B1 saad valida ühe juuksuri. |
| Telefoni või Messengeri teel kokku lepitud aeg | Lisa lehele **Broneeringud** uus rida: kuupäev, kell, juuksur, klient. Siis kaob see aeg ka veebilehelt. |
| Tühistamine | Muuda veerus **Staatus** väärtuseks **Tühistatud**. Aeg vabaneb veebilehel kohe. |
| Klient ei tulnud | Veerus **Tuli?** vali **Ei tulnud**. Hiljem näed, kes kipub ära jääma. |
| Puhkus, haigus, koolitus | Leht **Puudumised**: juuksur, alates, kuni. Kui kogu salong on kinni (näiteks riigipühal), kirjuta juuksuri asemele **Kõik**. |
| Tööajad | Leht **Juuksurid**. |
| Uus juuksur | Lisa uus rida lehele **Juuksurid**. Ta ilmub veebilehe vormi ise, `index.html` faili muutma ei pea. |
| Juuksuri oma link | `https://SINU-LEHT/?juuksur=Maire#broneeri` avab vormi nii, et Maire on juba valitud. Sobib Messengeri kiirvastuseks. |

Kui klient valib **Pole vahet**, paneb script ta selle juuksuri juurde, kes on sel kellaajal vaba ja kellel on sel
päeval kõige vähem kliente. Kinnituses näeb klient, kelle juurde ta läheb. Tabelis saab juuksurit hiljem muuta.

## Kaitse võltsbroneeringute eest

Script teeb ise järgmist:

- Võtab vastu ainult Eesti mobiilinumbreid.
- Ühel numbril saab korraga olla kuni 2 tulevast aega.
- Vormis on peidetud lõksuväli. Inimene seda ei näe, aga robot täidab selle ja siis ei salvestata midagi.
- Kui 10 minuti jooksul on tulnud juba 6 broneeringut, paneb script netibroneerimise pausile ja saadab sulle e-kirja.
  Vorm ütleb siis külastajale, et aja saab kinni panna telefonil.

Sinu teha on see:

- **Võlts rida:** vali see rida lehel **Broneeringud**, siis **Broneerimine → Blokeeri valitud rea number**.
  See number ei saa enam netis broneerida ja tema tulevased ajad märgitakse tühistatuks.
- **Pausilt maha:** **Broneerimine → Ava netibroneerimine**.
- **Ise pausile** (näiteks puhkuse ajaks): **Broneerimine → Peata netibroneerimine**.

Piire (2 aega numbri kohta, 6 broneeringut 10 minutiga) saab muuta faili `Code.gs` alguses.

## Kui midagi muudad

- Lahtiolekuajad on kahes kohas: `index.html` (`HOURS`) ja `Code.gs` (`OPENING_HOURS`). Muuda mõlemas.
- Pärast `Code.gs` muutmist tuleb avaldada uus versioon: **Deploy → Manage deployments** → pliiatsi ikoon →
  **Version: New version** → **Deploy**. Aadress jääb samaks. Kui uut versiooni ei tee, töötab edasi vana kood.

## Järgmised etapid

1. **SMS juuksurile** iga uue broneeringu kohta: millal, mis teenus, klient ja tema number. Selleks on vaja
   Messente kontot ja kokkulepet, kes SMSide eest maksab, ning juuksurite numbreid lehel **Juuksurid**.
2. **Meeldetuletus kliendile** päev varem SMSiga.
3. **Hommikune päevakava** igale juuksurile SMSiga.
4. Kui spämm siiski läbi tuleb: Cloudflare Turnstile (nähtamatu robotikontroll) või SMS-koodiga kinnitus.
