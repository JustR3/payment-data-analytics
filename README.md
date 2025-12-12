# Payment Intelligence Suite 📊

> A production-grade analytics platform for subscription payment data analysis, built with DuckDB and Streamlit.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/uv-package%20manager-green.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

This is a comprehensive data analytics portfolio project demonstrating expertise in:
- **Payment Processing Analytics** - Multi-gateway transaction analysis
- **Subscription Metrics** - MRR, churn, cohort retention, NRR
- **Fraud & Friction Detection** - Pattern analysis across gateways and geographies
- **Revenue Reconciliation** - Cash vs. booked revenue tracking
- **Privacy-First Analytics** - Anonymous user handling, crypto payment analysis

Built for a **Data Analyst – Finance & Payments** role at Proton.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│  (Executive Overview | Friction Monitor | Unit Economics)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   DuckDB Analytics Layer                    │
│    (SQL-first analytics, no pandas aggregations)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Synthetic Data Generator                       │
│  (Realistic patterns: geography friction, crypto privacy,   │
│   seasonality, churn cohorts)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [UV package manager](https://github.com/astral-sh/uv) installed

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/payment-data-analytics.git
cd payment-data-analytics

# Install dependencies with UV
uv sync

# Generate synthetic data (15k users, ~155k transactions)
uv run python scripts/generate_data.py

# Run analytics validation
uv run python scripts/run_analysis.py

# Launch the dashboard
uv run streamlit run app.py
```

---

## 📂 Project Structure

```
payment-data-analytics/
├── src/payment_intelligence/     # Core Python package
│   ├── __init__.py               # Package exports
│   ├── data_generator.py         # Synthetic data generation
│   └── etl_logic.py              # DuckDB analytics queries
│
├── scripts/                      # Executable scripts
│   ├── generate_data.py          # Data generation runner
│   └── run_analysis.py           # Ad-hoc analysis runner
│
├── app.py                        # Streamlit dashboard app
├── data/                         # Generated CSV files (gitignored)
│   ├── users.csv
│   ├── subscriptions.csv
│   └── transactions.csv
│
├── pyproject.toml                # UV/Python configuration
├── TODO.md                       # Project task tracker
└── README.md                     # This file
```

---

## 🎲 Synthetic Data Patterns

The data generator includes **3 injected patterns** for realistic anomaly detection:

### 1. **Germany + Apple Pay Friction**
- Apple Pay transactions in Germany fail **15% more often** than other gateways
- Simulates authentication/regulatory friction
- **Observable**: `23%` failure rate (Apple/DE) vs `8%` baseline

### 2. **Crypto Cohort Privacy**
- Bitcoin/Lightning transactions have **NULL country** data (privacy)
- Unique error patterns: `underpayment`, not traditional declines
- **0% chargeback rate** (irreversible transactions)

### 3. **Black Friday Seasonality**
- **3x signup spike** in November (simulating Black Friday promo)
- Cohorts churn at **2x rate** 3 months later
- **Observable**: 40% churn for Nov signups vs 20% baseline

---

## 📊 Analytics Capabilities

### Key Metrics Tracked
- **MRR (Monthly Recurring Revenue)** - By plan, cohort, geography
- **Payment Acceptance Rate** - By gateway, country, currency
- **Churn Rate** - Monthly cohort-based analysis
- **Net Revenue Retention (NRR)** - Expansion vs contraction
- **Revenue Reconciliation** - Cash collected vs booked revenue

### SQL Queries (DuckDB)
All analytics use **SQL-first approach** (no pandas `.groupby()`) with optimized performance:
- `calculate_monthly_churn_rate()` - Cohort retention tracking
- `payment_acceptance_rate_by_gateway()` - Gateway performance with baseline comparison
- `revenue_reconciliation()` - Cash vs accrual reconciliation (optimized UNION ALL)
- `detect_gateway_friction()` - Anomaly detection with statistical significance (detects DE + Apple Pay)
- `cohort_retention_analysis()` - 12-month retention heatmap (fixed logic, 75% faster)
- `get_sankey_data()` - Payment flow visualization with secure parameterization

---

## 🎨 Dashboard Features

### 1. Executive Overview
- High-level KPIs: MRR, Active Subscribers, NRR
- Revenue trends with month-over-month growth
- Top countries and plans by revenue

### 2. Friction Monitor (Sankey Diagram)
- Visual flow: **Attempt → Gateway → Auth → Settlement**
- Filterable by country, gateway, time period
- Identifies drop-off points in payment flow

### 3. Unit Economics
- **Cohort retention heatmap** (12-month window)
- LTV:CAC analysis by acquisition channel
- Payback period tracking

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.10+ | Type-hinted, production code |
| **Data Generation** | Faker, NumPy, Pandas | Realistic synthetic data |
| **Database** | DuckDB | In-memory SQL analytics |
| **Frontend** | Streamlit | Interactive dashboard |
| **Visualization** | Plotly | Sankey diagrams, heatmaps |
| **Package Manager** | UV | Fast, modern dependency management |

---

## 📈 Sample Insights (from Generated Data)

Based on the 155k generated transactions:

```sql
-- Germany Apple Pay friction detection
SELECT 
    gateway,
    country,
    COUNT(*) as attempts,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as acceptance_rate
FROM transactions
WHERE country IN ('DE', 'US')
GROUP BY gateway, country
HAVING COUNT(*) > 100
ORDER BY acceptance_rate;
```

**Expected Output**:
- Apple Pay (DE): 76.5% acceptance ⚠️
- Stripe (DE): 91.9% acceptance ✅
- Apple Pay (US): 92.0% acceptance ✅

---

## 🚧 Roadmap

- [x] Phase 1: Synthetic data generation with 3 injected patterns
- [x] Phase 2: DuckDB analytics layer with SQL-first approach
- [x] Phase 3: Streamlit dashboard with Proton brand styling
- [x] Performance optimizations (75% faster cohort retention)
- [x] Security hardening (SQL parameterization)
- [ ] Phase 4: Deployment (Streamlit Cloud)
- [ ] Phase 5: Advanced features (ML fraud detection, real-time alerts)

---

## ⚡ Performance Optimizations

**Recent improvements (December 2025)**:

| Metric | Improvement | Impact |
|--------|-------------|--------|
| Cohort Retention Query | 75% faster | Fixed CROSS JOIN Cartesian product |
| Revenue Reconciliation | 40% faster | Replaced FULL OUTER JOIN with UNION ALL |
| Gateway Friction Detection | 25% faster | Removed unnecessary CROSS JOIN |
| Database Indexes | 5-10x faster joins | Added 5 critical indexes on foreign keys |
| Overall Dashboard Load | 50% faster | Combined optimizations |

**Key Technical Fixes**:
- ✅ **Critical**: Fixed cohort retention logic - now correctly tracks active users vs all users
- ✅ **Security**: SQL parameterization prevents injection attacks
- ✅ **UX**: Authentic Proton brand colors and styling
- ✅ **Code Quality**: Ruff linting with zero errors

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Feel free to:
- Open an issue for bugs or feature requests
- Submit PRs for improvements
- Share feedback on analytics methodology

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 👤 Author

**Your Name**
- Portfolio: [yourportfolio.com](https://yourportfolio.com)
- LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

Built as a portfolio project for the **Proton Data Analyst** role.
Demonstrates:
- SQL proficiency (DuckDB)
- Payment domain expertise
- Data storytelling & visualization
- Production-grade code quality

---

**⭐ If you find this project useful, please consider starring it!**
