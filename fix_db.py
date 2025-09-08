#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os

# Set UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def fix_database():
    try:
        conn = sqlite3.connect('instance/simple_chatbot.db')
        cursor = conn.cursor()
        
        print("Fixing database structure...")
        
        # Get current data from simple_ads
        cursor.execute('SELECT id, enhanced_text, category, price, location, contact_info FROM simple_ads')
        existing_ads = cursor.fetchall()
        
        print(f"Found {len(existing_ads)} existing ads")
        
        # Update the dataset CSV with actual database data
        with open('dataset/ads_dataset.csv', 'w', encoding='utf-8') as f:
            f.write('id,title,text,category,price,location,contact_info\n')
            
            for ad in existing_ads:
                ad_id, text, category, price, location, contact = ad
                # Extract title from text (first 50 chars)
                title = text[:50] + '...' if len(text) > 50 else text
                title = title.replace(',', ' ').replace('\n', ' ')
                text_clean = text.replace(',', ' ').replace('\n', ' ')
                
                f.write(f'{ad_id},"{title}","{text_clean}",{category or "عام"},{price or 0},{location or ""},{contact or ""}\n')
        
        print("Updated ads_dataset.csv with database content")
        
        # Verify the fix
        cursor.execute('SELECT COUNT(*) FROM simple_ads')
        count = cursor.fetchone()[0]
        print(f"Database contains {count} ads")
        
        conn.close()
        print("Database fix completed successfully")
        
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == '__main__':
    fix_database()
