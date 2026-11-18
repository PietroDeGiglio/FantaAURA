import pandas as pd

# 1. Carica il file originale e il file dei ripescati
df_originale = pd.read_csv("Quotazioni_Serie_A_Caratteristiche.csv")
df_ripescati = pd.read_csv("Ripescaggio_Caratteristiche.csv")

# 2. Usa il "Nome" come chiave per far combaciare i giocatori
df_originale.set_index("Nome", inplace=True)
df_ripescati.set_index("Nome", inplace=True)

# 3. Aggiorna i dati mancanti dell'originale con quelli trovati nel ripescaggio
df_originale.update(df_ripescati)

# 4. Ripristina la colonna del nome e salva il risultato finale in Excel
df_originale.reset_index(inplace=True)
df_originale.to_excel("Listone_Finale_Completo.xlsx", index=False)

print("[✓] Unione completata! Il file finale è Listone_Finale_Completo.xlsx")