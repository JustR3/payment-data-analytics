#!/usr/bin/env python
"""
Script to run DuckDB analytics and validate synthetic data patterns.
Run with: uv run python scripts/run_analysis.py
"""

from payment_intelligence.etl_logic import PaymentAnalytics, validate_synthetic_patterns
import sys


def main():
    """Execute analytics validation."""
    print("🚀 Payment Intelligence Analytics Engine")
    print("=" * 70)
    print()
    
    try:
        # Initialize analytics with context manager
        with PaymentAnalytics(data_dir='./data') as analytics:
            # Load data into DuckDB
            analytics.load_data()
            
            # Validate synthetic patterns
            validate_synthetic_patterns(analytics)
            
            # Execute key analytics
            print("\n📊 EXECUTIVE METRICS")
            print("=" * 70)
            metrics = analytics.executive_metrics()
            print(f"💰 Current MRR: ${metrics['mrr']:,.2f}")
            print(f"👥 Active Subscriptions: {metrics['active_subscriptions']:,}")
            print(f"✅ Payment Success Rate: {metrics['payment_success_rate']:.1f}%")
            print(f"📈 Total Revenue (All Time): ${metrics['total_revenue']:,.2f}")
            print(f"📉 Current Churn Rate: {metrics['churn_rate']:.1f}%")
            print(f"💵 Avg Transaction Value: ${metrics['avg_transaction_value']:.2f}")
            
            # Show monthly churn analysis
            print("\n📊 MONTHLY CHURN ANALYSIS (Last 12 Months)")
            print("=" * 70)
            churn_df = analytics.calculate_monthly_churn_rate()
            print(churn_df.head(12).to_string(index=False))
            
            # Show gateway acceptance rates
            print("\n📊 GATEWAY ACCEPTANCE RATES")
            print("=" * 70)
            acceptance_df = analytics.payment_acceptance_rate_by_gateway(min_transactions=50)
            print(acceptance_df.head(15).to_string(index=False))
            
            # Show revenue reconciliation
            print("\n📊 REVENUE RECONCILIATION (Cash vs Booked)")
            print("=" * 70)
            recon_df = analytics.revenue_reconciliation()
            print(recon_df.head(6).to_string(index=False))
            
            # Show gateway friction detection
            print("\n📊 GATEWAY FRICTION DETECTION")
            print("=" * 70)
            friction_df = analytics.detect_gateway_friction()
            # Show only problematic gateways
            problematic = friction_df[friction_df['friction_flag'] != '🟢 Normal']
            if not problematic.empty:
                print(problematic.to_string(index=False))
            else:
                print("✓ No significant friction detected")
                print("\nTop performers:")
                print(friction_df.head(5).to_string(index=False))
            
            print("\n" + "=" * 70)
            print("✨ Analysis complete!")
            print("=" * 70)
            print("\n🎯 Next steps:")
            print("   Run: uv run streamlit run app.py (to launch dashboard)")
            
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Please run data generation first:")
        print("   uv run python scripts/generate_data.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
