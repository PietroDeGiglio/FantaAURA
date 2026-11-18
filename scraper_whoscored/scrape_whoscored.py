import asyncio
import re
import os
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd
from playwright.async_api import async_playwright

def genera_varianti_ricerca(nome_originale):
    nome = str(nome_originale).replace("-", "").strip()
    nome = re.sub(r'\s+', ' ', nome)
    parti = nome.split()
    if len(parti) <= 1: return [nome]
    
    cognomi = [p for p in parti if p.isupper() and len(p) > 1]
    nomi = [p for p in parti if not p.isupper()]
    cognomi = [c for c in cognomi if len(c) > 2 or c.lower() in ["de", "di", "da"]]
    
    varianti = []
    if cognomi and nomi:
        cognome_str = " ".join(cognomi).title()
        nome_str = " ".join(nomi).title()
        varianti.append(f"{nome_str} {cognome_str}")
        varianti.append(f"{nomi[0].title()} {cognome_str}")
        varianti.append(cognome_str)
        varianti.append(nome_str)
    else:
        varianti.append(nome.title())
        if len(parti) > 1: varianti.append(parti[-1].title())
    return list(dict.fromkeys(varianti))

def check_nome_in_url(url, nome_originale):
    """Il Filtro del DNA: verifica se il link appartiene davvero al giocatore."""
    url_slug = urllib.parse.unquote(url.split('/')[-1]).lower().replace('-', ' ')
    nome_pulito = str(nome_originale).replace("-", " ").lower()
    parti_nome = [p for p in nome_pulito.split() if len(p) > 2]
    
    # Almeno una parte del nome/cognome deve essere nel link
    match_trovati = sum(1 for p in parti_nome if p in url_slug)
    return match_trovati > 0

async def get_whoscored_url(page, termine_ricerca: str, team: str, nome_originale: str) -> str:
    encoded = urllib.parse.quote(termine_ricerca)
    search_url = f"https://it.whoscored.com/Search/?t={encoded}"
    
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(2)
        
        urls_and_texts = await page.evaluate('''() => {
            let results = [];
            document.querySelectorAll('tr').forEach(tr => {
                let a = tr.querySelector('a');
                if(a && a.href.toLowerCase().includes('/players/') && a.href.toLowerCase().includes('/show/')) {
                    results.push({ url: a.href, text: tr.innerText.toLowerCase() });
                }
            });
            return results;
        }''')

        if not urls_and_texts: return None

        # 1. Prova a trovare un match esatto (DNA + Squadra)
        for item in urls_and_texts:
            if team.lower() in item['text'] and check_nome_in_url(item['url'], nome_originale):
                return item['url']
                
        # 2. Se non trova la squadra (es. si è appena trasferito), ESIGE il match del DNA
        for item in urls_and_texts:
            if check_nome_in_url(item['url'], nome_originale):
                return item['url']
                
        # Nessun fallback casuale: se il nome non c'entra nulla, rinuncia.
        return None
        
    except Exception:
        return None

async def extract_and_verify_player(page, url: str, eta_fanta: int, original_name: str) -> dict:
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        await asyncio.sleep(2)

        profile_soup = BeautifulSoup(await page.content(), "html.parser")

        # Verifica Età
        eta_trovata = None
        info_spans = profile_soup.find_all("span")
        for span in info_spans:
            if "Età:" in span.get_text():
                testo_eta = span.find_next_sibling(string=True) or span.find_parent('dl').get_text()
                match_eta = re.search(r'Età:.*?(\d{2})', str(testo_eta).replace('\n', ''))
                if match_eta:
                    eta_trovata = int(match_eta.group(1))
                    break

        if eta_trovata and eta_fanta > 0 and abs(eta_trovata - eta_fanta) > 1:
            print(f"   [!] Scartato: Omonimo di età diversa ({eta_trovata} vs {eta_fanta})")
            return None

        # Estrazione Dati
        data = {"URL": url, "Ruoli": "N/D", "Punti di forza": "N/D", "Debolezze": "N/D", "Stile di gioco": "N/D"}

        positions = []
        for pos_el in profile_soup.select(".position-table-entry"):
            txt = re.sub(r'\s+', ' ', pos_el.get_text(separator=" ", strip=True))
            if txt and txt not in positions: positions.append(txt)
        if positions: data["Ruoli"] = " | ".join(positions)

        strengths, weaknesses, styles = [], [], []
        # Scudo anti-spazzatura potenziato
        tornei_vietati = ["World Cup", "League", "Serie", "Friendly", "Copa", "Coupe", "Cup", "Qualification", "Primera", "Division", "Championship", "Supercoppa", "Nations", "Eredivisie", "Liga"]
        
        for div in profile_soup.select(".iconize-icon-left"):
            tratto = div.get_text(strip=True)
            if len(tratto) <= 4 or tratto.isupper() or len(tratto.split()) == 1 or any(t in tratto for t in tornei_vietati):
                continue
            
            livello_el = div.find_next_sibling("div", class_=re.compile("sws-level-wrapper"))
            if livello_el:
                txt = livello_el.get_text(strip=True).lower()
                if "forte" in txt: strengths.append(tratto)
                elif "debole" in txt: weaknesses.append(tratto)
            else:
                styles.append(tratto)

        if strengths: data["Punti di forza"] = " | ".join(strengths)
        if weaknesses: data["Debolezze"] = " | ".join(weaknesses)
        if styles: data["Stile di gioco"] = " | ".join(styles)

        return data
    except Exception as e:
        print(f"   [!] Errore scheda {original_name}: {e}")
        return None

async def main():
    input_file = "giocatori_da_rifare_puliti.csv"
    output_file = "recupero_definitivo_blindato.csv"

    df_input = pd.read_csv(input_file)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="it-IT",
        )
        page = await context.new_page()

        await page.goto("https://it.whoscored.com/", timeout=30000)
        await asyncio.sleep(4)
        try:
            accept_btn = page.locator("button:has-text('Accetta'), button:has-text('Accept'), #didomi-notice-agree-button")
            if await accept_btn.count() > 0: await accept_btn.first.click()
        except Exception:
            pass

        for index, row in df_input.iterrows():
            nome_originale = str(row['Nome'])
            squadra = str(row['Squadra']).strip()
            eta = row.get("ETA'", 0)
            eta_fanta = int(eta) if pd.notna(eta) and str(eta).isdigit() else 0

            print(f"\n[{index + 1}/{len(df_input)}] Analisi: {nome_originale} (Età Fanta: {eta_fanta})...")
            
            varianti = genera_varianti_ricerca(nome_originale)
            dati_estratti = None

            for variante in varianti:
                print(f" -> Provo ricerca per: '{variante}'")
                # Ora passiamo anche il nome originale per il check del DNA
                url = await get_whoscored_url(page, variante, squadra, nome_originale)
                
                if url:
                    dati = await extract_and_verify_player(page, url, eta_fanta, nome_originale)
                    if dati:
                        dati_estratti = dati
                        print(f" [✓] Trovato e Verificato con: '{variante}'")
                        break
                await asyncio.sleep(1) 

            combined_row = row.to_dict()
            if dati_estratti:
                combined_row.update(dati_estratti)
            else:
                print(f" [-] Giocatore realmente assente/senza scheda per: {nome_originale}")
            
            df_row = pd.DataFrame([combined_row])
            mode = 'w' if not os.path.exists(output_file) else 'a'
            header = not os.path.exists(output_file)
            df_row.to_csv(output_file, index=False, mode=mode, header=header, encoding='utf-8-sig')

        await browser.close()
    print(f"\n[✓] Completato in totale sicurezza! Salvo in: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())