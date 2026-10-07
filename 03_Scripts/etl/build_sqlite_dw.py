import os
import sqlite3
import pandas as pd

# Define paths relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CLEANED_DIR = os.path.join(BASE_DIR, "02_Cleaned_Data")
DB_PATH = os.path.join(BASE_DIR, "ev_intelligence_dw.sqlite")

def create_sqlite_schema(conn):
    """Creates Star Schema tables in SQLite database."""
    cursor = conn.cursor()
    
    cursor.executescript("""
        DROP TABLE IF EXISTS fact_ev_forecasts;
        DROP TABLE IF EXISTS fact_stock_prices;
        DROP TABLE IF EXISTS fact_company_financials;
        DROP TABLE IF EXISTS fact_economic;
        DROP TABLE IF EXISTS fact_ev_metrics;
        DROP TABLE IF EXISTS dim_category;
        DROP TABLE IF EXISTS dim_mode;
        DROP TABLE IF EXISTS dim_powertrain;
        DROP TABLE IF EXISTS dim_company;
        DROP TABLE IF EXISTS dim_time;
        DROP TABLE IF EXISTS dim_country;

        -- Dimension: dim_country
        CREATE TABLE dim_country (
            country_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_name TEXT NOT NULL UNIQUE
        );

        -- Dimension: dim_time
        CREATE TABLE dim_time (
            time_id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL UNIQUE,
            quarter INTEGER,
            month INTEGER
        );

        -- Dimension: dim_company
        CREATE TABLE dim_company (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            ticker TEXT NOT NULL UNIQUE
        );

        -- Dimension: dim_powertrain
        CREATE TABLE dim_powertrain (
            powertrain_id INTEGER PRIMARY KEY AUTOINCREMENT,
            powertrain TEXT NOT NULL UNIQUE
        );

        -- Dimension: dim_mode
        CREATE TABLE dim_mode (
            mode_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT NOT NULL UNIQUE
        );

        -- Dimension: dim_category
        CREATE TABLE dim_category (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE
        );

        -- Fact: fact_ev_metrics
        CREATE TABLE fact_ev_metrics (
            ev_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            time_id INTEGER NOT NULL,
            powertrain_id INTEGER,
            mode_id INTEGER,
            category_id INTEGER,
            parameter TEXT NOT NULL,
            value REAL,
            unit TEXT,
            FOREIGN KEY (country_id) REFERENCES dim_country(country_id),
            FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
            FOREIGN KEY (powertrain_id) REFERENCES dim_powertrain(powertrain_id),
            FOREIGN KEY (mode_id) REFERENCES dim_mode(mode_id),
            FOREIGN KEY (category_id) REFERENCES dim_category(category_id)
        );

        -- Fact: fact_economic
        CREATE TABLE fact_economic (
            economic_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            time_id INTEGER NOT NULL,
            gdp REAL,
            population REAL,
            access_to_electricity REAL,
            crude_oil_price REAL,
            FOREIGN KEY (country_id) REFERENCES dim_country(country_id),
            FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
        );

        -- Fact: fact_company_financials
        CREATE TABLE fact_company_financials (
            financial_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            time_id INTEGER NOT NULL,
            revenue REAL,
            gross_profit REAL,
            operating_income REAL,
            net_income REAL,
            ebitda REAL,
            basic_eps REAL,
            diluted_eps REAL,
            FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
            FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
        );

        -- Fact: fact_stock_prices
        CREATE TABLE fact_stock_prices (
            stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            adj_close REAL NOT NULL,
            volume INTEGER NOT NULL,
            FOREIGN KEY (company_id) REFERENCES dim_company(company_id)
        );

        -- Fact: fact_ev_forecasts (Stores 2025-2030 Predictions)
        CREATE TABLE fact_ev_forecasts (
            forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER NOT NULL,
            time_id INTEGER NOT NULL,
            powertrain_id INTEGER,
            mode_id INTEGER,
            scenario TEXT NOT NULL,
            forecasted_sales REAL NOT NULL,
            lower_bound REAL,
            upper_bound REAL,
            FOREIGN KEY (country_id) REFERENCES dim_country(country_id),
            FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
            FOREIGN KEY (powertrain_id) REFERENCES dim_powertrain(powertrain_id),
            FOREIGN KEY (mode_id) REFERENCES dim_mode(mode_id)
        );
    """)
    conn.commit()

