# Payment Intelligence Suite - Project TODO

## 🎯 Project Goal
Build a deployed Streamlit application backed by DuckDB that analyzes synthetic subscription payment data for Proton Data Analyst role application.

---

## 📋 PHASE 1: SYNTHETIC DATA GENERATION

### Big Tasks
- [x] Set up project structure
- [ ] **Build `data_generator.py`**
  - [ ] Implement `users` table generation
  - [ ] Implement `subscriptions` table generation  
  - [ ] Implement `transactions` table generation
  - [ ] Inject Pattern #1: Germany/Apple Pay Friction (15% higher failure rate)
  - [ ] Inject Pattern #2: Crypto Cohort (NULL country, 0% chargeback, underpayment errors)
  - [ ] Inject Pattern #3: Black Friday Seasonality (November spike + 3-month churn)
  - [ ] Export to CSV files

### Small Tasks
- [ ] Add type hints to all functions
- [ ] Add docstrings with pattern documentation
- [ ] Validate data relationships (foreign keys)
- [ ] Test data generation with 10k, 25k, 50k rows
- [ ] Ensure proper date distributions (2-year history)

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
- [ ] **Build `app.py`**
  - [ ] Set up dark theme (Proton-style)
  - [ ] Sidebar navigation structure
  - [ ] Page 1: Executive Overview (MRR, Active Subs, NRR)
  - [ ] Page 2: Friction Monitor (Sankey: Attempt → Gateway → Auth → Settlement)
  - [ ] Page 3: Unit Economics (Cohort heatmap - 12 months)

### Small Tasks
- [ ] Add country filter functionality
- [ ] Implement date range selector
- [ ] Add metrics cards with delta indicators
- [ ] Create custom CSS for Proton branding
- [ ] Add data refresh mechanism
- [ ] Implement caching for performance
- [ ] Add export to PDF/CSV functionality

---

## 📋 PHASE 4: DEPLOYMENT & POLISH

### Big Tasks
- [ ] Create comprehensive README.md
- [ ] Set up requirements.txt
- [ ] Deploy to Streamlit Cloud
- [ ] Create demo video/GIF

### Small Tasks
- [ ] Add .gitignore
- [ ] Document installation steps
- [ ] Add environment variable support
- [ ] Create sample data for quick demo
- [ ] Add error handling and logging
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
