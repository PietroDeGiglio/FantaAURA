import sqlite3
import os

DB_PATH = "database/fantaaura.db"

def apply_migrations():
    """Applica la struttura relazionale della Fase 2 senza sovrascrivere i dati esistenti."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Identità Esterne
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_external_ids (
        player_id TEXT,
        source TEXT,
        external_id TEXT,
        PRIMARY KEY (player_id, source, external_id)
    )
    """)

    # 2. Database Squadre
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        normalized_name TEXT UNIQUE
    )
    """)

    # 3. Squadre per Stagione
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_seasons (
        team_id INTEGER,
        season TEXT,
        PRIMARY KEY (team_id, season)
    )
    """)

    # 4. Stagioni Giocatori (Storico e Corrente)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_seasons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id TEXT,
        season TEXT,
        team_id INTEGER,
        fantasy_role TEXT,
        mantra_role TEXT,
        fantacalcio_price INTEGER,
        fvm INTEGER,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(player_id, season)
    )
    """)

    # 5. Statistiche Stagionali Aggregate
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_season_stats (
        player_id TEXT,
        season TEXT,
        appearances INTEGER DEFAULT NULL,
        starts INTEGER DEFAULT NULL,
        substitute_appearances INTEGER DEFAULT NULL,
        minutes INTEGER DEFAULT NULL,
        goals INTEGER DEFAULT NULL,
        assists INTEGER DEFAULT NULL,
        penalties_scored INTEGER DEFAULT NULL,
        penalties_missed INTEGER DEFAULT NULL,
        yellow_cards INTEGER DEFAULT NULL,
        red_cards INTEGER DEFAULT NULL,
        own_goals INTEGER DEFAULT NULL,
        clean_sheets INTEGER DEFAULT NULL,
        mv REAL DEFAULT NULL,
        fm REAL DEFAULT NULL,
        bonus REAL DEFAULT NULL,
        malus REAL DEFAULT NULL,
        data_quality TEXT DEFAULT 'missing', -- 'complete', 'partial', 'missing', 'needs_review'
        PRIMARY KEY (player_id, season)
    )
    """)

    # 6. Partite (Calendario)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        season TEXT,
        matchday INTEGER,
        date TIMESTAMP,
        home_team_id INTEGER,
        away_team_id INTEGER,
        home_score INTEGER DEFAULT NULL,
        away_score INTEGER DEFAULT NULL,
        status TEXT
    )
    """)

    # 7. Statistiche Granulari per Singolo Match
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_match_stats (
        player_id TEXT,
        match_id TEXT,
        minutes INTEGER DEFAULT NULL,
        starter INTEGER DEFAULT NULL,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        penalties_scored INTEGER DEFAULT 0,
        penalties_missed INTEGER DEFAULT 0,
        yellow_cards INTEGER DEFAULT 0,
        red_cards INTEGER DEFAULT 0,
        own_goals INTEGER DEFAULT 0,
        clean_sheet INTEGER DEFAULT 0,
        mv REAL DEFAULT NULL,
        fm REAL DEFAULT NULL,
        bonus REAL DEFAULT 0,
        malus REAL DEFAULT 0,
        PRIMARY KEY (player_id, match_id)
    )
    """)

    # 8. Formazioni e Tattica
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lineups (
        match_id TEXT,
        team_id INTEGER,
        player_id TEXT,
        starter INTEGER,
        tactical_position TEXT, -- es. LWB, CB, CAM
        shirt_number INTEGER,
        minutes INTEGER,
        PRIMARY KEY (match_id, player_id)
    )
    """)

    conn.commit()
    conn.close()