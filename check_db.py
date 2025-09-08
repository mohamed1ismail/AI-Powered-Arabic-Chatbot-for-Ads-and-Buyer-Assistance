#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database():
    try:
        conn = sqlite3.connect('instance/simple_chatbot.db')
        cursor = conn.cursor()
        
        # Check current tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('Current tables:', tables)
        
        # Check if we have data
        try:
            cursor.execute('SELECT COUNT(*) FROM simple_ads')
            ads_count = cursor.fetchone()[0]
            print(f'Ads count: {ads_count}')
            
            cursor.execute('SELECT id, title, price FROM simple_ads LIMIT 3')
            sample_ads = cursor.fetchall()
            print('Sample ads:', sample_ads)
        except Exception as e:
            print('Error reading ads:', e)
        
        conn.close()
        print('Database check completed')
        
    except Exception as e:
        print('Database error:', e)

if __name__ == '__main__':
    check_database()
