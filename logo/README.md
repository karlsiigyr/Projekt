# Leola meestejuuksur: logo

Siin on kaks valmis suunda:

- **A-klassik**: nimi klassikalises kirjafondis (Pinyon Script), all MEESTEJUUKSUR ja VILJANDI.
- **B-kaarid**: nimi Bodoni kaldkirjas, kus L-täht on ühtlasi avatud käärid. See on edasi arendatud
  inspiratsioonipildist ja on minu soovitus.

Kõik variandid koos ukse- ja veebinäidisega näed, kui avad brauseris faili **`eelvaade.html`**.

## Kaustad

```
A-klassik/ ja B-kaarid/
  leola-…-must.svg / -valge.svg / -kuld.svg    põhilogo
  leola-…-nimi-….svg                           ainult nimi (veebi päis, väikesed kohad)
  leola-…-vertikaalne-….svg                    kitsas riba uksel või aknal, loetakse ülevalt alla
  leola-…-pitser-….svg                         ümmargune märk (kleebis, tempel, kinkekaart)
  leola-…-L-….svg                              L-märk (favicon, väga väikesed kohad)
  png/                                         samad failid PNG-na, läbipaistva taustaga
  favicon/                                     favicon.ico, favicon.svg, apple-touch-icon.png, icon-192/512.png
  sotsiaalmeedia/                              profiilipilt 1080×1080, lingi jagamispilt 1200×630
eelvaated/                                     ukse ja veebilehe näidispildid
allikas/                                       lähtekood ja fondid, millega kõik failid tehtud on
```

SVG on vektorfail, seda saab suurendada ükskõik kui suureks ilma, et kvaliteet kaoks. Kui mõni programm
SVG-d ei ava (Word, osa telefonirakendusi), kasuta `png/` kausta faile.

## Värvid

| Nimi | HEX | RGB |
|---|---|---|
| Must | `#141414` | 20, 20, 20 |
| Kuld | `#C2A36B` | 194, 163, 107 |
| Kreem (hele taust) | `#F4EFE6` | 244, 239, 230 |
| Tume taust | `#121212` | 18, 18, 18 |

Kuld näeb kõige parem välja mustal või väga tumedal taustal. Heledal taustal kasuta musta logo.

## Veebilehele

```html
<!-- päises -->
<img src="leola-kaarid-nimi-kuld.svg" alt="Leola meestejuuksur" height="56">

<!-- <head> sisse -->
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:image" content="/leola-kaarid-jagamispilt-1200x630.png">
```

- Kui logo on ekraanil kitsam kui ~200 px, kasuta „nimi” varianti. Põhilogo väike alarida jääb muidu liiga peeneks.
- Pealkirjadeks sobib sama font, mis logos: **Bodoni Moda** Google Fontsist (tasuta).
  Pinyon Scripti ära kasuta tavatekstis, ainult logos.

## Uksele (kleebiste tegijale)

- SVG-failides on tähed muudetud kontuurideks: fonte pole vaja, üks värv, sobib otse lõikeplotterile.
- Lõigatud kilena on väikseim mõistlik suurus (peenim detail ~0,8 mm):

  | Fail | Väikseim laius |
  |---|---|
  | A põhilogo | 45 cm |
  | B põhilogo | 40 cm |
  | A ainult nimi | 8 cm |
  | B ainult nimi | 22 cm |
  | Pitser | 18 cm läbimõõt |
  | Vertikaalne | A 32 cm, B 40 cm kõrge |

  Väiksemaks tasub võtta „nimi” variant või prinditud (mitte lõigatud) kleebis.
- Uksel paikneb logo tavaliselt silmade kõrgusel, keskkoht ~150–160 cm põrandast, laius 40–60 cm.
- Kui kile läheb klaasi sisepinnale, peeglib kleebiste tegija faili.
- Kuldne logo: metallik-kuldne kile või lehtkuld. Valge: matt valge kile. Väga peen variant on ka
  matistatud klaasi efektiga kile (näeb välja nagu söövitatud klaas).

## Fondid ja litsents

- **Bodoni Moda** (Owen Earl), SIL Open Font License 1.1
- **Pinyon Script** (Nicole Fally), SIL Open Font License 1.1

Mõlemad on tasuta ka äriliseks kasutuseks ja logos. Litsentsid on `allikas/fonts/*/OFL.txt`.

## Muutmine

Kõik failid tehakse koodist, nii et muudatus (värv, tekst, suurus) jõuab korraga igasse faili.

```bash
cd logo/allikas
pip install -r requirements.txt
python build.py                 # logofailid, favicon'id, sotsiaalmeedia pildid
python mockups/scenes.py        # näidispiltide stseenid
node mockups/shoot.mjs          # näidispildid (vajab: npm i playwright && npx playwright install chromium)
python preview.py               # eelvaade.html
```

Värvid on `build.py` alguses (`COLORS`), tekstid `leola.py` alguses (`TAGLINE`, `CITY`).
