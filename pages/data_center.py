import streamlit as st
import pandas as pd
from streamlit.runtime.scriptrunner import RerunException
from database.database import get_active_players_with_season, get_connection, generate_player_id, log_update
from utils.normalization import normalize_name

ROLE_MAP = {'P': 'Portiere', 'D': 'Difensore', 'C': 'Centrocampista', 'A': 'Attaccante'}

def show():
    st.markdown("<h2>DATA CENTER <span class='gold-text'>✦</span></h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Il cuore dei dati di FantaAURA.</p>", unsafe_allow_html=True)
    
    # KPIs
    players = get_active_players_with_season("2026/27")
    df_p = pd.DataFrame(players) if players else pd.DataFrame(columns=['fantasy_role_code'])
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("PLAYERS", len(df_p))
    c2.metric("PORTIERI", len(df_p[df_p['fantasy_role_code'] == 'P']) if not df_p.empty else 0)
    c3.metric("DIFENSORI", len(df_p[df_p['fantasy_role_code'] == 'D']) if not df_p.empty else 0)
    c4.metric("CENTROCAMPISTI", len(df_p[df_p['fantasy_role_code'] == 'C']) if not df_p.empty else 0)
    c5.metric("ATTACCANTI", len(df_p[df_p['fantasy_role_code'] == 'A']) if not df_p.empty else 0)
    
    st.markdown("---")
    tabs = st.tabs(["Importa Listone", "Data Quality", "Import History"])
    
    with tabs[0]:
        st.info("Carica il file Excel originale: Quotazioni_Fantacalcio_Stagione_2026_27.xlsx. FantaAURA analizzerà il foglio 'Tutti'.")
        
        # Reset state on file change
        uploaded_file = st.file_uploader("Seleziona file (.xlsx)", type=['xlsx'])
        
        if uploaded_file:
            if st.button("ANALIZZA LISTONE", type="primary", use_container_width=True):
                with st.spinner("Analisi in corso..."):
                    parse_real_listone(uploaded_file)
        
        # Display preview from session state
        if st.session_state.get('import_preview_ready'):
            show_import_preview()

    with tabs[1]:
        st.markdown("### DATA QUALITY")
        if not players:
            st.warning("Database vuoto.")
        else:
            q1, q2, q3 = st.columns(3)
            q1.metric("Giocatori Importati", len(df_p))
            q2.metric("Senza Foto", len(df_p[df_p['photo_status'] == 'needs_review']))
            q3.metric("Dati Storici Mancanti", len(df_p)) # Placeholder for historical
            
    with tabs[2]:
        st.markdown("### IMPORT HISTORY")
        conn = get_connection()
        logs = pd.read_sql_query("SELECT * FROM data_update_log ORDER BY finished_at DESC LIMIT 10", conn)
        conn.close()
        if not logs.empty:
            st.dataframe(logs[['finished_at', 'source', 'operation', 'status', 'records_added', 'records_updated']], hide_index=True)
        else:
            st.write("Dato non disponibile")

def parse_real_listone(file):
    try:
        xls = pd.ExcelFile(file)
        if 'Tutti' not in xls.sheet_names:
            st.error("ERRORE: Il foglio 'Tutti' non è presente nel file.")
            return
            
        # Parse skipping title row. Header is row 1 (0-indexed)
        df = pd.read_excel(xls, sheet_name='Tutti', header=1)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        req_cols = ['Id', 'R', 'RM', 'Nome', 'Squadra', 'Qt.A', 'Qt.I', 'Diff.', 'Qt.A M', 'Qt.I M', 'Diff.M', 'FVM', 'FVM M']
        missing = [c for c in req_cols if c not in df.columns]
        
        if missing:
            st.error(f"Struttura non valida. Colonne mancanti: {', '.join(missing)}")
            return
            
        df['Id'] = pd.to_numeric(df['Id'], errors='coerce')
        df.dropna(subset=['Id'], inplace=True)
        df['Id'] = df['Id'].astype(int).astype(str)
        df['normalized_name'] = df['Nome'].apply(normalize_name)
        
        run_diff_engine(df)
        
    except RerunException:
        raise
    except Exception as e:
        st.error(f"Errore parsing Excel: {str(e)}")

