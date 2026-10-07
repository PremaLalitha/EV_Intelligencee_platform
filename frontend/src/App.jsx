import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Zap,
  TrendingUp,
  Globe,
  BarChart3,
  Building2,
  Sliders,
  Compass,
  Layers,
  Sparkles,
  ShieldCheck,
  Cpu,
  RefreshCw,
  Sun,
  Moon
} from 'lucide-react';

// Register Chart.js modules
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [activeTab, setActiveTab] = useState('overview');
  const [kpis, setKpis] = useState({
    global_sales_2024: 17500000,
    global_sales_forecast_2030: 45000000,
    cagr_2024_2030_pct: 17.06,
    total_ev_stock_2024: 79000000,
    top_markets_2024: [
      { country_name: 'China', total_sales: 11000000 },
      { country_name: 'United States', total_sales: 1500000 },
      { country_name: 'Germany', total_sales: 520000 },
      { country_name: 'United Kingdom', total_sales: 450000 },
      { country_name: 'France', total_sales: 380000 }
    ],
    total_companies: 34,
    total_countries: 221,
    total_years: 26,
    total_dw_rows: 84000
  });


  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Historical Analytics state
  const [histData, setHistData] = useState([]);
  const [histCountry, setHistCountry] = useState('China');
  const [histPowertrain, setHistPowertrain] = useState('All');
  const [histMode, setHistMode] = useState('Cars');
  const [countriesList, setCountriesList] = useState([
    'World', 'China', 'United States', 'Germany', 'India', 'United Kingdom',
    'France', 'Norway', 'Japan', 'Canada', 'South Korea', 'Netherlands',
    'Sweden', 'Australia', 'Brazil', 'Italy', 'Spain', 'Vietnam',
    'Thailand', 'Indonesia', 'Belgium', 'Denmark', 'Switzerland', 'Austria',
    'Finland', 'Portugal', 'Turkey', 'Poland', 'New Zealand', 'Israel'
  ]);

  // Macroeconomic state
  const [macroData, setMacroData] = useState([]);
  const [macroCountry, setMacroCountry] = useState('China');

  // Forecast state
  const [forecastData, setForecastData] = useState([]);
  const [fcCountry, setFcCountry] = useState('China');
  const [fcPowertrain, setFcPowertrain] = useState('BEV');
  const [fcScenario, setFcScenario] = useState('Base Case');

  // Financials state
  const [financialsData, setFinancialsData] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState('Tesla');
  const [companiesList, setCompaniesList] = useState([
    { company_name: 'Tesla', ticker: 'TSLA' },
    { company_name: 'BYD', ticker: '1211.HK' },
    { company_name: 'Ford', ticker: 'F' },
    { company_name: 'General Motors', ticker: 'GM' },
    { company_name: 'Rivian', ticker: 'RIVN' },
    { company_name: 'Lucid', ticker: 'LCID' },
    { company_name: 'NIO', ticker: 'NIO' },
    { company_name: 'XPeng', ticker: 'XPEV' },
    { company_name: 'Li Auto', ticker: 'LI' },
    { company_name: 'Geely', ticker: '0175.HK' },
    { company_name: 'Mahindra and Mahindra', ticker: 'M&M.NS' },
    { company_name: 'Ashok Leyland', ticker: 'ASHOKLEY.NS' },
    { company_name: 'TVS Motor', ticker: 'TVSMOTOR.NS' },
    { company_name: 'Bajaj Auto', ticker: 'BAJAJ-AUTO.NS' },
    { company_name: 'Hero MotoCorp', ticker: 'HEROMOTOCO.NS' },
    { company_name: 'Ola Electric', ticker: 'OLAELEC.NS' },
    { company_name: 'Toyota', ticker: '7203.T' },
    { company_name: 'Honda', ticker: '7267.T' },
    { company_name: 'Nissan', ticker: '7201.T' },
    { company_name: 'Hyundai', ticker: '005380.KS' },
    { company_name: 'Kia', ticker: '000270.KS' },
    { company_name: 'BMW', ticker: 'BMW.DE' },
    { company_name: 'Mercedes Benz', ticker: 'MBG.DE' },
    { company_name: 'Volkswagen', ticker: 'VOW3.DE' },
    { company_name: 'Porsche', ticker: 'P911.DE' },
    { company_name: 'Volvo', ticker: 'VOLV-B.ST' },
    { company_name: 'Renault', ticker: 'RNO.PA' },
    { company_name: 'Ferrari', ticker: 'RACE' },
    { company_name: 'VinFast', ticker: 'VFS' }
  ]);

  // Decision Support state
  const [evalWeights, setEvalWeights] = useState({
    w_demand_growth: 0.35,
    w_infrastructure: 0.25,
    w_gdp_per_capita: 0.25,
    w_market_size: 0.15
  });
  const [evaluations, setEvaluations] = useState([]);
  const [riskFilter, setRiskFilter] = useState('All');

  // Scenario Simulator state
  const [simParams, setSimParams] = useState({
    gdp_growth_delta: 2.0,
    oil_price_delta: 15.0,
    subsidy_incentive: 'High',
    country: 'China'
  });
  const [simResults, setSimResults] = useState(null);

  // Data Warehouse Schema state
  const [schemaInfo, setSchemaInfo] = useState(null);

  const [loading, setLoading] = useState(false);

  // 1. Fetch Executive KPIs & Countries
  useEffect(() => {
    fetch('/api/kpis')
      .then(res => res.json())
      .then(data => setKpis(data))
      .catch(err => console.error('Error fetching KPIs:', err));

    fetch('/api/countries')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setCountriesList(data);
        }
      })
      .catch(err => console.error('Error fetching countries:', err));

    fetch('/api/schema')
      .then(res => res.json())
      .then(data => setSchemaInfo(data))
      .catch(err => console.error('Error fetching schema:', err));
  }, []);

  // 2. Fetch Historical Analytics Data
  useEffect(() => {
    let url = `/api/historical/sales?country=${histCountry}&parameter=EV sales`;
    if (histPowertrain !== 'All') url += `&powertrain=${histPowertrain}`;
    if (histMode !== 'All') url += `&mode=${histMode}`;

    fetch(url)
      .then(res => res.json())
      .then(data => setHistData(data))
      .catch(err => console.error('Error fetching historical:', err));
  }, [histCountry, histPowertrain, histMode]);

  // 3. Fetch Macroeconomic Data
  useEffect(() => {
    fetch(`/api/macroeconomic?country=${macroCountry}`)
      .then(res => res.json())
      .then(data => setMacroData(data))
      .catch(err => console.error('Error fetching macro:', err));
  }, [macroCountry]);

  // 4. Fetch Forecasts Data
  useEffect(() => {
    fetch(`/api/forecasts?country=${fcCountry}&powertrain=${fcPowertrain}&scenario=${fcScenario}`)
      .then(res => res.json())
      .then(data => setForecastData(data))
      .catch(err => console.error('Error fetching forecasts:', err));
  }, [fcCountry, fcPowertrain, fcScenario]);

  // 5. Fetch Financials & Stock Prices
  useEffect(() => {
    fetch(`/api/financials?company=${selectedCompany}`)
      .then(res => res.json())
      .then(data => setFinancialsData(data))
      .catch(err => console.error('Error fetching financials:', err));
  }, [selectedCompany]);

  // 6. Fetch Market Expansion Evaluator
  const runEvaluation = () => {
    fetch('/api/decision-support/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(evalWeights)
    })
      .then(res => res.json())
      .then(data => setEvaluations(data.evaluations || []))
      .catch(err => console.error('Error evaluating expansion:', err));
  };

  useEffect(() => {
    runEvaluation();
  }, [evalWeights]);

  // 7. Fetch Scenario Simulation
  const runSimulation = () => {
    fetch('/api/scenario-simulator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(simParams)
    })
      .then(res => res.json())
      .then(data => setSimResults(data))
      .catch(err => console.error('Error running simulation:', err));
  };

  useEffect(() => {
    runSimulation();
  }, [simParams]);

  // Helper number formatter
  const fmt = (num) => (num ? num.toLocaleString(undefined, { maximumFractionDigits: 0 }) : '0');

  // Filter evaluations by risk tier
  const filteredEvaluations = evaluations.filter(e => {
    if (riskFilter === 'All') return true;
    return e.risk_tier.includes(riskFilter);
  });

  return (
    <div className="app-layout">
      {/* LEFT SIDEBAR NAVIGATION */}
      <aside className="sidebar">
        <div>
          <div className="sidebar-brand">
            <div className="brand-icon">
              <Zap size={20} color="#ffffff" />
            </div>
            EV Intelligence
          </div>

          <nav className="sidebar-menu">
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              <Globe size={18} /> Executive Summary
            </button>
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'historical' ? 'active' : ''}`}
              onClick={() => setActiveTab('historical')}
            >
              <BarChart3 size={18} /> Past EV Sales (2015–2024)
            </button>
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'macro' ? 'active' : ''}`}
              onClick={() => setActiveTab('macro')}
            >
              <Cpu size={18} /> Country Economy & Oil Prices
            </button>
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'forecast' ? 'active' : ''}`}
              onClick={() => setActiveTab('forecast')}
            >
              <TrendingUp size={18} /> AI Future Sales Forecast (2025–2030)
            </button>
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'financials' ? 'active' : ''}`}
              onClick={() => setActiveTab('financials')}
            >
              <Building2 size={18} /> Car Company Financials & Stocks
            </button>
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'decision' ? 'active' : ''}`}
              onClick={() => setActiveTab('decision')}
            >
              <Compass size={18} /> Country Expansion Rankings
            </button>
            <button
              className={`sidebar-btn nav-btn ${activeTab === 'simulator' ? 'active' : ''}`}
              onClick={() => setActiveTab('simulator')}
            >
              <Sliders size={18} /> "What-If" Sales Simulator
            </button>

          </nav>
        </div>

        <div className="sidebar-footer">
          <button
            className="sidebar-btn"
            style={{ border: '1px solid var(--border-color)', justifyContent: 'center' }}
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? <Moon size={16} /> : <Sun size={16} />}
            <span>{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
          </button>

        </div>
      </aside>

      {/* Main Content Area */}
      <main className="app-container">
        {/* KPI Cards (Available across overview or top) */}
        {kpis && (
          <div className="kpi-grid">
            <div className="glass-card kpi-card">
              <div className="kpi-header">
                Total EVs Sold in 2024
                <div className="kpi-icon"><Zap size={18} /></div>
              </div>
              <div className="kpi-value">{fmt(kpis.global_sales_2024)}</div>
              <div className="kpi-sub"><TrendingUp size={14} /> Total Cars Sold Globally</div>
            </div>

            <div className="glass-card kpi-card">
              <div className="kpi-header">
                Predicted EVs Sold in 2030
                <div className="kpi-icon"><Sparkles size={18} /></div>
              </div>
              <div className="kpi-value">{fmt(kpis.global_sales_forecast_2030)}</div>
              <div className="kpi-sub"><TrendingUp size={14} /> AI Model Forecast</div>
            </div>

            <div className="glass-card kpi-card">
              <div className="kpi-header">
                Yearly Growth Rate (2024–2030)
                <div className="kpi-icon"><TrendingUp size={18} /></div>
              </div>
              <div className="kpi-value">+{kpis.cagr_2024_2030_pct}%</div>
              <div className="kpi-sub"><ShieldCheck size={14} /> Average Growth Per Year</div>
            </div>

            <div className="glass-card kpi-card">
              <div className="kpi-header">
                Total EVs Driving Today (2024)
                <div className="kpi-icon"><Globe size={18} /></div>
              </div>
              <div className="kpi-value">{fmt(kpis.total_ev_stock_2024)}</div>
              <div className="kpi-sub">Total Cars On The Road</div>
            </div>
          </div>
        )}

        {/* Executive Reference Legend */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h4 style={{ color: 'var(--accent-cyan)', fontSize: '0.92rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Quick Guide & Terms Explained
            </h4>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Easy Reference</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginTop: '14px', fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
            <div><strong style={{ color: 'var(--text-primary)' }}>BEV:</strong> 100% Pure Electric Car (Battery Only)</div>
            <div><strong style={{ color: 'var(--text-primary)' }}>PHEV:</strong> Plug-in Hybrid Car (Battery + Petrol Engine)</div>
            <div><strong style={{ color: 'var(--text-primary)' }}>CAGR:</strong> Average Growth Rate Per Year (%)</div>
            <div><strong style={{ color: 'var(--text-primary)' }}>GDP per Capita:</strong> Average Person Income & Buying Power</div>
            <div><strong style={{ color: 'var(--text-primary)' }}>OEM:</strong> Car Companies & Manufacturers (Tesla, BYD, etc.)</div>
          </div>
        </div>

        {/* TAB 1: EXECUTIVE OVERVIEW */}
        {activeTab === 'overview' && kpis && (
          <div>
            {/* Data Warehouse Entity Coverage Grid */}
            <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', marginBottom: '24px' }}>
              <div className="glass-card kpi-card" style={{ marginBottom: 0 }}>
                <div className="kpi-header">
                  Car Companies (OEMs)
                  <div className="kpi-icon"><Building2 size={18} /></div>
                </div>
                <div className="kpi-value" style={{ color: 'var(--accent-cyan)' }}>{kpis.total_companies || 34}</div>
                <div className="kpi-sub" style={{ color: 'var(--text-muted)' }}>Manufacturers & Stocks</div>
              </div>

              <div className="glass-card kpi-card" style={{ marginBottom: 0 }}>
                <div className="kpi-header">
                  Countries & Regions
                  <div className="kpi-icon"><Globe size={18} /></div>
                </div>
                <div className="kpi-value" style={{ color: 'var(--accent-emerald)' }}>{kpis.total_countries || 221}</div>
                <div className="kpi-sub" style={{ color: 'var(--text-muted)' }}>Global Coverage</div>
              </div>

              <div className="glass-card kpi-card" style={{ marginBottom: 0 }}>
                <div className="kpi-header">
                  Time Period Covered
                  <div className="kpi-icon"><BarChart3 size={18} /></div>
                </div>
                <div className="kpi-value" style={{ color: 'var(--accent-purple)' }}>{kpis.total_years || 26} Years</div>
                <div className="kpi-sub" style={{ color: 'var(--text-muted)' }}>2005 – 2030 Timeline</div>
              </div>

              <div className="glass-card kpi-card" style={{ marginBottom: 0 }}>
                <div className="kpi-header">
                  Powertrain Technologies
                  <div className="kpi-icon"><Zap size={18} /></div>
                </div>
                <div className="kpi-value" style={{ color: 'var(--accent-cyan)' }}>3</div>
                <div className="kpi-sub" style={{ color: 'var(--accent-emerald)' }}>BEV, PHEV, FCEV</div>
              </div>

              <div className="glass-card kpi-card" style={{ marginBottom: 0 }}>
                <div className="kpi-header">
                  Vehicle Categories
                  <div className="kpi-icon"><Sliders size={18} /></div>
                </div>
                <div className="kpi-value" style={{ color: 'var(--accent-amber)' }}>5</div>
                <div className="kpi-sub" style={{ color: 'var(--text-muted)' }}>Cars, Vans, Buses, 2/3W, Trucks</div>
              </div>
            </div>

            <div className="grid-2">
              <div className="glass-card">
                <h3>Global Top 5 EV Markets (2024 Volume)</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>
                  Annual sales leadership across key regional markets
                </p>
                <div style={{ height: '320px' }}>
                  <Bar
                    data={{
                      labels: kpis.top_markets_2024.map(m => m.country_name),
                      datasets: [{
                        label: '2024 EV Sales',
                        data: kpis.top_markets_2024.map(m => m.total_sales),
                        backgroundColor: [
                          'rgba(0, 242, 254, 0.85)',
                          'rgba(79, 172, 254, 0.85)',
                          'rgba(16, 185, 129, 0.85)',
                          'rgba(168, 85, 247, 0.85)',
                          'rgba(245, 158, 11, 0.85)'
                        ],
                        borderRadius: 8
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: {
                        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                      }
                    }}
                  />
                </div>
              </div>

              <div className="glass-card">
                <h3>Global Market Growth Summary</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>
                  Market structure and deployment trajectory
                </p>
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Country / Region</th>
                        <th>2024 EV Sales</th>
                        <th>Global Share %</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {kpis.top_markets_2024.map((m, idx) => (
                        <tr key={idx}>
                          <td><strong>{m.country_name}</strong></td>
                          <td>{fmt(m.total_sales)}</td>
                          <td>{((m.total_sales / kpis.top_markets_2024.reduce((a,b)=>a+b.total_sales,0)) * 100).toFixed(1)}%</td>
                          <td><span className="tag-risk low">High Growth</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: HISTORICAL MARKET ANALYTICS */}
        {activeTab === 'historical' && (
          <div>
            <div className="filter-bar">
              <div className="filter-group">
                <label className="filter-label">Country</label>
                <select className="filter-select" value={histCountry} onChange={e => setHistCountry(e.target.value)}>
                  {countriesList.map((c, idx) => (
                    <option key={idx} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Powertrain</label>
                <select className="filter-select" value={histPowertrain} onChange={e => setHistPowertrain(e.target.value)}>
                  <option value="All">All Powertrains</option>
                  <option value="BEV">BEV (Battery Electric)</option>
                  <option value="PHEV">PHEV (Plug-in Hybrid)</option>
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Vehicle Mode</label>
                <select className="filter-select" value={histMode} onChange={e => setHistMode(e.target.value)}>
                  <option value="All">All Modes</option>
                  <option value="Cars">Cars</option>
                  <option value="Vans">Vans</option>
                  <option value="Buses">Buses</option>
                  <option value="2 and 3 wheelers">2 & 3 Wheelers</option>
                </select>
              </div>
            </div>

            {histPowertrain === 'PHEV' && histMode === '2 and 3 wheelers' && (
              <div style={{ padding: '14px 18px', background: 'rgba(59, 130, 246, 0.12)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '12px', color: '#60a5fa', fontSize: '0.88rem', marginBottom: '20px' }}>
                💡 <strong>Data Insight:</strong> Plug-in Hybrid (PHEV) powertrains do not exist for 2 & 3 Wheelers (electric scooters/mopeds are manufactured exclusively as BEVs). To analyze PHEV market trends, switch Vehicle Mode to <strong>"Cars"</strong> or <strong>"Vans"</strong>.
              </div>
            )}

            <div className="glass-card" style={{ marginBottom: '28px' }}>
              <h3>Historical EV Sales Trend ({histCountry} - {histMode})</h3>
              <div style={{ height: '360px', marginTop: '16px' }}>
                <Line
                  data={{
                    labels: Array.from(new Set(histData.map(d => d.year))).sort((a,b) => a - b),
                    datasets: histPowertrain === 'All' ? [
                      {
                        label: 'BEV (Battery Electric)',
                        data: Array.from(new Set(histData.map(d => d.year))).sort((a,b) => a - b).map(y => {
                          const item = histData.find(d => d.year === y && d.powertrain === 'BEV');
                          return item ? item.value : 0;
                        }),
                        borderColor: '#00f2fe',
                        backgroundColor: 'rgba(0, 242, 254, 0.15)',
                        fill: true,
                        tension: 0.35,
                        pointRadius: 5
                      },
                      {
                        label: 'PHEV (Plug-in Hybrid)',
                        data: Array.from(new Set(histData.map(d => d.year))).sort((a,b) => a - b).map(y => {
                          const item = histData.find(d => d.year === y && d.powertrain === 'PHEV');
                          return item ? item.value : 0;
                        }),
                        borderColor: '#a855f7',
                        backgroundColor: 'rgba(168, 85, 247, 0.15)',
                        fill: true,
                        tension: 0.35,
                        pointRadius: 5
                      }
                    ] : [{
                      label: `${histCountry} ${histPowertrain} Sales`,
                      data: histData.map(d => d.value),
                      borderColor: histPowertrain === 'PHEV' ? '#a855f7' : '#00f2fe',
                      backgroundColor: histPowertrain === 'PHEV' ? 'rgba(168, 85, 247, 0.15)' : 'rgba(0, 242, 254, 0.15)',
                      fill: true,
                      tension: 0.35,
                      pointRadius: 5
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                      x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                    }
                  }}
                />
              </div>
            </div>

            <div className="glass-card">
              <h3>Detailed Historical Data Records</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Country</th>
                      <th>Powertrain</th>
                      <th>Vehicle Mode</th>
                      <th>Sales Volume</th>
                      <th>Unit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {histData.slice(0, 15).map((row, idx) => (
                      <tr key={idx}>
                        <td><strong>{row.year}</strong></td>
                        <td>{row.country_name}</td>
                        <td><span className="tag-risk low">{row.powertrain || 'BEV'}</span></td>
                        <td>{row.mode}</td>
                        <td>{fmt(row.value)}</td>
                        <td>{row.unit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: MACROECONOMIC & INFRASTRUCTURE */}
        {activeTab === 'macro' && (
          <div>
            <div className="filter-bar">
              <div className="filter-group">
                <label className="filter-label">Target Market</label>
                <select className="filter-select" value={macroCountry} onChange={e => setMacroCountry(e.target.value)}>
                  {countriesList.filter(c => c !== 'World').map((c, idx) => (
                    <option key={idx} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid-2">
              <div className="glass-card">
                <h3>GDP per Capita vs Electricity Access</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
                  Infrastructure readiness and purchasing power for {macroCountry}
                </p>
                <div style={{ height: '320px' }}>
                  <Line
                    data={{
                      labels: macroData.map(d => d.year),
                      datasets: [
                        {
                          label: 'GDP per Capita ($)',
                          data: macroData.map(d => d.gdp_per_capita),
                          borderColor: '#3b82f6',
                          yAxisID: 'y1'
                        },
                        {
                          label: 'Electricity Access (%)',
                          data: macroData.map(d => d.access_to_electricity),
                          borderColor: '#10b981',
                          yAxisID: 'y2'
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y1: { type: 'linear', position: 'left', ticks: { color: '#94a3b8' } },
                        y2: { type: 'linear', position: 'right', ticks: { color: '#94a3b8' }, max: 100 }
                      }
                    }}
                  />
                </div>
              </div>

              <div className="glass-card">
                <h3>Crude Oil Price Trajectory ($/bbl)</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
                  Energy commodity price volatility influencing EV adoption decisions
                </p>
                <div style={{ height: '320px' }}>
                  <Bar
                    data={{
                      labels: macroData.map(d => d.year),
                      datasets: [{
                        label: 'Crude Oil Price ($)',
                        data: macroData.map(d => d.crude_oil_price),
                        backgroundColor: 'rgba(245, 158, 11, 0.75)',
                        borderRadius: 6
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: { ticks: { color: '#94a3b8' } },
                        x: { ticks: { color: '#94a3b8' } }
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: 2025-2030 FORECASTS */}
        {activeTab === 'forecast' && (
          <div>
            <div className="filter-bar">
              <div className="filter-group">
                <label className="filter-label">Market</label>
                <select className="filter-select" value={fcCountry} onChange={e => setFcCountry(e.target.value)}>
                  {countriesList.map((c, idx) => (
                    <option key={idx} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Powertrain</label>
                <select className="filter-select" value={fcPowertrain} onChange={e => setFcPowertrain(e.target.value)}>
                  <option value="BEV">BEV (Battery Electric)</option>
                  <option value="PHEV">PHEV (Plug-in Hybrid)</option>
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Scenario Model</label>
                <select className="filter-select" value={fcScenario} onChange={e => setFcScenario(e.target.value)}>
                  <option value="Base Case">Base Case</option>
                  <option value="High Growth">High Growth</option>
                  <option value="Low Growth">Low Growth</option>
                </select>
              </div>
            </div>



            <div className="glass-card" style={{ marginBottom: '28px' }}>
              <h3>2025–2030 ML EV Sales Forecast ({fcCountry} - {fcScenario})</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
                Ensemble Machine Learning projection with confidence bound intervals
              </p>
              <div style={{ height: '360px' }}>
                <Line
                  data={{
                    labels: forecastData.map(d => d.year),
                    datasets: [
                      {
                        label: 'Forecasted EV Sales',
                        data: forecastData.map(d => d.forecasted_sales),
                        borderColor: '#00f2fe',
                        backgroundColor: 'rgba(0, 242, 254, 0.2)',
                        fill: false,
                        tension: 0.3,
                        pointRadius: 6
                      },
                      {
                        label: 'Upper Confidence Bound',
                        data: forecastData.map(d => d.upper_bound),
                        borderColor: 'rgba(16, 185, 129, 0.5)',
                        borderDash: [5, 5],
                        fill: false
                      },
                      {
                        label: 'Lower Confidence Bound',
                        data: forecastData.map(d => d.lower_bound),
                        borderColor: 'rgba(239, 68, 68, 0.5)',
                        borderDash: [5, 5],
                        fill: false
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                      x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                    }
                  }}
                />
              </div>
            </div>

            <div className="glass-card">
              <h3>Year-by-Year Forecast Table</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Forecasted Sales</th>
                      <th>Lower Bound (-20%)</th>
                      <th>Upper Bound (+25%)</th>
                      <th>Scenario</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecastData.map((row, idx) => (
                      <tr key={idx}>
                        <td><strong>{row.year}</strong></td>
                        <td><strong style={{ color: '#00f2fe' }}>{fmt(row.forecasted_sales)}</strong></td>
                        <td>{fmt(row.lower_bound)}</td>
                        <td>{fmt(row.upper_bound)}</td>
                        <td><span className="tag-risk low">{row.scenario}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: COMPANY FINANCIALS */}
        {activeTab === 'financials' && (
          <div>
            <div className="filter-bar">
              <div className="filter-group">
                <label className="filter-label">Select OEM / Manufacturer</label>
                <select className="filter-select" value={selectedCompany} onChange={e => setSelectedCompany(e.target.value)}>
                  {companiesList.map((c, idx) => (
                    <option key={idx} value={c.company_name}>
                      {c.company_name} ({c.ticker})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {financialsData && (
              <div className="grid-2">
                <div className="glass-card">
                  <h3>Financial Income Statements ({selectedCompany})</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
                    Annual revenue and net income trajectory ($)
                  </p>
                  <div style={{ height: '320px' }}>
                    <Bar
                      data={{
                        labels: financialsData.financials.map(f => f.year),
                        datasets: [
                          {
                            label: 'Revenue ($)',
                            data: financialsData.financials.map(f => f.revenue),
                            backgroundColor: 'rgba(59, 130, 246, 0.85)',
                            borderRadius: 6
                          },
                          {
                            label: 'Net Income ($)',
                            data: financialsData.financials.map(f => f.net_income),
                            backgroundColor: 'rgba(16, 185, 129, 0.85)',
                            borderRadius: 6
                          }
                        ]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          y: { ticks: { color: '#94a3b8' } },
                          x: { ticks: { color: '#94a3b8' } }
                        }
                      }}
                    />
                  </div>
                </div>

                <div className="glass-card">
                  <h3>Daily Stock Price Timeseries ({selectedCompany})</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
                    Historical closing stock price trends
                  </p>
                  <div style={{ height: '320px' }}>
                    <Line
                      data={{
                        labels: financialsData.stock_prices.filter((_, i) => i % 20 === 0).map(s => s.date),
                        datasets: [{
                          label: 'Close Price ($)',
                          data: financialsData.stock_prices.filter((_, i) => i % 20 === 0).map(s => s.close),
                          borderColor: '#a855f7',
                          backgroundColor: 'rgba(168, 85, 247, 0.1)',
                          fill: true,
                          tension: 0.2
                        }]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                          y: { ticks: { color: '#94a3b8' } },
                          x: { ticks: { display: false } }
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 6: DECISION SUPPORT MATRIX */}
        {activeTab === 'decision' && (
          <div>
            <div className="glass-card" style={{ marginBottom: '28px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div>
                  <h3>Country Expansion Priority Rankings</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    Adjust the priority sliders below to calculate which countries are best for selling or building electric cars
                  </p>
                </div>
                <button className="nav-btn active" onClick={runEvaluation}>
                  <RefreshCw size={14} /> Recalculate Rankings
                </button>
              </div>

              <div className="grid-2" style={{ marginBottom: '0' }}>
                <div>
                  <label className="filter-label">EV Sales Growth Importance: {(evalWeights.w_demand_growth * 100).toFixed(0)}%</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    className="range-slider"
                    value={evalWeights.w_demand_growth}
                    onChange={e => setEvalWeights({ ...evalWeights, w_demand_growth: parseFloat(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="filter-label">Electricity Grid Access Importance: {(evalWeights.w_infrastructure * 100).toFixed(0)}%</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    className="range-slider"
                    value={evalWeights.w_infrastructure}
                    onChange={e => setEvalWeights({ ...evalWeights, w_infrastructure: parseFloat(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="filter-label">People Income Level Importance: {(evalWeights.w_gdp_per_capita * 100).toFixed(0)}%</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    className="range-slider"
                    value={evalWeights.w_gdp_per_capita}
                    onChange={e => setEvalWeights({ ...evalWeights, w_gdp_per_capita: parseFloat(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="filter-label">Total Market Size Importance: {(evalWeights.w_market_size * 100).toFixed(0)}%</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    className="range-slider"
                    value={evalWeights.w_market_size}
                    onChange={e => setEvalWeights({ ...evalWeights, w_market_size: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
            </div>

            <div className="glass-card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <h3>Country Market Readiness & Expansion Index</h3>
                <select className="filter-select" value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
                  <option value="All">All Risk Tiers</option>
                  <option value="Low Risk">Low Risk / Top Tier</option>
                  <option value="Moderate Risk">Moderate Risk</option>
                  <option value="Emerging">Emerging Target</option>
                </select>
              </div>

              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Country</th>
                      <th>Attractiveness Score</th>
                      <th>4-Yr CAGR %</th>
                      <th>2024 EV Sales</th>
                      <th>GDP / Capita ($)</th>
                      <th>Risk Tier</th>
                      <th>Strategic Recommendation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEvaluations.map((row, idx) => (
                      <tr key={idx}>
                        <td><strong>#{idx + 1}</strong></td>
                        <td><strong>{row.country}</strong></td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <strong style={{ color: '#00f2fe' }}>{row.score}</strong> / 100
                          </div>
                        </td>
                        <td>+{row.cagr_pct}%</td>
                        <td>{fmt(row.sales_2024)}</td>
                        <td>${fmt(row.gdp_per_capita)}</td>
                        <td>
                          <span className={`tag-risk ${row.risk_tier.includes('Low') ? 'low' : (row.risk_tier.includes('Moderate') ? 'moderate' : 'high')}`}>
                            {row.risk_tier}
                          </span>
                        </td>
                        <td style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{row.recommendation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: WHAT-IF SCENARIO SIMULATOR */}
        {activeTab === 'simulator' && (
          <div>
            <div className="glass-card" style={{ marginBottom: '28px' }}>
              <h3>"What-If" Sales Simulator</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>
                Test how changes in economy, petrol prices, or government subsidies will increase or decrease future EV sales
              </p>

              <div className="grid-3">
                <div>
                  <label className="filter-label">Country Income Growth Shift: {simParams.gdp_growth_delta > 0 ? `+${simParams.gdp_growth_delta}` : simParams.gdp_growth_delta}%</label>
                  <input
                    type="range"
                    min="-4.0"
                    max="6.0"
                    step="0.5"
                    className="range-slider"
                    value={simParams.gdp_growth_delta}
                    onChange={e => setSimParams({ ...simParams, gdp_growth_delta: parseFloat(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="filter-label">Oil / Petrol Price Shift: {simParams.oil_price_delta > 0 ? `+${simParams.oil_price_delta}` : simParams.oil_price_delta} $/barrel</label>
                  <input
                    type="range"
                    min="-30"
                    max="50"
                    step="5"
                    className="range-slider"
                    value={simParams.oil_price_delta}
                    onChange={e => setSimParams({ ...simParams, oil_price_delta: parseFloat(e.target.value) })}
                  />
                </div>

                <div>
                  <label className="filter-label">Government EV Subsidies & Benefits</label>
                  <select
                    className="filter-select"
                    style={{ width: '100%' }}
                    value={simParams.subsidy_incentive}
                    onChange={e => setSimParams({ ...simParams, subsidy_incentive: e.target.value })}
                  >
                    <option value="High">High Subsidies (Heavy Government Support)</option>
                    <option value="Moderate">Moderate Subsidies (Standard Support)</option>
                    <option value="Low">Low Subsidies (No Government Support)</option>
                  </select>
                </div>
              </div>
            </div>

            {simResults && (
              <div className="glass-card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <h3>Simulated Demand Trajectory (2025–2030)</h3>
                  <div className="tag-risk low" style={{ fontSize: '0.88rem' }}>
                    Net Demand Shift: {simResults.parameters.net_demand_shift_pct > 0 ? `+${simResults.parameters.net_demand_shift_pct}` : simResults.parameters.net_demand_shift_pct}%
                  </div>
                </div>

                <div style={{ height: '360px', marginTop: '16px' }}>
                  <Line
                    data={{
                      labels: simResults.simulation.map(s => s.year),
                      datasets: [
                        {
                          label: 'Simulated EV Sales',
                          data: simResults.simulation.map(s => s.simulated_forecast),
                          borderColor: '#10b981',
                          backgroundColor: 'rgba(16, 185, 129, 0.15)',
                          fill: true,
                          tension: 0.35,
                          pointRadius: 6
                        },
                        {
                          label: 'Baseline ML Forecast',
                          data: simResults.simulation.map(s => s.base_forecast),
                          borderColor: '#94a3b8',
                          borderDash: [6, 6],
                          fill: false
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                      }
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        )}


      </main>
    </div>
  );
}
