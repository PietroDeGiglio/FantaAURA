import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), 'fantaaura.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS leagues (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT NOT NULL, participants INTEGER, 
        budget INTEGER, fantasy_type TEXT, defense_modifier BOOLEAN, goalkeeper_slots INTEGER, 
        defender_slots INTEGER, midfielder_slots INTEGER, forward_slots INTEGER, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        fantacalcio_player_id TEXT UNIQUE,
        display_name TEXT NOT NULL, 
        normalized_name TEXT NOT NULL,
        photo_url TEXT, 
        photo_source TEXT, 
        photo_status TEXT DEFAULT 'needs_review', 
        photo_last_checked TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS player_season (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id TEXT, season TEXT, team TEXT, fantasy_role_code TEXT, fantasy_role TEXT, mantra_role TEXT,
        price INTEGER, initial_price INTEGER, price_difference INTEGER, price_mantra INTEGER,
        initial_price_mantra INTEGER, price_difference_mantra INTEGER, fvm INTEGER, fvm_mantra INTEGER,
        active BOOLEAN DEFAULT 1, source TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (player_id) REFERENCES players (player_id),
        UNIQUE(player_id, season))''')

    c.execute('''CREATE TABLE IF NOT EXISTS data_update_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        finished_at TIMESTAMP, source TEXT, operation TEXT, records_found INTEGER, records_added INTEGER, 
        records_updated INTEGER, records_skipped INTEGER, records_failed INTEGER, status TEXT, error_message TEXT)''')
    
    c.execute('PRAGMA table_info(player_season)')
    ps_columns = [col[1] for col in c.fetchall()]
    if 'fantasy_role_code' not in ps_columns:
        try: c.execute('ALTER TABLE player_season ADD COLUMN fantasy_role_code TEXT')
        except: pass

    c.execute('PRAGMA table_info(player_season_stats)')
    pss_columns = [col[1] for col in c.fetchall()]
    if pss_columns and 'mv' not in pss_columns:
        c.execute('DROP TABLE player_season_stats')

    c.execute('''CREATE TABLE IF NOT EXISTS player_external_ids (
        player_id TEXT, source TEXT, external_id TEXT, PRIMARY KEY (player_id, source, external_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, normalized_name TEXT UNIQUE)''')

    c.execute('''CREATE TABLE IF NOT EXISTS team_seasons (
        team_id INTEGER, season TEXT, PRIMARY KEY (team_id, season))''')

    c.execute('''CREATE TABLE IF NOT EXISTS player_season_stats (
        player_id TEXT, season TEXT, appearances INTEGER DEFAULT NULL, starts INTEGER DEFAULT NULL,
        substitute_appearances INTEGER DEFAULT NULL, minutes INTEGER DEFAULT NULL, goals INTEGER DEFAULT NULL,
        assists INTEGER DEFAULT NULL, penalties_scored INTEGER DEFAULT NULL, penalties_missed INTEGER DEFAULT NULL,
        yellow_cards INTEGER DEFAULT NULL, red_cards INTEGER DEFAULT NULL, own_goals INTEGER DEFAULT NULL,
        clean_sheets INTEGER DEFAULT NULL, mv REAL DEFAULT NULL, fm REAL DEFAULT NULL,
        bonus REAL DEFAULT NULL, malus REAL DEFAULT NULL, data_quality TEXT DEFAULT 'missing',
        PRIMARY KEY (player_id, season))''')

    # PULIZIA STAGIONE DOPPIA
    c.execute("DELETE FROM player_season_stats WHERE season = '2026/27 (Corrente)'")

    c.execute('''CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY, season TEXT, matchday INTEGER, date TIMESTAMP,
        home_team_id INTEGER, away_team_id INTEGER, home_score INTEGER DEFAULT NULL,
        away_score INTEGER DEFAULT NULL, status TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS player_match_stats (
        player_id TEXT, match_id TEXT, minutes INTEGER DEFAULT NULL, starter INTEGER DEFAULT NULL,
        goals INTEGER DEFAULT 0, assists INTEGER DEFAULT 0, penalties_scored INTEGER DEFAULT 0,
        penalties_missed INTEGER DEFAULT 0, yellow_cards INTEGER DEFAULT 0, red_cards INTEGER DEFAULT 0,
        own_goals INTEGER DEFAULT 0, clean_sheet INTEGER DEFAULT 0, mv REAL DEFAULT NULL,
        fm REAL DEFAULT NULL, bonus REAL DEFAULT 0, malus REAL DEFAULT 0,
        PRIMARY KEY (player_id, match_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS lineups (
        match_id TEXT, team_id INTEGER, player_id TEXT, starter INTEGER,
        tactical_position TEXT, shirt_number INTEGER, minutes INTEGER,
        PRIMARY KEY (match_id, player_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS player_characteristics (
        player_id TEXT PRIMARY KEY,
        tactical_position TEXT,
        detailed_roles TEXT,
        strengths TEXT,
        weaknesses TEXT,
        play_style TEXT,
        FOREIGN KEY (player_id) REFERENCES players (player_id))''')

    conn.commit()
    conn.close()

def get_user():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, name FROM users ORDER BY id ASC LIMIT 1')
    user = c.fetchone()
    conn.close()
    return {"id": user[0], "name": user[1]} if user else None

def create_user(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def get_leagues(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM leagues WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    cols = [col[0] for col in c.description]
    leagues = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return leagues

def create_league(user_id, name, participants, budget, fantasy_type, defense_modifier, gk, df, mf, fw):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO leagues (user_id, name, participants, budget, fantasy_type, defense_modifier, goalkeeper_slots, defender_slots, midfielder_slots, forward_slots) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (user_id, name, participants, budget, fantasy_type, defense_modifier, gk, df, mf, fw))
    league_id = c.lastrowid
    conn.commit()
    conn.close()
    return league_id

def get_league_by_id(league_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM leagues WHERE id = ?', (league_id,))
    cols = [col[0] for col in c.description]
    row = c.fetchone()
    conn.close()
    return dict(zip(cols, row)) if row else None

def generate_player_id():
    return f"FA_{str(uuid.uuid4().hex)[:8].upper()}"

def get_active_players_with_season(season="2026/27"):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT p.player_id, p.fantacalcio_player_id, p.display_name, p.photo_url, p.photo_status,
                  s.team, s.fantasy_role_code, s.fantasy_role, s.mantra_role, 
                  s.price, s.initial_price, s.fvm, s.fvm_mantra, s.price_mantra, s.active
                  FROM players p
                  JOIN player_season s ON p.player_id = s.player_id
                  WHERE s.season = ?''', (season,))
    cols = [col[0] for col in c.description]
    players = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return players

def log_update(source, operation, found, added, updated, skipped, failed, status, error=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO data_update_log 
                  (source, operation, records_found, records_added, records_updated, records_skipped, records_failed, status, error_message, finished_at) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
              (source, operation, found, added, updated, skipped, failed, status, error))
    conn.commit()
    conn.close()