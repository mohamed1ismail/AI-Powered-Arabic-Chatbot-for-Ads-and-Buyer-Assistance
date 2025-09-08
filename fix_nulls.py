#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def fix_null_characters():
    """Fix NUL characters in the database."""
    try:
        conn = sqlite3.connect('instance/simple_chatbot.db')
        cursor = conn.cursor()
        
        # Get all ads
        cursor.execute("SELECT id, original_text, enhanced_text FROM simple_ads")
        ads = cursor.fetchall()
        
        # Update each ad to remove NUL characters
        for ad_id, original_text, enhanced_text in ads:
            if '\x00' in str(original_text) or '\x00' in str(enhanced_text):
                print(f"Fixing NUL characters in ad {ad_id}")
                clean_original = original_text.replace('\x00', '') if original_text else ''
                clean_enhanced = enhanced_text.replace('\x00', '') if enhanced_text else ''
                
                cursor.execute(
                    "UPDATE simple_ads SET original_text = ?, enhanced_text = ? WHERE id = ?",
                    (clean_original, clean_enhanced, ad_id)
                )
        
        conn.commit()
        print("Successfully fixed NUL characters in the database.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_null_characters()
