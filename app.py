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
    page_icon="�",
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
        --proton-background: #ffffff;      /* White background */
        --proton-surface: #f8f9fa;         /* Light surface color */
        --proton-surface-light: #ffffff;   /* White surface */
        --proton-text: #1a1a1a;            /* Primary text - dark */
        --proton-text-muted: #6c757d;      /* Muted text - gray */
        --proton-success: #1ea672;         /* Success green */
        --proton-warning: #ff9900;         /* Warning orange */
        --proton-danger: #dc3545;          /* Danger red */
        --proton-border: #dee2e6;          /* Light border color */
    }
    
    /* Main background - White */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    /* Sidebar styling - White with purple accent */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 2px solid #6d4aff;
    }
    
    /* Sidebar navigation items */
    [data-testid="stSidebar"] .element-container {
        color: #1a1a1a;
    }
    
    /* Metric cards - Proton style */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Headers - Proton typography */
    h1, h2, h3 {
        color: #1a1a1a;
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
    
    /* Info boxes - Light style */
    [data-testid="stAlert"] {
        background-color: #f8f9fa;
        border-left: 4px solid #6d4aff;
        color: #1a1a1a;
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
    
    /* Input fields - Light style */
    .stSelectbox, .stTextInput {
        background-color: #ffffff;
        border-color: #dee2e6;
        color: #1a1a1a;
    }
    
    /* DataFrames - white theme */
    [data-testid="stDataFrame"] {
        background-color: #ffffff;
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
    Auto-generates data if not present (for Streamlit Cloud deployment).

    Returns:
        PaymentAnalytics instance with data loaded
    """
    data_dir = "./data"
    lock_file = os.path.join(data_dir, ".generation_complete")
    
    # Check if data exists
    data_files = [
        os.path.join(data_dir, "users.csv"),
        os.path.join(data_dir, "subscriptions.csv"),
        os.path.join(data_dir, "transactions.csv"),
    ]
    
    # Race condition protection - check for lock file first
    if not os.path.exists(lock_file):
        if not all(os.path.exists(f) for f in data_files):
            st.info("🔄 Generating synthetic data (first run, ~30 seconds)...")
            
            try:
                # Import and run data generator
                from payment_intelligence.data_generator import PaymentDataGenerator
                
                os.makedirs(data_dir, exist_ok=True)
                generator = PaymentDataGenerator(num_users=15000)
                generator.generate_all_data(output_dir=data_dir)
                
                # Create lock file to prevent re-generation
                with open(lock_file, 'w') as f:
                    f.write("Data generation completed successfully")
                
                st.success("✅ Data generated successfully!")
            except Exception as e:
                st.error(f"❌ Data generation failed: {str(e)}")
                # Clean up partial files
                for f in data_files:
                    if os.path.exists(f):
                        os.remove(f)
                raise
    
    analytics = PaymentAnalytics(data_dir=data_dir)
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
            help="Monthly Recurring Revenue from active subscriptions",
        )

    with col2:
        st.metric(
            label="Active Subs (Current)",
            value=f"{metrics['active_subscriptions']:,}",
            delta="+24",
            help="Number of active subscribers",
        )

    with col3:
        st.metric(
            label="Auth Rate (L30D)",
            value=f"{metrics['payment_success_rate']:.1f}%",
            delta=f"{metrics['payment_success_rate'] - 90:.1f}%",
            delta_color="normal" if metrics["payment_success_rate"] >= 90 else "inverse",
            help="Payment authorization rate (last 30 days)",
        )

    with col4:
        # Display churn rate with proper precision
        churn_display = f"{metrics['churn_rate']:.2f}%"
        st.metric(
            label="Churn Rate (Last Mo)",
            value=churn_display,
            delta="-0.02%",
            delta_color="inverse",
            help="Churn rate from most recent complete month (inverse: down is good)",
        )

    with col5:
        st.metric(
            label="Avg Tx Value (All-Time)",
            value=f"${metrics['avg_transaction_value']:.2f}",
            help="Average successful transaction amount (all-time)",
        )

    st.markdown("---")

    # Monthly churn trend
    st.subheader("Monthly Churn Trend")
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
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=400,
            xaxis_title="Cohort Month",
            yaxis_title="Percentage (%)",
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#1a1a1a")
            ),
            font=dict(color="#1a1a1a", family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto"),
            xaxis=dict(gridcolor="#e9ecef"),
            yaxis=dict(gridcolor="#e9ecef"),
        )

        st.plotly_chart(fig, use_container_width=True)

    # Gateway performance table - professional styling
    st.subheader("Gateway Performance")
    acceptance_df = get_acceptance_rates(analytics)

    if not acceptance_df.empty:
        # Rename columns for professional display
        display_df = acceptance_df[[
            "gateway",
            "country",
            "total_attempts",
            "acceptance_rate_pct",
            "soft_decline_rate_pct",
            "hard_decline_rate_pct",
        ]].head(10).copy()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "gateway": "Gateway",
                "country": "Region",
                "total_attempts": st.column_config.NumberColumn(
                    "Tx Volume",
                    help="Total transaction attempts",
                    format="%d",
                ),
                "acceptance_rate_pct": st.column_config.ProgressColumn(
                    "Auth Rate",
                    help="Successful authorization rate",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
                "soft_decline_rate_pct": st.column_config.NumberColumn(
                    "Soft Declines",
                    help="Temporary decline rate",
                    format="%.2f%%",
                ),
                "hard_decline_rate_pct": st.column_config.NumberColumn(
                    "Hard Declines",
                    help="Permanent decline rate",
                    format="%.2f%%",
                ),
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
        # Get available countries
        countries = analytics.conn.execute("""
            SELECT DISTINCT country 
            FROM transactions 
            WHERE country IS NOT NULL 
            ORDER BY country
        """).df()

        country_options = ["All"] + countries["country"].tolist()
        selected_country = st.selectbox("Region Filter", options=country_options, index=0)

    with col2:
        st.caption(
            "Payment flow from attempt through gateway selection, authorization, and settlement. "
            "Width indicates transaction volume."
        )

    # Get Sankey data
    country_filter = None if selected_country == "All" else selected_country
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
                        line=dict(color="#dee2e6", width=2),
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
            font=dict(size=12, color="#1a1a1a"),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=600,
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Friction detection table - professional styling
    st.subheader("Detected Friction")
    friction_df = get_friction_data(analytics)

    if not friction_df.empty:
        # Show all friction levels in separate sections
        high_friction = friction_df[friction_df["friction_flag"] == "High Friction"]
        medium_friction = friction_df[friction_df["friction_flag"] == "Medium Friction"]
        low_friction = friction_df[friction_df["friction_flag"] == "Low Friction"]

        # High Friction (critical issues)
        if not high_friction.empty:
            st.error(f"⚠️ {len(high_friction)} gateway/region pairs with HIGH friction (>10% below baseline)")

            st.dataframe(
                high_friction[[
                    "gateway",
                    "country",
                    "attempts",
                    "acceptance_rate_pct",
                    "baseline_rate_pct",
                    "variance_from_baseline",
                    "common_errors",
                    "friction_flag",
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "gateway": "Gateway",
                    "country": "Region",
                    "attempts": st.column_config.NumberColumn(
                        "Volume",
                        format="%d",
                    ),
                    "acceptance_rate_pct": st.column_config.ProgressColumn(
                        "Auth Rate",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "baseline_rate_pct": st.column_config.NumberColumn(
                        "Baseline",
                        format="%.1f%%",
                    ),
                    "variance_from_baseline": st.column_config.NumberColumn(
                        "Variance",
                        format="%.1f%%",
                    ),
                    "common_errors": "Common Errors",
                    "friction_flag": "Status",
                },
            )

        # Medium Friction (warning zone)
        if not medium_friction.empty:
            st.warning(f"⚡ {len(medium_friction)} gateway/region pairs with MEDIUM friction (5-10% below baseline)")

            st.dataframe(
                medium_friction[[
                    "gateway",
                    "country",
                    "attempts",
                    "acceptance_rate_pct",
                    "baseline_rate_pct",
                    "variance_from_baseline",
                    "friction_flag",
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "gateway": "Gateway",
                    "country": "Region",
                    "attempts": st.column_config.NumberColumn(
                        "Volume",
                        format="%d",
                    ),
                    "acceptance_rate_pct": st.column_config.ProgressColumn(
                        "Auth Rate",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "baseline_rate_pct": st.column_config.NumberColumn(
                        "Baseline",
                        format="%.1f%%",
                    ),
                    "variance_from_baseline": st.column_config.NumberColumn(
                        "Variance",
                        format="%.1f%%",
                    ),
                    "friction_flag": "Status",
                },
            )

        # Low Friction (healthy performance)
        if not low_friction.empty:
            with st.expander(f"✅ {len(low_friction)} gateway/region pairs with LOW friction (healthy performance)", expanded=False):
                # Show top 10 performers
                top_performers = low_friction.nlargest(10, "acceptance_rate_pct")
                
                st.dataframe(
                    top_performers[[
                        "gateway",
                        "country",
                        "attempts",
                        "acceptance_rate_pct",
                        "variance_from_baseline",
                    ]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "gateway": "Gateway",
                        "country": "Region",
                        "attempts": st.column_config.NumberColumn("Volume", format="%d"),
                        "acceptance_rate_pct": st.column_config.ProgressColumn(
                            "Auth Rate",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "variance_from_baseline": st.column_config.NumberColumn(
                            "Variance",
                            format="%.1f%%",
                        ),
                    },
                )
        
        # Summary metrics
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Friction", len(high_friction), delta=f"{len(high_friction)}", delta_color="inverse")
        with col2:
            st.metric("Medium Friction", len(medium_friction), delta=f"{len(medium_friction)}", delta_color="off")
        with col3:
            st.metric("Low Friction", len(low_friction), delta=f"{len(low_friction)}", delta_color="normal")


def render_unit_economics(analytics):
    """
    Render Unit Economics page with cohort retention heatmap.

    Shows month-over-month retention for each signup cohort.
    """
    st.title("Cohort Analysis")
    st.markdown("---")

    st.caption(
        "12-month retention tracking by signup cohort. "
        "Darker purple indicates higher retention rates."
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
                    title=dict(text="Retention %", font=dict(color="#1a1a1a")),
                    ticksuffix="%",
                    tickfont=dict(color="#1a1a1a")
                ),
                hovertemplate="Cohort: %{y}<br>Month %{x}<br>Retention: %{z:.1f}%<extra></extra>",
            )
        )

        fig.update_layout(
            xaxis_title="Months Since Signup",
            yaxis_title="Signup Cohort",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=600,
            font=dict(color="#1a1a1a", family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto"),
            xaxis=dict(gridcolor="#e9ecef"),
            yaxis=dict(gridcolor="#e9ecef"),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Insights
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Key Insights")

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
            st.subheader("Cohort Performance")

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
    st.subheader("Revenue Reconciliation")

    recon_df = get_revenue_reconciliation(analytics)

    if not recon_df.empty:
        st.dataframe(
            recon_df.head(12),
            use_container_width=True,
            hide_index=True,
            column_config={
                "month": st.column_config.DateColumn("Month", format="MMM YYYY"),
                "cash_collected": st.column_config.NumberColumn(
                    "Cash Collected",
                    format="$%.2f",
                ),
                "booked_revenue": st.column_config.NumberColumn(
                    "Booked Revenue",
                    format="$%.2f",
                ),
                "variance": st.column_config.NumberColumn(
                    "Variance",
                    format="$%.2f",
                ),
                "variance_pct": st.column_config.NumberColumn(
                    "Variance %",
                    format="%.2f%%",
                ),
                "successful_payments": st.column_config.NumberColumn(
                    "Tx Count",
                    format="%d",
                ),
            },
        )


def main():
    """Main application entry point."""

    # Sidebar
    with st.sidebar:
        # Clean Proton-themed header
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
            ">Payment Intel</h1>
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

        page = st.radio(
            "Navigate",
            ["Overview", "Friction Monitor", "Cohort Analysis"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Data refresh
        if st.button("Refresh Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

    # Initialize analytics
    try:
        analytics = load_analytics()

        # Route to selected page
        if page == "Overview":
            render_executive_overview(analytics)
        elif page == "Friction Monitor":
            render_friction_monitor(analytics)
        elif page == "Cohort Analysis":
            render_unit_economics(analytics)

    except Exception as e:
        st.error(f"""
        ### ❌ Error Loading Dashboard
        
        {str(e)}
        
        Please ensure all dependencies are installed (`uv sync`) or try refreshing the data.
        """)

        if st.checkbox("Show error details"):
            import traceback

            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
