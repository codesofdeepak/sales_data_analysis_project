"""
Database module for Sales Analytics System
Centralized database operations to prevent duplication and ensure consistency
"""
import sqlite3
import pandas as pd
import os
from contextlib import contextmanager
from datetime import datetime

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sales_data.db")

@contextmanager
def get_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with proper schema and indexes"""
    with get_connection() as conn:
        # Create sales table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_date DATE NOT NULL,
                product VARCHAR(100) NOT NULL,
                customer VARCHAR(100) NOT NULL,
                sales DECIMAL(10, 2) NOT NULL,
                profit DECIMAL(10, 2) NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT chk_profit CHECK (profit <= sales)
            )
        """)
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON sales(order_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_product ON sales(product)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_customer ON sales(customer)")
        
        conn.commit()

def add_sale_record(order_date, product, customer, sales, profit, quantity):
    """
    Add a single sale record to the database
    Returns: (success, message)
    """
    try:
        # Validate data
        if not product or not customer:
            return False, "Product and Customer are required"
        
        if profit > sales:
            return False, "Profit cannot be greater than sales amount"
        
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sales (order_date, product, customer, sales, profit, quantity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_date.strftime("%Y-%m-%d") if hasattr(order_date, 'strftime') else order_date,
                product.strip(),
                customer.strip(),
                float(sales),
                float(profit),
                int(quantity)
            ))
            conn.commit()
            return True, f"Sale record #{cursor.lastrowid} added successfully"
    
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def get_all_sales():
    """Retrieve all sales records"""
    try:
        with get_connection() as conn:
            df = pd.read_sql("""
                SELECT id, order_date, product, customer, 
                       sales, profit, quantity, created_at
                FROM sales 
                ORDER BY order_date DESC, created_at DESC
            """, conn)
            return df
    except Exception as e:
        print(f"Error loading sales data: {e}")
        return pd.DataFrame()

def delete_sale_record(record_id):
    """Delete a sale record by ID"""
    try:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM sales WHERE id = ?", (int(record_id),))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting record: {e}")
        return False

def update_sale_record(record_id, **updates):
    """Update a sale record"""
    try:
        with get_connection() as conn:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(record_id)
            
            conn.execute(f"""
                UPDATE sales 
                SET {set_clause}
                WHERE id = ?
            """, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"Error updating record: {e}")
        return False

def get_sales_summary(start_date=None, end_date=None):
    """Get sales summary for analytics"""
    try:
        with get_connection() as conn:
            query = """
                SELECT 
                    order_date,
                    product,
                    customer,
                    SUM(sales) as total_sales,
                    SUM(profit) as total_profit,
                    SUM(quantity) as total_quantity,
                    COUNT(*) as transaction_count
                FROM sales
            """
            
            params = []
            if start_date and end_date:
                query += " WHERE order_date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            query += " GROUP BY order_date, product, customer ORDER BY order_date DESC"
            
            df = pd.read_sql(query, conn, params=params if params else None)
            return df
    except Exception as e:
        print(f"Error getting sales summary: {e}")
        return pd.DataFrame()

# Initialize database when module is imported
init_database()