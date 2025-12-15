"""
Payment Intelligence Suite - DuckDB Analytics Layer

This module provides SQL-first analytics for subscription payment data.
All aggregations are performed using DuckDB SQL (no pandas groupby operations).

Key Metrics:
- Monthly Recurring Revenue (MRR)
- Churn Rate (cohort-based)
- Payment Acceptance Rate by Gateway
- Revenue Reconciliation (Cash vs Booked)
- Gateway Friction Detection
- Net Revenue Retention (NRR)

Author: Data Engineering Portfolio
Date: December 2025
"""

import duckdb
from pathlib import Path
from typing import Dict, Optional, Any
import pandas as pd


class PaymentAnalytics:
    """
    DuckDB-powered analytics engine for payment intelligence.

    All analytics use pure SQL for performance and demonstration of SQL proficiency.
    """

    def __init__(self, data_dir: str = "./data", db_path: str = ":memory:"):
        """
        Initialize analytics engine with DuckDB connection.

        Args:
            data_dir: Directory containing CSV files
            db_path: DuckDB database path (:memory: for in-memory)
        """
        self.data_dir = Path(data_dir)
        self.conn = duckdb.connect(db_path)
        self.tables_loaded = False

    def load_data(self) -> None:
        """
        Load CSV files into DuckDB tables.
        Creates optimized schema with proper types and indexes.
        """
        print("📊 Loading data into DuckDB...")

        # Load users table
        users_path = self.data_dir / "users.csv"
        if not users_path.exists():
            raise FileNotFoundError(f"Users data not found at {users_path}")

        self.conn.execute(f"""
            CREATE TABLE users AS 
            SELECT 
                user_id,
                country,
                signup_date::DATE as signup_date,
                is_anonymous::BOOLEAN as is_anonymous
            FROM read_csv_auto('{users_path}')
        """)

        # Load subscriptions table
        subs_path = self.data_dir / "subscriptions.csv"
        self.conn.execute(f"""
            CREATE TABLE subscriptions AS 
            SELECT 
                sub_id,
                user_id,
                plan_type,
                mrr_amount::DECIMAL(10,2) as mrr_amount,
                status,
                start_date::DATE as start_date
            FROM read_csv_auto('{subs_path}')
        """)

        # Load transactions table
        txs_path = self.data_dir / "transactions.csv"
        self.conn.execute(f"""
            CREATE TABLE transactions AS 
            SELECT 
                tx_id,
                sub_id,
                gateway,
                currency,
                status,
                error_code,
                tx_date::DATE as tx_date,
                amount::DECIMAL(10,2) as amount,
                country
            FROM read_csv_auto('{txs_path}')
        """)

        # Create indexes for performance
        self.conn.execute("CREATE INDEX idx_users_id ON users(user_id)")
        self.conn.execute("CREATE INDEX idx_users_country ON users(country)")
        self.conn.execute("CREATE INDEX idx_users_signup ON users(signup_date)")
        self.conn.execute("CREATE INDEX idx_subs_user ON subscriptions(user_id)")
        self.conn.execute("CREATE INDEX idx_subs_status ON subscriptions(status)")
        self.conn.execute("CREATE INDEX idx_txs_sub ON transactions(sub_id)")
        self.conn.execute("CREATE INDEX idx_txs_gateway ON transactions(gateway)")
        self.conn.execute("CREATE INDEX idx_txs_date ON transactions(tx_date)")
        self.conn.execute("CREATE INDEX idx_txs_status ON transactions(status)")

        self.tables_loaded = True

        # Get row counts
        user_count = self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        sub_count = self.conn.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]
        tx_count = self.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

        print(f"   ✓ Loaded {user_count:,} users")
        print(f"   ✓ Loaded {sub_count:,} subscriptions")
        print(f"   ✓ Loaded {tx_count:,} transactions")
        print("   ✓ Indexes created\n")

    def calculate_monthly_churn_rate(self) -> pd.DataFrame:
        """
        Calculate monthly cohort-based churn rate.

        Churn Rate = (Churned Subs in Period) / (Active Subs at Start of Period)
        Uses cohort analysis by signup month.

        Returns:
            DataFrame with columns: cohort_month, total_subs, churned_subs, churn_rate
        """
        query = """
        WITH cohorts AS (
            SELECT 
                DATE_TRUNC('month', signup_date) as cohort_month,
                u.user_id,
                s.sub_id,
                s.status,
                s.start_date
            FROM users u
            JOIN subscriptions s ON u.user_id = s.user_id
        ),
        cohort_metrics AS (
            SELECT 
                cohort_month,
                COUNT(DISTINCT sub_id) as total_subs,
                SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) as churned_subs,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_subs,
                SUM(CASE WHEN status = 'Past Due' THEN 1 ELSE 0 END) as past_due_subs
            FROM cohorts
            GROUP BY cohort_month
        )
        SELECT 
            cohort_month,
            total_subs,
            churned_subs,
            active_subs,
            past_due_subs,
            ROUND(churned_subs::DECIMAL / NULLIF(total_subs, 0) * 100, 2) as churn_rate_pct,
            ROUND(active_subs::DECIMAL / NULLIF(total_subs, 0) * 100, 2) as retention_rate_pct
        FROM cohort_metrics
        ORDER BY cohort_month DESC
        LIMIT 24
        """

        return self.conn.execute(query).df()

    def payment_acceptance_rate_by_gateway(self, min_transactions: int = 100) -> pd.DataFrame:
        """
        Calculate payment acceptance rate by gateway and country.

        Acceptance Rate = (Successful Txs) / (Total Attempts)
        Filters out low-volume gateway/country pairs for statistical significance.

        Args:
            min_transactions: Minimum transaction count for inclusion

        Returns:
            DataFrame with columns: gateway, country, attempts, success, acceptance_rate
        """
        query = f"""
        WITH date_range AS (
            SELECT MAX(tx_date) - INTERVAL '90 days' as min_date
            FROM transactions
        ),
        gateway_stats AS (
            SELECT 
                gateway,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as successful_txs,
                SUM(CASE WHEN status = 'Soft Decline' THEN 1 ELSE 0 END) as soft_declines,
                SUM(CASE WHEN status = 'Hard Decline' THEN 1 ELSE 0 END) as hard_declines
            FROM transactions, date_range
            WHERE tx_date >= date_range.min_date
            GROUP BY gateway, country
            HAVING COUNT(*) >= {min_transactions}
        )
        SELECT 
            gateway,
            country,
            total_attempts,
            successful_txs,
            soft_declines,
            hard_declines,
            ROUND(successful_txs::DECIMAL / total_attempts * 100, 2) as acceptance_rate_pct,
            ROUND(soft_declines::DECIMAL / total_attempts * 100, 2) as soft_decline_rate_pct,
            ROUND(hard_declines::DECIMAL / total_attempts * 100, 2) as hard_decline_rate_pct
        FROM gateway_stats
        ORDER BY total_attempts DESC, acceptance_rate_pct ASC
        """

        return self.conn.execute(query).df()

    def revenue_reconciliation(self) -> pd.DataFrame:
        """
        Reconcile cash collected vs booked revenue.

        Cash Revenue = Sum of successful transaction amounts
        Booked Revenue = Sum of subscription MRR (active + past due)
        Variance = Cash - Booked (should be close to 0 for healthy business)

        Returns:
            DataFrame with monthly cash vs booked revenue reconciliation
        """
        query = """
        WITH combined_revenue AS (
            -- Cash transactions
            SELECT 
                DATE_TRUNC('month', tx_date) as month,
                SUM(amount) as cash_collected,
                0 as booked_revenue,
                COUNT(*) as successful_payments,
                COUNT(*) as total_attempts,
                0 as active_subscriptions
            FROM transactions
            WHERE status = 'Success'
            GROUP BY DATE_TRUNC('month', tx_date)
            
            UNION ALL
            
            -- Booked MRR
            SELECT 
                DATE_TRUNC('month', start_date) as month,
                0 as cash_collected,
                SUM(mrr_amount) as booked_revenue,
                0 as successful_payments,
                0 as total_attempts,
                COUNT(DISTINCT sub_id) as active_subscriptions
            FROM subscriptions
            WHERE status IN ('Active', 'Past Due')
            GROUP BY DATE_TRUNC('month', start_date)
        ),
        monthly_totals AS (
            SELECT 
                month,
                SUM(cash_collected) as cash_collected,
                SUM(booked_revenue) as booked_revenue,
                SUM(successful_payments) as successful_payments,
                SUM(total_attempts) as total_attempts,
                SUM(active_subscriptions) as active_subscriptions
            FROM combined_revenue
            GROUP BY month
        )
        SELECT 
            month,
            cash_collected,
            booked_revenue,
            cash_collected - booked_revenue as variance,
            ROUND((cash_collected - booked_revenue) / NULLIF(booked_revenue, 0) * 100, 2) as variance_pct,
            successful_payments,
            total_attempts,
            active_subscriptions
        FROM monthly_totals
        WHERE month IS NOT NULL
        ORDER BY month DESC
        LIMIT 12
        """

        return self.conn.execute(query).df()

    def detect_gateway_friction(self) -> pd.DataFrame:
        """
        Detect gateway friction patterns (specifically Germany + Apple Pay).

        Compares acceptance rates across gateway/country combinations to identify
        anomalies. Highlights combinations with significantly lower acceptance rates.

        Returns:
            DataFrame with gateway friction analysis and anomaly flags
        """
        query = """
        WITH date_range AS (
            SELECT MAX(tx_date) - INTERVAL '90 days' as min_date
            FROM transactions
        ),
        baseline_acceptance AS (
            SELECT 
                AVG(CASE WHEN status = 'Success' THEN 1.0 ELSE 0.0 END) as overall_acceptance_rate
            FROM transactions, date_range
            WHERE tx_date >= date_range.min_date
        ),
        gateway_country_stats AS (
            SELECT 
                gateway,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as attempts,
                SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as successes,
                ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) * 100, 2) as acceptance_rate,
                (
                    SELECT STRING_AGG(error_code, ', ')
                    FROM (
                        SELECT error_code, COUNT(*) as cnt
                        FROM transactions t2
                        WHERE t2.gateway = t1.gateway 
                            AND COALESCE(t2.country, 'Unknown') = COALESCE(t1.country, 'Unknown')
                            AND t2.status != 'Success'
                        GROUP BY error_code
                        ORDER BY cnt DESC
                        LIMIT 3
                    )
                ) as common_errors
            FROM transactions t1, date_range
            WHERE t1.tx_date >= date_range.min_date
            GROUP BY gateway, country
            HAVING COUNT(*) >= 50  -- Statistical significance
        )
        SELECT 
            g.gateway,
            g.country,
            g.attempts,
            g.successes,
            g.acceptance_rate as acceptance_rate_pct,
            ROUND(b.overall_acceptance_rate * 100, 2) as baseline_rate_pct,
            ROUND(g.acceptance_rate - (b.overall_acceptance_rate * 100), 2) as variance_from_baseline,
            g.common_errors,
            CASE 
                WHEN g.acceptance_rate < (b.overall_acceptance_rate * 100 - 10) THEN 'High Friction'
                WHEN g.acceptance_rate < (b.overall_acceptance_rate * 100 - 5) THEN 'Medium Friction'
                ELSE 'Low Friction'
            END as friction_flag
        FROM gateway_country_stats g, baseline_acceptance b
        ORDER BY variance_from_baseline ASC, attempts DESC
        """

        return self.conn.execute(query).df()

    def cohort_retention_analysis(self, cohort_months: int = 12) -> pd.DataFrame:
        """
        Calculate cohort retention over time for heatmap visualization.

        Shows month-over-month retention for each signup cohort.
        Essential for unit economics and LTV calculations.

        Args:
            cohort_months: Number of cohort months to analyze

        Returns:
            DataFrame with cohort_month, months_since_signup, retention_rate
        """
        query = f"""
        WITH cohort_base AS (
            SELECT 
                DATE_TRUNC('month', u.signup_date) as cohort_month,
                u.user_id,
                u.signup_date
            FROM users u
        ),
        cohort_sizes AS (
            SELECT 
                cohort_month,
                COUNT(DISTINCT user_id) as cohort_size
            FROM cohort_base
            GROUP BY cohort_month
        ),
        user_transaction_months AS (
            -- Get successful transactions with user_id from subscriptions
            SELECT DISTINCT
                DATE_TRUNC('month', t.tx_date) as transaction_month,
                s.user_id
            FROM transactions t
            JOIN subscriptions s ON t.sub_id = s.sub_id
            WHERE t.status = 'Success'
        ),
        retention_by_month AS (
            SELECT 
                cb.cohort_month,
                DATE_DIFF('month', cb.cohort_month, utm.transaction_month) as months_since_signup,
                COUNT(DISTINCT utm.user_id) as retained_users,
                cs.cohort_size
            FROM cohort_base cb
            JOIN cohort_sizes cs ON cb.cohort_month = cs.cohort_month
            LEFT JOIN user_transaction_months utm 
                ON cb.user_id = utm.user_id
                AND DATE_DIFF('month', cb.cohort_month, utm.transaction_month) BETWEEN 0 AND 12
            WHERE utm.transaction_month IS NOT NULL
            GROUP BY cb.cohort_month, DATE_DIFF('month', cb.cohort_month, utm.transaction_month), cs.cohort_size
        )
        SELECT 
            cohort_month,
            months_since_signup,
            retained_users,
            cohort_size,
            ROUND(retained_users::DECIMAL / NULLIF(cohort_size, 0) * 100, 1) as retention_rate_pct
        FROM retention_by_month
        WHERE cohort_month >= CURRENT_DATE - INTERVAL '{cohort_months} months'
        ORDER BY cohort_month, months_since_signup
        """

        return self.conn.execute(query).df()

    def executive_metrics(self) -> Dict[str, Any]:
        """
        Calculate high-level executive metrics for dashboard overview.

        Returns:
            Dictionary with MRR, active subs, NRR, and growth metrics
        """
        metrics = {}

        # Current MRR
        mrr_result = self.conn.execute("""
            SELECT 
                SUM(mrr_amount) as current_mrr,
                COUNT(DISTINCT sub_id) as active_subs
            FROM subscriptions
            WHERE status = 'Active'
        """).fetchone()
        metrics["mrr"] = float(mrr_result[0]) if mrr_result[0] else 0
        metrics["active_subscriptions"] = int(mrr_result[1]) if mrr_result[1] else 0

        # Payment success rate (last 30 days from most recent data)
        success_rate = self.conn.execute("""
            WITH date_range AS (
                SELECT MAX(tx_date) - INTERVAL '30 days' as min_date
                FROM transactions
            )
            SELECT 
                ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) * 100, 2) as success_rate
            FROM transactions, date_range
            WHERE tx_date >= date_range.min_date
        """).fetchone()
        metrics["payment_success_rate"] = float(success_rate[0]) if success_rate[0] is not None else 0

        # Total revenue (all time)
        total_revenue = self.conn.execute("""
            SELECT SUM(amount) as total_revenue
            FROM transactions
            WHERE status = 'Success'
        """).fetchone()
        metrics["total_revenue"] = float(total_revenue[0]) if total_revenue[0] is not None else 0

        # Churn rate (most recent complete month)
        churn_rate = self.conn.execute("""
            WITH latest_complete_month AS (
                SELECT DATE_TRUNC('month', MAX(tx_date)) - INTERVAL '1 month' as target_month
                FROM transactions
            ),
            month_start_subs AS (
                SELECT COUNT(*) as total_subs
                FROM subscriptions s, latest_complete_month m
                WHERE s.start_date <= m.target_month
                    AND s.status IN ('Active', 'Churned', 'Past Due')
            ),
            month_churned AS (
                SELECT COUNT(*) as churned
                FROM subscriptions s, latest_complete_month m
                WHERE s.status = 'Churned'
                    AND s.start_date <= m.target_month
            )
            SELECT 
                ROUND(c.churned::DECIMAL / NULLIF(t.total_subs, 0) * 100, 2) as churn_rate
            FROM month_churned c, month_start_subs t
        """).fetchone()
        metrics["churn_rate"] = float(churn_rate[0]) if churn_rate[0] is not None else 0

        # Average transaction value
        avg_tx_value = self.conn.execute("""
            SELECT ROUND(AVG(amount), 2) as avg_tx_value
            FROM transactions
            WHERE status = 'Success'
        """).fetchone()
        metrics["avg_transaction_value"] = float(avg_tx_value[0]) if avg_tx_value[0] else 0

        return metrics

    def get_sankey_data(self, country_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Generate data for Sankey diagram: Attempt → Gateway → Auth → Settlement.

        Args:
            country_filter: Optional country code to filter by

        Returns:
            DataFrame with source, target, value for Plotly Sankey
        """
        query = """
        WITH flow_data AS (
            SELECT 
                'Attempt' as source,
                gateway as target,
                COUNT(*) as value
            FROM transactions
            WHERE ? IS NULL OR country = ?
            GROUP BY gateway
            
            UNION ALL
            
            SELECT 
                gateway as source,
                CASE 
                    WHEN status = 'Success' THEN 'Authorized'
                    WHEN status = 'Soft Decline' THEN 'Soft Decline'
                    WHEN status = 'Hard Decline' THEN 'Hard Decline'
                END as target,
                COUNT(*) as value
            FROM transactions
            WHERE ? IS NULL OR country = ?
            GROUP BY gateway, status
            
            UNION ALL
            
            SELECT 
                'Authorized' as source,
                'Settled' as target,
                COUNT(*) as value
            FROM transactions
            WHERE status = 'Success' 
                AND (? IS NULL OR country = ?)
        )
        SELECT source, target, value
        FROM flow_data
        WHERE target IS NOT NULL
        ORDER BY value DESC
        """

        return self.conn.execute(query, [country_filter, country_filter, country_filter, country_filter, country_filter, country_filter]).df()

    def close(self) -> None:
        """Close DuckDB connection."""
        if self.conn:
            self.conn.close()
            print("🔌 DuckDB connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __del__(self):
        """Cleanup on garbage collection."""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception:
                pass  # Silently ignore cleanup errors


def validate_synthetic_patterns(analytics: PaymentAnalytics) -> None:
    """
    Validate that injected synthetic data patterns are detectable.

    Args:
        analytics: PaymentAnalytics instance with loaded data
    """
    print("=" * 70)
    print("🔍 PATTERN VALIDATION - Confirming Synthetic Data Anomalies")
    print("=" * 70)

    # Pattern 1: Germany + Apple Pay Friction
    print("\n📍 Pattern 1: Germany + Apple Pay Friction")
    print("-" * 70)
    friction = analytics.detect_gateway_friction()
    de_apple = friction[(friction["gateway"] == "Apple Pay") & (friction["country"] == "DE")]

    if not de_apple.empty:
        print(f"✓ Apple Pay (Germany): {de_apple.iloc[0]['acceptance_rate_pct']:.1f}% acceptance")
        print(f"  Baseline: {de_apple.iloc[0]['baseline_rate_pct']:.1f}%")
        print(f"  Variance: {de_apple.iloc[0]['variance_from_baseline']:.1f}%")
        print(f"  Flag: {de_apple.iloc[0]['friction_flag']}")

    # Pattern 2: Bitcoin Privacy
    print("\n📍 Pattern 2: Bitcoin Privacy & Error Patterns")
    print("-" * 70)
    btc_stats = analytics.conn.execute("""
        SELECT 
            COUNT(*) as total_btc_txs,
            SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) as null_country_count,
            SUM(CASE WHEN error_code = 'underpayment' THEN 1 ELSE 0 END) as underpayment_errors,
            ROUND(SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) * 100, 1) as null_pct
        FROM transactions
        WHERE gateway = 'Bitcoin'
    """).fetchone()

    print(f"✓ Bitcoin transactions: {btc_stats[0]:,}")
    print(f"  NULL countries: {btc_stats[1]:,} ({btc_stats[3]:.1f}%)")
    print(f"  Underpayment errors: {btc_stats[2]:,}")

    # Pattern 3: Black Friday Churn
    print("\n📍 Pattern 3: Black Friday Seasonality & Churn")
    print("-" * 70)
    churn_data = analytics.calculate_monthly_churn_rate()

    # Find November cohorts
    nov_cohorts = churn_data[churn_data["cohort_month"].astype(str).str.contains("-11-")]
    if not nov_cohorts.empty:
        avg_nov_churn = nov_cohorts["churn_rate_pct"].mean()
        overall_avg_churn = churn_data["churn_rate_pct"].mean()
        print(f"✓ November cohorts avg churn: {avg_nov_churn:.1f}%")
        print(f"  Overall avg churn: {overall_avg_churn:.1f}%")
        print(f"  Difference: {avg_nov_churn - overall_avg_churn:.1f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # This module is meant to be imported, but we can demo basic functionality
    print("PaymentAnalytics module loaded successfully!")
    print("Import this module in your scripts or Streamlit app.")
