---
name: joemonster-art
description: "Use when writing or formatting articles for JoeMonster.org. Covers HTML structure, styling rules, box design, and text formatting conventions specific to the JoeMonster CMS. Trigger when user mentions: joemonster, artykuł na JM, sformatuj artykuł, napisz artykuł, art JM, CMS JM."
---

# JoeMonster Article Style Guide

Style guide for writing and formatting HTML articles for JoeMonster.org CMS.

## Zasady Pisania

### 1. Konkret ponad abstrakcję

Pokazuj, nie opowiadaj.

- ❌ "Nasz produkt poprawia wydajność"
- ✅ "Zespół Sary skrócił czas odpowiedzi z 4 godzin do 30 minut"
- Konkretne liczby, imiona, sytuacje > ogólniki

### 2. Jedna myśl = jeden akapit

- **Zdanie otwierające:** przedstawia główną myśl
- **Rozwinięcie:** 2–4 zdania z przykładami lub wyjaśnieniem
- **Zamknięcie:** naturalne przejście do kolejnego akapitu

### 3. Pokazuj transformację

Ludzie zapamiętują zmianę, nie stan statyczny: Przed → Po, Problem → Rozwiązanie, Chaos → Porządek.

Przykład: "Z 200 nierozwiązanych zgłoszeń do inbox zero w 3 dni"

### 4. Głos aktywny

- ❌ "Projekt został zakończony przez zespół"
- ✅ "Zespół zakończył projekt"
- Aktywny głos = więcej energii, klarowności, sprawczości

### 5. Konwersacyjny język

Unikaj nadmiernego żargonu, używaj potocznych zwrotów ("naprawdę super"), aby tekst brzmiał jak żywa rozmowa. Czasem bądź ironiczny, ale zawsze życzliwy.

### 6. Wytnij zbędne słowa

Każde słowo musi pracować. Usuń:

- "W zasadzie", "właściwie", "jakby"
- "Bardzo", "naprawdę", "całkiem"
- Podwójne określenia: "całkowicie kompletny"

### 7. Rozpoczynaj mocno

Pierwsze zdanie decyduje, czy ktoś czyta dalej.

- ✅ "Sarah straciła klienta wartego 50k€"
- ❌ "W dzisiejszych czasach biznes jest trudny"
- Unikaj truizmów i oczywistości

### 8. Pisz dla konkretnego człowieka

Nie pisz "dla wszystkich". Wyobraź sobie jedną osobę – jak mówi? Co ją boli? Co chce osiągnąć? Pisz tak, jakbyś rozmawiał z tą osobą przy kawie.

### 9. Używaj prostych słów

- ❌ "Wykorzystujemy zaawansowane metodologie"
- ✅ "Używamy sprawdzonych metod"
- Im prostsze słowo, tym silniejszy przekaz

### 10. Rytm i różnorodność

Mieszaj długość zdań. Krótkie zdania = energia, akcent. Długie zdania = wyjaśnienie, kontekst. Unikaj monotonii.

### 11. Edytuj bezlitośnie

Pierwsze pisanie = myślenie na papierze. Druga wersja = komunikacja z czytelnikiem. Pomiędzy nimi: wytnij 30–50% tekstu.

### 12. Zmysłowe szczegóły

Użyj dźwięków, zapachów, emocji, żeby czytelnik mógł się "zanurzyć" w doświadczeniu.

### 13. Autentyczność

Dziel się szczerze zarówno wątpliwościami, porażkami jak i sukcesami.

### 14. Cytaty

Dodawaj cytaty ważnych postaci, twórców, odkrywców, świadków.

### 15. Postawa wobec polityki i obyczajów

JoeMonster nie jest ani lewicowy, ani prawicowy. Jedyna strona, po której stoimy, to strona prawdy.

- **Hipokryzja > przekonania.** Nie atakujemy ludzi za to, w co wierzą ani co robią w sypialni. Atakujemy rozbieżność między deklaracjami a czynami. Polityk walczący z „ideologią gender", którego mąż zakłada sztuczne cycki — problem nie jest w cycki, problem jest w kłamstwo.
- **Życzliwość wobec człowieka, bezlitosność wobec pozy.** Każdy ma prawo do swoich dziwactw, fetyszy, słabości. Nikt nie ma prawa udawać, że ich nie ma, jednocześnie potępiając innych za to samo.
- **Nie moralizuj — pokaż kontrast.** Czytelnik sam wyciągnie wnioski. Zestawienie cytatu „jesteśmy otwartą książką" z fałszywym imieniem „Jason" na portalu webcam mówi więcej niż akapit komentarza.

## Uniwersalna Formuła Struktury

Dla większości tekstów:

1. **Hook** (przyciągnij uwagę) – konkret, problem, pytanie
2. **Kontekst** (dlaczego to ważne) – relatowalne tło
3. **Rozwinięcie** (konkretne informacje) – fakty, przykłady, dane
4. **Transformacja** (co się zmieniło) – przed/po
5. **Wniosek** (co z tego wynika) – lekcja lub call to action

Klucz: **Konkret + Prostota + Transformacja = Silny tekst**

## Praca ze źródłami

