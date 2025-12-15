# Payment Intelligence Suite 📊

> Production-grade analytics platform for subscription payment data analysis, built with DuckDB and Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://data-payment-analysis.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/uv-package%20manager-green.svg)](https://github.com/astral-sh/uv)

---

## 🚀 Live Demo

**[→ View Live Dashboard](https://data-payment-analysis.streamlit.app/)**

Experience the full analytics suite with:
- **25,000+ synthetic transactions** across 4 payment gateways (2,500 users)
- **Real-time friction detection** - identifies payment gateway anomalies
- **Interactive Sankey flow diagrams** with region filtering
- **12-month cohort retention analysis** with heatmap visualization

![Dashboard Demo](demo.gif)

---

## 🎯 Project Overview

Comprehensive payment analytics platform demonstrating:
- **Payment Processing Analytics** - Multi-gateway transaction analysis
- **Subscription Metrics** - MRR, churn, cohort retention
- **Fraud & Friction Detection** - Statistical anomaly detection across gateways and geographies
- **Revenue Reconciliation** - Cash vs. booked revenue tracking
- **Privacy-First Analytics** - Anonymous user handling, crypto payment analysis

---

## 🏗️ Architecture

**Data Pipeline Flow** (bottom-up):

```
┌─────────────────────────────────────────────────────────────┐
│              Synthetic Data Generator                       │
│  (Realistic patterns: geography friction, crypto privacy,   │
│   seasonality, churn cohorts)                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼ CSVs (users, subscriptions, transactions)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   DuckDB Analytics Layer                    │
│    (SQL-first analytics, no pandas aggregations)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼ DataFrames (metrics, friction, cohorts)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│  (Executive Overview | Friction Monitor | Cohort Analysis)  │
└─────────────────────────────────────────────────────────────┘
```

**Layer Responsibilities**:
1. **Data Generator** - Creates synthetic datasets with injected patterns
2. **Analytics Layer** - Transforms raw data into business metrics via SQL
3. **Dashboard** - Visualizes insights with interactive charts and tables

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [UV package manager](https://github.com/astral-sh/uv) (installation instructions below)

### Installation

```bash
# Clone the repository
git clone https://github.com/JustR3/payment-data-analytics.git
cd payment-data-analytics

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies with UV
uv sync

# Generate synthetic data (15,000 users for local development)
uv run python scripts/generate_data.py

# Launch the dashboard
uv run streamlit run app.py
```

**Note**: The repository includes pre-generated sample data (2,500 users, ~25,000 transactions) for Streamlit Cloud deployment. The app will auto-generate a minimal dataset (1,000 users) only if data files are missing.

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
├── data/                         # Pre-generated sample data
│   ├── users.csv                 # 2,500 users
│   ├── subscriptions.csv         # ~3,100 subscriptions
│   └── transactions.csv          # ~25,000 transactions
│
├── pyproject.toml                # UV/Python configuration
├── TODO.md                       # Project task tracker
└── README.md                     # This file
```

---

## 🎲 Synthetic Data Patterns

The data generator injects **5 realistic patterns** to demonstrate anomaly detection capabilities:

### 1. **Payment Gateway Friction (Regional)**
Two distinct friction patterns:
- **Germany + Apple Pay**: 15% higher failure rate (High friction, >10% variance)
- **France + PayPal**: 9% higher failure rate (Medium friction, 5-10% variance)
- Simulates authentication/regulatory friction (e.g., SCA requirements in EU)
- **Detection**: Three-tier classification (High >10%, Medium 5-10%, Low <5% variance)
- **Note**: Specific variance values may fluctuate with dataset size due to statistical sampling

### 2. **Crypto Payment Privacy**
- Bitcoin transactions have **NULL country** data (privacy-first approach)
- Unique error patterns: `underpayment`, not traditional card declines
- **0% chargeback rate** (irreversible cryptocurrency transactions)
- **Observable**: 100% NULL country for Bitcoin gateway

### 3. **Black Friday Seasonality**
- **3x signup spike** in November (simulating promotional campaigns)
- November cohorts show **higher churn rates** 3 months later
- **Observable**: Elevated November signups vs monthly baseline

### 4. **Multi-Gateway Distribution**
- Realistic payment method distribution across Stripe, PayPal, Apple Pay, Bitcoin
- Geography-based payment preferences (e.g., higher PayPal usage in Europe)
- **Observable**: Varied transaction volumes across gateway/region pairs

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
- `detect_gateway_friction()` - Anomaly detection with statistical significance across gateway/region pairs
- `cohort_retention_analysis()` - 12-month retention heatmap (fixed logic, 75% faster)
- `get_sankey_data()` - Payment flow visualization with secure parameterization

---

## 🎨 Dashboard Features

### 1. Executive Overview
- **Real-time KPIs**: MRR, Active Subscriptions, Auth Rate (L30D), Churn Rate, Avg Transaction Value
- Monthly churn and retention trends with Plotly visualizations
- Gateway performance table with acceptance rates and decline analysis

### 2. Friction Monitor
- **Interactive Sankey Diagram**: Payment flow from Attempt → Gateway → Authorization → Settlement
- **Three-tier friction detection**: 
  - High (>10% variance): Significant payment friction requiring immediate attention
  - Medium (5-10% variance): Moderate regional payment issues
  - Low (<5% variance): Optimal gateway performance
- Country filtering with detailed variance analysis
- Common error pattern identification (including authentication_failed, card_declined, fraud_detected, insufficient_funds, expired_card, network_error, and crypto-specific underpayment errors)

### 3. Cohort Analysis
- **12-month retention heatmap** with Proton purple gradient visualization
- Month-over-month retention tracking by signup cohort
- Key metrics: Month 1, Month 6, and Month 12 average retention
- Revenue reconciliation table (cash collected vs booked revenue)

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

## 📈 Live Data Insights

Based on the deployed application with 25k+ transactions:

**Friction Detection Example**:
```sql
-- Statistical anomaly detection in production
SELECT 
    gateway,
    country,
    COUNT(*) as attempts,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100, 1) as acceptance_rate
FROM transactions
WHERE country IS NOT NULL
GROUP BY gateway, country
HAVING COUNT(*) >= 50
ORDER BY acceptance_rate;
```

**Live Dashboard Features**:
- Detects payment gateway friction patterns across regions
- Compares individual gateway/country performance vs baseline
- Identifies high-friction combinations requiring operational attention
- Shows common error patterns (authentication failures, card declines, fraud flags)

The friction detection algorithm successfully identifies statistically significant variances from baseline acceptance rates.

---

## 🚧 Development Status

- [x] Synthetic data generation with 4 injected patterns
- [x] DuckDB analytics layer with SQL-first approach
- [x] Streamlit dashboard with Proton brand styling
- [x] Performance optimizations (75% faster cohort retention)
- [x] Security hardening (SQL parameterization, race condition protection)
- [x] **Deployed to Streamlit Cloud** - [Live Demo](https://data-payment-analysis.streamlit.app/)
- [x] Bug fixes: data-relative date filtering, proper churn calculation
- [ ] Advanced features: ML fraud detection, real-time alerts, CSV export

---

## ⚡ Performance Optimizations

**Production improvements (December 2025)**:

| Metric | Before | After | Improvement | Impact |
|--------|--------|-------|-------------|--------|
| Cohort Retention Query | ~800ms | ~200ms | 75% faster | Fixed CROSS JOIN Cartesian product |
| Revenue Reconciliation | ~500ms | ~300ms | 40% faster | Replaced FULL OUTER JOIN with UNION ALL |
| Gateway Friction Detection | ~400ms | ~300ms | 25% faster | Removed unnecessary CROSS JOIN |
| Database Indexes | N/A | N/A | 5-10x faster joins | Added 5 critical indexes on foreign keys |
| Date Filtering | N/A | N/A | Future-proof | Data-relative dates instead of CURRENT_DATE |
| Overall Dashboard Load | ~3.5s | ~1.7s | 50% faster | Combined optimizations |

*Note: Timings are approximate and measured on 25k transaction dataset with DuckDB in-memory mode.*

**Critical Bug Fixes**:
- ✅ Fixed churn rate calculation - now accurately reflects monthly churn
- ✅ Race condition protection - safe concurrent data generation
- ✅ Database connection cleanup - prevents memory leaks
- ✅ SQL query optimization - limited error aggregation, improved performance

---

## 🛠️ Technical Highlights

- **Type-safe Python** - Full type hints with mypy compatibility
- **SQL-first analytics** - Zero pandas `.groupby()`, all DuckDB SQL
- **Secure queries** - Parameterized SQL prevents injection attacks
- **Production logging** - Comprehensive error handling and data validation
- **Code quality** - Ruff linted with zero errors
- **White-label design** - Proton brand colors (#6d4aff) with professional UX

---

## 🤝 Contributing

This is a portfolio project demonstrating production-grade data engineering practices. Suggestions and feedback are welcome:
- Open issues for bugs or feature requests
- Submit PRs for improvements
- Share analytics methodology feedback

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## Summary

Built to demonstrate:
- Advanced SQL proficiency (DuckDB)
- Payment domain expertise
- Data storytelling & visualization
- Production-grade code quality

**Stack**: Python 3.10+ • DuckDB • Streamlit • Plotly • UV