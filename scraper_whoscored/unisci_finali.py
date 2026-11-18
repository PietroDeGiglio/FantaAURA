import pandas as pd

# 1. Carica il listone generale (con i buchi) e il file con i giocatori recuperati
df_base = pd.read_csv("Quotazioni_Serie_A_Caratteristiche.csv")
df_aggiornamenti = pd.read_csv("giocatori_buoni_puliti.csv")

# 2. Rimuove per sicurezza eventuali giocatori duplicati nei singoli file
df_base = df_base.drop_duplicates(subset=['Nome'], keep='first')
df_aggiornamenti = df_aggiornamenti.drop_duplicates(subset=['Nome'], keep='first')

# 3. Imposta la colonna "Nome" come chiave di registro per l'incastro
df_base.set_index('Nome', inplace=True)
df_aggiornamenti.set_index('Nome', inplace=True)

# 4. Incolla i dati trovati sopra le righe vuote del listone base
df_base.update(df_aggiornamenti)

# 5. Ripristina la colonna "Nome" e converte il file finale in un Excel pronto per l'asta
df_base.reset_index(inplace=True)
output_file = "Listone_Fantacalcio_Definitivo.xlsx"
df_base.to_excel(output_file, index=False)

print(f"[✓] Unione completata! Il tuo file finale è stato salvato come: {output_file}")