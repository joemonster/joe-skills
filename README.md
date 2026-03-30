# Joe Skills

Skille Claude Code do użytku wewnętrznego.

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
| `audio-transcript` | Transkrypcja audio z podziałem na mówców (Gemini Flash) |
| `joemonster-art` | Formatowanie artykułów HTML dla JoeMonster.org |
| `web-scraper` | Scraping artykułów do markdown (direct fetch + Firecrawl) |
