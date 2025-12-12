#!/usr/bin/env python
"""
Script to generate synthetic payment data.
Run with: uv run python scripts/generate_data.py
"""

from payment_intelligence.data_generator import PaymentDataGenerator


def main():
    """Main execution function."""
    # Generate dataset with 15,000 users (will produce ~35k-40k transactions)
    generator = PaymentDataGenerator(num_users=15000)
    data = generator.generate_all_data(output_dir='./data')
    
    print("\n" + "="*60)
    print("✨ Data generation complete!")
    print("="*60)
    print(f"📁 Files created:")
    print(f"   - data/users.csv ({len(data['users']):,} rows)")
    print(f"   - data/subscriptions.csv ({len(data['subscriptions']):,} rows)")
    print(f"   - data/transactions.csv ({len(data['transactions']):,} rows)")
    print("\n🎯 Next steps:")
    print("   1. Run: uv run python scripts/etl_logic.py (to validate patterns with SQL)")
    print("   2. Run: uv run streamlit run app.py (to launch dashboard)")


if __name__ == '__main__':
    main()
