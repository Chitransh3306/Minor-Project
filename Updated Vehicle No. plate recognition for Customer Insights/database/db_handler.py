import sqlite3
import pandas as pd
import os

DB_PATH = "database/vehicle_data.db"
SCHEMA_PATH = "database/schema.sql"

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize DB and create tables if not exist."""
    with connect_db() as conn:
        conn.executescript(open(SCHEMA_PATH).read())
        conn.commit()

def import_csv_data():
    """Import static reference tables (Demographics, Items, Prefers) from CSVs."""
    with connect_db() as conn:
        # Demographics
        if os.path.exists("database/demographics.csv"):
            df = pd.read_csv("database/demographics.csv")
            df.to_sql("Demographics", conn, if_exists="append", index=False)
        # Items
        if os.path.exists("database/items.csv"):
            df = pd.read_csv("database/items.csv")
            df.to_sql("Items", conn, if_exists="append", index=False)
        # Prefers
        if os.path.exists("database/prefers.csv"):
            df = pd.read_csv("database/prefers.csv")
            df.to_sql("Prefers", conn, if_exists="append", index=False)
        conn.commit()

def insert_vehicle(plate_no, state_code, state_name):
    """Insert recognized vehicle and its region."""
    with connect_db() as conn:
        conn.execute("INSERT OR IGNORE INTO State (State_Code, State_Name) VALUES (?, ?)", (state_code, state_name))
        conn.execute("INSERT OR IGNORE INTO Vehicle_Record (Plate_No, State_Code) VALUES (?, ?)", (plate_no, state_code))
        conn.commit()

def fetch_state_counts():
    """Fetch aggregated vehicle counts per state."""
    with connect_db() as conn:
        df = pd.read_sql_query("""
            SELECT s.State_Name as state_name, COUNT(v.Record_ID) as count
            FROM Vehicle_Record v
            JOIN State s ON v.State_Code = s.State_Code
            GROUP BY s.State_Name
            ORDER BY count DESC
        """, conn)
    return df

def fetch_recommendations(top_states):
    """Fetch suggested stock items for given states."""
    with connect_db() as conn:
        recs = []
        for state_code in top_states:
            demo = pd.read_sql_query("SELECT * FROM Demographics WHERE State_Code = ?", conn, params=[state_code])
            if demo.empty:
                continue
            demo_id = demo.iloc[0]['Demographic_ID']
            items = pd.read_sql_query("""
                SELECT i.Item_Name, i.Category FROM Prefers p
                JOIN Items i ON p.Item_ID = i.Item_ID
                WHERE p.Demographic_ID = ?
            """, conn, params=[demo_id])
            if not items.empty:
                recs.append({
                    "State_Code": state_code,
                    "Essentials": demo.iloc[0]['Essentials'],
                    "Food_Preference": demo.iloc[0]['Food_Preference'],
                    "Suggested_Items": ", ".join(items['Item_Name'].tolist())
                })
        return pd.DataFrame(recs)
