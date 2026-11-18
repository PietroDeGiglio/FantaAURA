import asyncio
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def extract_player_data(page, url, original_name):
    try:
        if url.startswith("http://"):
            url = url.replace("http://", "https://")
            
        # Aumentato il timeout e ignorato il caricamento delle pubblicità
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)

        profile_soup = BeautifulSoup(await page.content(), "html.parser")
        data = {"URL": url, "Ruoli": "N/D", "Punti di forza": "N/D", "Debolezze": "N/D", "Stile di gioco": "N/D"}

        positions = []
        for pos_el in profile_soup.select(".position-table-entry"):
            txt = re.sub(r'\s+', ' ', pos_el.get_text(separator=" ", strip=True))
            if txt and txt not in positions: positions.append(txt)
        if positions: data["Ruoli"] = " | ".join(positions)

        strengths, weaknesses, styles = [], [], []
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
    input_file = "fileconurl.xlsx"
    output_file = "giocatori_manuali_estratti.csv"

    df = pd.read_excel(input_file)
    urls_to_process = []
    
    for index, row in df.iterrows():
        url = str(row.get('Unnamed: 1', ''))
        if 'whoscored.com' in url:
            urls_to_process.append({'Nome': row['Nome'], 'URL_Target': url.strip()})

    print(f"[*] Trovati {len(urls_to_process)} link manuali da estrarre.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="it-IT",
        )
        page = await context.new_page()

        try:
            # FIX: Aggiunto wait_until="domcontentloaded" e alzato il timeout a 60 secondi
            await page.goto("https://it.whoscored.com/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"[!] Avviso: caricamento home page lento, ma procedo. Dettaglio: {e}")

        try:
            accept_btn = page.locator("button:has-text('Accetta'), button:has-text('Accept'), #didomi-notice-agree-button")
            if await accept_btn.count() > 0: await accept_btn.first.click()
        except Exception:
            pass

        for i, player in enumerate(urls_to_process):
            print(f"[{i+1}/{len(urls_to_process)}] Estrazione: {player['Nome']}")
            dati = await extract_player_data(page, player['URL_Target'], player['Nome'])
            
            if dati:
                row_data = {"Nome": player['Nome']}
                row_data.update(dati)
                df_row = pd.DataFrame([row_data])
                
                mode = 'w' if not os.path.exists(output_file) else 'a'
                header = not os.path.exists(output_file)
                df_row.to_csv(output_file, index=False, mode=mode, header=header, encoding='utf-8-sig')
            
            await asyncio.sleep(1)

        await browser.close()
    
    print(f"\n[✓] Estrazione completata! Salvo in: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())