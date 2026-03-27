# Joe Skills

Skille Claude Code do użytku wewnętrznego.

## Wymagania (Windows)

### Git

1. Pobierz z https://git-scm.com/downloads/win
2. Zainstaluj — wszystkie opcje domyślne, klikaj Next
3. Sprawdź w PowerShell: `git --version`

### Python

1. Pobierz z https://www.python.org/downloads/
2. **Ważne:** przy instalacji zaznacz **"Add Python to PATH"** na dole
3. Sprawdź w PowerShell: `python --version`

### PowerShell

Naciśnij `Win + R`, wpisz `powershell`, naciśnij Enter. Wszystkie komendy poniżej wpisuj tam.

## Instalacja

### 1. Sklonuj repo

```powershell
git clone https://github.com/joemonster/joe-skills.git $env:USERPROFILE\Appki\joe-skills
```

### 2. Wrzuć config.json do folderu repo

Dostaniesz go od admina (plik z kluczami API). Skopiuj go do folderu `%USERPROFILE%\Appki\joe-skills\`. Wzór w `config.json.example`.

### 3. Zainstaluj

```powershell
python $env:USERPROFILE\Appki\joe-skills\install.py
```

Skrypt kopiuje skille do `~/.claude/skills/` i klucze do `~/.claude/skills/joe-config.json`.

Gotowe — Claude Code widzi skille automatycznie.

## Aktualizacja

```powershell
cd $env:USERPROFILE\Appki\joe-skills
git pull
python install.py
```

## Dostępne skille

| Skill | Opis |
|-------|------|
| `audio-transcript` | Transkrypcja audio z podziałem na mówców (Gemini Flash) |
| `web-scraper` | Scraping artykułów do markdown (direct fetch + Firecrawl) |
