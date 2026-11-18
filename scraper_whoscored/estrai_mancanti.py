import pandas as pd

def pulisci_nome(nome):
    # Rimuove i trattini (es. "EDERSON -")
    nome = str(nome).replace("-", "").strip()
    nome = " ".join(nome.split())
    
    parti = nome.split()
    # Identifica i cognomi (tutti in maiuscolo) e i nomi
    cognomi = [p.capitalize() for p in parti if p.isupper() and len(p) > 1]
    nomi = [p for p in parti if not p.isupper()]
    
    # Rimuove sigle di una o due lettere come "FP" o "S"
    cognomi = [c for c in cognomi if len(c) > 2 or c.lower() in ["de", "di", "da"]]
    
    # Inverte in "Nome Cognome"
    if cognomi and nomi:
        return f"{' '.join(nomi)} {' '.join(cognomi)}"
    
    return nome.title()

# Carica i dati appena estratti
df = pd.read_csv("Quotazioni_Serie_A_Caratteristiche.csv")

# Seleziona solo le righe dove lo scraper ha fallito
mancanti = df[(df['URL'] == 'N/D') | (df['Ruoli'] == 'N/D')].copy()

# Applica la formula di pulizia per creare nomi perfetti per WhoScored
mancanti['Nome'] = mancanti['Nome'].apply(pulisci_nome)

# Elimina le colonne vuote per fare pulizia (lo scraper le ricreerà)
mancanti = mancanti.drop(columns=['Ruoli', 'Punti di forza', 'Debolezze', 'Stile di gioco', 'URL'], errors='ignore')

# Salva il file Excel per il ripescaggio
mancanti.to_excel("giocatori_mancanti_puliti.xlsx", index=False)
print(f"[✓] File creato! Trovati {len(mancanti)} giocatori da ripescare.")