import pandas as pd
import os
import streamlit as st

# --- 1. MOTORE CALENDARIO (Per Fixture Lab e Tabella 38 Giornate) ---
TIERS = {
    'Inter': 1, 'Napoli': 1, 'Roma': 1, 'Como': 1, 'Milan': 1, 'Juventus': 1,
    'Atalanta': 2, 'Bologna': 2, 'Lazio': 2, 'Udinese': 2, 'Sassuolo': 2,
    'Torino': 3, 'Parma': 3, 'Cagliari': 3, 'Fiorentina': 3, 'Genoa': 3,
    'Lecce': 4, 'Monza': 4, 'Frosinone': 4, 'Venezia': 4
}

def get_match_difficulty(team, opp, is_home):
    opp_score = {1: 4, 2: 3, 3: 2, 4: 1}.get(TIERS.get(opp, 3), 2)
    my_str = {1: 2, 2: 1.5, 3: 1, 4: 0.5}.get(TIERS.get(team, 3), 1)
    loc_mod = -0.5 if is_home else 1.0
    val = (opp_score + loc_mod) - my_str
    
    if val >= 2.5: return "🔴"
    elif val <= 0.5: return "🟢"
    else: return "🟠"

@st.cache_data
def get_team_difficulties():
    file_path = None
    possibili_paths = [
        r"C:\FantaAURA\Calendario_Serie_A_2026-27.csv",
        "Calendario_Serie_A_2026-27.csv",
        os.path.join(os.path.dirname(__file__), "Calendario_Serie_A_2026-27.csv")
    ]
    for p in possibili_paths:
        if os.path.exists(p):
            file_path = p; break
            
    if not file_path: return {} 
    
    df_cal = pd.read_csv(file_path)
    cal_dict = {}
    for idx, row in df_cal.iterrows():
        g = int(str(row['Giornata']).replace('Giornata ', ''))
        casa, trasf = str(row['Casa']).strip(), str(row['Trasferta']).strip()
        if casa not in cal_dict: cal_dict[casa] = {}
        if trasf not in cal_dict: cal_dict[trasf] = {}
        cal_dict[casa][g] = {'diff': get_match_difficulty(casa, trasf, True), 'opp': trasf, 'is_home': True}
        cal_dict[trasf][g] = {'diff': get_match_difficulty(trasf, casa, False), 'opp': casa, 'is_home': False}
    return cal_dict


# --- 2. MOTORE AFFINITÀ FANTALAB (Per GK Lab e Ordinamento Giocatori) ---
FANTALAB_PAIRS = {
    "Roma-Bologna": 95, "Atalanta-Sassuolo": 95, "Inter-Bologna": 95, "Como-Bologna": 93, 
    "Como-Udinese": 93, "Lazio-Lecce": 93, "Milan-Fiorentina": 93, "Milan-Lecce": 93, 
    "Napoli-Lecce": 93, "Roma-Monza": 93, "Napoli-Torino": 93, "Milan-Parma": 93, 
    "Lazio-Cagliari": 92, "Juventus-Cagliari": 92, "Como-Torino": 92,
    "Genoa-Lecce": 93, "Genoa-Frosinone": 92, "Parma-Genoa": 91, "Bologna-Venezia": 91, 
    "Sassuolo-Venezia": 91, "Torino-Frosinone": 89, "Udinese-Genoa": 88, 
    "Cagliari-Fiorentina": 87, "Fiorentina-Venezia": 87, "Torino-Lecce": 87, "Parma-Monza": 87,
    "Inter-Cagliari": 93, "Inter-Monza": 93, "Inter-Torino": 92, "Inter-Sassuolo": 91,
    "Juventus-Bologna": 92, "Juventus-Lazio": 92, "Juventus-Torino": 92, "Juventus-Parma": 91, "Juventus-Fiorentina": 91,
    "Atalanta-Monza": 92, "Atalanta-Bologna": 91, "Atalanta-Udinese": 91,
    "Como-Fiorentina": 92, "Como-Sassuolo": 92,
    "Milan-Sassuolo": 92,
    "Napoli-Frosinone": 91, "Napoli-Fiorentina": 89,
    "Roma-Venezia": 92, "Roma-Genoa": 89
}

@st.cache_data
def get_exact_affinities():
    affinities = {}
    for pair, score in FANTALAB_PAIRS.items():
        teams = pair.split('-')
        t1, t2 = teams[0], teams[1]
        if t1 not in affinities: affinities[t1] = []
        if t2 not in affinities: affinities[t2] = []
        
        if not any(x['team'] == t2 for x in affinities[t1]): affinities[t1].append({'team': t2, 'score': score})
        if not any(x['team'] == t1 for x in affinities[t2]): affinities[t2].append({'team': t1, 'score': score})
        
    for t in affinities:
        affinities[t] = sorted(affinities[t], key=lambda x: x['score'], reverse=True)
    return affinities