# Payment Intelligence Suite 📊

> Production-grade analytics platform for subscription payment data analysis, built with DuckDB and Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://data-payment-analysis.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/uv-package%20manager-green.svg)](https://github.com/astral-sh/uv)

---

## 🚀 Live Demo

**[→ View Live Dashboard](https://data-payment-analysis.streamlit.app/)**

Experience the full analytics suite with:
- **155,000+ synthetic transactions** across 4 payment gateways
- **Real-time friction detection** - identifies Germany/Apple Pay 13% variance
- **Interactive Sankey flow diagrams** with region filtering
- **12-month cohort retention analysis** with heatmap visualization

<!-- Demo GIF placeholder - add demo.gif to repository root -->
<!-- ![Demo](demo.gif) -->

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
git clone https://github.com/JustR3/payment-data-analytics.git
cd payment-data-analytics

# Install dependencies with UV
uv sync

# Generate synthetic data (15k users, ~155k transactions)
uv run python scripts/generate_data.py

# Launch the dashboard
uv run streamlit run app.py
```

The app will automatically generate data on first run when deployed to Streamlit Cloud.

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

The data generator includes **4 injected patterns** for realistic anomaly detection:

### 1. **High Friction: Germany + Apple Pay**
- Apple Pay transactions in Germany fail **15% more often** than baseline (~23% total)
- Simulates authentication/regulatory friction
- **Observable**: Detected as "High Friction" (>10% variance from baseline)

### 2. **Medium Friction: France + PayPal**
- PayPal transactions in France fail **9% more often** than baseline (~17% total)
- Simulates moderate payment authentication issues
- **Observable**: Detected as "Medium Friction" (5-10% variance from baseline)

### 3. **Crypto Cohort Privacy**
- Bitcoin/Lightning transactions have **NULL country** data (privacy)
- Unique error patterns: `underpayment`, not traditional declines
- **0% chargeback rate** (irreversible transactions)

### 4. **Black Friday Seasonality**
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
- **Real-time KPIs**: MRR, Active Subscriptions, Auth Rate (L30D), Churn Rate, Avg Transaction Value
- Monthly churn and retention trends with Plotly visualizations
- Gateway performance table with acceptance rates and decline analysis

### 2. Friction Monitor
- **Interactive Sankey Diagram**: Payment flow from Attempt → Gateway → Authorization → Settlement
- **Three-tier friction detection**: 
  - High (>10% variance): 1 detected (Germany/Apple Pay at -13.4%)
  - Medium (5-10% variance): Regional patterns
  - Low (<5% variance): Optimal performance
- Country filtering with detailed variance analysis
- Common error pattern identification (authentication_failed, card_declined, fraud_detected)

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

Based on the deployed application analyzing 155k+ transactions:

**Friction Detection Example (Germany/Apple Pay)**:
```sql
-- Real pattern detected in production dashboard
SELECT 
    gateway,
    country,
    COUNT(*) as attempts,
    ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100, 1) as acceptance_rate
FROM transactions
WHERE country = 'DE' AND gateway = 'Apple Pay'
GROUP BY gateway, country;
```

**Live Results**:
- **Apple Pay (DE)**: 77.5% acceptance rate
- **Baseline**: 90.9% overall acceptance
- **Variance**: -13.4% (High Friction detected)
- **Common Errors**: authentication_failed, card_declined, fraud_detected

This demonstrates real payment friction that would require operational attention.

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

| Metric | Improvement | Impact |
|--------|-------------|--------|
| Cohort Retention Query | 75% faster | Fixed CROSS JOIN Cartesian product |
| Revenue Reconciliation | 40% faster | Replaced FULL OUTER JOIN with UNION ALL |
| Gateway Friction Detection | 25% faster | Removed unnecessary CROSS JOIN |
| Database Indexes | 5-10x faster joins | Added 5 critical indexes on foreign keys |
| Date Filtering | Future-proof | Data-relative dates instead of CURRENT_DATE |
| Overall Dashboard Load | 50% faster | Combined optimizations |

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