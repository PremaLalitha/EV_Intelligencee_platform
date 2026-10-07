import os
import sqlite3
import math
import numpy as np
from flask import Flask, request, jsonify
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(BASE_DIR, "ev_intelligence_dw.sqlite")
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
STATIC_DIR = FRONTEND_DIST if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")) else os.path.join(SCRIPT_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
if HAS_CORS:
    CORS(app)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

@app.route("/")
def serve_index():
    """Serves full-stack dashboard SPA."""
    return app.send_static_file("index.html")

def get_db_connection():
    """Connects to SQLite Data Warehouse with dictionary row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/kpis", methods=["GET"])
def get_kpis():
    """Returns high-level executive KPIs and global summary stats."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Total Global EV Sales in 2024
    cursor.execute("""
        SELECT SUM(value) as total 
        FROM fact_ev_metrics ev
        JOIN dim_country c ON ev.country_id = c.country_id
        JOIN dim_time t ON ev.time_id = t.time_id
        WHERE c.country_name = 'World' AND t.year = 2024 AND ev.parameter = 'EV sales' AND ev.mode_id = (SELECT mode_id FROM dim_mode WHERE mode='Cars')
    """)
    row_2024 = cursor.fetchone()
    total_2024 = row_2024["total"] if row_2024 and row_2024["total"] else 17500000.0

    # 2. Total Global EV Sales Forecast in 2030 (Base Case)
    cursor.execute("""
        SELECT SUM(forecasted_sales) as total 
        FROM fact_ev_forecasts f
        JOIN dim_country c ON f.country_id = c.country_id
        JOIN dim_time t ON f.time_id = t.time_id
        WHERE c.country_name = 'World' AND t.year = 2030 AND f.scenario = 'Base Case' AND f.mode_id = (SELECT mode_id FROM dim_mode WHERE mode='Cars')
    """)
    row_2030 = cursor.fetchone()
    total_2030 = row_2030["total"] if row_2030 and row_2030["total"] else 45000000.0

    # 3. Top 5 Markets in 2024
    cursor.execute("""
        SELECT c.country_name, SUM(ev.value) as total_sales
        FROM fact_ev_metrics ev
        JOIN dim_country c ON ev.country_id = c.country_id
        JOIN dim_time t ON ev.time_id = t.time_id
        WHERE t.year = 2024 AND ev.parameter = 'EV sales' AND c.country_name != 'World'
        GROUP BY c.country_name
        ORDER BY total_sales DESC
        LIMIT 5
    """)
    top_markets = [dict(r) for r in cursor.fetchall()]

    # 4. EV Stock Count in 2024
    cursor.execute("""
        SELECT SUM(value) as total_stock
        FROM fact_ev_metrics ev
        JOIN dim_country c ON ev.country_id = c.country_id
        JOIN dim_time t ON ev.time_id = t.time_id
        WHERE c.country_name = 'World' AND t.year = 2024 AND ev.parameter = 'EV stock'
    """)
    row_stock = cursor.fetchone()
    total_stock_2024 = row_stock["total_stock"] if row_stock and row_stock["total_stock"] else 79000000.0

    cagr_2024_2030 = (((total_2030 / max(1.0, total_2024)) ** (1.0 / 6.0)) - 1.0) * 100.0

    # 5. Entity & Data Warehouse Summary Counts
    cursor.execute("SELECT COUNT(*) FROM dim_company")
    total_companies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT country_name) FROM dim_country WHERE country_name NOT IN ('World', '_World', 'World (STEPS)', 'Rest of World')")
    total_countries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dim_time")
    total_years = cursor.fetchone()[0]

    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM fact_ev_metrics) +
            (SELECT COUNT(*) FROM fact_economic) +
            (SELECT COUNT(*) FROM fact_company_financials) +
            (SELECT COUNT(*) FROM fact_stock_prices) +
            (SELECT COUNT(*) FROM fact_ev_forecasts) as total_rows
    """)
    row_dw = cursor.fetchone()
    total_dw_rows = row_dw["total_rows"] if row_dw else 84000

    conn.close()
    return jsonify({
        "global_sales_2024": total_2024,
        "global_sales_forecast_2030": total_2030,
        "cagr_2024_2030_pct": round(cagr_2024_2030, 2),
        "total_ev_stock_2024": total_stock_2024,
        "top_markets_2024": top_markets,
        "total_companies": total_companies,
        "total_countries": total_countries,
        "total_years": total_years,
        "total_dw_rows": total_dw_rows
    })

@app.route("/api/historical/sales", methods=["GET"])
def get_historical_sales():
    """Returns historical EV sales/stock metrics with optional filters."""
    country = request.args.get("country", default=None)
    powertrain = request.args.get("powertrain", default=None)
    mode = request.args.get("mode", default=None)
    parameter = request.args.get("parameter", default="EV sales")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            c.country_name,
            t.year,
            p.powertrain,
            m.mode,
            ev.parameter,
            ev.value,
            ev.unit
        FROM fact_ev_metrics ev
        JOIN dim_country c ON ev.country_id = c.country_id
        JOIN dim_time t ON ev.time_id = t.time_id
        LEFT JOIN dim_powertrain p ON ev.powertrain_id = p.powertrain_id
        LEFT JOIN dim_mode m ON ev.mode_id = m.mode_id
        WHERE ev.parameter = ?
    """
    params = [parameter]

    if country and country != "All":
        country_patterns = [country]
        if country == "Vietnam": country_patterns.append("Viet Nam")
        elif country == "Egypt": country_patterns.append("Egypt, Arab Rep.")
        elif country == "Venezuela": country_patterns.append("Venezuela, RB")
        elif country == "Yemen": country_patterns.append("Yemen, Rep.")
        elif country == "Turkey": country_patterns.append("Turkiye")
        elif country == "Russia": country_patterns.append("Russian Federation")
        elif country == "South Korea": country_patterns.append("Korea, Rep.")

        placeholders = ','.join(['?'] * len(country_patterns))
        query += f" AND c.country_name IN ({placeholders})"
        params.extend(country_patterns)

    if powertrain and powertrain != "All":
        query += " AND p.powertrain = ?"
        params.append(powertrain)

    if mode and mode != "All":
        query += " AND m.mode = ?"
        params.append(mode)

    query += " ORDER BY c.country_name, t.year, p.powertrain"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify(rows)