def run_diff_engine(df_new):
    db_players = get_active_players_with_season("2026/27")
    db_map = {str(p['fantacalcio_player_id']): p for p in db_players if p.get('fantacalcio_player_id')}
    
    new_players, updated_players, unchanged_players = [], [], []
    active_ids = set()
    
    for _, row in df_new.iterrows():
        fca_id = str(row['Id'])
        active_ids.add(fca_id)
        
        if fca_id in db_map:
            p = db_map[fca_id]
            changes = {}
            if str(p['team']) != str(row['Squadra']): changes['Squadra'] = f"{p['team']} → {row['Squadra']}"
            if str(p['price']) != str(row['Qt.A']): changes['Qt.A'] = f"{p['price']} → {row['Qt.A']}"
            if str(p['fvm']) != str(row['FVM']): changes['FVM'] = f"{p['fvm']} → {row['FVM']}"
            if str(p['mantra_role']) != str(row['RM']): changes['Mantra'] = f"{p['mantra_role']} → {row['RM']}"
            if str(p['fantasy_role_code']) != str(row['R']): changes['Ruolo'] = f"{p['fantasy_role_code']} → {row['R']}"
            
            if changes:
                updated_players.append({"player_id": p['player_id'], "Nome": p['display_name'], "Modifiche": changes, "raw": row.to_dict()})
            else:
                unchanged_players.append(p['display_name'])
        else:
            new_players.append({"Nome": row['Nome'], "Squadra": row['Squadra'], "R": row['R'], "Qt.A": row['Qt.A'], "raw": row.to_dict()})
            
    removed_players = [p for f_id, p in db_map.items() if f_id not in active_ids and p['active'] == 1]
    
    st.session_state.import_preview_ready = True
    st.session_state.new_players = new_players
    st.session_state.updated_players = updated_players
    st.session_state.unchanged_players = unchanged_players
    st.session_state.removed_players = removed_players
    st.rerun()

def show_import_preview():
    st.markdown("### PREVIEW AGGIORNAMENTO LISTONE")
    new_p = st.session_state.new_players
    upd_p = st.session_state.updated_players
    unc_p = st.session_state.unchanged_players
    rem_p = st.session_state.removed_players
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NUOVI", len(new_p))
    c2.metric("AGGIORNATI", len(upd_p))
    c3.metric("INVARIATI", len(unc_p))
    c4.metric("RIMOSSI", len(rem_p))
    
    t1, t2, t3 = st.tabs(["Nuovi", "Aggiornati", "Rimossi (Disattivati)"])
    with t1: st.dataframe(pd.DataFrame([{k:v for k,v in p.items() if k != 'raw'} for p in new_p])) if new_p else st.write("Nessuno")
    with t2: 
        if upd_p:
            display_updates = [{"Nome": p["Nome"], "Modifiche": ", ".join([f"{k}: {v}" for k,v in p["Modifiche"].items()])} for p in upd_p]
            st.dataframe(pd.DataFrame(display_updates))
        else: st.write("Nessuno")
    with t3: st.dataframe(pd.DataFrame([p['display_name'] for p in rem_p], columns=["Nome"])) if rem_p else st.write("Nessuno")
    
    st.write("")
    if st.button("CONFERMA IMPORTAZIONE", type="primary", use_container_width=True):
        apply_database_update(new_p, upd_p, rem_p)
        st.session_state.import_preview_ready = False
        st.rerun()

def apply_database_update(new_players, updated_players, removed_players):
    conn = get_connection()
    c = conn.cursor()
    season = "2026/27"
    try:
        # INSERT NEW (Players + Player_Season)
        for p in new_players:
            pid = generate_player_id()
            row = p['raw']
            role_ext = ROLE_MAP.get(row['R'], row['R'])
            
            c.execute('''INSERT INTO players 
                (player_id, fantacalcio_player_id, display_name, normalized_name, photo_status)
                VALUES (?, ?, ?, ?, 'needs_review')''', 
                (pid, str(row['Id']), row['Nome'], normalize_name(row['Nome'])))
                 
            c.execute('''INSERT INTO player_season (player_id, season, team, fantasy_role_code, fantasy_role, mantra_role, price, initial_price, price_difference, price_mantra, initial_price_mantra, price_difference_mantra, fvm, fvm_mantra, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Fantacalcio.it')''',
                (pid, season, row['Squadra'], row['R'], role_ext, row['RM'], row['Qt.A'], row['Qt.I'], row['Diff.'], row['Qt.A M'], row['Qt.I M'], row['Diff.M'], row['FVM'], row['FVM M']))

        # UPDATE EXISTING
        for p in updated_players:
            pid = p['player_id']
            row = p['raw']
            role_ext = ROLE_MAP.get(row['R'], row['R'])
                
            c.execute('''INSERT OR REPLACE INTO player_season (id, player_id, season, team, fantasy_role_code, fantasy_role, mantra_role, price, initial_price, price_difference, price_mantra, initial_price_mantra, price_difference_mantra, fvm, fvm_mantra, source, active)
                VALUES ((SELECT id FROM player_season WHERE player_id=? AND season=?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Fantacalcio.it', 1)''',
                (pid, season, pid, season, row['Squadra'], row['R'], role_ext, row['RM'], row['Qt.A'], row['Qt.I'], row['Diff.'], row['Qt.A M'], row['Qt.I M'], row['Diff.M'], row['FVM'], row['FVM M']))

        # DEACTIVATE REMOVED (Ceduti)
        for p in removed_players:
            c.execute('UPDATE player_season SET active = 0, updated_at = CURRENT_TIMESTAMP WHERE player_id = ? AND season = ?', (p['player_id'], season))
            
        conn.commit()
        log_update("Listone Fantacalcio.it", "Import 2026/27", len(new_players)+len(updated_players)+len(removed_players), len(new_players), len(updated_players), 0, 0, "Successo")
        
    except Exception as e:
        conn.rollback()
        log_update("Listone Fantacalcio.it", "Import 2026/27", 0, 0, 0, 0, 1, "Errore", str(e))
    finally:
        conn.close()
