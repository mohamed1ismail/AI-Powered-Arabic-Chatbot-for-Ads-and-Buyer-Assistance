#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_schema():
    """Check the database schema and sample data."""
    try:
        conn = sqlite3.connect('instance/simple_chatbot.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", tables)
        
        # Check simple_ads columns
        cursor.execute("PRAGMA table_info(simple_ads)")
        columns = cursor.fetchall()
        print("\nColumns in simple_ads:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Get sample data
        cursor.execute("SELECT * FROM simple_ads LIMIT 3")
        sample_data = cursor.fetchall()
        print("\nSample data:")
        for row in sample_data:
            print(row)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_schema()
