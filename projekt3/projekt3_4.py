import sys
from requests import get
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

# Získá HTML text z URL s ošetřením chyb.
def get_html_response(url):
    try:
        return get(url).text
    except ConnectionError:
        print("Chyba připojení: Nemohu se připojit k serveru. Zkontrolujte vaše připojení k internetu.")
        sys.exit()
    except Timeout:
        print("Časový limit: Požadavek trval příliš dlouho. Server neodpověděl včas.")
        sys.exit()
    except RequestException as e:
        print(f"Obecná chyba požadavku: {e}")
        sys.exit()
    except Exception as e:
        print(f"Něco se pokazilo: {e}")
        sys.exit()

# Najde hledanou obec v HTML a ověří její existenci.
def find_voting_area(html, nazev_obce):
    soup = BeautifulSoup(html, features="html.parser")
    nalez = soup.find(string=nazev_obce)
    if not nalez:
        print("Taková obec neexistuje! Zkus to znovu.")
        sys.exit()
    return nalez

# Získá odkaz na další stránku s podrobnostmi o obci.
def get_area_link(nalez):
    nearest_table = find_nearest_table(nalez, 'tr')
    a_tag = nearest_table.findAll('a')
    for vse in a_tag:
        hreference = vse.get('href')
    return hreference

# Zpracuje výsledky volební oblasti a vrátí seznam výsledků
def process_voting_results(tables):
    all_results = []
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cislo = row.find('td', class_='cislo')
            overflow_name = row.find('td', class_='overflow_name')
            center = row.find('td', class_='center')
            if cislo and overflow_name and center:
                data = {
                    'cislo': cislo.get_text(strip=True),
                    'overflow_name': overflow_name.get_text(strip=True),
                    'center': center.get_text(strip=True),
                    'cislo_href': cislo.find('a')['href'] if cislo.find('a') else None,
                    'center_href': center.find('a')['href'] if center.find('a') else None
                }
                all_results.append(data)
    return all_results

# Získá podrobnosti z odkazu na jednotlivé okrsky
def get_district_details(result):
    cely_radek = {}
    print(result['cislo'], result['overflow_name'])
    cely_radek['code'] = result['cislo']
    cely_radek['location'] = result['overflow_name']

    vyber_okrsku = "https://volby.cz/pls/ps2017nss/" + result['cislo_href']
    okrsek = get(vyber_okrsku)
    okrsek_html = BeautifulSoup(okrsek.text, features="html.parser")

    # Horní tabulka
    table = okrsek_html.find('table', attrs={'id': True})
    td_elements = table.find_all('td', class_='cislo', attrs={'data-rel': True})
    values = [td.get_text(strip=True) for td in td_elements]
    cely_radek['registered'] = int(values[0].replace(" ", "").replace("\xa0", ""))
    cely_radek['envelopes'] = int(values[1].replace(" ", "").replace("\xa0", ""))
    cely_radek['valid'] = int(values[3].replace(" ", "").replace("\xa0", ""))

    # Spodní tabulka
    table1 = okrsek_html.find('table', attrs={'id': False})
    tr_elements = table1.find_all('tr')
    for tr in tr_elements:
        td_elements_1 = tr.find_all('td')
        values = [td.get_text(strip=True) for td in td_elements_1]
        if values:
            cely_radek[values[1]] = int(values[2].replace(" ", "").replace("\xa0", ""))
    
    return cely_radek

# Zapíše data do CSV souboru
def save_to_csv(vysledky_list, vystupni_soubor):
    df = pd.DataFrame(vysledky_list)
    print(df)
    df.to_csv(vystupni_soubor, sep=',', index=False, encoding='utf-8-sig')
    print(f"Tabulka byla úspěšně zapsána do souboru {vystupni_soubor}")

# Hlavní funkce programu, která koordinuje všechny kroky
def main():
    if len(sys.argv) != 3:
        print("Program je třeba spustit se dvěma argumenty:")
        print("1. název územního celku")
        print("2. název výstupního souboru CSV")
        exit()

    nazev_obce = sys.argv[1]
    vystupni_soubor = sys.argv[2]

    print(f"Název obce: {nazev_obce}")
    print(f"Výstupní soubor: {vystupni_soubor}")

    adresa = "https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    html = get_html_response(adresa)
    nalez = find_voting_area(html, nazev_obce)
    hreference = get_area_link(nalez)
    vyber_okresu = "https://volby.cz/pls/ps2017nss/" + hreference
    obce = get(vyber_okresu)
    obce_html = BeautifulSoup(obce.text, features="html.parser")
    tables = obce_html.find_all('table', class_='table')
    
    all_results = process_voting_results(tables)
    vysledky_list = []
    
    try:
        for result in all_results:
            cely_radek = get_district_details(result)
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

    save_to_csv(vysledky_list, vystupni_soubor)

if __name__ == "__main__":
    main()
