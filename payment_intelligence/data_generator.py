# ...existing imports...

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
        created_dates = pd.Timestamp.now() - pd.to_timedelta(days_ago, unit='D')
        
        return pd.DataFrame({
            'user_id': user_ids,
            'country': countries,
            'created_at': created_dates,
        })

    def generate_subscriptions(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """Generate subscriptions with optimized probability."""
        # 70% of users have subscriptions (reduced complexity)
        active_users = users_df.sample(frac=0.7, random_state=self.seed)
        
        subscription_ids = np.arange(1, len(active_users) + 1)
        
        # Vectorized status assignment (85% active, 15% cancelled)
        statuses = np.random.choice(
            ['active', 'cancelled'],
            size=len(active_users),
            p=[0.85, 0.15]
        )
        
        # Fixed price tiers for simplicity
        prices = np.random.choice([9.99, 19.99, 49.99], size=len(active_users))
        
        df = pd.DataFrame({
            'subscription_id': subscription_ids,
            'user_id': active_users['user_id'].values,
            'status': statuses,
            'price': prices,
            'created_at': active_users['created_at'].values,
        })
        
        # Add cancellation dates for cancelled subs
        df['cancelled_at'] = None
        cancelled_mask = df['status'] == 'cancelled'
        df.loc[cancelled_mask, 'cancelled_at'] = df.loc[cancelled_mask, 'created_at'] + \
            pd.to_timedelta(np.random.randint(30, 365, size=cancelled_mask.sum()), unit='D')
        
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
                tx_date = sub['created_at'] + pd.Timedelta(days=days_offset)
                
                # Skip if after cancellation
                if sub['cancelled_at'] and tx_date > sub['cancelled_at']:
                    break
                
                transactions.append({
                    'transaction_id': len(transactions) + 1,
                    'subscription_id': sub['subscription_id'],
                    'amount': sub['price'],
                    'gateway': np.random.choice(self.gateways, p=self.gateway_weights),
                    'status': np.random.choice(self.statuses, p=self.status_weights),
                    'transaction_date': tx_date,
                    'country': np.random.choice(self.countries, p=self.country_weights),
                    'error_code': None if np.random.random() > 0.15 else f'ERR_{np.random.randint(100, 999)}',
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
