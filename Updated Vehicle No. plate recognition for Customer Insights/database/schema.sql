CREATE TABLE IF NOT EXISTS Vehicle_Record (
    Record_ID Integer PRIMARY KEY AUTOINCREMENT,
    Plate_No TEXT UNIQUE NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    State_Code TEXT,                                 -- RJ
    FOREIGN KEY(State_Code) REFERENCES State(State_Code)
);


CREATE TABLE IF NOT EXISTS State (
    State_Code TEXT PRIMARY KEY,
    State_Name TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS Demographics (
    Demographic_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    State_Code TEXT,
    Age_bracket TEXT,               -- eg "0-17", "18-25", "26-40"
    Gender_Ratio TEXT,              -- eg "62:38"
    Essentials TEXT,                -- "Rice", "Candy"
    Food_Preference TEXT,           -- "Veg", "Non-Veg", "Mixed"
    FOREIGN KEY(State_Code) REFERENCES State(State_Code)
);


CREATE TABLE IF NOT EXISTS Items (
    Item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Item_Name TEXT NOT NULL,
    Category TEXT              -- eg. "Food", "Essential"
);


CREATE TABLE IF NOT EXISTS Stock (
    Item_ID INTEGER PRIMARY KEY,
    Quantity INTEGER NOT NULL,
    FOREIGN KEY(Item_ID) REFERENCES Items(Item_ID)
);


CREATE TABLE IF NOT EXISTS Prefers (
    Demographic_ID INTEGER,
    Item_ID INTEGER,
    FOREIGN KEY(Demographic_ID) REFERENCES Demographics(Demographic_ID),
    FOREIGN KEY(Item_ID) REFERENCES Items(Item_ID),
    PRIMARY KEY (Demographic_ID, Item_ID)
);


