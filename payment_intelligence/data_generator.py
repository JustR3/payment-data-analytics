import random
from pathlib import Path
import numpy as np
import pandas as pd
from faker import Faker

class PaymentDataGenerator:
    """Optimized data generator for faster generation on Streamlit Cloud."""
    
    def __init__(self, num_users: int = 500, seed: int = 42):
        """
        Initialize generator with reduced default size.
        
        Args:
            num_users: Number of users (default 500 for faster loading)
            seed: Random seed for reproducibility
        """
        self.num_users = num_users
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # Reduced probability distributions for faster generation
        self.gateways = ['Stripe', 'PayPal', 'Apple Pay']  # Reduced from 4
        self.gateway_weights = [0.5, 0.3, 0.2]
        
        self.countries = ['US', 'UK', 'DE', 'FR', 'CA']  # Reduced from more
        self.country_weights = [0.4, 0.2, 0.15, 0.15, 0.1]
        
        # Optimized status distribution
        self.statuses = ['success', 'soft_decline', 'hard_decline']
        self.status_weights = [0.85, 0.10, 0.05]

    def generate_users(self) -> pd.DataFrame:
        """Generate users with vectorized operations."""
        # Vectorized generation for speed
        user_ids = np.arange(1, self.num_users + 1)
        countries = np.random.choice(
            self.countries, 
            size=self.num_users, 
            p=self.country_weights
        )
        
        # Batch date generation
        days_ago = np.random.randint(30, 730, size=self.num_users)
        signup_dates = pd.Timestamp.now() - pd.to_timedelta(days_ago, unit='D')
        
        # Random anonymous flag (10% anonymous)
        is_anonymous = np.random.choice([True, False], size=self.num_users, p=[0.1, 0.9])
        
        return pd.DataFrame({
            'user_id': user_ids,
            'country': countries,
            'signup_date': signup_dates,
            'is_anonymous': is_anonymous,
        })

    def generate_subscriptions(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """Generate subscriptions with optimized probability."""
        # 70% of users have subscriptions (reduced complexity)
        active_users = users_df.sample(frac=0.7, random_state=self.seed)
        
        subscription_ids = np.arange(1, len(active_users) + 1)
        
        # Vectorized status assignment (85% Active, 15% Cancelled) - match CSV casing
        statuses = np.random.choice(
            ['Active', 'Cancelled'],
            size=len(active_users),
            p=[0.85, 0.15]
        )
        
        # Fixed price tiers for MRR
        mrr_amounts = np.random.choice([3.99, 9.99, 19.99], size=len(active_users))
        
        # Plan types matching Proton
        plan_types = np.random.choice(
            ['Proton Drive', 'Proton Mail', 'Proton VPN', 'Proton Bundle'],
            size=len(active_users),
            p=[0.25, 0.35, 0.25, 0.15]
        )
        
        df = pd.DataFrame({
            'sub_id': subscription_ids,
            'user_id': active_users['user_id'].values,
            'plan_type': plan_types,
            'mrr_amount': mrr_amounts,
            'status': statuses,
            'start_date': active_users['signup_date'].values,
        })
        
        return df

    def generate_transactions(self, subscriptions_df: pd.DataFrame) -> pd.DataFrame:
        """Generate transactions with optimized batch processing."""
        transactions = []
        
        # Average 3 transactions per subscription (reduced from higher)
        for _, sub in subscriptions_df.iterrows():
            num_txs = np.random.randint(1, 6)
            
            for i in range(num_txs):
                # Vectorized transaction generation
                days_offset = 30 * i + np.random.randint(0, 10)
                tx_date = sub['start_date'] + pd.Timedelta(days=days_offset)
                
                # Skip if subscription is cancelled and tx is after start
                if sub['status'] == 'Cancelled' and i > 2:
                    break
                
                # Match CSV casing for status
                status_choice = np.random.choice(self.statuses, p=self.status_weights)
                status_formatted = status_choice.replace('_', ' ').title()  # 'success' -> 'Success'
                
                transactions.append({
                    'tx_id': len(transactions) + 1,
                    'sub_id': sub['sub_id'],
                    'gateway': np.random.choice(self.gateways, p=self.gateway_weights),
                    'currency': 'USD',
                    'status': status_formatted if status_choice == 'success' else status_choice.replace('_', ' ').title(),
                    'error_code': '' if status_choice == 'success' else f'ERR_{np.random.randint(100, 999)}',
                    'tx_date': tx_date,
                    'amount': sub['mrr_amount'],
                    'country': np.random.choice(self.countries, p=self.country_weights),
                })
        
        return pd.DataFrame(transactions)

    def generate_all_data(self, output_dir: str = "./data"):
        """Generate all data files with progress tracking."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate with progress indication
        users_df = self.generate_users()
        users_df.to_csv(output_path / "users.csv", index=False)
        
        subscriptions_df = self.generate_subscriptions(users_df)
        subscriptions_df.to_csv(output_path / "subscriptions.csv", index=False)
        
        transactions_df = self.generate_transactions(subscriptions_df)
        transactions_df.to_csv(output_path / "transactions.csv", index=False)
        
        return len(users_df), len(subscriptions_df), len(transactions_df)
