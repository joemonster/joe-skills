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
- Headings use `<h2>`: Arial 18px, color `#333`, line-height 1.5em
- Images: `width="700"`, centered
- Blockquote: `border-left: 10px solid #09f`, `font-size: 125%`

## Text Styling

- **Never** color body text for emphasis – use `<strong>` / `<b>` only
- Colored text allowed **only** in box divs, headings, and table rows
- Decorative boxes: background color, **no** left accent border
- All box/table styles defined in `<style>` via classes, never inline
- Use en-dashes (–) in text, not em-dashes (—)
- Sources right-aligned, `font-size: 12px`
- Zero padding, zero filler sentences

## Serie

Zasady konkretnych serii w `series/`:

- [Fake Patrol](series/fake-patrol.md) – demaskowanie fałszywych informacji

Gdy user pisze artykuł do konkretnej serii, przeczytaj odpowiedni plik z `series/` i zastosuj jego zasady razem z ogólnym style guide powyżej.
