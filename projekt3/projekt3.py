"""
projekt3.py: třetí projekt do Engeto Online Python Akademie

author: Tomas TIKAL
email: tikal@3t.cz
discord: ti_to_80805
"""
import sys
from requests import *
from bs4 import BeautifulSoup
import pandas as pd
from requests.exceptions import ConnectionError, Timeout, RequestException

# Funkce pro nalezení nejbližšího tagu <table>
def find_nearest_table(element, tagovani):
    parent = element.parent
    while parent is not None:
        if parent.name == tagovani:
            return parent
        parent = parent.parent
    return None


if(len(sys.argv) != 3):
    print("Program je třeba spustit se dvěma argumenty:")
    print("1. název územního celku")
    print("2. název výstupního souboru CSV")
    exit()

nazev_obce = sys.argv[1]
vystupni_soubor = sys.argv[2]

print("Název obce", nazev_obce)
print("Výstupní soubor", vystupni_soubor)

adresa = "https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
odpoved = get(adresa)

rozdelene_html = BeautifulSoup(odpoved.text, features="html.parser")

# kontrola správného názvu obce
nalez = rozdelene_html.find(string=nazev_obce)
if(not nalez):
    print("taková obec neexistuje! Zkus to znovu.")
    exit()

# Najít nejbližší <table> tag pro nalezený text
nearest_table = find_nearest_table(nalez, 'tr')

a_tag = nearest_table.findAll('a')
for vse in a_tag:
    hreference = vse.get('href')

# skok na další stránku a výběr obce
vyber_okresu = "https://volby.cz/pls/ps2017nss/" + hreference

# print(vyber_okresu)
obce = get(vyber_okresu)
obce_html = BeautifulSoup(obce.text, features="html.parser")

# Najít všechny <table> tagy s třídou "table"
tables = obce_html.find_all('table', class_='table')

# Inicializovat seznam pro uložení výsledků
all_results = []
vysledky_list = []

# Projít každou tabulku s třídou "table"
for table in tables:
    # Najít všechny <tr> tagy v tabulce
    rows = table.find_all('tr')
    
    # Projít každý <tr> tag a najít <td> tagy s požadovanými třídami
    for row in rows:
        cislo = row.find('td', class_='cislo')
        overflow_name = row.find('td', class_='overflow_name')
        center = row.find('td', class_='center')
        
        if cislo and overflow_name and center:
            # Přidat nalezené hodnoty do slovníku a uložit do výsledků
            data = {
                'cislo': cislo.get_text(strip=True),
                'overflow_name': overflow_name.get_text(strip=True),
                'center': center.get_text(strip=True),
                'cislo_href': cislo.find('a')['href'] if cislo.find('a') else None,
                'center_href': center.find('a')['href'] if center.find('a') else None
            }
            all_results.append(data)

# ošetření výpadku spojení této delší komunikace do Internetu
try:

    # Výpis hodnot klíče 'cislo' (code) a 'overflow_name' (název obce)
    for result in all_results:
        # Slovník pro ukládání požadovaných hodnot každého okrsku
        cely_radek = {}

        print()
        print(result['cislo'], result['overflow_name'])

        cely_radek['code'] = result['cislo']
        cely_radek['location'] = result['overflow_name']

        # Výběr okrsku
        vyber_okrsku = "https://volby.cz/pls/ps2017nss/" + result['cislo_href']
        okrsek = get(vyber_okrsku)
        okrsek_html = BeautifulSoup(okrsek.text, features="html.parser")

        # Najít tabulku s id - horní tabulka 
        table = okrsek_html.find('table', attrs={'id': True})

        # Najít všechny <td> tagy s třídou "cislo" a atributem data-rel
        td_elements = table.find_all('td', class_='cislo', attrs={'data-rel': True})

        # Uložit hodnoty do seznamu
        values = [td.get_text(strip=True) for td in td_elements]

        # uloží do proměnných s vyloučením speciálních znaků v řetězci
        cely_radek['registered'] = int(values[0].replace(" ", "").replace("\xa0", ""))
        cely_radek['envelopes'] = int(values[1].replace(" ", "").replace("\xa0", ""))
        cely_radek['valid'] = int(values[3].replace(" ", "").replace("\xa0", ""))

        # Najít tabulku BEZ id  - spodní tabulka
        table1 = okrsek_html.find('table', attrs={'id': False})

        tr_elements = table1.find_all('tr')

        # Projít všechny <tr> a najít všechny <td> tagy
        for tr in tr_elements:
            td_elements_1 = tr.find_all('td')
            polozky = {}
            values = [td.get_text(strip=True) for td in td_elements_1]
            if values != []:
                cely_radek[values[1]] = int(values[2].replace(" ", "").replace("\xa0", ""))

        # zápis do listu 
        vysledky_list.append(cely_radek)

except ConnectionError:
    print("Chyba připojení: Nemohu se připojit k serveru. Zkontrolujte vaše připojení k internetu.")
    exit()
except Timeout:
    print("Časový limit: Požadavek trval příliš dlouho. Server neodpověděl včas.")
    exit()
except RequestException as e:
    print(f"Obecná chyba požadavku: {e}")
    exit()
except Exception as e:
    print(f"Něco se pokazilo: {e}")
    exit()


# Vytvoření DataFrame z dat
df = pd.DataFrame(vysledky_list)

# Výpis tabulky na obrazovku i do zvoleného CSV souboru
print(df)
df.to_csv(vystupni_soubor, sep=',', index=False, encoding='utf-8-sig')
print("Tabulka byla úspěšně zapsána do souboru", vystupni_soubor)
