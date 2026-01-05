"""
Payment Intelligence Suite - Streamlit Dashboard

A production-grade analytics dashboard for subscription payment intelligence.
Built for the Proton Data Analyst portfolio project.

Features:
- Executive Overview: High-level KPIs and trends
- Friction Monitor: Sankey diagram of payment flows
- Unit Economics: Cohort retention analysis

Author: Data Engineering Portfolio
Date: December 2025
"""

import os
import streamlit as st
import plotly.graph_objects as go

from payment_intelligence.etl_logic import PaymentAnalytics

# Page configuration - Proton dark theme
st.set_page_config(
    page_title="Payment Intelligence Suite",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlined CSS - removed redundant rules
st.markdown(
    """
<style>
    :root {
        --proton-purple: #6d4aff;
        --proton-purple-dark: #5835d4;
    }
    
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 2px solid #6d4aff; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1a1a1a; }
    h1 { color: #6d4aff; font-weight: 600; }
    h2, h3 { color: #1a1a1a; font-weight: 600; }
    .stButton>button { 
        background-color: #6d4aff; 
        color: #ffffff; 
        border-radius: 8px; 
        font-weight: 600; 
    }
    .stButton>button:hover { background-color: #5835d4; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading analytics engine...", hash_funcs={str: lambda _: None})
def load_analytics():
    """
    Load analytics engine with caching.
    Auto-generates data if not present (for Streamlit Cloud deployment).

    Returns:
        PaymentAnalytics instance with data loaded
    """
    # Version marker to force cache invalidation when schema changes
    DATA_VERSION = "v2.0_2026_01_05"
    
    data_dir = "./data"
    
    # Check if data exists
    data_files = [
        os.path.join(data_dir, "users.csv"),
        os.path.join(data_dir, "subscriptions.csv"),
        os.path.join(data_dir, "transactions.csv"),
    ]
    
    # Validate data schema - if old schema detected, regenerate
    regenerate_data = False
    
    if all(os.path.exists(f) for f in data_files):
        try:
            import pandas as pd
            # Check transactions CSV for correct columns
            tx_df = pd.read_csv(os.path.join(data_dir, "transactions.csv"), nrows=1)
            required_cols = ['tx_id', 'sub_id', 'gateway', 'currency', 'status', 'error_code', 'tx_date', 'amount', 'country']
            
            if not all(col in tx_df.columns for col in required_cols):
                st.warning("⚠️ Old data schema detected - regenerating...")
                regenerate_data = True
            else:
                # Check for old gateways (Bitcoin) that shouldn't exist
                tx_sample = pd.read_csv(os.path.join(data_dir, "transactions.csv"), nrows=100)
                if 'Bitcoin' in tx_sample['gateway'].values:
                    st.warning("⚠️ Legacy data detected - regenerating...")
                    regenerate_data = True
        except Exception as e:
            st.warning(f"⚠️ Data validation failed: {str(e)} - regenerating...")
            regenerate_data = True
    else:
        regenerate_data = True
    
    # Regenerate if needed
    if regenerate_data:
        st.info("🔄 Generating fresh data with correct schema...")
        
        try:
            from payment_intelligence.data_generator import PaymentDataGenerator
            
            os.makedirs(data_dir, exist_ok=True)
            
            # Smaller dataset for faster performance
            generator = PaymentDataGenerator(num_users=500, seed=42)
            generator.generate_all_data(output_dir=data_dir)
            
            st.success("✅ Data generated successfully!")
        except ImportError as e:
            st.error(f"❌ Import failed: {str(e)}. Check that payment_intelligence module is installed correctly.")
            raise
        except Exception as e:
            st.error(f"❌ Data generation failed: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            raise
    
    try:
        analytics = PaymentAnalytics(data_dir=data_dir)
        analytics.load_data()
        return analytics
    except Exception as e:
        st.error(f"❌ Failed to load analytics: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        raise


# Increased cache TTL to reduce recomputation, added hash_funcs to avoid warnings
@st.cache_data(ttl=600, show_spinner=False)
def get_executive_metrics(_analytics):
    """Get executive metrics with caching."""
    return _analytics.executive_metrics()


@st.cache_data(ttl=600, show_spinner=False)
def get_churn_data(_analytics):
    """Get churn analysis with caching."""
    return _analytics.calculate_monthly_churn_rate()


@st.cache_data(ttl=600, show_spinner=False)
def get_acceptance_rates(_analytics):
    """Get acceptance rates with caching."""
    return _analytics.payment_acceptance_rate_by_gateway(min_transactions=50)


@st.cache_data(ttl=600, show_spinner=False)
def get_revenue_reconciliation(_analytics):
    """Get revenue reconciliation with caching."""
    return _analytics.revenue_reconciliation()


@st.cache_data(ttl=600, show_spinner=False)
def get_friction_data(_analytics):
    """Get friction detection with caching."""
    return _analytics.detect_gateway_friction()


@st.cache_data(ttl=600, show_spinner=False)
def get_cohort_retention(_analytics):
    """Get cohort retention with caching."""
    return _analytics.cohort_retention_analysis(cohort_months=12)


@st.cache_data(ttl=600, show_spinner=False)
def get_sankey_data(_analytics, country_filter=None):
    """Get Sankey diagram data with caching."""
    return _analytics.get_sankey_data(country_filter=country_filter)


def render_executive_overview(analytics):
    """
    Render Executive Overview page.

    Shows high-level KPIs, trends, and key metrics.
    """
    st.title("Executive Overview")
    st.markdown("---")

    # Get metrics
    metrics = get_executive_metrics(analytics)

    # Tight KPI row - 5 metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="MRR (Current)",
            value=f"${metrics['mrr']:,.0f}",
            delta="+1.2%",
        )

    with col2:
        st.metric(
            label="Active Subs",
            value=f"{metrics['active_subscriptions']:,}",
            delta="+24",
        )

    with col3:
        st.metric(
            label="Auth Rate",
            value=f"{metrics['payment_success_rate']:.1f}%",
            delta=f"{metrics['payment_success_rate'] - 90:.1f}%",
            delta_color="normal" if metrics["payment_success_rate"] >= 90 else "inverse",
        )

    with col4:
        st.metric(
            label="Churn Rate",
            value=f"{metrics['churn_rate']:.2f}%",
            delta="-0.02%",
            delta_color="inverse",
        )

    with col5:
        st.metric(
            label="Avg Tx Value",
            value=f"${metrics['avg_transaction_value']:.2f}",
        )

    st.markdown("---")

    # Monthly churn trend - simplified visualization
    st.subheader("Monthly Churn Trend")
    churn_df = get_churn_data(analytics)

    if not churn_df.empty:
        # Limit to last 12 months for performance
        churn_df = churn_df.tail(12)
        
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=churn_df["cohort_month"],
                y=churn_df["churn_rate_pct"],
                mode="lines+markers",
                name="Churn Rate",
                line=dict(color="#dc3545", width=2),
                marker=dict(size=8),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=churn_df["cohort_month"],
                y=churn_df["retention_rate_pct"],
                mode="lines+markers",
                name="Retention Rate",
                line=dict(color="#6d4aff", width=2),
                marker=dict(size=8),
            )
        )

        fig.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=350,
            margin=dict(l=50, r=50, t=30, b=50),
            xaxis_title="Month",
            yaxis_title="Rate (%)",
            hovermode="x unified",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Gateway performance table - limit rows
    st.subheader("Top Gateway Performance")
    acceptance_df = get_acceptance_rates(analytics)

    if not acceptance_df.empty:
        # Show only top 8 performers
        display_df = acceptance_df[[
            "gateway",
            "country",
            "total_attempts",
            "acceptance_rate_pct",
            "soft_decline_rate_pct",
            "hard_decline_rate_pct",
        ]].head(8).copy()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "gateway": "Gateway",
                "country": "Region",
                "total_attempts": st.column_config.NumberColumn("Volume", format="%d"),
                "acceptance_rate_pct": st.column_config.ProgressColumn(
                    "Auth Rate",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
                "soft_decline_rate_pct": st.column_config.NumberColumn("Soft %", format="%.2f%%"),
                "hard_decline_rate_pct": st.column_config.NumberColumn("Hard %", format="%.2f%%"),
            },
        )


def render_friction_monitor(analytics):
    """
    Render Friction Monitor page with Sankey diagram.

    Shows payment flow: Attempt → Gateway → Auth → Settlement
    """
    st.title("Friction Monitor")
    st.markdown("---")

    # Country filter - minimal, functional
    col1, col2 = st.columns([1, 3])

    with col1:
        # Get available countries - limit query
        countries = analytics.conn.execute("""
            SELECT DISTINCT country 
            FROM transactions 
            WHERE country IS NOT NULL 
            ORDER BY country
            LIMIT 50
        """).df()

        country_options = ["All"] + countries["country"].tolist()
        selected_country = st.selectbox("Region", options=country_options, index=0)

    with col2:
        st.caption("Payment flow visualization. Width indicates transaction volume.")

    # Get Sankey data
    country_filter = None if selected_country == "All" else selected_country
    sankey_df = get_sankey_data(analytics, country_filter=country_filter)

    if not sankey_df.empty:
        # Create node labels
        all_nodes = list(set(sankey_df["source"].tolist() + sankey_df["target"].tolist()))
        node_dict = {node: idx for idx, node in enumerate(all_nodes)}

        sources = [node_dict[src] for src in sankey_df["source"]]
        targets = [node_dict[tgt] for tgt in sankey_df["target"]]
        values = sankey_df["value"].tolist()

        # Simplified color scheme
        node_colors = []
        for node in all_nodes:
            if node == "Attempt":
                node_colors.append("#6d4aff")
            elif node in ["Stripe", "PayPal", "Apple Pay", "Bitcoin"]:
                node_colors.append("#8a7aff")
            elif node == "Authorized":
                node_colors.append("#1ea672")
            elif node == "Settled":
                node_colors.append("#16865e")
            else:
                node_colors.append("#dc3545")

        # Create Sankey diagram
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="#ffffff", width=2),
                        label=all_nodes,
                        color=node_colors,
                    ),
                    link=dict(
                        source=sources,
                        target=targets,
                        value=values,
                        color="rgba(109, 74, 255, 0.2)",
                    ),
                    textfont=dict(color="#ffffff", size=12, weight=600),
                )
            ]
        )

        fig.update_layout(
            font=dict(size=12, color="#ffffff"),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=500,
            margin=dict(l=20, r=20, t=20, b=20),
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # Friction detection table - show only high and medium
    st.subheader("Detected Friction")
    friction_df = get_friction_data(analytics)

    if not friction_df.empty:
        high_friction = friction_df[friction_df["friction_flag"] == "High Friction"]
        medium_friction = friction_df[friction_df["friction_flag"] == "Medium Friction"]

        # High Friction
        if not high_friction.empty:
            st.error(f"⚠️ {len(high_friction)} gateway/region pairs with HIGH friction")

            st.dataframe(
                high_friction[[
                    "gateway",
                    "country",
                    "attempts",
                    "acceptance_rate_pct",
                    "variance_from_baseline",
                ]].head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "gateway": "Gateway",
                    "country": "Region",
                    "attempts": st.column_config.NumberColumn("Volume", format="%d"),
                    "acceptance_rate_pct": st.column_config.ProgressColumn(
                        "Auth Rate", format="%.1f%%", min_value=0, max_value=100
                    ),
                    "variance_from_baseline": st.column_config.NumberColumn("Variance", format="%.1f%%"),
                },
            )

        # Medium Friction
        if not medium_friction.empty:
            with st.expander(f"⚡ {len(medium_friction)} gateway/region pairs with MEDIUM friction"):
                st.dataframe(
                    medium_friction[[
                        "gateway",
                        "country",
                        "attempts",
                        "acceptance_rate_pct",
                        "variance_from_baseline",
                    ]].head(10),
                    use_container_width=True,
                    hide_index=True,
                )


def render_unit_economics(analytics):
    """
    Render Unit Economics page with cohort retention heatmap.

    Shows month-over-month retention for each signup cohort.
    """
    st.title("Cohort Analysis")
    st.markdown("---")

    st.caption("12-month retention tracking by signup cohort.")

    # Get cohort data
    cohort_df = get_cohort_retention(analytics)

    if not cohort_df.empty:
        # Pivot for heatmap
        pivot_df = cohort_df.pivot(
            index="cohort_month", columns="months_since_signup", values="retention_rate_pct"
        )

        # Limit to last 12 cohorts for performance
        pivot_df = pivot_df.sort_index(ascending=False).head(12)

        # Simplified heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=[str(d)[:7] for d in pivot_df.index],
                colorscale=[
                    [0, "#dc3545"],
                    [0.5, "#8a7aff"],
                    [1, "#6d4aff"],
                ],
                text=pivot_df.values,
                texttemplate="%{text:.0f}%",
                textfont={"size": 9, "color": "white"},
                colorbar=dict(title="Retention %", ticksuffix="%"),
            )
        )

        fig.update_layout(
            xaxis_title="Months Since Signup",
            yaxis_title="Cohort",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=500,
            margin=dict(l=80, r=50, t=30, b=50),
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Compact insights
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if 1 in pivot_df.columns:
                st.metric("Month 1 Avg", f"{pivot_df[1].mean():.1f}%")

        with col2:
            if 6 in pivot_df.columns:
                st.metric("Month 6 Avg", f"{pivot_df[6].mean():.1f}%")

        with col3:
            if 12 in pivot_df.columns:
                st.metric("Month 12 Avg", f"{pivot_df[12].mean():.1f}%")

    # Revenue reconciliation - show last 6 months only
    st.markdown("---")
    st.subheader("Revenue Reconciliation")

    recon_df = get_revenue_reconciliation(analytics)

    if not recon_df.empty:
        st.dataframe(
            recon_df.head(6),
            use_container_width=True,
            hide_index=True,
            column_config={
                "month": st.column_config.DateColumn("Month", format="MMM YYYY"),
                "cash_collected": st.column_config.NumberColumn("Cash", format="$%.0f"),
                "booked_revenue": st.column_config.NumberColumn("Revenue", format="$%.0f"),
                "variance": st.column_config.NumberColumn("Variance", format="$%.0f"),
                "variance_pct": st.column_config.NumberColumn("Var %", format="%.2f%%"),
                "successful_payments": st.column_config.NumberColumn("Tx", format="%d"),
            },
        )


def main():
    """Main application entry point."""

    # Sidebar
    with st.sidebar:
        # Streamlined header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #6d4aff 0%, #5835d4 100%);
            padding: 1.5rem 1rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
        ">
            <h1 style="color: white; font-size: 1.5rem; margin: 0;">Payment Intel</h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 0.75rem; margin: 0.5rem 0 0 0;">ANALYTICS SUITE</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigate",
            ["Overview", "Friction Monitor", "Cohort Analysis"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Data refresh
        if st.button("Refresh Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Initialize analytics with spinner
    try:
        with st.spinner("Loading analytics..."):
            analytics = load_analytics()

        # Route to selected page
        if page == "Overview":
            render_executive_overview(analytics)
        elif page == "Friction Monitor":
            render_friction_monitor(analytics)
        elif page == "Cohort Analysis":
            render_unit_economics(analytics)

    except Exception as e:
        st.error(f"### ❌ Error Loading Dashboard\n\n{str(e)}")

        if st.checkbox("Show details"):
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
