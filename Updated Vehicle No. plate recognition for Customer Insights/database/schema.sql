-- Master table for Indian States and Union Territories
CREATE TABLE IF NOT EXISTS State (
    State_Code TEXT PRIMARY KEY,
    State_Name TEXT NOT NULL
);

-- Vehicle detection records with timestamp (tracks every visit)
CREATE TABLE IF NOT EXISTS Vehicle_Record (
    Record_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Plate_No TEXT NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    State_Code TEXT,
    Confidence REAL DEFAULT 1.0,
    FOREIGN KEY(State_Code) REFERENCES State(State_Code)
);

-- Demographic profiles for each state
CREATE TABLE IF NOT EXISTS Demographics (
    Demographic_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    State_Code TEXT NOT NULL,
    Age_bracket TEXT,
    Gender_Ratio TEXT,
    Essentials TEXT,
    Food_Preference TEXT,
    FOREIGN KEY(State_Code) REFERENCES State(State_Code)
);

-- Items catalog
CREATE TABLE IF NOT EXISTS Items (
    Item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item_Name TEXT NOT NULL,
    Category TEXT
);

-- Store inventory stock levels
CREATE TABLE IF NOT EXISTS Stock (
    Item_ID INTEGER PRIMARY KEY,
    Quantity INTEGER NOT NULL DEFAULT 100,
    FOREIGN KEY(Item_ID) REFERENCES Items(Item_ID)
);

-- Demographics to Item preference mapping
CREATE TABLE IF NOT EXISTS Prefers (
    Demographic_ID INTEGER,
    Item_ID INTEGER,
    PRIMARY KEY (Demographic_ID, Item_ID),
    FOREIGN KEY(Demographic_ID) REFERENCES Demographics(Demographic_ID),
    FOREIGN KEY(Item_ID) REFERENCES Items(Item_ID)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_vehicle_state ON Vehicle_Record(State_Code);
CREATE INDEX IF NOT EXISTS idx_demographics_state ON Demographics(State_Code);