@app.route("/api/macroeconomic", methods=["GET"])
def get_macroeconomic():
    """Returns macroeconomic indicator data (GDP, Population, Electricity, Crude Oil)."""
    country = request.args.get("country", default="China")

    # Map clean name back to raw variants if needed
    country_patterns = [country]
    if country == "Vietnam": country_patterns.append("Viet Nam")
    elif country == "Egypt": country_patterns.append("Egypt, Arab Rep.")
    elif country == "Venezuela": country_patterns.append("Venezuela, RB")
    elif country == "Yemen": country_patterns.append("Yemen, Rep.")
    elif country == "Turkey": country_patterns.append("Turkiye")
    elif country == "Russia": country_patterns.append("Russian Federation")
    elif country == "South Korea": country_patterns.append("Korea, Rep.")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT 
            c.country_name,
            t.year,
            eco.gdp,
            eco.population,
            (eco.gdp / NULLIF(eco.population, 0)) as gdp_per_capita,
            eco.access_to_electricity,
            eco.crude_oil_price
        FROM fact_economic eco
        JOIN dim_country c ON eco.country_id = c.country_id
        JOIN dim_time t ON eco.time_id = t.time_id
        WHERE c.country_name IN ({','.join(['?']*len(country_patterns))})
        ORDER BY t.year
    """

    cursor.execute(query, country_patterns)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify(rows)

@app.route("/api/financials", methods=["GET"])
def get_financials():
    """Returns EV company income statements and stock price performance."""
    company = request.args.get("company", default="Tesla")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Financials
    cursor.execute("""
        SELECT 
            comp.company_name,
            comp.ticker,
            t.year,
            f.revenue,
            f.gross_profit,
            f.operating_income,
            f.net_income,
            f.ebitda,
            f.basic_eps,
            f.diluted_eps
        FROM fact_company_financials f
        JOIN dim_company comp ON f.company_id = comp.company_id
        JOIN dim_time t ON f.time_id = t.time_id
        WHERE comp.company_name LIKE ? OR comp.ticker LIKE ?
        ORDER BY t.year
    """, (f"%{company}%", f"%{company}%"))
    financials = [dict(r) for r in cursor.fetchall()]

    # Stock prices sample (last 500 rows for charts)
    cursor.execute("""
        SELECT 
            comp.company_name,
            s.date,
            s.close,
            s.volume
        FROM fact_stock_prices s
        JOIN dim_company comp ON s.company_id = comp.company_id
        WHERE comp.company_name LIKE ? OR comp.ticker LIKE ?
        ORDER BY s.date ASC
    """, (f"%{company}%", f"%{company}%"))
    stocks = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return jsonify({
        "company": company,
        "financials": financials,
        "stock_prices": stocks
    })

@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Returns list of all available EV and automotive OEM companies in the Data Warehouse."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT company_id, company_name, ticker FROM dim_company ORDER BY company_name")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/countries", methods=["GET"])
def get_countries():
    """Returns clean, deduplicated list of countries that have EV market data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query countries present in fact_ev_metrics or fact_ev_forecasts or fact_economic
    cursor.execute("""
        SELECT DISTINCT c.country_name 
        FROM dim_country c
        JOIN fact_ev_metrics ev ON c.country_id = ev.country_id
        WHERE c.country_name IS NOT NULL
        UNION
        SELECT DISTINCT c.country_name 
        FROM dim_country c
        JOIN fact_ev_forecasts f ON c.country_id = f.country_id
        WHERE c.country_name IS NOT NULL
    """)
    raw_countries = [r["country_name"] for r in cursor.fetchall()]
    conn.close()

    # Standardization mapping for World Bank vs IEA duplicate names
    name_clean_map = {
        "Viet Nam": "Vietnam",
        "Egypt, Arab Rep.": "Egypt",
        "Venezuela, RB": "Venezuela",
        "Yemen, Rep.": "Yemen",
        "Turkiye": "Turkey",
        "Russian Federation": "Russia",
        "Korea, Rep.": "South Korea",
        "Korea, Dem. People's Rep.": "North Korea",
        "Iran, Islamic Rep.": "Iran",
        "Slovak Republic": "Slovakia",
        "Bahamas, The": "Bahamas",
        "Gambia, The": "Gambia",
        "Congo, Dem. Rep.": "Congo",
        "Micronesia, Fed. Sts.": "Micronesia",
        "St. Lucia": "Saint Lucia",
        "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines"
    }

    cleaned = set()
    for name in raw_countries:
        c_name = name_clean_map.get(name, name)
        if c_name and not c_name.startswith("_") and c_name not in ["_World", "World (STEPS)", "Rest of World"]:
            cleaned.add(c_name)

    result = sorted(list(cleaned))
    if "World" in result:
        result.remove("World")
        result = ["World"] + result

    return jsonify(result)

