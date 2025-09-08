#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

def check_schema():
    """Check the database schema and sample data with proper encoding."""
    try:
        # Set stdout to use UTF-8 encoding
        sys.stdout.reconfigure(encoding='utf-8')
        
        conn = sqlite3.connect('instance/simple_chatbot.db')
        conn.text_factory = str  # This will return strings as UTF-8
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
        
        # Get sample data - only show first 100 characters of each text field
        cursor.execute("""
            SELECT 
                id, 
                substr(original_text, 1, 100) || '...' as original_text_preview,
                substr(enhanced_text, 1, 100) || '...' as enhanced_text_preview,
                category,
                price,
                location
            FROM simple_ads 
            LIMIT 3
        """)
        
        sample_data = cursor.fetchall()
        print("\nSample data (first 100 chars of text fields):")
        for row in sample_data:
            print(f"\nAd ID: {row[0]}")
            print(f"Original: {row[1]}")
            print(f"Enhanced: {row[2]}")
            print(f"Category: {row[3]}")
            print(f"Price: {row[4]}")
            print(f"Location: {row[5]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_schema()
