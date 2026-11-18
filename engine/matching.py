import unicodedata
import re
import sqlite3
import difflib

def normalize_name(name):
    if not name: return ""
    n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
    n = re.sub(r'[^a-z0-9\s]', '', n.lower())
    return re.sub(r'\s+', ' ', n).strip()

def get_player_match(db_path, external_id, source, raw_name, team, season, role=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    norm_name = normalize_name(raw_name)
    norm_team = normalize_name(team)
    
    # Prendi la prima lettera del ruolo
    norm_role = str(role).strip().upper()[0] if role and str(role).strip() and str(role).strip() != "nan" else ""

    if external_id and external_id != "nan":
        cursor.execute("SELECT player_id FROM player_external_ids WHERE source=? AND external_id=?", (source, external_id))
        res = cursor.fetchone()
        if res:
            conn.close()
            return 'EXACT_ID', res[0], 100

    # Estrae tutti i giocatori. COALESCE ci salva anche se mancano i codici ruolo vecchi.
    cursor.execute("""
        SELECT p.player_id, p.normalized_name, GROUP_CONCAT(LOWER(s.team)), GROUP_CONCAT(UPPER(COALESCE(s.fantasy_role_code, SUBSTR(s.fantasy_role, 1, 1))))
        FROM players p 
        LEFT JOIN player_season s ON p.player_id = s.player_id
        GROUP BY p.player_id
    """)
    all_players = cursor.fetchall()
    
    best_id = None
    best_score = 0
    best_type = 'NEEDS_REVIEW'

    for p_id, p_norm, p_teams, p_roles in all_players:
        # 1. Punteggio Matematico di Similarità
        score = difflib.SequenceMatcher(None, norm_name, p_norm).ratio()
        
        # 2. Bonus Squadra (+20%)
        team_matched = False
        if p_teams and norm_team:
            if norm_team in p_teams or p_teams in norm_team or any(t in norm_team for t in p_teams.split(',')):
                score += 0.2
                team_matched = True
                
        # 3. Bonus Ruolo (+10%)
        if p_roles and norm_role and norm_role in p_roles:
            score += 0.1
            
        # 4. Penalità Omonimia Estrema (-30%)
        db_words = p_norm.split()
        csv_words = norm_name.split()
        if db_words and csv_words and db_words[0] == csv_words[0]:
            if len(db_words) > 1 and len(csv_words) > 1:
                # Se l'iniziale del nome è diversa, abbatti il punteggio
                if db_words[1][0] != csv_words[1][0]:
                    score -= 0.3
                    
        if score > best_score:
            best_score = score
            best_id = p_id
            
            if score >= 0.8:
                best_type = 'FUZZY_MATCH_HIGH'
            elif score >= 0.65:
                best_type = 'FUZZY_MATCH_LOW'

    conn.close()
    
    # Se il punteggio finale supera la soglia di sicurezza, il match è validato
    if best_score >= 0.65:
        return best_type, best_id, int(min(best_score * 100, 100))
    
    return 'NEEDS_REVIEW', None, 50