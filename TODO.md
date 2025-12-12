# Payment Intelligence Suite - Project TODO

## 🎯 Project Goal
Build a deployed Streamlit application backed by DuckDB that analyzes synthetic subscription payment data for Proton Data Analyst role application.

---

## 📋 PHASE 1: SYNTHETIC DATA GENERATION

### Big Tasks
- [x] Set up project structure
- [x] **Build `data_generator.py`**
  - [x] Implement `users` table generation
  - [x] Implement `subscriptions` table generation  
  - [x] Implement `transactions` table generation
  - [x] Inject Pattern #1: Germany/Apple Pay Friction (15% higher failure rate)
  - [x] Inject Pattern #2: Crypto Cohort (NULL country, 0% chargeback, underpayment errors)
  - [x] Inject Pattern #3: Black Friday Seasonality (November spike + 3-month churn)
  - [x] Export to CSV files

### Small Tasks
- [x] Add type hints to all functions
- [x] Add docstrings with pattern documentation
- [x] Validate data relationships (foreign keys)
- [x] Test data generation with 10k, 25k, 50k rows
- [x] Ensure proper date distributions (2-year history)

---

## 📋 PHASE 2: ANALYTICS & SQL

### Big Tasks
- [x] **Build `etl_logic.py`**
  - [x] Set up DuckDB connection and schema
  - [x] Query: `calculate_monthly_churn_rate()`
  - [x] Query: `payment_acceptance_rate_by_gateway()`
  - [x] Query: `revenue_reconciliation()` (Cash vs. Booked)
  - [x] Query: Detect Germany/Apple Pay friction pattern
  - [x] Query: Cohort retention analysis

### Small Tasks
- [x] Add SQL query documentation
- [x] Implement connection pooling/cleanup
- [x] Add query performance logging
- [x] Create helper function for loading CSVs into DuckDB
- [x] Add data validation checks

---

## 📋 PHASE 3: STREAMLIT DASHBOARD

### Big Tasks
- [x] **Build `app.py`**
  - [x] Set up dark theme (Proton-style)
  - [x] Sidebar navigation structure
  - [x] Page 1: Executive Overview (MRR, Active Subs, NRR)
  - [x] Page 2: Friction Monitor (Sankey: Attempt → Gateway → Auth → Settlement)
  - [x] Page 3: Unit Economics (Cohort heatmap - 12 months)

### Small Tasks
- [x] Add country filter functionality
- [x] Implement date range selector
- [x] Add metrics cards with delta indicators
- [x] Create custom CSS for Proton branding
- [x] Add data refresh mechanism
- [x] Implement caching for performance
- [ ] Add export to PDF/CSV functionality

---

## 📋 PHASE 4: DEPLOYMENT & POLISH

### Big Tasks
- [x] Create comprehensive README.md
- [x] Set up project dependencies (pyproject.toml with UV)
- [ ] Deploy to Streamlit Cloud
- [ ] Create demo video/GIF

### Small Tasks
- [x] Add .gitignore
- [x] Document installation steps
- [ ] Add environment variable support
- [ ] Create sample data for quick demo
- [x] Add error handling and logging
- [ ] Write unit tests for key functions
- [ ] Add performance benchmarks

---

## 🎓 LEARNING OBJECTIVES DEMONSTRATED

### Technical Skills
- [ ] Advanced Python (type hints, modular design)
- [ ] SQL proficiency (DuckDB analytics)
- [ ] Data visualization (Plotly Sankey diagrams)
- [ ] Web frameworks (Streamlit)
- [ ] Synthetic data generation with realistic patterns

### Business Acumen
- [ ] Payment gateway analysis
- [ ] Fraud/friction detection
- [ ] Revenue reconciliation
- [ ] Cohort retention metrics
- [ ] Privacy considerations (anonymous users, crypto)

### Domain Knowledge
- [ ] Subscription business metrics (MRR, NRR, churn)
- [ ] Payment processing flows
- [ ] Geographic payment preferences
- [ ] Decline code analysis
- [ ] Multi-currency handling

---

## 🚀 NEXT STEPS
1. ✅ Complete `data_generator.py` with all injected patterns
2. Run data generation and validate CSV outputs
3. Build `etl_logic.py` and validate pattern detection
4. Build Streamlit dashboard incrementally
5. Deploy and create portfolio documentation

---

## 📊 SUCCESS METRICS
- [ ] 10,000–50,000 transaction records generated
- [ ] All 3 injected patterns detectable in analytics
- [ ] Dashboard loads in <2 seconds
- [ ] Sankey diagram clearly shows payment friction
- [ ] Code is production-grade (linted, typed, documented)
