# Projekt 3 - Engeto Online Python Akademie

Tento projekt je třetím úkolem v rámci Engeto Online Python Akademie. Projekt je zaměřen na získávání a zpracování volebních dat z webových stránek.

## Autor

- **Jméno**: Tomáš Tikal
- **Email**: tikal@3t.cz
- **Discord**: ti_to_80805

## Popis

Skript `projekt3.py` získává a analyzuje volební výsledky z webu volby.cz. Uživatel zadá název územního celku (obce) a název výstupního souboru, kam budou výsledky uloženy. Skript automaticky stáhne, zpracuje a uloží data do CSV souboru.

## Instalace

1. Ujistěte se, že máte nainstalován Python verze 3.x.
2. Nainstalujte požadované knihovny:

   ```bash
   pip install -r requirements.txt

Kde requirements.txt obsahuje:
beautifulsoup4==4.12.3
bs4==0.0.2
certifi==2024.7.4
charset-normalizer==3.3.2
idna==3.7
numpy==2.1.0
pandas==2.2.2
python-dateutil==2.9.0.post0
pytz==2024.1
requests==2.32.3
six==1.16.0
soupsieve==2.5
tzdata==2024.1
urllib3==2.2.2


## Skript se spouští s dvěma argumenty:

Název územního celku (obce).
Název výstupního souboru (CSV).
Příklad použití:
python projekt3.py "Benešov" vysledky_benesov.csv


## Činnost skriptu:

Zkontroluje existenci obce.
Stáhne volební výsledky pro zadanou obec.
Zpracuje výsledky a uloží je do CSV souboru.
Příklad výstupu:
Tabulka byla úspěšně zapsána do souboru vysledky_benesov.csv

Po úspěšném spuštění skriptu bude na obrazovce vypsána tabulka s volebními výsledky a zároveň bude uložena do souboru specifikovaného uživatelem.

## Chybové ošetření

Pokud dojde k chybě připojení nebo jiným problémům během zpracování, skript vypíše odpovídající chybovou zprávu.

Skript obsahuje chybové ošetření pro:

Chyby připojení k internetu
Časové limity při stahování dat
Obecné chyby při stahování dat

## Licence

Tento projekt je vytvořen pro studijní účely v rámci Engeto Online Python Akademie.




