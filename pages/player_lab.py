import streamlit as st
from database.database import get_active_players_with_season
from components.player_row import render_player_row, fetch_historical_stats, fetch_characteristics, get_gk_stats_from_excel, get_gk_data
from aura_engine import get_exact_affinities

# --- DATABASE TIRATORI ESTRATTO DALL'EXCEL ---
SPECIALISTS_DATA = {
    'Atalanta': {'Rigoristi': ['Scamacca', 'Krstovic', 'Samardzic'], 'Piazzati': ['De Ketelaere', 'Samardzic', 'Gaetano']}, 
    'Bologna': {'Rigoristi': ['Orsolini', 'Bernardeschi', 'Dovbyk'], 'Piazzati': ['Orsolini', 'Bernardeschi', 'Miranda J.']}, 
    'Cagliari': {'Rigoristi': ['Nzola', 'Kevin Carlos', 'Mina'], 'Piazzati': ['Fazzini', 'Maldini', 'Romano']}, 
    'Como': {'Rigoristi': ['Da Cunha', 'Kean', 'Douvikas'], 'Piazzati': ['Paz N.', 'Baturina', 'Milla']}, 
    'Fiorentina': {'Rigoristi': ['Beto', 'Pellegrino M.', 'Goncalves P.'], 'Piazzati': ['Mastantuono', 'Atta', 'Goncalves P.']}, 
    'Frosinone': {'Rigoristi': ['Calò', 'Schmid', 'Bobcek'], 'Piazzati': ['Calò', 'Schmid', 'Ghedjemis']}, 
    'Genoa': {'Rigoristi': ['Colombo', 'Ostigard', 'Vitinha O.'], 'Piazzati': ['Baldanzi', 'Vitinha O.', 'Messias']}, 
    'Inter': {'Rigoristi': ['Calhanoglu', 'Zielinski', 'Martinez L.'], 'Piazzati': ['Calhanoglu', 'Dimarco', 'Zielinski']}, 
    'Juventus': {'Rigoristi': ['Kolo Muani', 'Woltemade', 'Gonzalez N.'], 'Piazzati': ['Yildiz', 'Locatelli', 'Douglas Luiz']}, 
    'Lazio': {'Rigoristi': ['Zaccagni', 'Pinamonti', 'Gudmundsson A.'], 'Piazzati': ['Rovella', 'Zaccagni', 'Gudmundsson A.']}, 
    'Lecce': {'Rigoristi': ['Geubbels', 'Stulic', 'Berisha M.'], 'Piazzati': ['Pierotti', 'Berisha M.', 'Gandelman']}, 
    'Milan': {'Rigoristi': ['Ramos G.', 'Pulisic', 'Modric'], 'Piazzati': ['Modric', 'Pulisic', 'Saelemaekers']}, 
    'Monza': {'Rigoristi': ['Cutrone', 'Varela G.', 'Ngonge'], 'Piazzati': ['Ngonge', 'Folorunsho', 'Pessina']}, 
    'Napoli': {'Rigoristi': ['De Bruyne', 'Hojlund', 'Politano'], 'Piazzati': ['De Bruyne', 'Politano', 'Neres']}, 
    'Parma': {'Rigoristi': ['Tourè E.', 'Valeri', 'Bernabè'], 'Piazzati': ['Bernabè', 'Nicolussi Caviglia', 'Valeri']}, 
    'Roma': {'Rigoristi': ['Malen', 'Dybala', 'Castro S.'], 'Piazzati': ['Dybala', 'Malen', 'Pellegrini Lo.']}, 
    'Sassuolo': {'Rigoristi': ['Berardi', 'Esposito Se.', 'Laurientè'], 'Piazzati': ['Berardi', 'Laurientè', 'Adzic']}, 
    'Torino': {'Rigoristi': ['Vlasic', 'Simeone', 'Mandragora'], 'Piazzati': ['Vlasic', 'Mandragora', 'Gineitis']}, 
    'Udinese': {'Rigoristi': ['Davis K.', 'Solet', 'Zaniolo'], 'Piazzati': ['Zaniolo', 'Ekkelenkamp', 'Unai Gomez']}, 
    'Venezia': {'Rigoristi': ['Busio', 'Adams A.', 'Adorante'], 'Piazzati': ['Busio', 'Yeboah J.', 'Perez K.']}
}

