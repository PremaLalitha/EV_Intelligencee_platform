import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Define paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_DIR = os.path.join(BASE_DIR, "01_Raw_Data")
CLEANED_DIR = os.path.join(BASE_DIR, "02_Cleaned_Data")
SQL_DIR = os.path.join(BASE_DIR, "04_SQL")

# MySQL Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "1979"
DB_NAME = "ev_intelligence_dw"

def connect_mysql(use_db=True):
    """Establishes connection to MySQL."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME if use_db else None
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database_and_tables():
    """Reads schema.sql and creates the database and tables."""
    print("Initializing database and tables...")
    schema_path = os.path.join(SQL_DIR, "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Schema file not found at {schema_path}!")
        return False

    # Connect to MySQL server without database first to ensure database exists
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_commands = f.read().split(';')
        
    for command in sql_commands:
        # Clean command
        command = command.strip()
        if not command:
            continue
        try:
            cursor.execute(command)
        except Error as e:
            # Ignore database/table drop errors if they don't exist
            if "database doesn't exist" in str(e).lower() or "unknown table" in str(e).lower():
                continue
            print(f"Error executing statement:\n{command}\nError: {e}")
            cursor.close()
            conn.close()
            return False
            
    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables initialized successfully!")
    return True

def run_etl():
    """Loads cleaned files and processes/inserts them into the database."""
    conn = connect_mysql()
    if not conn:
        print("Could not connect to database. Aborting ETL.")
        return
    cursor = conn.cursor()

    try:
        # 1. Load Cleaned CSV Files
        print("Reading cleaned CSV files...")
        iea = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_iea_ev_data.csv"))
        gdp = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_gdp.csv"))
        pop = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_population.csv"))
        elec = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_electricity_access.csv"))
        company_fin = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_company_financials.csv"))
        stock = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_stock_prices.csv"))
        oil = pd.read_csv(os.path.join(CLEANED_DIR, "cleaned_crude_oil.csv"))

        # -------------------------------------------------------------
        # DIMENSION TABLES
        # -------------------------------------------------------------
        
        # 1. dim_country
        print("Loading dim_country...")
        countries = pd.concat([
            iea[["Country"]],
            gdp[["Country"]],
            pop[["Country"]],
            elec[["Country"]]
        ]).drop_duplicates().reset_index(drop=True)
        countries = countries.rename(columns={"Country": "country_name"})
        
        for _, row in countries.iterrows():
            cursor.execute(
                "INSERT INTO dim_country (country_name) VALUES (%s) ON DUPLICATE KEY UPDATE country_name=country_name",
                (row["country_name"],)
            )
        conn.commit()

        # 2. dim_time
        print("Loading dim_time...")
        years = pd.concat([
            iea[["Year"]],
            gdp[["Year"]],
            pop[["Year"]],
            elec[["Year"]]
        ]).drop_duplicates().sort_values("Year").reset_index(drop=True)
        
        for _, row in years.iterrows():
            cursor.execute(
                "INSERT INTO dim_time (year) VALUES (%s) ON DUPLICATE KEY UPDATE year=year",
                (int(row["Year"]),)
            )
        conn.commit()

        # 3. dim_company
        print("Loading dim_company...")
        companies = pd.concat([
            company_fin[["Company", "Ticker"]],
            stock[["Company", "Ticker"]]
        ]).drop_duplicates().reset_index(drop=True)
        companies = companies.rename(columns={"Company": "company_name", "Ticker": "ticker"})
        
        for _, row in companies.iterrows():
            cursor.execute(
                "INSERT INTO dim_company (company_name, ticker) VALUES (%s, %s) ON DUPLICATE KEY UPDATE company_name=%s",
                (row["company_name"], row["ticker"], row["company_name"])
            )
        conn.commit()

        # 4. dim_powertrain
        print("Loading dim_powertrain...")
        powertrains = iea[["Powertrain"]].drop_duplicates().dropna().reset_index(drop=True)
        powertrains = powertrains.rename(columns={"Powertrain": "powertrain"})
        
        for _, row in powertrains.iterrows():
            cursor.execute(
                "INSERT INTO dim_powertrain (powertrain) VALUES (%s) ON DUPLICATE KEY UPDATE powertrain=powertrain",
                (row["powertrain"],)
            )
        conn.commit()

        # 5. dim_mode
        print("Loading dim_mode...")
        modes = iea[["Mode"]].drop_duplicates().dropna().reset_index(drop=True)
        modes = modes.rename(columns={"Mode": "mode"})
        
        for _, row in modes.iterrows():
            cursor.execute(
                "INSERT INTO dim_mode (mode) VALUES (%s) ON DUPLICATE KEY UPDATE mode=mode",
                (row["mode"],)
            )
        conn.commit()

        # 6. dim_category
        print("Loading dim_category...")
        categories = iea[["Category"]].drop_duplicates().dropna().reset_index(drop=True)
        categories = categories.rename(columns={"Category": "category"})
        
        for _, row in categories.iterrows():
            cursor.execute(
                "INSERT INTO dim_category (category) VALUES (%s) ON DUPLICATE KEY UPDATE category=category",
                (row["category"],)
            )
        conn.commit()

        # Retrieve Lookup Maps
        cursor.execute("SELECT country_id, country_name FROM dim_country")
        country_map = {name: id for id, name in cursor.fetchall()}

        cursor.execute("SELECT time_id, year FROM dim_time")
        time_map = {year: id for id, year in cursor.fetchall()}

        cursor.execute("SELECT powertrain_id, powertrain FROM dim_powertrain")
        powertrain_map = {name: id for id, name in cursor.fetchall()}

        cursor.execute("SELECT mode_id, mode FROM dim_mode")
        mode_map = {name: id for id, name in cursor.fetchall()}

        cursor.execute("SELECT category_id, category FROM dim_category")
        category_map = {name: id for id, name in cursor.fetchall()}

        cursor.execute("SELECT company_id, company_name FROM dim_company")
        company_map = {name: id for id, name in cursor.fetchall()}

        # -------------------------------------------------------------
        # FACT TABLES
        # -------------------------------------------------------------
        
        # 1. fact_ev_metrics
        print("Loading fact_ev_metrics...")
        ev = iea.copy()
        ev["country_id"] = ev["Country"].map(country_map)
        ev["time_id"] = ev["Year"].map(time_map)
        ev["powertrain_id"] = ev["Powertrain"].map(powertrain_map)
        ev["mode_id"] = ev["Mode"].map(mode_map)
        ev["category_id"] = ev["Category"].map(category_map)
        
        ev_final = ev[[
            "country_id", "time_id", "powertrain_id", "mode_id", "category_id",
            "Parameter", "Value", "Unit"
        ]].dropna(subset=["country_id", "time_id"])
        
        # Clear old records first
        cursor.execute("DELETE FROM fact_ev_metrics")
        
        ev_insert_query = """
            INSERT INTO fact_ev_metrics 
            (country_id, time_id, powertrain_id, mode_id, category_id, parameter, value, unit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        ev_data = [
            (
                int(row["country_id"]),
                int(row["time_id"]),
                int(row["powertrain_id"]) if pd.notna(row["powertrain_id"]) else None,
                int(row["mode_id"]) if pd.notna(row["mode_id"]) else None,
                int(row["category_id"]) if pd.notna(row["category_id"]) else None,
                row["Parameter"],
                float(row["Value"]) if pd.notna(row["Value"]) else None,
                row["Unit"]
            )
            for _, row in ev_final.iterrows()
        ]
        cursor.executemany(ev_insert_query, ev_data)
        conn.commit()

        # 2. fact_economic
        print("Loading fact_economic...")
        eco = gdp.merge(pop[["Country", "Year", "Population"]], on=["Country", "Year"], how="outer")
        eco = eco.merge(elec[["Country", "Year", "Access_to_Electricity"]], on=["Country", "Year"], how="outer")
        eco = eco.merge(oil, on="Year", how="left")
        
        eco["country_id"] = eco["Country"].map(country_map)
        eco["time_id"] = eco["Year"].map(time_map)
        
        eco_final = eco[[
            "country_id", "time_id", "GDP", "Population", "Access_to_Electricity", "Crude_Oil_Price"
        ]].dropna(subset=["country_id", "time_id"])
        
        cursor.execute("DELETE FROM fact_economic")
        
        eco_insert_query = """
            INSERT INTO fact_economic 
            (country_id, time_id, gdp, population, access_to_electricity, crude_oil_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        eco_data = [
            (
                int(row["country_id"]),
                int(row["time_id"]),
                float(row["GDP"]) if pd.notna(row["GDP"]) else None,
                float(row["Population"]) if pd.notna(row["Population"]) else None,
                float(row["Access_to_Electricity"]) if pd.notna(row["Access_to_Electricity"]) else None,
                float(row["Crude_Oil_Price"]) if pd.notna(row["Crude_Oil_Price"]) else None
            )
            for _, row in eco_final.iterrows()
        ]
        cursor.executemany(eco_insert_query, eco_data)
        conn.commit()

        # 3. fact_company_financials
        print("Loading fact_company_financials...")
        fin = company_fin.copy()
        fin["company_id"] = fin["Company"].map(company_map)
        fin["time_id"] = fin["Year"].map(time_map)
        
        fin_final = fin[[
            "company_id", "time_id", "Revenue", "Gross Profit", "Operating Income",
            "Net Income", "EBITDA", "Basic EPS", "Diluted EPS"
        ]].dropna(subset=["company_id", "time_id"])
        
        cursor.execute("DELETE FROM fact_company_financials")
        
        fin_insert_query = """
            INSERT INTO fact_company_financials 
            (company_id, time_id, revenue, gross_profit, operating_income, 
             net_income, ebitda, basic_eps, diluted_eps)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        fin_data = [
            (
                int(row["company_id"]),
                int(row["time_id"]),
                float(row["Revenue"]) if pd.notna(row["Revenue"]) else None,
                float(row["Gross Profit"]) if pd.notna(row["Gross Profit"]) else None,
                float(row["Operating Income"]) if pd.notna(row["Operating Income"]) else None,
                float(row["Net Income"]) if pd.notna(row["Net Income"]) else None,
                float(row["EBITDA"]) if pd.notna(row["EBITDA"]) else None,
                float(row["Basic EPS"]) if pd.notna(row["Basic EPS"]) else None,
                float(row["Diluted EPS"]) if pd.notna(row["Diluted EPS"]) else None
            )
            for _, row in fin_final.iterrows()
        ]
        cursor.executemany(fin_insert_query, fin_data)
        conn.commit()

        # 4. fact_stock_prices
        print("Loading fact_stock_prices (this might take a few moments)...")
        stock_copy = stock.copy()
        stock_copy["company_id"] = stock_copy["Company"].map(company_map)
        stock_copy["Date"] = pd.to_datetime(stock_copy["Date"])
        
        stock_final = stock_copy[[
            "company_id", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"
        ]].dropna(subset=["company_id"])
        
        cursor.execute("DELETE FROM fact_stock_prices")
        
        stock_insert_query = """
            INSERT INTO fact_stock_prices 
            (company_id, date, open, high, low, close, adj_close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Batch insert stock prices due to large volume
        stock_data = [
            (
                int(row["company_id"]),
                row["Date"].date().strftime('%Y-%m-%d'),
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                float(row["Adj Close"]),
                int(row["Volume"])
            )
            for _, row in stock_final.iterrows()
        ]
        
        batch_size = 5000
        for i in range(0, len(stock_data), batch_size):
            cursor.executemany(stock_insert_query, stock_data[i:i+batch_size])
        conn.commit()

        # Print row counts to verify loading
        print("\n=== Data Warehouse Load Verification ===")
        tables = [
            "dim_country", "dim_time", "dim_company", "dim_powertrain", "dim_mode", "dim_category",
            "fact_ev_metrics", "fact_economic", "fact_company_financials", "fact_stock_prices"
        ]
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"{table}: {cursor.fetchone()[0]} rows loaded")
        print("========================================\n")

    except Exception as e:
        print(f"ETL failed due to error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if create_database_and_tables():
        run_etl()