def load_data(conn):
    """Populates dimensions and fact tables from cleaned CSV files."""
    cursor = conn.cursor()
    
    print("Reading cleaned CSV files...")
    iea = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_iea_ev_data.csv"))
    gdp = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_gdp.csv"))
    pop = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_population.csv"))
    elec = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_electricity_access.csv"))
    company_fin = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_company_financials.csv"))
    stock = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_stock_prices.csv"))
    oil = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_crude_oil.csv"))

    # 1. dim_country
    print("Populating dim_country...")
    all_countries = pd.concat([
        iea[["Country"]], gdp[["Country"]], pop[["Country"]], elec[["Country"]]
    ]).drop_duplicates().dropna().reset_index(drop=True)
    all_countries.columns = ["country_name"]
    for name in all_countries["country_name"]:
        cursor.execute("INSERT OR IGNORE INTO dim_country (country_name) VALUES (?)", (name,))
    conn.commit()

    # 2. dim_time (include years 2010 through 2030 for forecasting)
    print("Populating dim_time...")
    all_years = list(range(2005, 2031))
    for yr in all_years:
        cursor.execute("INSERT OR IGNORE INTO dim_time (year) VALUES (?)", (yr,))
    conn.commit()

    # 3. dim_company
    print("Populating dim_company...")
    companies = pd.concat([
        company_fin[["Company", "Ticker"]], stock[["Company", "Ticker"]]
    ]).drop_duplicates().dropna().reset_index(drop=True)
    for _, row in companies.iterrows():
        cursor.execute("INSERT OR IGNORE INTO dim_company (company_name, ticker) VALUES (?, ?)",
                       (row["Company"], row["Ticker"]))
    conn.commit()

    # 4. dim_powertrain
    print("Populating dim_powertrain...")
    powertrains = iea[["Powertrain"]].drop_duplicates().dropna().reset_index(drop=True)
    for pt in powertrains["Powertrain"]:
        cursor.execute("INSERT OR IGNORE INTO dim_powertrain (powertrain) VALUES (?)", (pt,))
    conn.commit()

    # 5. dim_mode
    print("Populating dim_mode...")
    modes = iea[["Mode"]].drop_duplicates().dropna().reset_index(drop=True)
    for md in modes["Mode"]:
        cursor.execute("INSERT OR IGNORE INTO dim_mode (mode) VALUES (?)", (md,))
    conn.commit()

    # 6. dim_category
    print("Populating dim_category...")
    categories = iea[["Category"]].drop_duplicates().dropna().reset_index(drop=True)
    for cat in categories["Category"]:
        cursor.execute("INSERT OR IGNORE INTO dim_category (category) VALUES (?)", (cat,))
    conn.commit()

    # Build Map Dicts
    cursor.execute("SELECT country_name, country_id FROM dim_country")
    country_map = dict(cursor.fetchall())

    cursor.execute("SELECT year, time_id FROM dim_time")
    time_map = dict(cursor.fetchall())

    cursor.execute("SELECT company_name, company_id FROM dim_company")
    company_map = dict(cursor.fetchall())

    cursor.execute("SELECT powertrain, powertrain_id FROM dim_powertrain")
    powertrain_map = dict(cursor.fetchall())

    cursor.execute("SELECT mode, mode_id FROM dim_mode")
    mode_map = dict(cursor.fetchall())

    cursor.execute("SELECT category, category_id FROM dim_category")
    category_map = dict(cursor.fetchall())

    # 7. fact_ev_metrics
    print("Populating fact_ev_metrics...")
    ev_rows = []
    for _, r in iea.iterrows():
        c_id = country_map.get(r["Country"])
        t_id = time_map.get(r["Year"])
        if c_id and t_id:
            pt_id = powertrain_map.get(r["Powertrain"])
            md_id = mode_map.get(r["Mode"])
            cat_id = category_map.get(r["Category"])
            val = float(r["Value"]) if pd.notna(r["Value"]) else None
            ev_rows.append((c_id, t_id, pt_id, md_id, cat_id, r["Parameter"], val, r["Unit"]))
    
    cursor.executemany("""
        INSERT INTO fact_ev_metrics 
        (country_id, time_id, powertrain_id, mode_id, category_id, parameter, value, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ev_rows)
    conn.commit()

    # 8. fact_economic
    print("Populating fact_economic...")
    eco = gdp.merge(pop[["Country", "Year", "Population"]], on=["Country", "Year"], how="outer")
    eco = eco.merge(elec[["Country", "Year", "Access_to_Electricity"]], on=["Country", "Year"], how="outer")
    eco = eco.merge(oil, on="Year", how="left")

    eco_rows = []
    for _, r in eco.iterrows():
        c_id = country_map.get(r["Country"])
        t_id = time_map.get(r["Year"])
        if c_id and t_id:
            g_val = float(r["GDP"]) if pd.notna(r.get("GDP")) else None
            p_val = float(r["Population"]) if pd.notna(r.get("Population")) else None
            e_val = float(r["Access_to_Electricity"]) if pd.notna(r.get("Access_to_Electricity")) else None
            o_val = float(r["Crude_Oil_Price"]) if pd.notna(r.get("Crude_Oil_Price")) else None
            eco_rows.append((c_id, t_id, g_val, p_val, e_val, o_val))

    cursor.executemany("""
        INSERT INTO fact_economic 
        (country_id, time_id, gdp, population, access_to_electricity, crude_oil_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, eco_rows)
    conn.commit()

    # 9. fact_company_financials
    print("Populating fact_company_financials...")
    fin_rows = []
    for _, r in company_fin.iterrows():
        comp_id = company_map.get(r["Company"])
        t_id = time_map.get(r["Year"])
        if comp_id and t_id:
            fin_rows.append((
                comp_id, t_id,
                float(r["Revenue"]) if pd.notna(r["Revenue"]) else None,
                float(r["Gross Profit"]) if pd.notna(r["Gross Profit"]) else None,
                float(r["Operating Income"]) if pd.notna(r["Operating Income"]) else None,
                float(r["Net Income"]) if pd.notna(r["Net Income"]) else None,
                float(r["EBITDA"]) if pd.notna(r["EBITDA"]) else None,
                float(r["Basic EPS"]) if pd.notna(r["Basic EPS"]) else None,
                float(r["Diluted EPS"]) if pd.notna(r["Diluted EPS"]) else None
            ))
    cursor.executemany("""
        INSERT INTO fact_company_financials
        (company_id, time_id, revenue, gross_profit, operating_income, net_income, ebitda, basic_eps, diluted_eps)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fin_rows)
    conn.commit()

    # 10. fact_stock_prices
    print("Populating fact_stock_prices...")
    stock_rows = []
    for _, r in stock.iterrows():
        comp_id = company_map.get(r["Company"])
        if comp_id:
            stock_rows.append((
                comp_id, str(r["Date"])[:10],
                float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["Close"]),
                float(r["Adj Close"]), int(r["Volume"])
            ))
    
    # Batch insert stock rows
    batch_size = 10000
    for i in range(0, len(stock_rows), batch_size):
        cursor.executemany("""
            INSERT INTO fact_stock_prices 
            (company_id, date, open, high, low, close, adj_close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, stock_rows[i:i+batch_size])
    conn.commit()

    # Print Row Counts
    print("\n==========================================")
    print(" SQLite Data Warehouse Load Verification ")
    print("==========================================")
    tables = [
        "dim_country", "dim_time", "dim_company", "dim_powertrain", "dim_mode", "dim_category",
        "fact_ev_metrics", "fact_economic", "fact_company_financials", "fact_stock_prices"
    ]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f" {table}: {cursor.fetchone()[0]} rows loaded")
    print("==========================================\n")

def main():
    print(f"Building SQLite Data Warehouse at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    create_sqlite_schema(conn)
    load_data(conn)
    conn.close()
    print("SQLite Data Warehouse built successfully!")

if __name__ == "__main__":
    main()
