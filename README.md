# Joe Skills

Skille Claude Code do użytku wewnętrznego.

## Szybka instalacja (jeśli masz już Claude Code)

Otwórz Claude Code i wklej ten prompt:

```
Sprawdź czy mam zainstalowane git i python3 — jeśli nie, zainstaluj je (na macOS przez brew, na Windows pobierz instalatory). Potem sklonuj repo https://github.com/joemonster/joe-skills.git do ~/Appki/joe-skills (jeśli jeszcze nie istnieje) i uruchom python install.py z tego folderu. Jeśli w repo nie ma pliku config.json, powiedz mi że muszę go dostać od admina i wrzucić do folderu repo, a potem odpalić install.py jeszcze raz.
```

## Instalacja od zera

Jeśli nie masz jeszcze Claude Code, Git lub Pythona — poniżej instrukcje krok po kroku.

## Instalacja na Windows

### Wymagania

#### Git

1. Pobierz z https://git-scm.com/downloads/win
2. Zainstaluj — wszystkie opcje domyślne, klikaj Next
3. Sprawdź w PowerShell: `git --version`

#### Python

1. Pobierz z https://www.python.org/downloads/
2. **Ważne:** przy instalacji zaznacz **"Add Python to PATH"** na dole
3. Sprawdź w PowerShell: `python --version`

#### Node.js (potrzebny do Claude Code)

1. Pobierz z https://nodejs.org/ (wersja LTS)
2. Zainstaluj — wszystkie opcje domyślne
3. Sprawdź w PowerShell: `node --version`

#### Claude Code

W PowerShell:

```powershell
npm install -g @anthropic-ai/claude-code
```

Po instalacji uruchom `claude` w PowerShell żeby się zalogować.

#### PowerShell

Naciśnij `Win + R`, wpisz `powershell`, naciśnij Enter. Wszystkie komendy poniżej wpisuj tam.

### Kroki

#### 1. Sklonuj repo

```powershell
git clone https://github.com/joemonster/joe-skills.git $env:USERPROFILE\Appki\joe-skills
```

#### 2. Wrzuć config.json do folderu repo

Dostaniesz go od admina (plik z kluczami API). Skopiuj go do folderu `%USERPROFILE%\Appki\joe-skills\`. Wzór w `config.json.example`.

#### 3. Zainstaluj

```powershell
python $env:USERPROFILE\Appki\joe-skills\install.py
```

Skrypt kopiuje skille do `~/.claude/skills/` i klucze do `~/.claude/skills/joe-config.json`.

Gotowe — Claude Code widzi skille automatycznie.

### Aktualizacja

```powershell
cd $env:USERPROFILE\Appki\joe-skills
git pull
python install.py
```

## Instalacja na macOS

### Wymagania

#### Git

Git jest preinstalowany na macOS. Jeśli nie masz, przy pierwszym użyciu system zaproponuje instalację Xcode Command Line Tools. Sprawdź w Terminalu:

```bash
git --version
```

#### Python

macOS ma preinstalowanego Pythona 3 (od Monterey). Sprawdź:

```bash
python3 --version
```

Jeśli nie masz, zainstaluj przez Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

#### Node.js (potrzebny do Claude Code)

```bash
brew install node
```

Albo pobierz z https://nodejs.org/ (wersja LTS). Sprawdź: `node --version`

#### Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Po instalacji uruchom `claude` w Terminalu żeby się zalogować.

#### Terminal

Otwórz Spotlight (`Cmd + Spacja`), wpisz `Terminal`, naciśnij Enter. Wszystkie komendy poniżej wpisuj tam.

### Kroki

#### 1. Sklonuj repo

```bash
git clone https://github.com/joemonster/joe-skills.git ~/Appki/joe-skills
```

#### 2. Wrzuć config.json do folderu repo

Dostaniesz go od admina (plik z kluczami API). Skopiuj go do folderu `~/Appki/joe-skills/`. Wzór w `config.json.example`.

#### 3. Zainstaluj

```bash
python3 ~/Appki/joe-skills/install.py
```

Gotowe — Claude Code widzi skille automatycznie.

### Aktualizacja

```bash
cd ~/Appki/joe-skills
git pull
python3 install.py
```

## Dostępne skille

| Skill | Opis |
|-------|------|
| `ai-image-gen` | Generowanie obrazów AI (10 modeli: Gemini, Flux, GPT Image, Recraft) |
| `audio-transcript` | Transkrypcja audio z podziałem na mówców (Gemini Flash) |
| `joemonster-art` | Formatowanie artykułów HTML dla JoeMonster.org |
| `web-scraper` | Scraping artykułów do markdown (direct fetch + Firecrawl) |