TEAM_COLORS = {
    "Atalanta": "linear-gradient(135deg, #000000 50%, #1a5bb8 50%)", "Bologna": "linear-gradient(135deg, #002b5c 50%, #ba0f14 50%)",
    "Cagliari": "linear-gradient(135deg, #002350 50%, #b32a2a 50%)", "Como": "linear-gradient(135deg, #00509a 50%, #ffffff 50%)",
    "Empoli": "linear-gradient(135deg, #00509a 100%, #00509a 100%)", "Fiorentina": "linear-gradient(135deg, #482e92 100%, #482e92 100%)",
    "Genoa": "linear-gradient(135deg, #ba0f14 50%, #002b5c 50%)", "Inter": "linear-gradient(135deg, #000000 50%, #005ca8 50%)",
    "Juventus": "linear-gradient(135deg, #ffffff 50%, #000000 50%)", "Lazio": "linear-gradient(135deg, #87d8f7 50%, #ffffff 50%)",
    "Lecce": "linear-gradient(135deg, #ffcc00 50%, #d10000 50%)", "Milan": "linear-gradient(135deg, #fb090b 50%, #000000 50%)",
    "Monza": "linear-gradient(135deg, #e3001b 50%, #ffffff 50%)", "Napoli": "linear-gradient(135deg, #00a0e0 100%, #00a0e0 100%)",
    "Parma": "linear-gradient(135deg, #ffd100 50%, #002d72 50%)", "Roma": "linear-gradient(135deg, #8e1f2f 50%, #f0b516 50%)",
    "Torino": "linear-gradient(135deg, #8a1e32 100%, #8a1e32 100%)", "Udinese": "linear-gradient(135deg, #000000 50%, #ffffff 50%)",
    "Venezia": "linear-gradient(135deg, #ff6b00 33%, #000000 33%, #000000 66%, #007a4d 66%)", "Verona": "linear-gradient(135deg, #002d72 50%, #ffd100 50%)"
}

ROLE_ICONS = {"P": "🧤", "D": "🛡️", "C": "🎯", "A": "⚔️"}

# Funzione universale per leggere FVM e numeri italiani (es. 70,5) in modo sicuro
def safe_float(val):
    try:
        if isinstance(val, str):
            val = val.replace(',', '.').strip()
        return float(val) if val is not None and val != '' else 0.0
    except:
        return 0.0

def get_recent_stat(player_id, stat_type):
    storico = fetch_historical_stats(player_id)
    if not storico: return 0
    valid_seasons = ['2025/26', '2025/2026', '25/26', '2026/27', '2026/2027']
    val, count = 0, 0
    for row in storico:
        season = str(row[0])
        if any(vs in season for vs in valid_seasons):
            if stat_type == 'gol' and row[2] is not None: val += int(row[2])
            elif stat_type == 'assist' and row[3] is not None: val += int(row[3])
            elif stat_type == 'mv' and row[4] is not None:
                try: val += float(row[4]); count += 1
                except: pass
            elif stat_type == 'fm' and len(row) > 5 and row[5] is not None:
                try: val += float(row[5]); count += 1
                except: pass
    if stat_type in ['mv', 'fm']: return (val / count) if count > 0 else 0
    return val

def get_specialist_rank(player_name, team_name, category):
    for t_key, t_data in SPECIALISTS_DATA.items():
        if str(team_name).lower() == t_key.lower():
            for idx, name in enumerate(t_data.get(category, [])):
                if not name: continue
                n_clean = name.lower().replace('.', '')
                p_clean = player_name.lower()
                if n_clean in p_clean: return idx + 1
                parts = n_clean.split()
                if parts and len(parts[0]) >= 3 and parts[0] in p_clean: return idx + 1
    return 99