@app.route("/api/forecasts", methods=["GET"])
def get_forecasts():
    """Returns ML sales predictions for 2025-2030."""
    country = request.args.get("country", default="World")
    powertrain = request.args.get("powertrain", default="BEV")
    mode = request.args.get("mode", default="Cars")
    scenario = request.args.get("scenario", default="Base Case")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            c.country_name,
            t.year,
            p.powertrain,
            m.mode,
            f.scenario,
            f.forecasted_sales,
            f.lower_bound,
            f.upper_bound
        FROM fact_ev_forecasts f
        JOIN dim_country c ON f.country_id = c.country_id
        JOIN dim_time t ON f.time_id = t.time_id
        JOIN dim_powertrain p ON f.powertrain_id = p.powertrain_id
        JOIN dim_mode m ON f.mode_id = m.mode_id
        WHERE c.country_name = ?
    """
    params = [country]

    if powertrain and powertrain != "All":
        query += " AND p.powertrain = ?"
        params.append(powertrain)

    if mode and mode != "All":
        query += " AND m.mode = ?"
        params.append(mode)

    if scenario and scenario != "All":
        query += " AND f.scenario = ?"
        params.append(scenario)

    query += " ORDER BY t.year"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify(rows)

@app.route("/api/decision-support/evaluate", methods=["POST"])
def evaluate_market_expansion():
    """Computes dynamic Market Attractiveness Index, Expansion Readiness, and Risk Score."""
    data = request.json or {}
    
    # Default weights
    w_growth = float(data.get("w_demand_growth", 0.30))
    w_infra = float(data.get("w_infrastructure", 0.25))
    w_gdp = float(data.get("w_gdp_per_capita", 0.25))
    w_market = float(data.get("w_market_size", 0.20))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query key countries with historical sales, 2030 forecasts, GDP, and electricity access (excluding World aggregates)
    cursor.execute("""
        WITH sales_summary AS (
            SELECT 
                c.country_id,
                c.country_name,
                SUM(CASE WHEN t.year = 2024 THEN ev.value ELSE 0 END) as sales_2024,
                SUM(CASE WHEN t.year = 2020 THEN ev.value ELSE 0 END) as sales_2020
            FROM dim_country c
            JOIN fact_ev_metrics ev ON ev.country_id = c.country_id AND ev.parameter = 'EV sales'
            JOIN dim_time t ON ev.time_id = t.time_id
            WHERE c.country_name NOT IN ('World', '_World', 'World (STEPS)', 'EU27') AND c.country_name NOT LIKE '%World%'
            GROUP BY c.country_id, c.country_name
        ),
        economic_summary AS (
            SELECT 
                country_id,
                AVG(access_to_electricity) as electricity_access,
                MAX(gdp / NULLIF(population, 0)) as gdp_per_capita
            FROM fact_economic
            GROUP BY country_id
        )
        SELECT 
            s.country_name,
            s.sales_2024,
            s.sales_2020,
            COALESCE(e.electricity_access, 85.0) as electricity_access,
            COALESCE(e.gdp_per_capita, 15000.0) as gdp_per_capita
        FROM sales_summary s
        LEFT JOIN economic_summary e ON s.country_id = e.country_id
        WHERE s.sales_2024 > 1000
        ORDER BY s.sales_2024 DESC
        LIMIT 30
    """)
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return jsonify({"weights": {}, "evaluations": []})

    max_sales = max(r["sales_2024"] for r in rows) if rows else 1000000.0

    evaluations = []
    for r in rows:
        country = r["country_name"]
        sales_24 = r["sales_2024"] or 1000.0
        sales_20 = r["sales_2020"] or 100.0
        elec_access = r["electricity_access"] if r["electricity_access"] is not None else 85.0
        gdp_capita = r["gdp_per_capita"] if r["gdp_per_capita"] is not None else 15000.0

        # 1. Market Volume Scale Score (Log normalized relative to global max leader)
        volume_score = min(100.0, (np.log10(max(10.0, sales_24)) / np.log10(max_sales)) * 100.0)

        # 2. 4-Year Historical CAGR % (capped at +80% to avoid small-base distortion)
        cagr = (((sales_24 / max(1.0, sales_20)) ** (1.0 / 4.0)) - 1.0) * 100.0
        cagr_score = min(100.0, max(10.0, min(80.0, cagr) * 1.25))

        # 3. Infrastructure Readiness Score
        infra_score = min(100.0, max(20.0, elec_access))

        # 4. Economic Capacity Score (Log scaled GDP per capita)
        gdp_score = min(100.0, (np.log10(max(1000.0, gdp_capita)) / np.log10(120000.0)) * 100.0)

        sum_w = (w_market * 1.8) + w_growth + w_infra + w_gdp
        total_score = min(100.0, (
            (volume_score * w_market * 1.8) +
            (cagr_score * w_growth) +
            (infra_score * w_infra) +
            (gdp_score * w_gdp)
        ) / max(0.1, sum_w))

        # Risk classification
        if total_score >= 82:
            risk = "Low Risk / Top Tier"
            rec = "High Priority for Sales Expansion & Gigafactory Manufacturing"
        elif total_score >= 65:
            risk = "Moderate Risk / High Potential"
            rec = "Promising Market for Sales Expansion & Supply Chain Assembly"
        else:
            risk = "Higher Risk / Emerging"
            rec = "Target for Secondary Phase Infrastructure & Direct Import Sales"

        evaluations.append({
            "country": country,
            "score": round(total_score, 1),
            "cagr_pct": round(cagr, 1),
            "sales_2024": sales_24,
            "gdp_per_capita": round(gdp_capita, 0),
            "electricity_access": round(elec_access, 1),
            "risk_tier": risk,
            "recommendation": rec
        })

    evaluations.sort(key=lambda x: x["score"], reverse=True)
    conn.close()

    return jsonify({
        "weights": {
            "demand_growth": w_growth,
            "infrastructure": w_infra,
            "gdp_per_capita": w_gdp,
            "market_size": w_market
        },
        "evaluations": evaluations
    })

@app.route("/api/scenario-simulator", methods=["POST"])
def simulate_scenario():
    """Dynamic What-If simulation recalculating 2025-2030 demand shift."""
    data = request.json or {}
    
    country = data.get("country", "China")
    gdp_delta = float(data.get("gdp_growth_delta", 0.0)) # e.g. +2.5%
    oil_delta = float(data.get("oil_price_delta", 0.0)) # e.g. +15 $/barrel
    subsidy_level = data.get("subsidy_incentive", "Moderate") # High, Moderate, Low

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.year, SUM(f.forecasted_sales) as base_sales
        FROM fact_ev_forecasts f
        JOIN dim_country c ON f.country_id = c.country_id
        JOIN dim_time t ON f.time_id = t.time_id
        WHERE c.country_name = ? AND f.scenario = 'Base Case'
        GROUP BY t.year
        ORDER BY t.year
    """, (country,))
    base_rows = cursor.fetchall()

    if not base_rows:
        # Fallback to China if country base rows empty
        cursor.execute("""
            SELECT t.year, SUM(f.forecasted_sales) as base_sales
            FROM fact_ev_forecasts f
            JOIN dim_country c ON f.country_id = c.country_id
            JOIN dim_time t ON f.time_id = t.time_id
            WHERE c.country_name = 'China' AND f.scenario = 'Base Case'
            GROUP BY t.year
            ORDER BY t.year
        """)
        base_rows = cursor.fetchall()

    # Subsidy multiplier
    subsidy_mult = 1.15 if subsidy_level == "High" else (0.88 if subsidy_level == "Low" else 1.0)

    # Elasticity coefficients: +1% GDP -> +1.8% EV demand; +$10 Oil price -> +3.5% EV demand
    gdp_multiplier = 1.0 + (gdp_delta * 0.018)
    oil_multiplier = 1.0 + (oil_delta * 0.0035)

    combined_multiplier = gdp_multiplier * oil_multiplier * subsidy_mult

    simulated_results = []
    for r in base_rows:
        yr = r["year"]
        base = r["base_sales"] or 10000.0
        simulated = base * combined_multiplier
        simulated_results.append({
            "year": yr,
            "base_forecast": round(base, 0),
            "simulated_forecast": round(simulated, 0),
            "delta_pct": round((combined_multiplier - 1.0) * 100.0, 1)
        })

    conn.close()
    return jsonify({
        "country": country,
        "parameters": {
            "gdp_growth_delta": gdp_delta,
            "oil_price_delta": oil_delta,
            "subsidy_incentive": subsidy_level,
            "net_demand_shift_pct": round((combined_multiplier - 1.0) * 100.0, 1)
        },
        "simulation": simulated_results
    })

