import streamlit as st
import sqlite3
import os
import base64
from aura_engine import get_exact_affinities

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'fantaaura.db')

def calculate_fvm_proporzionato(fvm_base, budget_selezionato, budget_base=500):
    if not fvm_base: return 0
    return int(round((fvm_base * budget_selezionato) / budget_base))

@st.cache_data(show_spinner=False)
def fetch_historical_stats(player_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT season, appearances, goals, assists, mv, fm FROM player_season_stats WHERE player_id = ? ORDER BY season DESC", (player_id,))
        rows = c.fetchall()
        conn.close(); return rows
    except: return []

@st.cache_data(show_spinner=False)
def fetch_characteristics(player_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT tactical_position, detailed_roles, strengths, weaknesses, play_style FROM player_characteristics WHERE player_id = ?", (player_id,))
        row = c.fetchone()
        conn.close(); return row
    except: return None

@st.cache_data(show_spinner=False)
def get_team_logo_b64(team_name):
    if not team_name or team_name == "Svincolato": return None
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "loghi", f"{team_name}.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f: encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

@st.cache_data(show_spinner=False)
def precarica_tutti_i_titolari():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = """
            SELECT p.team, p.fantasy_role_code, p.display_name 
            FROM players p
            LEFT JOIN player_season_stats s 
                ON p.player_id = s.player_id 
                AND s.season IN ('2026/27', '2026/2027')
            WHERE p.active = 1
            GROUP BY p.player_id
            ORDER BY MAX(COALESCE(CAST(s.appearances AS INTEGER), 0)) DESC, p.fvm DESC
        """
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        
        titolari_dict = {}
        for row in rows:
            team, role, name = row
            if team not in titolari_dict: titolari_dict[team] = {}
            if role not in titolari_dict[team]:
                titolari_dict[team][role] = name
        return titolari_dict
    except Exception:
        return {}

def get_top_player_for_role(team_name, role_code):
    titolari = precarica_tutti_i_titolari()
    return titolari.get(team_name, {}).get(role_code, "Sconosciuto")

# --- NUOVO SISTEMA: ESTRAZIONE DATI PORTIERI DAGLI EXCEL ---
@st.cache_data(show_spinner=False)
def get_gk_stats_from_excel():
    gk_stats = {}
    
    # Clean Sheets 2025/26 estratti dalla tua lista esatta
    cs_dict_2526 = {
        'butez': 19, 'svilar': 18, 'sommer': 15, 'maignan': 13, 'carnesecchi': 13, 
        'di gregorio': 13, 'provedel': 12, 'audero': 11, 'milinkovic': 11, 'okoye': 10, 
        'falcone': 10, 'de gea': 10, 'paleari': 9, 'caprile': 8, 'skorupski': 7, 
        'corvi': 7, 'muric': 6, 'montipò': 5, 'montipo': 5, 'suzuki': 5, 'bijlow': 5, 
        'leali': 4, 'semper': 4, 'martinez': 3, 'motta': 3, 'israel': 3, 
        'meret': 3, 'ravaglia': 2, 'turati': 2, 'pessina': 2, 'perin': 2, 
        'rinaldi': 1, 'perilli': 1, 'scuffet': 1, 'sava': 1, 'terracciano': 1
    }
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_2526, file_2627 = None, None
    
    # Cerca i tuoi due file Excel nella cartella
    for f in os.listdir(base_dir):
        if '2025_26' in f and f.endswith('.xlsx'): file_2526 = os.path.join(base_dir, f)
        elif '2026_27' in f and f.endswith('.xlsx'): file_2627 = os.path.join(base_dir, f)
        
    try:
        import pandas as pd
        if file_2526:
            df = pd.read_excel(file_2526, skiprows=1) # Salta la riga del titolo
            for _, row in df.iterrows():
                if str(row.get('R', '')).upper() in ['P', 'POR']:
                    name = str(row.get('Nome', '')).lower()
                    gs = int(row.get('Gs', 0)) if pd.notna(row.get('Gs')) else 0
                    rp = int(row.get('Rp', 0)) if pd.notna(row.get('Rp')) else 0
                    
                    cs = 0
                    for k, v in cs_dict_2526.items():
                        if k in name or name in k:
                            cs = v; break
                            
                    if name not in gk_stats: gk_stats[name] = {}
                    gk_stats[name]['2025/26'] = {'gs': gs, 'rp': rp, 'cs': cs}
                    
        if file_2627:
            df2 = pd.read_excel(file_2627, skiprows=1)
            for _, row in df2.iterrows():
                if str(row.get('R', '')).upper() in ['P', 'POR']:
                    name = str(row.get('Nome', '')).lower()
                    pv = int(row.get('Pv', 0)) if pd.notna(row.get('Pv')) else 0
                    gs = int(row.get('Gs', 0)) if pd.notna(row.get('Gs')) else 0
                    rp = int(row.get('Rp', 0)) if pd.notna(row.get('Rp')) else 0
                    
                    # Stima Clean Sheet per la stagione in corso (se Gs=0, CS=Pv)
                    cs = pv if gs == 0 else max(0, pv - gs)
                    
                    if name not in gk_stats: gk_stats[name] = {}
                    gk_stats[name]['2026/27'] = {'gs': gs, 'rp': rp, 'cs': cs}
    except: pass
        
    return gk_stats

def get_gk_data(player_name, season, gk_dict):
    name_low = str(player_name).lower()
    for k, v in gk_dict.items():
        if k in name_low or name_low in k:
            return v.get(season, {'gs': '-', 'rp': '-', 'cs': '-'})
    return {'gs': '-', 'rp': '-', 'cs': '-'}
# -----------------------------------------------------------

def render_player_row(player, selected_budget, team_colors_dict=None, role_icons_dict=None):
    r_map = {"Portiere": "P", "Difensore": "D", "Centrocampista": "C", "Attaccante": "A"}
    r = r_map.get(player.get('fantasy_role', ''), player.get('fantasy_role_code', ''))
    r_lower = r.lower()

    team_name = player.get('team', 'Svincolato').strip()
    logo_b64 = get_team_logo_b64(team_name)
    icon_html = f"<img src='{logo_b64}' style='width: 38px; height: 38px; object-fit: contain; drop-shadow: 0 0 5px rgba(255,255,255,0.2);'>" if logo_b64 else f"<span>{role_icons_dict.get(r, '⚽') if role_icons_dict else '⚽'}</span>"
    bg_col = "transparent" if logo_b64 else team_colors_dict.get(team_name, "linear-gradient(135deg, #222, #111)") if team_colors_dict else "linear-gradient(135deg, #222, #111)"

    qta, fvm = player.get('price') or "-", player.get('fvm') or 0
    fvm_prop = calculate_fvm_proporzionato(fvm, selected_budget)

    storico, chars = fetch_historical_stats(player['player_id']), fetch_characteristics(player['player_id'])
    
    html = f"""
    <style>
        details.fanta-row > summary::-webkit-details-marker {{ display: none; }}
        details.fanta-row > summary {{ list-style: none; outline: none; cursor: pointer; }}
        details.fanta-row[open] .player-row {{ border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom-color: transparent; }}
    </style>
    <details class="fanta-row" style="margin-bottom: 8px;" name="fanta-accordion">
        <summary>
            <div class="player-row accent-{r_lower}" style="margin-bottom: 0;">
                <div class="pr-left">
                    <div class="pr-photo" style="background: {bg_col}; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; border: {'none' if logo_b64 else '2px solid #1A1A1A'}; box-shadow: {'none' if logo_b64 else 'inset 0 0 10px rgba(0,0,0,0.5)'};">
                        {icon_html}
                    </div>
                    <div class="pr-info">
                        <p class="pr-name">{player['display_name']}</p>
                        <p class="pr-team">{team_name}</p>
                    </div>
                </div>
                <div class="pr-role"><span class="badge-{r_lower}">{r}</span></div>
                <div class="pr-stats">
                    <div class="pr-stat-box"><span class="pr-stat-val">{qta}</span><span class="pr-stat-lbl">Q. INI</span></div>
                    <div class="pr-stat-box highlight-box"><span class="pr-stat-val pr-fvm-pers">{fvm_prop}</span><span class="pr-stat-lbl">FVM ({selected_budget})</span></div>
                </div>
            </div>
        </summary>
    """

    def clean_val(v): return v if v and str(v).lower() != "nan" else "-"

    if chars:
        tactical, roles, strns, weaks, style = chars
        html += f"""
        <div style="background-color: #0D0D0D; padding: 15px 20px; border-left: 1px solid #1A1A1A; border-right: 1px solid #1A1A1A; border-top: 1px dashed #222;">
            <h5 style="color: #00D9FF; margin-top: 0; margin-bottom: 12px; font-size: 0.85rem; text-transform: uppercase;">Profilo Tattico & Tecnico</h5>
            <div style="display: flex; flex-wrap: wrap; gap: 15px; color: #ccc; font-size: 0.85rem;">
                <div style="flex: 1; min-width: 250px;"><span style="color: #888;">Posizione:</span> <strong style="color: #fff;">{clean_val(tactical)}</strong><br><span style="color: #888;">Ruoli:</span> <span style="color: #fff;">{clean_val(roles)}</span></div>
                <div style="flex: 1; min-width: 250px;"><span style="color: #39FF14;">✚ Punti di Forza:</span> <span style="color: #fff;">{clean_val(strns)}</span><br><span style="color: #FF3B5C;">✖ Debolezze:</span> <span style="color: #fff;">{clean_val(weaks)}</span></div>
            </div>
        </div>
        """
        
    affinities = get_exact_affinities()
    
    if team_name in affinities and r == 'P':
        top_matches = affinities[team_name][:4]
        pairs_html = ""
        for p_data in top_matches:
            p_logo = get_team_logo_b64(p_data['team'])
            p_icon = f"<img src='{p_logo}' style='width:24px; height:24px; vertical-align:middle; margin-right:5px;'>" if p_logo else ""
            
            player_affine = get_top_player_for_role(p_data['team'], 'P')
            display_title = f"{p_icon}<br><span style='font-size: 0.85rem; color: #ccc;'>{player_affine}</span>"

            pairs_html += f"""
            <div style="background: #111; padding: 12px; border-radius: 8px; border: 1px solid #333; flex: 1; min-width: 140px; text-align: center;">
                <div style="font-weight: 800; color: #fff; margin-bottom: 5px; font-size: 0.95rem; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    {display_title}
                </div>
                <div style="font-size: 1rem; font-weight: 900; color: #39FF14; margin-top: 5px;">
                    {p_data['score']}%
                </div>
            </div>
            """
            
        html += f"""
        <div style="background-color: #0D0D0D; padding: 15px 20px; border-left: 1px solid #1A1A1A; border-right: 1px solid #1A1A1A; border-top: 1px dashed #222;">
            <h5 style="color: #FFD700; margin-top: 0; margin-bottom: 12px; font-size: 0.85rem; text-transform: uppercase;">Coppie Consigliate FantaLab (Alternanza Calendario)</h5>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">{pairs_html}</div>
        </div>
        """

    if storico:
        table_rows = ""
        # SE È UN PORTIERE, USA LA NUOVA TABELLA CON GS E CS!
        if r == 'P':
            gk_dict = get_gk_stats_from_excel()
            for row in storico:
                season = str(row[0])
                pv = row[1] if row[1] is not None else "-"
                mv = row[4] if row[4] is not None else "-"
                fm = row[5] if row[5] is not None else "-"
                
                s_key = '2025/26' if '25/26' in season else '2026/27'
                gk_data = get_gk_data(player['display_name'], s_key, gk_dict)
                gs, cs, rp = gk_data['gs'], gk_data['cs'], gk_data['rp']
                
                table_rows += f'<tr style="border-bottom: 1px solid #1A1A1A;"><td style="padding: 10px 5px; color:#fff;">{season}</td><td>{pv}</td><td>{gs}</td><td><strong style="color:#00D9FF;">{cs}</strong></td><td>{rp}</td><td>{mv}</td><td><strong style="color:#FFD700;">{fm}</strong></td></tr>'
                
            header = '<th style="padding: 0 5px 8px 5px; font-weight: 500;">Stagione</th><th style="padding-bottom: 8px;">Pv</th><th style="padding-bottom: 8px;">GS</th><th style="padding-bottom: 8px;">CS</th><th style="padding-bottom: 8px;">RP</th><th style="padding-bottom: 8px;">MV</th><th style="padding-bottom: 8px;">FM</th>'
        
        # ALTRIMENTI, USA LA VECCHIA TABELLA CON GOL E ASSIST
        else:
            for row in storico:
                season, pv, gol, ass, mv, fm = row[0], row[1], row[2], row[3], row[4], row[5]
                table_rows += f'<tr style="border-bottom: 1px solid #1A1A1A;"><td style="padding: 10px 5px; color:#fff;">{season}</td><td>{pv if pv is not None else "-"}</td><td>{gol if gol is not None else "-"}</td><td>{ass if ass is not None else "-"}</td><td>{mv if mv is not None else "-"}</td><td><strong style="color:#FFD700;">{fm if fm is not None else "-"}</strong></td></tr>'
            header = '<th style="padding: 0 5px 8px 5px; font-weight: 500;">Stagione</th><th style="padding-bottom: 8px;">Pv</th><th style="padding-bottom: 8px;">Gol</th><th style="padding-bottom: 8px;">Ass</th><th style="padding-bottom: 8px;">MV</th><th style="padding-bottom: 8px;">FM</th>'

        html += f"""
        <div style="background-color: #0D0D0D; padding: 15px 20px; border-radius: 0 0 12px 12px; border: 1px solid #1A1A1A; border-top: 1px dashed #222;">
            <h5 style="color: #FFD700; margin-top: 0; margin-bottom: 10px; font-size: 0.85rem; text-transform: uppercase;">Storico AURA</h5>
            <table style="width:100%; text-align:left; color:#888; font-size:0.9rem; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #333;">{header}</tr>
                {table_rows}
            </table>
        </div>
        """
    else: html += '<div style="background-color: #0D0D0D; padding: 15px 20px; border-radius: 0 0 12px 12px; border: 1px solid #1A1A1A; border-top: 1px dashed #222;"><p style="color: #666; font-size: 0.85rem; margin: 0;">Nessun dato storico archiviato.</p></div>'

    html += "</details>"
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)