def show():
    st.markdown("""
    <style>
        span[data-baseweb="tag"] span { color: #FFFFFF !important; font-weight: 800 !important; }
        span[data-baseweb="tag"] svg { fill: #FFFFFF !important; color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2>PLAYER DATABASE <span class='gold-text'>✦</span></h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Esplora il listone e applica i filtri avanzati di scouting.</p>", unsafe_allow_html=True)
    
    players = get_active_players_with_season("2026/27")
    if not players:
        st.warning("Nessun dato disponibile. Vai al Data Center per importare il listone.")
        return
        
    gk_dict = get_gk_stats_from_excel()
        
    col_s, col_b, col_o = st.columns([2, 1, 1])
    with col_s: search = st.text_input("🔎 Cerca giocatore...", placeholder="Es. Lautaro...")
    with col_b: selected_budget = st.selectbox("Budget FVM", options=[300, 400, 500, 600, 700, 800, 900, 1000], index=2)
    with col_o:
        sort_by = st.selectbox("Ordina per", [
            "FVM (Decrescente)", "FVM (Crescente)", "Quotazione (Decrescente)", "Quotazione (Crescente)", 
            "⚽ Più Gol (25/26 - 26/27)", "🎯 Più Assist (25/26 - 26/27)", "📈 Miglior Media Voto (Recenti)", "🔥 Miglior FantaMedia (Recenti)",
            "🚫 Più Clean Sheet (Portieri)", "🧤 Più Rigori Parati (Portieri)", "🧱 Miglior Media Gol Subiti (Muro)",
            "👑 Miglior Coppia AURA (FantaLab)", "Alfabetico (A-Z)", "Alfabetico (Z-A)"
        ], index=0)
        
    col_r, col_t, col_st = st.columns(3)
    with col_r:
        role_map = {"🧤 Portiere": "P", "🛡️ Difensore": "D", "🎯 Centrocampista": "C", "⚔️ Attaccante": "A"}
        f_roles_full = st.multiselect("Ruolo", options=list(role_map.keys()))
        f_roles = [role_map[r] for r in f_roles_full]
    with col_t:
        teams = sorted(list(set([p['team'] for p in players if p.get('team')])))
        f_teams = st.multiselect("Squadra", options=teams)
    with col_st:
        f_status = st.selectbox("Stato", ["Attivi", "Tutti", "Rimossi"])
        
    aura_filters = st.multiselect("🔮 Filtri Speciali AURA", ["🚀 Spinta Offensiva", "🛡️ Da Modificatore", "⚽ Istinto del Gol", "🎯 Fabbrica di Assist", "🎯 Rigorista", "👟 Tiratore Piazzati", "👑 Tiratore da Fermo Totale", "✅ Buon Titolare", "🧤 Para Rigori", "🚫 Clean Sheet Master", "🧱 Muro Invalicabile"])
        
    filtered = []
    for p in players:
        if search and search.lower() not in p['display_name'].lower(): continue
        if f_roles and p.get('fantasy_role_code', '') not in f_roles: continue
        if f_teams and p.get('team') not in f_teams: continue
        if f_status == "Attivi" and p.get('active', 1) != 1: continue
        if f_status == "Rimossi" and p.get('active', 1) == 1: continue

        storico = fetch_historical_stats(p['player_id'])
        chars = fetch_characteristics(p['player_id'])
        
        pres_2627 = 0
        if storico:
            for row in storico:
                if str(row[0]) in ['2026/27', '2026/2027']:
                    try: pres_2627 = int(row[1]) if row[1] is not None else 0
                    except: pass
                    break
        p['presenze_2627'] = pres_2627

        p['rig_rank'] = get_specialist_rank(p['display_name'], p.get('team', ''), 'Rigoristi')
        p['piaz_rank'] = get_specialist_rank(p['display_name'], p.get('team', ''), 'Piazzati')

        if 'original_name' not in p: p['original_name'] = p['display_name']
        badges = ""
        if p['rig_rank'] <= 3: badges += f" <span style='color:#FF3B5C; font-size:0.65rem; border:1px solid rgba(255,59,92,0.5); border-radius:4px; padding:2px 6px; margin-left:6px; background:rgba(255,59,92,0.1);'>{p['rig_rank']}° Rig.</span>"
        if p['piaz_rank'] <= 3: badges += f" <span style='color:#00D9FF; font-size:0.65rem; border:1px solid rgba(0,217,255,0.5); border-radius:4px; padding:2px 6px; margin-left:6px; background:rgba(0,217,255,0.1);'>{p['piaz_rank']}° Piaz.</span>"
        p['display_name'] = p['original_name'] + badges

        r_code = str(p.get('fantasy_role_code', 'A'))[0].upper()
        player_tags = []
        is_dc = r_code in ['D', 'C']
        is_p = r_code == 'P'
        
        all_text = " ".join([str(c) for c in chars if c]).lower() if chars else ""
        tot_gol = sum([row[2] for row in storico if row[2] is not None]) if storico else 0
        tot_ass = sum([row[3] for row in storico if row[3] is not None]) if storico else 0
        
        mv_2526, fm_2526, pres_2526 = 0, 0, 0
        if storico:
            for row in storico:
                if row[0] in ['2025/26', '2025/2026', '25/26']:
                    try:
                        pres_2526 = int(row[1]) if row[1] is not None else 0
                        mv_2526 = float(row[4]) if row[4] is not None else 0
                        fm_2526 = float(row[5]) if len(row) > 5 and row[5] is not None else 0
                    except: pass
                    break
        p['fm_2526'] = fm_2526
        p['presenze_2526'] = pres_2526
        
        p['tot_cs'] = 0
        p['tot_rp'] = 0
        p['tot_gs'] = 0

        if is_p:
            d25 = get_gk_data(p['original_name'], '2025/26', gk_dict)
            d26 = get_gk_data(p['original_name'], '2026/27', gk_dict)
            
            def s2n(val):
                try: return int(float(str(val).strip()))
                except: return 0
            
            pv26_excel = s2n(d26.get('pv'))
            if pv26_excel > 0:
                p['presenze_2627'] = pv26_excel

            p['tot_cs'] = s2n(d25.get('cs')) + s2n(d26.get('cs'))
            p['tot_rp'] = s2n(d25.get('rp')) + s2n(d26.get('rp'))
            p['tot_gs'] = s2n(d25.get('gs')) + s2n(d26.get('gs'))
            
            if p['tot_rp'] >= 2: player_tags.append("🧤 Para Rigori")
            if p['tot_cs'] >= 10: player_tags.append("🚫 Clean Sheet Master")
            
            pres_tot = p['presenze_2526'] + p['presenze_2627']
            
            # MAGIA MURO INVALICABILE: Calcolo GS/Partite
            if pres_tot > 0 and p['tot_gs'] <= (pres_tot * 1.15):
                # Il filtro salva i portieri storici (>= 15 pres) O i portieri scesi in campo quest'anno (pres > 0)
                if pres_tot >= 15 or p['presenze_2627'] > 0:
                    player_tags.append("🧱 Muro Invalicabile")

        if is_dc and any(w in all_text for w in ['esterno', 'trequartista', 'inseriment', 'incursore', 'spinta', 'ala', 'offensiv']) or (r_code == 'D' and (tot_gol >= 2 or tot_ass >= 3)) or (r_code == 'C' and (tot_gol >= 4 or tot_ass >= 4)): 
            player_tags.append("🚀 Spinta Offensiva")
        
        if r_code == 'D' and (mv_2526 >= 6.0 or any(w in all_text for w in ['marcatura', 'anticipo', 'pulit', 'leader', 'solido', 'roccios'])): 
            player_tags.append("🛡️ Da Modificatore")
            
        if tot_gol >= 4 or any(w in all_text for w in ['finalizzazion', 'fiuto', 'tir', 'istinto', 'bomber']): player_tags.append("⚽ Istinto del Gol")
        if tot_ass >= 4 or any(w in all_text for w in ['cross', 'visione', 'chiave', 'regista']): player_tags.append("🎯 Fabbrica di Assist")
            
        if p['rig_rank'] <= 3: player_tags.append("🎯 Rigorista")
        if p['piaz_rank'] <= 3: player_tags.append("👟 Tiratore Piazzati")
        if p['rig_rank'] <= 3 and p['piaz_rank'] <= 3: player_tags.append("👑 Tiratore da Fermo Totale")
            
        if fm_2526 >= 6.0 and pres_2526 >= 15: player_tags.append("✅ Buon Titolare")
            
        if aura_filters and not all(tag in player_tags for tag in aura_filters): continue
            
        filtered.append(p)
        
    affinities = get_exact_affinities()

    # ==============================================================================
    # 1. AUTO-SORT DEI FILTRI SPECIALI AURA
    # ==============================================================================
    if "🚫 Clean Sheet Master" in aura_filters:
        filtered.sort(key=lambda x: (x.get('tot_cs', 0), safe_float(x.get('fvm'))), reverse=True)
        st.info("📊 **Ordinamento AURA Attivo:** Portieri ordinati per il maggior numero di Clean Sheet.")
    elif "🧤 Para Rigori" in aura_filters:
        filtered.sort(key=lambda x: (x.get('tot_rp', 0), safe_float(x.get('fvm'))), reverse=True)
        st.info("📊 **Ordinamento AURA Attivo:** Portieri ordinati per il maggior numero di Rigori Parati.")
    elif "🧱 Muro Invalicabile" in aura_filters:
        def sort_muro(x):
            is_p = (str(x.get('fantasy_role_code', 'A'))[0].upper() == 'P')
            pres_tot = safe_float(x.get('presenze_2627', 0)) + safe_float(x.get('presenze_2526', 0))
            fvm_val = safe_float(x.get('fvm', 0))
            
            # Applica la Media ai Portieri Storici O a chi è sceso in campo nel 2026/27
            if is_p and pres_tot > 0 and (pres_tot >= 15 or safe_float(x.get('presenze_2627', 0)) > 0):
                media_gs = safe_float(x.get('tot_gs', 0)) / pres_tot
                return (media_gs, -fvm_val)
            return (9999, 0)
        
        filtered.sort(key=sort_muro)
        st.info("📊 **Ordinamento AURA Attivo:** Portieri ordinati per la miglior media Gol Subiti / Partite.")
    elif "🎯 Rigorista" in aura_filters:
        filtered.sort(key=lambda x: (x.get('rig_rank', 99), -safe_float(x.get('fvm'))))
        st.info("📊 **Ordinamento AURA Attivo:** Giocatori ordinati per gerarchia Rigoristi (1°, 2°, 3°).")
    elif "👟 Tiratore Piazzati" in aura_filters:
        filtered.sort(key=lambda x: (x.get('piaz_rank', 99), -safe_float(x.get('fvm'))))
        st.info("📊 **Ordinamento AURA Attivo:** Giocatori ordinati per gerarchia Piazzati (1°, 2°, 3°).")
    elif "👑 Tiratore da Fermo Totale" in aura_filters:
        filtered.sort(key=lambda x: (x.get('rig_rank', 99) + x.get('piaz_rank', 99), -safe_float(x.get('fvm'))))
        st.info("📊 **Ordinamento AURA Attivo:** Giocatori ordinati per la combinazione Rigori + Piazzati.")
    elif "✅ Buon Titolare" in aura_filters:
        filtered.sort(key=lambda x: (safe_float(x.get('fm_2526')), safe_float(x.get('presenze_2526'))), reverse=True)
        st.info("📊 **Ordinamento AURA Attivo:** Giocatori ordinati per FantaMedia e Numero di Presenze.")
    
    # ==============================================================================
    # 2. ORDINAMENTI DAL MENU A TENDINA
    # ==============================================================================
    else:
        if sort_by == "FVM (Decrescente)": 
            filtered.sort(key=lambda x: safe_float(x.get('fvm')), reverse=True)
        elif sort_by == "FVM (Crescente)": 
            filtered.sort(key=lambda x: safe_float(x.get('fvm')), reverse=False)
        elif sort_by == "Quotazione (Decrescente)": 
            filtered.sort(key=lambda x: safe_float(x.get('price')), reverse=True)
        elif sort_by == "Quotazione (Crescente)": 
            filtered.sort(key=lambda x: safe_float(x.get('price')), reverse=False)
        elif sort_by == "⚽ Più Gol (25/26 - 26/27)": 
            filtered.sort(key=lambda x: safe_float(get_recent_stat(x['player_id'], 'gol')), reverse=True)
        elif sort_by == "🎯 Più Assist (25/26 - 26/27)": 
            filtered.sort(key=lambda x: safe_float(get_recent_stat(x['player_id'], 'assist')), reverse=True)
        elif sort_by == "📈 Miglior Media Voto (Recenti)": 
            filtered.sort(key=lambda x: safe_float(get_recent_stat(x['player_id'], 'mv')), reverse=True)
        elif sort_by == "🔥 Miglior FantaMedia (Recenti)": 
            filtered.sort(key=lambda x: safe_float(get_recent_stat(x['player_id'], 'fm')), reverse=True)
            
        elif sort_by == "🚫 Più Clean Sheet (Portieri)":
            filtered.sort(key=lambda x: (x.get('tot_cs', 0), safe_float(x.get('fvm'))), reverse=True)
            st.info("📊 **Ordinamento AURA Attivo:** Portieri ordinati per il maggior numero di Clean Sheet storici.")
        elif sort_by == "🧤 Più Rigori Parati (Portieri)":
            filtered.sort(key=lambda x: (x.get('tot_rp', 0), safe_float(x.get('fvm'))), reverse=True)
            st.info("📊 **Ordinamento AURA Attivo:** Portieri ordinati per il maggior numero di Rigori Parati storici.")
        elif sort_by == "🧱 Miglior Media Gol Subiti (Muro)":
            def sort_gs(x):
                is_p = (str(x.get('fantasy_role_code', 'A'))[0].upper() == 'P')
                pres_tot = safe_float(x.get('presenze_2627', 0)) + safe_float(x.get('presenze_2526', 0))
                fvm_val = safe_float(x.get('fvm', 0))
                
                if is_p and pres_tot > 0 and (pres_tot >= 15 or safe_float(x.get('presenze_2627', 0)) > 0):
                    media_gs = safe_float(x.get('tot_gs', 0)) / pres_tot
                    return (media_gs, -fvm_val)
                return (9999, 0)
                
            filtered.sort(key=sort_gs)
            st.info("📊 **Ordinamento AURA Attivo:** Portieri ordinati dalla miglior media Gol Subiti/Partita. Sono inclusi tutti i portieri attivi nella stagione 26/27!")

        elif sort_by == "👑 Miglior Coppia AURA (FantaLab)":
            def sort_coppia_aura(x):
                is_p = (str(x.get('fantasy_role_code', 'A'))[0].upper() == 'P')
                team = x.get('team', 'Svincolato')
                aff_score = safe_float(affinities.get(team, [{'score': 0}])[0]['score'])
                fvm = safe_float(x.get('fvm'))
                pres_2627 = safe_float(x.get('presenze_2627', 0))
                
                if is_p:
                    is_titolare = 1 if pres_2627 > 0 else 0
                    return (is_titolare, aff_score, fvm)
                else:
                    return (1, aff_score, fvm)

            filtered.sort(key=sort_coppia_aura, reverse=True)
            st.info("📊 **Ordinamento AURA Attivo:** Giocatori ordinati per miglior incrocio FantaLab. Per i Portieri la titolarità è calcolata sulla stagione 2026/2027; per gli altri segue l'FVM.")
        elif sort_by == "Alfabetico (A-Z)": 
            filtered.sort(key=lambda x: str(x.get('display_name', '')))
        elif sort_by == "Alfabetico (Z-A)": 
            filtered.sort(key=lambda x: str(x.get('display_name', '')), reverse=True)
        
    st.write(f"**Trovati:** {len(filtered)} giocatori")
    
    items_per_page = 20
    total_pages = max(1, (len(filtered) - 1) // items_per_page + 1)
    if "pl_page" not in st.session_state: st.session_state.pl_page = 1
    if st.session_state.pl_page > total_pages: st.session_state.pl_page = 1
    
    start_idx = (st.session_state.pl_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    st.write("")
    for p in filtered[start_idx:end_idx]:
        render_player_row(p, selected_budget, TEAM_COLORS, ROLE_ICONS)
        
    if total_pages > 1:
        st.write("")
        c1, c2, c3 = st.columns([1,2,1])
        with c1:
            if st.button("← Precedente", disabled=(st.session_state.pl_page == 1)): st.session_state.pl_page -= 1; st.rerun()
        with c2: st.markdown(f"<p style='text-align:center; color:#888;'>Pagina {st.session_state.pl_page} di {total_pages}</p>", unsafe_allow_html=True)
        with c3:
            if st.button("Successiva →", disabled=(st.session_state.pl_page == total_pages)): st.session_state.pl_page += 1; st.rerun()