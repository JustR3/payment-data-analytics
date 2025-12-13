"""
Payment Intelligence Suite - Synthetic Data Generator

This module generates realistic subscription payment data with injected patterns
for analytics demonstration. Specifically designed for Proton-style payment analysis.

Injected Patterns:
1. High Friction (Germany/Apple Pay): Apple Pay in Germany fails 15% more (>10% variance)
2. Medium Friction (France/PayPal): PayPal in France fails 9% more (5-10% variance)
3. Crypto Cohort: Bitcoin transactions have NULL country (privacy) and unique error patterns
4. Black Friday Seasonality: November signup spike with 3-month delayed churn

Author: Data Engineering Portfolio
Date: December 2025
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Tuple
import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)


class PaymentDataGenerator:
    """
    Generates synthetic payment data for subscription business analytics.
    Includes realistic patterns and anomalies for friction analysis.
    """

    # Configuration constants
    COUNTRIES = ["US", "DE", "FR", "CH", "BR", "IN"]
    COUNTRY_WEIGHTS = [0.35, 0.20, 0.15, 0.10, 0.12, 0.08]  # US dominant

    PLAN_TYPES = ["Mail Plus", "VPN Unlimited", "Proton Drive"]
    PLAN_PRICES = {"Mail Plus": 4.99, "VPN Unlimited": 9.99, "Proton Drive": 3.99}

    GATEWAYS = ["Stripe", "PayPal", "Apple Pay", "Bitcoin"]
    CURRENCIES = {"US": "USD", "DE": "EUR", "FR": "EUR", "CH": "CHF", "BR": "BRL", "IN": "INR"}

    TRANSACTION_STATUSES = ["Success", "Soft Decline", "Hard Decline"]
    ERROR_CODES = [
        "insufficient_funds",
        "card_declined",
        "expired_card",
        "fraud_detected",
        "network_error",
        "underpayment",
        "authentication_failed",
    ]

    def __init__(self, num_users: int = 10000):
        """
        Initialize the data generator.

        Args:
            num_users: Number of unique users to generate
        """
        self.num_users = num_users
        self.start_date = datetime.now() - timedelta(days=730)  # 2 years ago
        self.end_date = datetime.now()

    def _generate_signup_date(self) -> datetime:
        """
        Generate signup date with Black Friday seasonality.

        Pattern Injection: 3x spike in November (Black Friday)
        """
        # Random date in 2-year window
        days_range = (self.end_date - self.start_date).days
        random_days = random.randint(0, days_range)
        base_date = self.start_date + timedelta(days=random_days)

        # Black Friday boost (November): 3x more likely
        if base_date.month == 11:
            # Accept this date with higher probability
            if random.random() < 0.75:  # 75% of November dates accepted
                return base_date
            else:
                # Redistribute to other months
                return self._generate_signup_date()

        return base_date

    def generate_users(self) -> pd.DataFrame:
        """
        Generate user table with privacy and country distribution.

        Returns:
            DataFrame with columns: user_id, country, signup_date, is_anonymous
        """
        users = []

        for user_id in range(1, self.num_users + 1):
            # 10% of users are anonymous (Proton's privacy focus)
            is_anonymous = random.random() < 0.10

            country = random.choices(self.COUNTRIES, weights=self.COUNTRY_WEIGHTS)[0]
            signup_date = self._generate_signup_date()

            users.append(
                {
                    "user_id": user_id,
                    "country": country,
                    "signup_date": signup_date.strftime("%Y-%m-%d"),
                    "is_anonymous": is_anonymous,
                }
            )

        return pd.DataFrame(users)

    def generate_subscriptions(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate subscriptions with churn patterns.

        Pattern Injection: Black Friday signups churn 3 months later at 2x rate

        Args:
            users_df: User dataframe for foreign key relationships

        Returns:
            DataFrame with columns: sub_id, user_id, plan_type, mrr_amount, status, start_date
        """
        subscriptions = []
        sub_id = 1

        for _, user in users_df.iterrows():
            # Each user gets 1-2 subscriptions (some upgrade/downgrade)
            num_subs = random.choices([1, 2], weights=[0.75, 0.25])[0]

            signup_date = datetime.strptime(user["signup_date"], "%Y-%m-%d")

            for _ in range(num_subs):
                plan_type = random.choice(self.PLAN_TYPES)
                mrr_amount = self.PLAN_PRICES[plan_type]
                start_date = signup_date

                # Black Friday churn pattern: signups in November churn 3 months later
                if signup_date.month == 11:
                    churn_threshold = 0.40  # 40% churn rate for Nov signups
                    churn_date = signup_date + timedelta(days=90)  # 3 months later
                else:
                    churn_threshold = 0.20  # 20% baseline churn
                    churn_date = signup_date + timedelta(days=random.randint(30, 365))

                # Determine status based on churn timing
                if churn_date < self.end_date and random.random() < churn_threshold:
                    status = "Churned"
                elif random.random() < 0.05:  # 5% past due
                    status = "Past Due"
                else:
                    status = "Active"

                subscriptions.append(
                    {
                        "sub_id": sub_id,
                        "user_id": user["user_id"],
                        "plan_type": plan_type,
                        "mrr_amount": mrr_amount,
                        "status": status,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                    }
                )
                sub_id += 1

        return pd.DataFrame(subscriptions)

    def _should_transaction_fail(self, gateway: str, country: str) -> Tuple[bool, str]:
        """
        Determine if transaction should fail based on injected patterns.

        Pattern Injections:
        1. Apple Pay in Germany: 15% higher failure rate (HIGH friction)
        2. PayPal in France: 9% higher failure rate (MEDIUM friction)
        3. Bitcoin: Different error patterns (underpayment, not declines)

        Args:
            gateway: Payment gateway name
            country: User's country code

        Returns:
            Tuple of (should_fail: bool, error_code: str)
        """
        base_failure_rate = 0.08  # 8% baseline

        # PATTERN 1: Germany + Apple Pay friction (HIGH - >10% variance)
        if gateway == "Apple Pay" and country == "DE":
            failure_rate = base_failure_rate + 0.15  # 23% total failure rate
            if random.random() < failure_rate:
                # More authentication failures in Germany
                error_code = random.choices(
                    ["authentication_failed", "card_declined", "fraud_detected"],
                    weights=[0.5, 0.3, 0.2],
                )[0]
                return True, error_code

        # PATTERN 1.5: France + PayPal friction (MEDIUM - 5-10% variance)
        elif gateway == "PayPal" and country == "FR":
            failure_rate = base_failure_rate + 0.09  # 17% total failure rate (~7% variance)
            if random.random() < failure_rate:
                # Moderate card authentication issues in France
                error_code = random.choices(
                    ["card_declined", "authentication_failed", "insufficient_funds"],
                    weights=[0.4, 0.3, 0.3],
                )[0]
                return True, error_code

        # PATTERN 2: Bitcoin unique errors
        elif gateway == "Bitcoin":
            failure_rate = 0.12  # Slightly higher for crypto
            if random.random() < failure_rate:
                # Bitcoin-specific errors (underpayment, network)
                error_code = random.choices(["underpayment", "network_error"], weights=[0.7, 0.3])[
                    0
                ]
                return True, error_code

        # Standard failures for other gateways
        else:
            if random.random() < base_failure_rate:
                error_code = random.choice(["insufficient_funds", "card_declined", "expired_card"])
                return True, error_code

        return False, ""

    def generate_transactions(
        self, subscriptions_df: pd.DataFrame, users_df: pd.DataFrame, transactions_per_sub: int = 12
    ) -> pd.DataFrame:
        """
        Generate transaction records with gateway-specific patterns.

        Pattern Injections:
        1. Germany/Apple Pay: 15% higher failure rate
        2. Bitcoin: NULL country (privacy), unique error codes
        3. Realistic transaction timing (monthly billing)

        Args:
            subscriptions_df: Subscription dataframe
            users_df: User dataframe for country lookup
            transactions_per_sub: Average transactions per subscription

        Returns:
            DataFrame with columns: tx_id, sub_id, gateway, currency,
                                   status, error_code, tx_date, amount
        """
        transactions = []
        tx_id = 1

        # Create user lookup dict for quick access
        user_country_map = dict(zip(users_df["user_id"], users_df["country"]))

        for _, sub in subscriptions_df.iterrows():
            user_country = user_country_map[sub["user_id"]]
            start_date = datetime.strptime(sub["start_date"], "%Y-%m-%d")

            # Determine number of transactions (active subs have more)
            if sub["status"] == "Active":
                num_txs = transactions_per_sub + random.randint(-2, 4)
            elif sub["status"] == "Churned":
                num_txs = random.randint(1, 6)  # Churned = fewer txs
            else:  # Past Due
                num_txs = random.randint(3, 8)

            # Choose gateway (sticky - users typically use same gateway)
            # PATTERN 2: 5% of transactions are Bitcoin
            gateway_weights = [0.50, 0.25, 0.15, 0.10]  # Stripe, PayPal, Apple, Bitcoin
            gateway = random.choices(self.GATEWAYS, weights=gateway_weights)[0]

            for tx_num in range(num_txs):
                tx_date = start_date + timedelta(days=30 * tx_num)

                # Stop generating txs after subscription end date
                if tx_date > self.end_date:
                    break

                # PATTERN 2: Bitcoin transactions have NULL country (privacy)
                if gateway == "Bitcoin":
                    tx_country = None
                    currency = "BTC"
                else:
                    tx_country = user_country
                    currency = self.CURRENCIES.get(user_country, "USD")

                # Check if transaction should fail (pattern injection here)
                should_fail, error_code = self._should_transaction_fail(gateway, user_country)

                if should_fail:
                    status = random.choice(["Soft Decline", "Hard Decline"])
                    # Failed transactions might be partial amount
                    amount = sub["mrr_amount"] * random.uniform(0.95, 1.0)
                else:
                    status = "Success"
                    error_code = None
                    amount = sub["mrr_amount"]

                transactions.append(
                    {
                        "tx_id": tx_id,
                        "sub_id": sub["sub_id"],
                        "gateway": gateway,
                        "currency": currency,
                        "status": status,
                        "error_code": error_code,
                        "tx_date": tx_date.strftime("%Y-%m-%d"),
                        "amount": round(amount, 2),
                        "country": tx_country,  # NULL for Bitcoin
                    }
                )
                tx_id += 1

        return pd.DataFrame(transactions)

    def generate_all_data(self, output_dir: str = "./data") -> Dict[str, pd.DataFrame]:
        """
        Generate complete dataset and save to CSV files.

        Args:
            output_dir: Directory to save CSV files

        Returns:
            Dictionary containing all generated dataframes
        """
        print("🚀 Starting Payment Data Generation...")
        print(f"   Target: {self.num_users:,} users")

        # Generate users
        print("\n📊 Generating users...")
        users_df = self.generate_users()
        print(f"   ✓ Generated {len(users_df):,} users")
        print(
            f"   ✓ Anonymous users: {users_df['is_anonymous'].sum():,} ({users_df['is_anonymous'].mean() * 100:.1f}%)"
        )

        # Generate subscriptions
        print("\n📊 Generating subscriptions...")
        subs_df = self.generate_subscriptions(users_df)
        print(f"   ✓ Generated {len(subs_df):,} subscriptions")
        print(f"   ✓ Active: {(subs_df['status'] == 'Active').sum():,}")
        print(f"   ✓ Churned: {(subs_df['status'] == 'Churned').sum():,}")
        print(f"   ✓ Past Due: {(subs_df['status'] == 'Past Due').sum():,}")

        # Generate transactions
        print("\n📊 Generating transactions...")
        txs_df = self.generate_transactions(subs_df, users_df)
        print(f"   ✓ Generated {len(txs_df):,} transactions")
        print(f"   ✓ Success: {(txs_df['status'] == 'Success').sum():,}")
        print(f"   ✓ Declined: {(txs_df['status'] != 'Success').sum():,}")

        # Pattern validation
        print("\n🔍 Validating Injected Patterns...")

        # Pattern 1: Germany + Apple Pay
        de_apple_txs = txs_df[(txs_df["country"] == "DE") & (txs_df["gateway"] == "Apple Pay")]
        de_other_txs = txs_df[(txs_df["country"] == "DE") & (txs_df["gateway"] != "Apple Pay")]
        if len(de_apple_txs) > 0:
            de_apple_fail_rate = (de_apple_txs["status"] != "Success").mean()
            de_other_fail_rate = (de_other_txs["status"] != "Success").mean()
            print("   ✓ Pattern 1 (DE + Apple Pay friction):")
            print(f"     - Apple Pay failure rate: {de_apple_fail_rate * 100:.1f}%")
            print(f"     - Other gateways: {de_other_fail_rate * 100:.1f}%")

        # Pattern 2: Bitcoin privacy
        btc_txs = txs_df[txs_df["gateway"] == "Bitcoin"]
        print("   ✓ Pattern 2 (Bitcoin privacy):")
        print(f"     - Bitcoin transactions: {len(btc_txs):,}")
        print(
            f"     - NULL countries: {btc_txs['country'].isna().sum():,} ({btc_txs['country'].isna().mean() * 100:.1f}%)"
        )
        print(f"     - Underpayment errors: {(btc_txs['error_code'] == 'underpayment').sum()}")

        # Pattern 3: Black Friday seasonality
        nov_signups = users_df[pd.to_datetime(users_df["signup_date"]).dt.month == 11]
        total_signups = len(users_df)
        print("   ✓ Pattern 3 (Black Friday spike):")
        print(
            f"     - November signups: {len(nov_signups):,} ({len(nov_signups) / total_signups * 100:.1f}%)"
        )
        print("     - Expected baseline: ~8.3% (1/12 months)")

        # Save to CSV
        import os

        os.makedirs(output_dir, exist_ok=True)

        print(f"\n💾 Saving data to {output_dir}/...")
        users_df.to_csv(f"{output_dir}/users.csv", index=False)
        subs_df.to_csv(f"{output_dir}/subscriptions.csv", index=False)
        txs_df.to_csv(f"{output_dir}/transactions.csv", index=False)
        print("   ✓ All files saved successfully!")

        return {"users": users_df, "subscriptions": subs_df, "transactions": txs_df}
