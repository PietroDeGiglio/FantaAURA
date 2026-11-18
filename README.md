# FantaAURA

Il tool di fantacalcio definitivo — colori sociali Nero e Oro.

App Streamlit per analisi giocatori di Serie A (stagioni 2022–2026), listone 2026/27,
preparazione e simulazione asta, accoppiate da calendario e gestione della lega.

## Avvio

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Struttura

- `app.py` — entry point Streamlit
- `pages/` — pagine (dashboard, player lab, GK lab, fixture lab, data center, lega…)
- `components/`, `styles/` — UI e tema
- `database/` — SQLite (`fantaaura.db`) e schema
- `engine/`, `core/`, `utils/` — logica di matching, normalizzazione, FVM
- `loghi/`, `assets/` — immagini
- `scraper_whoscored/` — scraper WhoScored per le caratteristiche dei giocatori e script di unione dei dati
