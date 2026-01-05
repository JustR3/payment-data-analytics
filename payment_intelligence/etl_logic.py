import duckdb
import pandas as pd
from pathlib import Path

class PaymentAnalytics:
    """Optimized analytics engine with query caching and efficient data loading."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        # Use in-memory database for faster queries on Streamlit Cloud
        self.conn = duckdb.connect(":memory:")
        self._data_loaded = False
        
    def load_data(self):
        """Load CSV data into DuckDB with optimized settings."""
        if self._data_loaded:
            return
            
        try:
            # Batch load all CSVs at once with optimized settings
            self.conn.execute(f"""
                SET threads TO 2;  -- Limit threads for free tier
                SET memory_limit = '500MB';  -- Conservative memory usage
                
                CREATE TABLE users AS 
                SELECT * FROM read_csv_auto('{self.data_dir}/users.csv');
                
                CREATE TABLE subscriptions AS 
                SELECT * FROM read_csv_auto('{self.data_dir}/subscriptions.csv');
                
                CREATE TABLE transactions AS 
                SELECT * FROM read_csv_auto('{self.data_dir}/transactions.csv');
            """)
            
            # Validate data loaded
            user_count = self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            sub_count = self.conn.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]
            tx_count = self.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            
            if user_count == 0 or sub_count == 0 or tx_count == 0:
                raise ValueError(f"Data validation failed: users={user_count}, subs={sub_count}, txs={tx_count}")
            
            # Create indexes for frequently queried columns
            self.conn.execute("""
                CREATE INDEX idx_user_id ON users(user_id);
                CREATE INDEX idx_sub_user ON subscriptions(user_id);
                CREATE INDEX idx_tx_sub ON transactions(sub_id);
                CREATE INDEX idx_tx_date ON transactions(tx_date);
                CREATE INDEX idx_tx_status ON transactions(status);
            """)
            
            self._data_loaded = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to load data into DuckDB: {str(e)}") from e

    def executive_metrics(self) -> dict:
        """Get executive metrics with single optimized query."""
        # Combine multiple queries into one for efficiency
        result = self.conn.execute("""
            WITH active_subs AS (
                SELECT COUNT(*) as active_count,
                       SUM(mrr_amount) as total_mrr
                FROM subscriptions
                WHERE status = 'Active'
            ),
            recent_txs AS (
                SELECT 
                    AVG(CASE WHEN status = 'Success' THEN amount ELSE NULL END) as avg_tx,
                    COUNT(CASE WHEN status = 'Success' THEN 1 END)::FLOAT / 
                    NULLIF(COUNT(*), 0) * 100 as success_rate
                FROM transactions
                WHERE tx_date >= CURRENT_DATE - INTERVAL '30 days'
            ),
            churn_calc AS (
                SELECT 
                    COUNT(CASE WHEN status = 'Cancelled' THEN 1 END)::FLOAT /
                    NULLIF(COUNT(*), 0) * 100 as churn_rate
                FROM subscriptions
            )
            SELECT 
                a.active_count,
                a.total_mrr,
                r.avg_tx,
                r.success_rate,
                COALESCE(c.churn_rate, 0) as churn_rate
            FROM active_subs a, recent_txs r, churn_calc c
        """).fetchone()
        
        return {
            'active_subscriptions': result[0] or 0,
            'mrr': result[1] or 0,
            'avg_transaction_value': result[2] or 0,
            'payment_success_rate': result[3] or 0,
            'churn_rate': result[4] or 0,
        }

    def calculate_monthly_churn_rate(self) -> pd.DataFrame:
        """Optimized monthly churn calculation."""
        return self.conn.execute("""
            WITH monthly_stats AS (
                SELECT 
                    DATE_TRUNC('month', start_date) as cohort_month,
                    COUNT(*) as total_subs,
                    COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as churned
                FROM subscriptions
                WHERE start_date >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', start_date)
            )
            SELECT 
                cohort_month,
                total_subs,
                churned,
                (churned::FLOAT / NULLIF(total_subs, 0) * 100) as churn_rate_pct,
                (100 - (churned::FLOAT / NULLIF(total_subs, 0) * 100)) as retention_rate_pct
            FROM monthly_stats
            ORDER BY cohort_month
        """).df()

    def payment_acceptance_rate_by_gateway(self, min_transactions: int = 50) -> pd.DataFrame:
        """Optimized gateway performance analysis."""
        return self.conn.execute(f"""
            SELECT 
                gateway,
                country,
                COUNT(*) as total_attempts,
                COUNT(CASE WHEN status = 'Success' THEN 1 END)::FLOAT / 
                    NULLIF(COUNT(*), 0) * 100 as acceptance_rate_pct,
                COUNT(CASE WHEN status = 'Soft Decline' THEN 1 END)::FLOAT / 
                    NULLIF(COUNT(*), 0) * 100 as soft_decline_rate_pct,
                COUNT(CASE WHEN status = 'Hard Decline' THEN 1 END)::FLOAT / 
                    NULLIF(COUNT(*), 0) * 100 as hard_decline_rate_pct
            FROM transactions
            GROUP BY gateway, country
            HAVING COUNT(*) >= {min_transactions}
            ORDER BY acceptance_rate_pct DESC
            LIMIT 50
        """).df()

    def detect_gateway_friction(self) -> pd.DataFrame:
        """Optimized friction detection with single query."""
        return self.conn.execute("""
            WITH gateway_stats AS (
                SELECT 
                    gateway,
                    country,
                    COUNT(*) as attempts,
                    COUNT(CASE WHEN status = 'Success' THEN 1 END)::FLOAT / 
                        NULLIF(COUNT(*), 0) * 100 as acceptance_rate_pct,
                    STRING_AGG(DISTINCT error_code, ', ') as common_errors
                FROM transactions
                GROUP BY gateway, country
                HAVING COUNT(*) >= 30
            ),
            baseline AS (
                SELECT AVG(acceptance_rate_pct) as baseline_rate
                FROM gateway_stats
            )
            SELECT 
                g.*,
                b.baseline_rate as baseline_rate_pct,
                (g.acceptance_rate_pct - b.baseline_rate) as variance_from_baseline,
                CASE 
                    WHEN (g.acceptance_rate_pct - b.baseline_rate) < -10 THEN 'High Friction'
                    WHEN (g.acceptance_rate_pct - b.baseline_rate) < -5 THEN 'Medium Friction'
                    ELSE 'Low Friction'
                END as friction_flag
            FROM gateway_stats g, baseline b
            ORDER BY variance_from_baseline ASC
            LIMIT 100
        """).df()

    def cohort_retention_analysis(self, cohort_months: int = 12) -> pd.DataFrame:
        """Optimized cohort retention with window functions."""
        return self.conn.execute(f"""
            WITH cohorts AS (
                SELECT 
                    user_id,
                    DATE_TRUNC('month', start_date) as cohort_month
                FROM subscriptions
                WHERE start_date >= CURRENT_DATE - INTERVAL '{cohort_months} months'
            ),
            sub_months AS (
                SELECT 
                    s.user_id,
                    c.cohort_month,
                    DATE_TRUNC('month', s.start_date) as sub_month,
                    DATEDIFF('month', c.cohort_month, DATE_TRUNC('month', s.start_date)) as months_since_signup
                FROM subscriptions s
                JOIN cohorts c ON s.user_id = c.user_id
                WHERE s.status IN ('Active', 'Cancelled')
            )
            SELECT 
                cohort_month,
                months_since_signup,
                COUNT(DISTINCT user_id) as retained_users,
                COUNT(DISTINCT user_id)::FLOAT / 
                    FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (
                        PARTITION BY cohort_month ORDER BY months_since_signup
                    ) * 100 as retention_rate_pct
            FROM sub_months
            WHERE months_since_signup BETWEEN 0 AND 12
            GROUP BY cohort_month, months_since_signup
            ORDER BY cohort_month DESC, months_since_signup
        """).df()

    def get_sankey_data(self, country_filter: str = None) -> pd.DataFrame:
        """Optimized Sankey diagram data generation."""
        country_clause = f"AND country = '{country_filter}'" if country_filter else ""
        
        return self.conn.execute(f"""
            -- Attempt to Gateway
            SELECT 'Attempt' as source, gateway as target, COUNT(*) as value
            FROM transactions
            WHERE 1=1 {country_clause}
            GROUP BY gateway
            
            UNION ALL
            
            -- Gateway to Status
            SELECT gateway as source, 
                   CASE status 
                       WHEN 'Success' THEN 'Authorized'
                       ELSE 'Declined'
                   END as target,
                   COUNT(*) as value
            FROM transactions
            WHERE 1=1 {country_clause}
            GROUP BY gateway, target
            
            UNION ALL
            
            -- Authorized to Settled
            SELECT 'Authorized' as source, 'Settled' as target, COUNT(*) as value
            FROM transactions
            WHERE status = 'Success' {country_clause}
        """).df()

    def revenue_reconciliation(self) -> pd.DataFrame:
        """Optimized revenue reconciliation."""
        return self.conn.execute("""
            WITH monthly_cash AS (
                SELECT 
                    DATE_TRUNC('month', tx_date) as month,
                    SUM(amount) as cash_collected,
                    COUNT(*) as successful_payments
                FROM transactions
                WHERE status = 'Success'
                GROUP BY DATE_TRUNC('month', tx_date)
            ),
            monthly_revenue AS (
                SELECT 
                    DATE_TRUNC('month', start_date) as month,
                    SUM(mrr_amount) as booked_revenue
                FROM subscriptions
                WHERE status = 'Active'
                GROUP BY DATE_TRUNC('month', start_date)
            )
            SELECT 
                COALESCE(c.month, r.month) as month,
                c.cash_collected,
                r.booked_revenue,
                (c.cash_collected - r.booked_revenue) as variance,
                (c.cash_collected - r.booked_revenue) / NULLIF(r.booked_revenue, 0) * 100 as variance_pct,
                c.successful_payments
            FROM monthly_cash c
            FULL OUTER JOIN monthly_revenue r ON c.month = r.month
            ORDER BY month DESC
            LIMIT 12
        """).df()
    
    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
