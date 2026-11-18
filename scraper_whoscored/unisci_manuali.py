import pandas as pd

# 1. Carica il listone definitivo (senza il _2 nel nome) e il file appena estratto
df_listone = pd.read_excel("Listone_Fantacalcio_Definitivo.xlsx")
df_manuali = pd.read_csv("giocatori_manuali_estratti.csv")

# 2. Imposta la colonna "Nome" come chiave per far combaciare le righe in modo esatto
df_listone.set_index('Nome', inplace=True)
df_manuali.set_index('Nome', inplace=True)

# 3. Aggiorna il listone principale sovrascrivendo i valori vuoti con le nuove statistiche
df_listone.update(df_manuali)

# 4. Ripristina l'impaginazione corretta
df_listone.reset_index(inplace=True)

# 5. Salva il file definitivo pronto per l'asta
output = "Listone_Fantacalcio_PRONTO_ASTA.xlsx"
df_listone.to_excel(output, index=False)

print(f"[✓] Lavoro completato! Database chiuso al 100%. Apri il file: {output}")