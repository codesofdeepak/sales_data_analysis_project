"""
Analytics Dashboard for Sales Analytics System
Provides insights, visualizations, and forecasts
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
import database as db
import numpy as np
from scipy import stats

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .positive-change {
        color: #10B981;
        font-weight: bold;
    }
    .negative-change {
        color: #EF4444;
        font-weight: bold;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for filters
if 'date_range' not in st.session_state:
    st.session_state.date_range = None
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = "All"

# Main title
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📊 Sales Analytics Dashboard</h1>", 
            unsafe_allow_html=True)

# ===============================
# SIDEBAR - FILTERS AND CONTROLS
# ===============================
with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
    # Load data for filters
    df_all = db.get_all_sales()
    
    if not df_all.empty:
        # Date range selector
        df_all['order_date'] = pd.to_datetime(df_all['order_date'])
        min_date = df_all['order_date'].min().date()
        max_date = df_all['order_date'].max().date()
        
        date_range = st.date_input(
            "📅 Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Product filter
        products = ["All"] + sorted(df_all['product'].unique().tolist())
        selected_product = st.selectbox(
            "📦 Filter by Product",
            products,
            index=0
        )
        
        # Time period selector
        time_period = st.selectbox(
            "⏰ Analysis Period",
            ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
            index=2
        )
        
        # Additional filters
        st.subheader("🎯 Advanced Filters")
        
        min_sales = st.number_input(
            "Minimum Sales Amount",
            min_value=0.0,
            value=0.0,
            step=100.0
        )
        
        min_profit = st.number_input(
            "Minimum Profit",
            min_value=0.0,
            value=0.0,
            step=100.0
        )
        
        # Update session state
        st.session_state.date_range = date_range
        st.session_state.selected_product = selected_product
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
        
        if st.button("📥 Export Dashboard Data", use_container_width=True):
            st.info("Export functionality would be implemented here")
    
    else:
        st.warning("No data available. Please add sales data first.")
    
    st.divider()
    st.caption("Dashboard Last Updated:")
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ===============================
# MAIN CONTENT AREA
# ===============================
if df_all.empty:
    st.warning("""
    ⚠️ **No sales data available for analysis**
    
    Please visit the **Data Entry** page to add sales records first.
    """)
    st.stop()

# Apply filters
df = df_all.copy()
df['order_date'] = pd.to_datetime(df['order_date'])

if len(st.session_state.date_range) == 2:
    start_date, end_date = st.session_state.date_range
    mask = (df['order_date'].dt.date >= start_date) & (df['order_date'].dt.date <= end_date)
    df = df[mask]

if st.session_state.selected_product != "All":
    df = df[df['product'] == st.session_state.selected_product]

# Apply advanced filters
df = df[df['sales'] >= min_sales]
df = df[df['profit'] >= min_profit]

if df.empty:
    st.warning("No data matches the selected filters. Please adjust your filter criteria.")
    st.stop()

# ===============================
# ROW 1: KEY PERFORMANCE INDICATORS (KPIs)
# ===============================
st.subheader("📈 Key Performance Indicators")

# Calculate KPIs
total_sales = df['sales'].sum()
total_profit = df['profit'].sum()
total_orders = len(df)
avg_order_value = total_sales / total_orders if total_orders > 0 else 0
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
avg_profit_per_order = total_profit / total_orders if total_orders > 0 else 0

# Create KPI cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Sales</div>
        <div class="metric-value">₹{total_sales:,.0f}</div>
        <div>All Time</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <div class="metric-label">Total Profit</div>
        <div class="metric-value">₹{total_profit:,.0f}</div>
        <div>{profit_margin:.1f}% Margin</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="metric-label">Total Orders</div>
        <div class="metric-value">{total_orders:,}</div>
        <div>Avg ₹{avg_order_value:,.0f}/order</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <div class="metric-label">Avg Profit/Order</div>
        <div class="metric-value">₹{avg_profit_per_order:,.0f}</div>
        <div>Per Transaction</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===============================
# ROW 2: TREND ANALYSIS
# ===============================
st.subheader("📊 Sales Trend Analysis")

# Prepare data for time series
df['year_month'] = df['order_date'].dt.strftime('%Y-%m')
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['week'] = df['order_date'].dt.isocalendar().week
df['quarter'] = df['order_date'].dt.quarter

# Group by selected time period
if time_period == "Daily":
    period_col = 'order_date'
    group_format = '%Y-%m-%d'
elif time_period == "Weekly":
    period_col = 'week'
    group_format = None
elif time_period == "Monthly":
    period_col = 'year_month'
    group_format = None
elif time_period == "Quarterly":
    period_col = 'quarter'
    group_format = None
else:  # Yearly
    period_col = 'year'
    group_format = None

if group_format:
    df[period_col] = df['order_date'].dt.strftime(group_format)

trend_data = df.groupby(period_col).agg({
    'sales': 'sum',
    'profit': 'sum',
    'quantity': 'sum',
    'id': 'count'
}).reset_index()
trend_data.rename(columns={'id': 'transactions'}, inplace=True)

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("**Sales Trend Over Time**")
    
    fig1 = px.line(
        trend_data,
        x=period_col,
        y='sales',
        markers=True,
        line_shape='spline',
        title=f"{time_period} Sales Trend"
    )
    fig1.update_layout(
        xaxis_title=time_period,
        yaxis_title="Sales (₹)",
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("**Profit Margin Trend**")
    
    trend_data['profit_margin'] = (trend_data['profit'] / trend_data['sales'] * 100)
    
    fig2 = px.bar(
        trend_data,
        x=period_col,
        y='profit_margin',
        title=f"{time_period} Profit Margin (%)"
    )
    fig2.update_layout(
        xaxis_title=time_period,
        yaxis_title="Profit Margin %",
        yaxis_tickformat=".1f%"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# ROW 3: PRODUCT AND CUSTOMER ANALYSIS
# ===============================
st.subheader("👥 Product & Customer Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("**Top 10 Products by Sales**")
    
    product_sales = df.groupby('product').agg({
        'sales': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).nlargest(10, 'sales').reset_index()
    
    product_sales['profit_margin'] = (product_sales['profit'] / product_sales['sales'] * 100)
    
    fig3 = px.bar(
        product_sales,
        x='sales',
        y='product',
        orientation='h',
        color='profit_margin',
        color_continuous_scale='Viridis',
        title="Top Products Performance"
    )
    fig3.update_layout(
        xaxis_title="Sales (₹)",
        yaxis_title="Product",
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("**Top 10 Customers**")
    
    customer_sales = df.groupby('customer').agg({
        'sales': 'sum',
        'profit': 'sum',
        'id': 'count'
    }).nlargest(10, 'sales').reset_index()
    customer_sales.rename(columns={'id': 'transactions'}, inplace=True)
    
    fig4 = px.scatter(
        customer_sales,
        x='transactions',
        y='sales',
        size='profit',
        color='profit',
        hover_name='customer',
        size_max=60,
        title="Customer Value Analysis"
    )
    fig4.update_layout(
        xaxis_title="Number of Transactions",
        yaxis_title="Total Sales (₹)"
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# ROW 4: PROFITABILITY ANALYSIS
# ===============================
st.subheader("💰 Profitability Analysis")

# Calculate profitability metrics
profit_analysis = df.groupby('product').agg({
    'sales': 'sum',
    'profit': 'sum',
    'quantity': 'sum'
}).reset_index()

profit_analysis['profit_margin'] = (profit_analysis['profit'] / profit_analysis['sales'] * 100)
profit_analysis['avg_price'] = profit_analysis['sales'] / profit_analysis['quantity']
profit_analysis['profit_per_unit'] = profit_analysis['profit'] / profit_analysis['quantity']

# Create scatter plot for profitability vs sales
fig5 = px.scatter(
    profit_analysis,
    x='sales',
    y='profit_margin',
    size='quantity',
    color='profit',
    hover_name='product',
    title="Product Profitability Matrix",
    labels={
        'sales': 'Total Sales (₹)',
        'profit_margin': 'Profit Margin (%)',
        'quantity': 'Units Sold',
        'profit': 'Total Profit (₹)'
    }
)

fig5.update_layout(
    xaxis_title="Total Sales (₹)",
    yaxis_title="Profit Margin (%)",
    hovermode='closest'
)

# Add quadrant lines
median_sales = profit_analysis['sales'].median()
median_margin = profit_analysis['profit_margin'].median()

fig5.add_hline(
    y=median_margin,
    line_dash="dash",
    line_color="gray",
    annotation_text=f"Median Margin: {median_margin:.1f}%"
)

fig5.add_vline(
    x=median_sales,
    line_dash="dash",
    line_color="gray",
    annotation_text=f"Median Sales: ₹{median_sales:,.0f}"
)

st.plotly_chart(fig5, use_container_width=True)

# ===============================
# ROW 5: DATA TABLE AND EXPORT
# ===============================
st.subheader("📋 Detailed Data View")

# Show filtered data
with st.expander("View Filtered Data Table", expanded=False):
    display_df = df.copy()
    display_df['order_date'] = display_df['order_date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.sort_values('order_date', ascending=False)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "id": "ID",
            "order_date": "Date",
            "product": "Product",
            "customer": "Customer",
            "quantity": "Qty",
            "sales": st.column_config.NumberColumn(
                "Sales (₹)",
                format="₹%.2f"
            ),
            "profit": st.column_config.NumberColumn(
                "Profit (₹)",
                format="₹%.2f"
            )
        },
        hide_index=True
    )
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"filtered_sales_data_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Simple Excel export using to_excel
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Sales Data')
        
        st.download_button(
            label="📊 Download as Excel",
            data=buffer.getvalue(),
            file_name=f"filtered_sales_data_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ===============================
# FOOTER AND STATISTICS
# ===============================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📅 Date Range",
        f"{st.session_state.date_range[0] if st.session_state.date_range else 'N/A'} to {st.session_state.date_range[1] if st.session_state.date_range else 'N/A'}"
    )

with col2:
    st.metric(
        "📦 Products Analyzed",
        f"{len(df['product'].unique())} of {len(df_all['product'].unique())}"
    )

with col3:
    st.metric(
        "🔄 Data Freshness",
        f"Updated: {datetime.now().strftime('%H:%M:%S')}"
    )

st.caption("💡 **Tip:** Use the sidebar filters to customize your analysis. All charts are interactive!")