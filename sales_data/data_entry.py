"""
Data Entry Module for Sales Analytics System
Handles adding, viewing, and managing sales records
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
import database as db

# Page configuration
st.set_page_config(
    page_title="Sales Data Entry",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #FEE2E2;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #EF4444;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #DBEAFE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    .stButton button {
        width: 100%;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_submission' not in st.session_state:
    st.session_state.last_submission = None
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = False
if 'delete_record_id' not in st.session_state:
    st.session_state.delete_record_id = None

# Main title
st.markdown('<h1 class="main-header">🧾 Sales Data Entry System</h1>', unsafe_allow_html=True)

# Sidebar for additional features
with st.sidebar:
    st.header("📊 Quick Stats")
    
    # Load current data for stats
    df_all = db.get_all_sales()
    
    if not df_all.empty:
        total_sales = df_all['sales'].sum()
        total_profit = df_all['profit'].sum()
        total_records = len(df_all)
        
        st.metric("Total Records", f"{total_records:,}")
        st.metric("Total Sales", f"₹{total_sales:,.2f}")
        st.metric("Total Profit", f"₹{total_profit:,.2f}")
        st.metric("Avg. Profit Margin", 
                  f"{(total_profit/total_sales*100 if total_sales > 0 else 0):.1f}%")
        
        # Date filters for data view
        st.divider()
        st.subheader("📅 Filter Data")
        
        if 'df' in locals() and not df_all.empty:
            min_date = pd.to_datetime(df_all['order_date']).min().date()
            max_date = pd.to_datetime(df_all['order_date']).max().date()
            
            date_filter = st.date_input(
                "Filter by Date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_filter) == 2:
                mask = (pd.to_datetime(df_all['order_date']).dt.date >= date_filter[0]) & \
                       (pd.to_datetime(df_all['order_date']).dt.date <= date_filter[1])
                df_all = df_all[mask]
    
    st.divider()
    st.markdown("---")
    st.caption("Developed with ❤️ using Streamlit")

# ===============================
# SECTION 1: ADD NEW SALE
# ===============================
st.markdown('<h2 class="sub-header">➕ Add New Sale Record</h2>', unsafe_allow_html=True)

# Create form in columns for better layout
with st.form(key="add_sale_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        order_date = st.date_input(
            "📅 Order Date",
            value=date.today(),
            help="Select the date of the sale"
        )
        
        product = st.text_input(
            "📦 Product Name *",
            placeholder="Enter product name",
            help="Required field"
        )
        
        customer = st.text_input(
            "👤 Customer Name *",
            placeholder="Enter customer name",
            help="Required field"
        )
    
    with col2:
        quantity = st.number_input(
            "🔢 Quantity *",
            min_value=1,
            value=1,
            step=1,
            help="Number of units sold"
        )
        
        sales = st.number_input(
            "💰 Sales Amount (₹) *",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
            help="Total sales amount in Rupees"
        )
        
        profit = st.number_input(
            "📈 Profit (₹) *",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
            help="Profit from this sale"
        )
    
    # Form validation messages
    if profit > sales:
        st.markdown('<div class="error-box">⚠️ Profit cannot exceed sales amount</div>', 
                   unsafe_allow_html=True)
    
    # Submit button
    submit_button = st.form_submit_button(
        label="💾 Save Sale Record",
        type="primary",
        use_container_width=True
    )

# Handle form submission
if submit_button:
    # Validate required fields
    if not product.strip() or not customer.strip():
        st.markdown('<div class="error-box">❌ Product and Customer names are required</div>', 
                   unsafe_allow_html=True)
    elif profit > sales:
        st.markdown('<div class="error-box">❌ Profit cannot be greater than sales amount</div>', 
                   unsafe_allow_html=True)
    else:
        # Add record to database
        success, message = db.add_sale_record(order_date, product, customer, sales, profit, quantity)
        
        if success:
            st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
            st.session_state.last_submission = datetime.now()
            
            # Show success details
            with st.expander("View Saved Details", expanded=False):
                st.write(f"**Date:** {order_date}")
                st.write(f"**Product:** {product}")
                st.write(f"**Customer:** {customer}")
                st.write(f"**Quantity:** {quantity}")
                st.write(f"**Sales:** ₹{sales:,.2f}")
                st.write(f"**Profit:** ₹{profit:,.2f}")
            
            # Refresh button
            if st.button("🔄 Refresh Data View", key="refresh_after_add"):
                st.session_state.refresh_data = True
                st.rerun()
        else:
            st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)

# ===============================
# SECTION 2: VIEW AND MANAGE SALES DATA
# ===============================
st.markdown('<h2 class="sub-header">📋 Sales Records Management</h2>', unsafe_allow_html=True)

# Refresh control
col_refresh, col_stats = st.columns([1, 3])
with col_refresh:
    if st.button("🔄 Refresh Data", key="refresh_main"):
        st.session_state.refresh_data = True
        st.rerun()

# Load data
df = db.get_all_sales()

if df.empty:
    st.markdown('<div class="info-box">ℹ️ No sales records found. Add your first sale above!</div>', 
               unsafe_allow_html=True)
else:
    # Display summary
    with col_stats:
        st.info(f"📊 Showing {len(df):,} sales records")
    
    # Convert date column for better display
    df_display = df.copy()
    df_display['order_date'] = pd.to_datetime(df_display['order_date']).dt.strftime('%Y-%m-%d')
    df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Format currency columns
    df_display['sales'] = df_display['sales'].apply(lambda x: f"₹{x:,.2f}")
    df_display['profit'] = df_display['profit'].apply(lambda x: f"₹{x:,.2f}")
    
    # Display data with container for better scrolling
    with st.container():
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_order=["id", "order_date", "product", "customer", "quantity", "sales", "profit", "created_at"],
            column_config={
                "id": "ID",
                "order_date": "Order Date",
                "product": "Product",
                "customer": "Customer",
                "quantity": "Qty",
                "sales": "Sales (₹)",
                "profit": "Profit (₹)",
                "created_at": "Added On"
            }
        )
    
    # ===============================
    # SECTION 3: DELETE RECORDS
    # ===============================
    st.markdown('<h3 class="sub-header">🗑️ Delete Records</h3>', unsafe_allow_html=True)
    
    col_id, col_confirm = st.columns([1, 2])
    
    with col_id:
        record_id = st.number_input(
            "Enter Record ID to delete",
            min_value=1,
            max_value=int(df['id'].max()) if not df.empty else 1,
            step=1,
            help="Enter the ID of the record you want to delete"
        )
    
    with col_confirm:
        if st.button("⚠️ Delete Record", type="secondary", key="delete_btn"):
            if record_id > 0:
                # Confirm deletion
                with st.expander("⚠️ Confirm Deletion", expanded=True):
                    st.warning(f"You are about to delete record #{record_id}. This action cannot be undone!")
                    
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes, Delete It", type="primary"):
                            success = db.delete_sale_record(record_id)
                            if success:
                                st.success(f"✅ Record #{record_id} deleted successfully!")
                                st.session_state.delete_record_id = record_id
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete record #{record_id}")
                    with col_no:
                        if st.button("Cancel"):
                            st.info("Deletion cancelled")
            else:
                st.error("Please enter a valid record ID")

# ===============================
# SECTION 4: DATA EXPORT
# ===============================
if not df.empty:
    st.markdown('<h3 class="sub-header">📥 Export Data</h3>', unsafe_allow_html=True)
    
    col_csv, col_excel = st.columns(2)
    
    # CSV Export
    with col_csv:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"sales_data_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Excel Export
    with col_excel:
        # For Excel export, we need to use a different approach
        @st.cache_data
        def convert_df_to_excel(df):
            from io import BytesIO
            import xlsxwriter
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sales Data')
                writer.save()
            return output.getvalue()
        
        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="📊 Download as Excel",
            data=excel_data,
            file_name=f"sales_data_{date.today()}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 1rem;'>
    <p>Sales Data Entry System v1.0 • Last Updated: March 2024</p>
    <p>All data is securely stored in the local database</p>
</div>
""", unsafe_allow_html=True)