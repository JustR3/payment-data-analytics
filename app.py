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

# Custom CSS for Proton brand theme
st.markdown(
    """
<style>
    /* Proton authentic color palette */
    :root {
        --proton-purple: #6d4aff;          /* Proton primary purple */
        --proton-purple-dark: #5835d4;     /* Darker purple variant */
        --proton-background: #0c0c14;      /* True Proton dark background */
        --proton-surface: #1c1b22;         /* Surface color */
        --proton-surface-light: #2e2d39;   /* Lighter surface */
        --proton-text: #ffffff;            /* Primary text */
        --proton-text-muted: #a8a8b3;      /* Muted text */
        --proton-success: #1ea672;         /* Success green */
        --proton-warning: #ff9900;         /* Warning orange */
        --proton-danger: #dc3545;          /* Danger red */
        --proton-border: #3a3a48;          /* Border color */
    }
    
    /* Main background - Proton dark */
    .stApp {
        background-color: #0c0c14;
        color: #ffffff;
    }
    
    /* Sidebar styling - Proton surface */
    [data-testid="stSidebar"] {
        background-color: #1c1b22;
        border-right: 2px solid #6d4aff;
    }
    
    /* Sidebar navigation items */
    [data-testid="stSidebar"] .element-container {
        color: #ffffff;
    }
    
    /* Metric cards - Proton style */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Headers - Proton typography */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    h1 {
        color: #6d4aff;
    }
    
    /* Dividers - Proton purple accent */
    hr {
        border-color: #6d4aff;
        opacity: 0.3;
        margin: 2rem 0;
    }
    
    /* Info boxes - Proton surface style */
    [data-testid="stAlert"] {
        background-color: #2e2d39;
        border-left: 4px solid #6d4aff;
        color: #ffffff;
    }
    
    /* Buttons - Proton purple */
    .stButton>button {
        background-color: #6d4aff;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #5835d4;
        box-shadow: 0 4px 12px rgba(109, 74, 255, 0.4);
    }
    
    /* Input fields - Proton style */
    .stSelectbox, .stTextInput {
        background-color: #2e2d39;
        border-color: #3a3a48;
        color: #ffffff;
    }
    
    /* DataFrames - dark theme */
    [data-testid="stDataFrame"] {
        background-color: #1c1b22;
    }
    
    /* Success/Warning/Danger badges */
    .badge-success {
        background-color: #1ea672;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .badge-warning {
        background-color: #ff9900;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .badge-danger {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_analytics():
    """
    Load analytics engine with caching.

    Returns:
        PaymentAnalytics instance with data loaded
    """
    analytics = PaymentAnalytics(data_dir="./data")
    analytics.load_data()
    return analytics


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_executive_metrics(_analytics):
    """Get executive metrics with caching."""
    return _analytics.executive_metrics()


@st.cache_data(ttl=300)
def get_churn_data(_analytics):
    """Get churn analysis with caching."""
    return _analytics.calculate_monthly_churn_rate()


@st.cache_data(ttl=300)
def get_acceptance_rates(_analytics):
    """Get acceptance rates with caching."""
    return _analytics.payment_acceptance_rate_by_gateway(min_transactions=50)


@st.cache_data(ttl=300)
def get_revenue_reconciliation(_analytics):
    """Get revenue reconciliation with caching."""
    return _analytics.revenue_reconciliation()


@st.cache_data(ttl=300)
def get_friction_data(_analytics):
    """Get friction detection with caching."""
    return _analytics.detect_gateway_friction()


@st.cache_data(ttl=300)
def get_cohort_retention(_analytics):
    """Get cohort retention with caching."""
    return _analytics.cohort_retention_analysis(cohort_months=12)


@st.cache_data(ttl=300)
def get_sankey_data(_analytics, country_filter=None):
    """Get Sankey diagram data with caching."""
    return _analytics.get_sankey_data(country_filter=country_filter)


def render_executive_overview(analytics):
    """
    Render Executive Overview page.

    Shows high-level KPIs, trends, and key metrics.
    """
    st.title("💼 Executive Overview")
    st.markdown("---")

    # Get metrics
    metrics = get_executive_metrics(analytics)

    # Top KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Monthly Recurring Revenue",
            value=f"${metrics['mrr']:,.2f}",
            delta="MRR",
            help="Total MRR from active subscriptions",
        )

    with col2:
        st.metric(
            label="👥 Active Subscriptions",
            value=f"{metrics['active_subscriptions']:,}",
            delta=None,
            help="Number of active subscribers",
        )

    with col3:
        st.metric(
            label="✅ Payment Success Rate",
            value=f"{metrics['payment_success_rate']:.1f}%",
            delta=f"{metrics['payment_success_rate'] - 90:.1f}%",
            delta_color="normal" if metrics["payment_success_rate"] >= 90 else "inverse",
            help="Success rate over last 30 days",
        )

    with col4:
        st.metric(
            label="📉 Churn Rate",
            value=f"{metrics['churn_rate']:.1f}%",
            delta=f"{metrics['churn_rate'] - 15:.1f}%",
            delta_color="inverse",
            help="Current month churn rate",
        )

    st.markdown("---")

    # Revenue metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="📈 Total Revenue (All Time)",
            value=f"${metrics['total_revenue']:,.2f}",
            help="Cumulative successful transaction revenue",
        )

    with col2:
        st.metric(
            label="💵 Average Transaction Value",
            value=f"${metrics['avg_transaction_value']:.2f}",
            help="Average value of successful transactions",
        )

    st.markdown("---")

    # Monthly churn trend
    st.subheader("📊 Monthly Churn Trend")
    churn_df = get_churn_data(analytics)

    if not churn_df.empty:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=churn_df["cohort_month"],
                y=churn_df["churn_rate_pct"],
                mode="lines+markers",
                name="Churn Rate",
                line=dict(color="#dc3545", width=3),
                marker=dict(size=10, color="#dc3545"),
                hovertemplate="%{y:.1f}%<extra></extra>",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=churn_df["cohort_month"],
                y=churn_df["retention_rate_pct"],
                mode="lines+markers",
                name="Retention Rate",
                line=dict(color="#6d4aff", width=3),
                marker=dict(size=10, color="#6d4aff"),
                hovertemplate="%{y:.1f}%<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="Monthly Churn & Retention Trends",
                font=dict(color="#6d4aff", size=18)
            ),
            template="plotly_dark",
            plot_bgcolor="#0c0c14",
            paper_bgcolor="#0c0c14",
            height=400,
            xaxis_title="Cohort Month",
            yaxis_title="Percentage (%)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="white")
            ),
            font=dict(color="white", family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto"),
            xaxis=dict(gridcolor="#2e2d39"),
            yaxis=dict(gridcolor="#2e2d39"),
        )

        st.plotly_chart(fig, width="stretch")

    # Gateway performance table
    st.subheader("🚪 Gateway Performance")
    acceptance_df = get_acceptance_rates(analytics)

    if not acceptance_df.empty:
        # Add color coding
        def color_acceptance_rate(val):
            if val >= 90:
                return "background-color: #1ea672; color: white"
            elif val >= 80:
                return "background-color: #ff9900; color: white"
            else:
                return "background-color: #dc3545; color: white"

        display_df = acceptance_df[
            [
                "gateway",
                "country",
                "total_attempts",
                "acceptance_rate_pct",
                "soft_decline_rate_pct",
                "hard_decline_rate_pct",
            ]
        ].head(10)

        st.dataframe(
            display_df.style.map(color_acceptance_rate, subset=["acceptance_rate_pct"]).format(
                {
                    "acceptance_rate_pct": "{:.2f}%",
                    "soft_decline_rate_pct": "{:.2f}%",
                    "hard_decline_rate_pct": "{:.2f}%",
                    "total_attempts": "{:,}",
                }
            ),
            width="stretch",
            height=400,
        )


def render_friction_monitor(analytics):
    """
    Render Friction Monitor page with Sankey diagram.

    Shows payment flow: Attempt → Gateway → Auth → Settlement
    """
    st.title("🔍 Friction Monitor")
    st.markdown("---")

    # Country filter
    col1, col2 = st.columns([1, 3])

    with col1:
        # Get available countries
        countries = analytics.conn.execute("""
            SELECT DISTINCT country 
            FROM transactions 
            WHERE country IS NOT NULL 
            ORDER BY country
        """).df()

        country_options = ["All Countries"] + countries["country"].tolist()
        selected_country = st.selectbox("🌍 Filter by Country", options=country_options, index=0)

    with col2:
        st.info(
            "💡 **Sankey Flow**: Visualizes payment journey from initial attempt through "
            "gateway selection, authorization, and final settlement. Width represents volume."
        )

    # Get Sankey data
    country_filter = None if selected_country == "All Countries" else selected_country
    sankey_df = get_sankey_data(analytics, country_filter=country_filter)

    if not sankey_df.empty:
        # Create node labels (unique sources and targets)
        all_nodes = list(set(sankey_df["source"].tolist() + sankey_df["target"].tolist()))
        node_dict = {node: idx for idx, node in enumerate(all_nodes)}

        # Map sources and targets to indices
        sources = [node_dict[src] for src in sankey_df["source"]]
        targets = [node_dict[tgt] for tgt in sankey_df["target"]]
        values = sankey_df["value"].tolist()

        # Color scheme - Proton brand palette
        node_colors = []
        for node in all_nodes:
            if node == "Attempt":
                node_colors.append("#6d4aff")  # Proton primary purple
            elif node in ["Stripe", "PayPal", "Apple Pay", "Bitcoin"]:
                node_colors.append("#8a7aff")  # Lighter Proton purple
            elif node == "Authorized":
                node_colors.append("#1ea672")  # Proton success green
            elif node == "Settled":
                node_colors.append("#16865e")  # Darker success green
            else:
                node_colors.append("#dc3545")  # Proton danger red

        # Create Sankey diagram
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="#1c1b22", width=2),
                        label=all_nodes,
                        color=node_colors,
                        customdata=all_nodes,
                        hovertemplate="%{customdata}<br>%{value:,} transactions<extra></extra>",
                    ),
                    link=dict(
                        source=sources,
                        target=targets,
                        value=values,
                        color="rgba(109, 74, 255, 0.25)",
                        hovertemplate="%{source.label} → %{target.label}<br>%{value:,} transactions<extra></extra>",
                    ),
                )
            ]
        )

        fig.update_layout(
            title=dict(
                text=f"Payment Flow Analysis{' - ' + selected_country if country_filter else ''}",
                font=dict(size=20, color="#6d4aff", family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto"),
            ),
            font=dict(size=12, color="white"),
            plot_bgcolor="#0c0c14",
            paper_bgcolor="#0c0c14",
            height=600,
        )

        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Friction detection table
    st.subheader("⚠️ Detected Payment Friction")
    friction_df = get_friction_data(analytics)

    if not friction_df.empty:
        # Filter to show problematic ones first
        problematic = friction_df[friction_df["friction_flag"] != "🟢 Normal"]

        if not problematic.empty:
            st.warning(f"Found {len(problematic)} gateway/country pairs with elevated friction!")

            display_cols = [
                "gateway",
                "country",
                "attempts",
                "acceptance_rate_pct",
                "baseline_rate_pct",
                "variance_from_baseline",
                "common_errors",
                "friction_flag",
            ]

            st.dataframe(
                problematic[display_cols].style.format(
                    {
                        "acceptance_rate_pct": "{:.2f}%",
                        "baseline_rate_pct": "{:.2f}%",
                        "variance_from_baseline": "{:.2f}%",
                        "attempts": "{:,}",
                    }
                ),
                width="stretch",
                height=400,
            )
        else:
            st.success("✅ No significant payment friction detected across gateways!")

            # Show top performers
            st.subheader("🌟 Top Performing Gateway/Country Pairs")
            top_performers = friction_df.nlargest(10, "acceptance_rate_pct")
            st.dataframe(
                top_performers[display_cols].style.format(
                    {
                        "acceptance_rate_pct": "{:.2f}%",
                        "baseline_rate_pct": "{:.2f}%",
                        "variance_from_baseline": "{:.2f}%",
                        "attempts": "{:,}",
                    }
                ),
                width="stretch",
            )


def render_unit_economics(analytics):
    """
    Render Unit Economics page with cohort retention heatmap.

    Shows month-over-month retention for each signup cohort.
    """
    st.title("💎 Unit Economics")
    st.markdown("---")

    st.info(
        "📊 **Cohort Retention Analysis**: Track how each monthly signup cohort retains "
        "over their lifetime. Darker colors indicate higher retention rates."
    )

    # Get cohort data
    cohort_df = get_cohort_retention(analytics)

    if not cohort_df.empty:
        # Pivot for heatmap
        pivot_df = cohort_df.pivot(
            index="cohort_month", columns="months_since_signup", values="retention_rate_pct"
        )

        # Sort by cohort month descending
        pivot_df = pivot_df.sort_index(ascending=False)

        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=[str(d)[:7] for d in pivot_df.index],  # Format dates
                colorscale=[
                    [0, "#dc3545"],      # Proton red for low retention
                    [0.3, "#ff9900"],    # Proton orange for medium-low
                    [0.6, "#8a7aff"],    # Light Proton purple for medium-high
                    [1, "#6d4aff"],      # Proton primary purple for high retention
                ],
                text=pivot_df.values,
                texttemplate="%{text:.1f}%",
                textfont={"size": 10, "color": "white"},
                colorbar=dict(
                    title=dict(text="Retention %", font=dict(color="white")),
                    ticksuffix="%",
                    tickfont=dict(color="white")
                ),
                hovertemplate="Cohort: %{y}<br>Month %{x}<br>Retention: %{z:.1f}%<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="12-Month Cohort Retention Heatmap",
                font=dict(color="#6d4aff", size=20)
            ),
            xaxis_title="Months Since Signup",
            yaxis_title="Signup Cohort",
            template="plotly_dark",
            plot_bgcolor="#0c0c14",
            paper_bgcolor="#0c0c14",
            height=600,
            font=dict(color="white", family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto"),
            xaxis=dict(gridcolor="#2e2d39"),
            yaxis=dict(gridcolor="#2e2d39"),
        )

        st.plotly_chart(fig, width="stretch")

        # Insights
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Key Insights")

            # Calculate average retention at different stages
            if 1 in pivot_df.columns:
                avg_month_1 = pivot_df[1].mean()
                st.metric("Month 1 Avg Retention", f"{avg_month_1:.1f}%")

            if 6 in pivot_df.columns:
                avg_month_6 = pivot_df[6].mean()
                st.metric("Month 6 Avg Retention", f"{avg_month_6:.1f}%")

            if 12 in pivot_df.columns:
                avg_month_12 = pivot_df[12].mean()
                st.metric("Month 12 Avg Retention", f"{avg_month_12:.1f}%")

        with col2:
            st.subheader("💡 Cohort Performance")

            # Best performing cohort
            best_cohort = pivot_df.mean(axis=1).idxmax()
            best_cohort_retention = pivot_df.mean(axis=1).max()

            st.markdown(f"""
            **Best Cohort**: `{str(best_cohort)[:7]}`  
            Average Retention: `{best_cohort_retention:.1f}%`
            
            **Worst Cohort**: `{str(pivot_df.mean(axis=1).idxmin())[:7]}`  
            Average Retention: `{pivot_df.mean(axis=1).min():.1f}%`
            """)

    # Revenue reconciliation
    st.markdown("---")
    st.subheader("💰 Revenue Reconciliation (Cash vs Booked)")

    recon_df = get_revenue_reconciliation(analytics)

    if not recon_df.empty:
        # Show table
        display_df = recon_df[
            [
                "month",
                "cash_collected",
                "booked_revenue",
                "variance",
                "variance_pct",
                "successful_payments",
            ]
        ].head(12)

        st.dataframe(
            display_df.style.format(
                {
                    "cash_collected": "${:,.2f}",
                    "booked_revenue": "${:,.2f}",
                    "variance": "${:,.2f}",
                    "variance_pct": "{:.2f}%",
                    "successful_payments": "{:,}",
                }
            ),
            width="stretch",
            height=400,
        )


def main():
    """Main application entry point."""

    # Sidebar
    with st.sidebar:
        # Custom Proton-themed header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #6d4aff 0%, #5835d4 100%);
            padding: 1.5rem 1rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(109, 74, 255, 0.3);
        ">
            <h1 style="
                color: white;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0;
                letter-spacing: -0.02em;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            ">💳 Payment Intel</h1>
            <p style="
                color: rgba(255,255,255,0.9);
                font-size: 0.75rem;
                margin: 0.5rem 0 0 0;
                font-weight: 500;
                letter-spacing: 0.05em;
            ">ANALYTICS SUITE</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.title("Navigation")
        page = st.radio(
            "Select Page",
            ["💼 Executive Overview", "🔍 Friction Monitor", "💎 Unit Economics"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        st.markdown("""
        ### 📊 About
        **Payment Intelligence Suite**
        
        Production-grade analytics for subscription payment data.
        
        **Tech Stack:**
        - DuckDB (SQL Analytics)
        - Streamlit (Dashboard)
        - Plotly (Visualizations)
        
        ---
        
        **Portfolio Project**  
        Built for Proton Data Analyst role
        """)

        # Data refresh
        if st.button("🔄 Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

    # Initialize analytics
    try:
        analytics = load_analytics()

        # Route to selected page
        if page == "💼 Executive Overview":
            render_executive_overview(analytics)
        elif page == "🔍 Friction Monitor":
            render_friction_monitor(analytics)
        elif page == "💎 Unit Economics":
            render_unit_economics(analytics)

    except FileNotFoundError:
        st.error("""
        ### ❌ Data Not Found
        
        Please generate synthetic data first:
        
        ```bash
        uv run python scripts/generate_data.py
        ```
        """)
    except Exception as e:
        st.error(f"""
        ### ❌ Error Loading Dashboard
        
        {str(e)}
        
        Please ensure:
        1. Data has been generated
        2. All dependencies are installed (`uv sync`)
        """)

        if st.checkbox("Show error details"):
            import traceback

            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