Do przeglądania źródeł (weryfikacja informacji, pobieranie zdjęć ilustracyjnych) używaj skilla `web-scraper`. Pozwala pobrać pełną treść artykułu jako markdown wraz z listą obrazków i ich URL-ami.

## HTML Structure

- Use `<br><br>` between paragraphs – CMS JM strips `<p>` tags
- Base text inside `#arcik`: Arial 16px, line-height 150%
- Title uses `<h1>`: Montserrat/Arial, 25px, color `#444`, `line-height: 120%`, `letter-spacing: -1px`, `word-spacing: -.3px`
- Headings use `<h2>`: Montserrat/'Roboto Slab'/Arial, 22px, color `#333`, line-height 1.5em
- Images: `width="700"`, centered
- Blockquote: `border-left: 10px solid #09f`, `font-size: 110%`, `color: #444`

## Text Styling

- **Never** color body text for emphasis – use `<strong>` / `<b>` only
- Colored text allowed **only** in box divs, headings, and table rows
- Decorative boxes: `<div class="box">` (szary), `<div class="box red">`, `<div class="box blue">`, `<div class="box green">`, `<div class="box yellow">`. **No** left accent border
- All box/table styles defined in `<style>` via classes, never inline
- Use en-dashes (–) in text, not em-dashes (—)
- Sources right-aligned, `font-size: 12px`
- Zero padding, zero filler sentences

## Preview HTML

Gdy user prosi o preview / podgląd artykułu, generuj pełny dokument HTML z:

```html
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[tytuł artykułu] – JoeMonster preview</title>
<style>
body {
  background: #fff;
  margin: 0;
  padding: 40px 0;
  font-family: Arial, sans-serif;
  font-size: 16px;
  line-height: 150%;
  color: #333;
}
#arcik {
  max-width: 700px;
  margin: 0 auto;
  padding: 0 15px;
}
h1 {
  font-family: Montserrat, Arial, sans-serif;
  color: #444;
  text-decoration: none;
  line-height: 120%;
  margin: 0 0 5px;
  display: block;
  font-size: 25px;
  word-spacing: -.3px;
  letter-spacing: -1px;
}
h2 {
  font-size: 22px;
  color: #333;
  line-height: 1.5em;
  font-family: Montserrat, 'Roboto Slab', Arial, sans-serif;
}
blockquote {
  padding: 5px 15px 2px 10px;
  margin: 10px 5px;
  border-left: 10px solid #09f;
  color: #444;
  line-height: 150%;
  font-size: 110%;
  text-align: left;
}
.box {
  background-color: #f0f4f8;
  padding: 15px;
  margin: 15px 0;
  font-size: 95% !important;
  border-radius: 10px;
  border: 1px solid #aaa;
}
.box.red {
  background-color: #ffe3e3;
  border: 1px solid #fb8b8b;
}
.box.blue {
  background-color: #cfe6f9;
  border: 1px solid #8fb5c8;
}
.box.green {
  background-color: #c8f5cf;
  border: 1px solid #3ed65c;
}
.box.yellow {
  background-color: #ffe192;
  border: 1px solid #ffc56a;
}
.img-wrap {
  margin: 15px 0;
}
.img-wrap img {
  display: block;
  max-width: 100%;
  height: auto;
}
.img-caption {
  font-size: 90% !important;
  color: #555;
  margin: 5px;
  text-align: center;
}
.source {
  font-size: 12px;
  text-align: right;
  color: #888;
  clear: both;
}
</style>
</head>
<body>
<div id="arcik">
<h1>[tytuł]</h1>
<!-- treść artykułu -->
</div>
</body>
</html>
```

Obrazki w preview owijaj w `.img-wrap` z opcjonalnym `.img-caption`. Źródło na końcu w `<div class="source">`.

Boxy — klasa bazowa `.box` (szary) + modyfikator koloru jako druga klasa:
- `<div class="box">` — szary (domyślny, neutralny)
- `<div class="box red">` — ostrzeżenia, zakazy, czego NIE robić
- `<div class="box blue">` — informacje, fakty, definicje
- `<div class="box green">` — porady, co robić, pozytywne wskazówki
- `<div class="box yellow">` — ciekawostki, uwagi, podsumowania

## Przykłady

Gotowe, sformatowane artykuły w `przykłady/`:

- [01-arche-seks-demografia.md](przykłady/01-arche-seks-demografia.md) – felieton prowokacyjny, clickbait, ironia, triada, kontrast sacrum/profanum
- [02-plonacy-food-truck-japonia.md](przykłady/02-plonacy-food-truck-japonia.md) – reportaż sensacyjny + poradnik, antyteza, dygresja prawna, boxy ostrzegawcze
- [03-omaty-polska.md](przykłady/03-omaty-polska.md) – felieton obserwacyjny, gradacja absurdu, timeline, ironia, puenta
- [04-pluszowy-jamnik-ztm.md](przykłady/04-pluszowy-jamnik-ztm.md) – artykuł interwencyjny, Dawid vs Goliat, paradoks, satyrа na biurokrację

## Serie

Zasady konkretnych serii w `series/`:

- [Fake Patrol](series/fake-patrol.md) – demaskowanie fałszywych informacji

Gdy user pisze artykuł do konkretnej serii, przeczytaj odpowiedni plik z `series/` i zastosuj jego zasady razem z ogólnym style guide powyżej.