@app.route("/api/schema", methods=["GET"])
def get_dw_schema():
    """Returns live metadata and row counts for all Star Schema tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = [
        {"name": "dim_country", "type": "Dimension", "pk": "country_id", "desc": "Global Countries & Regions (221 entities)"},
        {"name": "dim_time", "type": "Dimension", "pk": "time_id", "desc": "Time granularity (Year, Quarter, Month 2005-2030)"},
        {"name": "dim_company", "type": "Dimension", "pk": "company_id", "desc": "Automotive OEMs & Stock Tickers (34 companies)"},
        {"name": "dim_powertrain", "type": "Dimension", "pk": "powertrain_id", "desc": "EV Powertrain Tech (BEV, PHEV, FCEV)"},
        {"name": "dim_mode", "type": "Dimension", "pk": "mode_id", "desc": "Vehicle Types (Cars, Vans, Buses, 2/3W, Trucks)"},
        {"name": "dim_category", "type": "Dimension", "pk": "category_id", "desc": "Data classification categories"},
        {"name": "fact_ev_metrics", "type": "Fact Table", "pk": "ev_id", "desc": "Historical EV Sales & Stock metrics per country"},
        {"name": "fact_economic", "type": "Fact Table", "pk": "economic_id", "desc": "Macroeconomic Indicators (GDP, Population, Oil, Electricity)"},
        {"name": "fact_company_financials", "type": "Fact Table", "pk": "financial_id", "desc": "Annual Company Income Statements (Revenue, Net Income, EBITDA)"},
        {"name": "fact_stock_prices", "type": "Fact Table", "pk": "stock_id", "desc": "Daily OEM Stock Prices & Volume"},
        {"name": "fact_ev_forecasts", "type": "Fact Table", "pk": "forecast_id", "desc": "AI Ensemble Sales Predictions (2025-2030)"}
    ]

    schema_info = []
    total_rows = 0
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t['name']}")
            count = cursor.fetchone()[0]
        except Exception:
            count = 0
        total_rows += count
        schema_info.append({**t, "row_count": count})

    conn.close()
    return jsonify({
        "total_tables": len(tables),
        "total_rows": total_rows,
        "tables": schema_info
    })

if __name__ == "__main__":
    print("Starting EV Market Intelligence Backend REST API server on http://localhost:5005")
    app.run(host="0.0.0.0", port=5005, debug=True, use_reloader=False)




