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
        self.conn.execute("CREATE INDEX idx_users_country ON users(country)")
        self.conn.execute("CREATE INDEX idx_subs_status ON subscriptions(status)")
        self.conn.execute("CREATE INDEX idx_txs_gateway ON transactions(gateway)")
        self.conn.execute("CREATE INDEX idx_txs_date ON transactions(tx_date)")

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
        WITH gateway_stats AS (
            SELECT 
                gateway,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as successful_txs,
                SUM(CASE WHEN status = 'Soft Decline' THEN 1 ELSE 0 END) as soft_declines,
                SUM(CASE WHEN status = 'Hard Decline' THEN 1 ELSE 0 END) as hard_declines
            FROM transactions
            WHERE tx_date >= CURRENT_DATE - INTERVAL '90 days'
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
        WITH monthly_cash AS (
            SELECT 
                DATE_TRUNC('month', tx_date) as month,
                SUM(CASE WHEN status = 'Success' THEN amount ELSE 0 END) as cash_collected,
                COUNT(CASE WHEN status = 'Success' THEN 1 END) as successful_payments,
                COUNT(*) as total_attempts
            FROM transactions
            GROUP BY DATE_TRUNC('month', tx_date)
        ),
        monthly_booked AS (
            SELECT 
                DATE_TRUNC('month', s.start_date) as month,
                SUM(s.mrr_amount) as booked_revenue,
                COUNT(DISTINCT s.sub_id) as active_subscriptions
            FROM subscriptions s
            WHERE s.status IN ('Active', 'Past Due')
            GROUP BY DATE_TRUNC('month', s.start_date)
        )
        SELECT 
            COALESCE(c.month, b.month) as month,
            COALESCE(c.cash_collected, 0) as cash_collected,
            COALESCE(b.booked_revenue, 0) as booked_revenue,
            COALESCE(c.cash_collected, 0) - COALESCE(b.booked_revenue, 0) as variance,
            ROUND((COALESCE(c.cash_collected, 0) - COALESCE(b.booked_revenue, 0)) / 
                  NULLIF(COALESCE(b.booked_revenue, 0), 0) * 100, 2) as variance_pct,
            COALESCE(c.successful_payments, 0) as successful_payments,
            COALESCE(c.total_attempts, 0) as total_attempts,
            COALESCE(b.active_subscriptions, 0) as active_subscriptions
        FROM monthly_cash c
        FULL OUTER JOIN monthly_booked b ON c.month = b.month
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
        WITH baseline_acceptance AS (
            SELECT 
                AVG(CASE WHEN status = 'Success' THEN 1.0 ELSE 0.0 END) as overall_acceptance_rate
            FROM transactions
        ),
        gateway_country_stats AS (
            SELECT 
                gateway,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as attempts,
                SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) as successes,
                ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) * 100, 2) as acceptance_rate,
                STRING_AGG(DISTINCT error_code, ', ') as common_errors
            FROM transactions
            WHERE tx_date >= CURRENT_DATE - INTERVAL '90 days'
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
                WHEN g.acceptance_rate < (b.overall_acceptance_rate * 100 - 10) THEN '🔴 High Friction'
                WHEN g.acceptance_rate < (b.overall_acceptance_rate * 100 - 5) THEN '🟡 Medium Friction'
                ELSE '🟢 Normal'
            END as friction_flag
        FROM gateway_country_stats g
        CROSS JOIN baseline_acceptance b
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
        WITH cohorts AS (
            SELECT 
                DATE_TRUNC('month', u.signup_date) as cohort_month,
                u.user_id,
                s.sub_id,
                s.status,
                DATE_DIFF('month', u.signup_date, CURRENT_DATE) as months_since_signup
            FROM users u
            JOIN subscriptions s ON u.user_id = s.user_id
        ),
        cohort_sizes AS (
            SELECT 
                cohort_month,
                COUNT(DISTINCT user_id) as cohort_size
            FROM cohorts
            GROUP BY cohort_month
        ),
        retention_by_month AS (
            SELECT 
                c.cohort_month,
                c.months_since_signup,
                COUNT(DISTINCT CASE WHEN c.status = 'Active' THEN c.user_id END) as retained_users,
                cs.cohort_size
            FROM cohorts c
            JOIN cohort_sizes cs ON c.cohort_month = cs.cohort_month
            WHERE c.months_since_signup <= 12
            GROUP BY c.cohort_month, c.months_since_signup, cs.cohort_size
        )
        SELECT 
            cohort_month,
            months_since_signup,
            retained_users,
            cohort_size,
            ROUND(retained_users::DECIMAL / cohort_size * 100, 1) as retention_rate_pct
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

        # Payment success rate (last 30 days)
        success_rate = self.conn.execute("""
            SELECT 
                ROUND(SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) * 100, 2) as success_rate
            FROM transactions
            WHERE tx_date >= CURRENT_DATE - INTERVAL '30 days'
        """).fetchone()
        metrics["payment_success_rate"] = float(success_rate[0]) if success_rate[0] else 0

        # Total revenue (all time)
        total_revenue = self.conn.execute("""
            SELECT SUM(amount) as total_revenue
            FROM transactions
            WHERE status = 'Success'
        """).fetchone()
        metrics["total_revenue"] = float(total_revenue[0]) if total_revenue[0] else 0

        # Churn rate (current month)
        churn_rate = self.conn.execute("""
            WITH current_month_cohort AS (
                SELECT COUNT(*) as total_subs
                FROM subscriptions
                WHERE DATE_TRUNC('month', start_date) = DATE_TRUNC('month', CURRENT_DATE)
            ),
            churned_this_month AS (
                SELECT COUNT(*) as churned
                FROM subscriptions
                WHERE status = 'Churned'
                AND DATE_TRUNC('month', start_date) = DATE_TRUNC('month', CURRENT_DATE)
            )
            SELECT 
                ROUND(c.churned::DECIMAL / NULLIF(t.total_subs, 0) * 100, 2) as churn_rate
            FROM churned_this_month c, current_month_cohort t
        """).fetchone()
        metrics["churn_rate"] = float(churn_rate[0]) if churn_rate[0] and churn_rate[0] else 0

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
        # Build WHERE clauses conditionally
        if country_filter:
            where_country = f"WHERE country = '{country_filter}'"
            and_country = f"AND country = '{country_filter}'"
        else:
            where_country = ""
            and_country = ""

        query = f"""
        WITH flow_data AS (
            SELECT 
                'Attempt' as source,
                gateway as target,
                COUNT(*) as value
            FROM transactions
            {where_country}
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
            {where_country}
            GROUP BY gateway, status
            
            UNION ALL
            
            SELECT 
                'Authorized' as source,
                'Settled' as target,
                COUNT(*) as value
            FROM transactions
            WHERE status = 'Success' {and_country}
        )
        SELECT source, target, value
        FROM flow_data
        WHERE target IS NOT NULL
        ORDER BY value DESC
        """

        return self.conn.execute(query).df()

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
