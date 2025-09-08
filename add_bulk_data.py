#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import random
import pandas as pd
from datetime import datetime

# --- Configuration ---
DB_PATH = 'instance/simple_chatbot.db'
CSV_PATH = 'dataset/ads_dataset.csv'
NUM_ADS_TO_ADD = 100
USER_ID = 1  # Assuming a default user ID for all ads

# --- Sample Data ---
PHONE_BRANDS = {
    'Samsung': ['Galaxy S24', 'Galaxy Z Fold 5', 'Galaxy A55', 'Galaxy S23 Ultra'],
    'Apple': ['iPhone 15 Pro Max', 'iPhone 15', 'iPhone 14 Pro', 'iPhone SE'],
    'Xiaomi': ['Redmi Note 13', 'Poco F6', 'Xiaomi 14', 'Redmi 12'],
    'Oppo': ['Reno 11', 'A78', 'Find X7', 'Reno 10'],
    'Realme': ['GT Neo 6', 'Realme 12 Pro+', 'C55', 'Narzo 50'],
}

CLOTHING_BRANDS = ['Nike', 'Adidas', 'Zara', 'H&M', 'Puma', 'LC Waikiki', 'Defacto']
CLOTHING_TYPES = {
    'هودي': ['صوف', 'ميلتون', 'قطن', 'مبطن'],
    'تيشيرت': ['قطن', 'بولو', 'أوفر سايز', 'رياضي'],
    'بنطلون': ['جينز', 'رياضي', 'قماش', 'جبردين']
}
CLOTHING_COLORS = ['أسود', 'أبيض', 'أزرق', 'رمادي', 'أحمر', 'أخضر', 'بيج']

LOCATIONS = ['القاهرة', 'الجيزة', 'الإسكندرية', 'المنصورة', 'أسيوط', 'الأقصر', 'طنطا']
CONDITIONS = ['جديد', 'استعمال خفيف', 'بحالة ممتازة']

# --- Helper Functions ---
def generate_random_price(min_price, max_price):
    """Generates a random price within a given range."""
    return round(random.uniform(min_price, max_price), 2)

def generate_clothing_data():
    """Generates a random set of data for a clothing ad."""
    item_type = random.choice(list(CLOTHING_TYPES.keys()))
    brand = random.choice(CLOTHING_BRANDS)
    material = random.choice(CLOTHING_TYPES[item_type])
    color = random.choice(CLOTHING_COLORS)
    condition = random.choice(CONDITIONS)
    price = generate_random_price(150, 2500)  # Price range for clothes
    location = random.choice(LOCATIONS)
    contact = f"01{random.randint(0, 2)}{random.randint(10000000, 99999999)}"
    
    title = f"{item_type} {brand} {material} - لون {color}"
    text = f"{title}, {condition}. السعر: {price} جنيه. للمعاينة في {location}. للتواصل: {contact}."
    
    return {
        'title': title,
        'text': text,
        'category': 'ملابس',
        'price': price,
        'location': location,
        'contact_info': contact
    }

# --- Main Script ---
def add_bulk_ads(num_ads, data_generator_func):
    """Adds a specified number of ads to the database and CSV file."""
    print(f"Starting to add {num_ads} new ads...")
    
    new_ads_for_db = []
    for _ in range(num_ads):
        ad_data = data_generator_func()
        new_ads_for_db.append((
            USER_ID,
            ad_data['text'],
            ad_data['text'],
            ad_data['category'],
            ad_data['price'],
            ad_data['location'],
            ad_data['contact_info'],
            'approved',  # Set as approved to be searchable
            datetime.utcnow()
        ))

    # --- Update SQLite Database ---
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.executemany("""
            INSERT INTO simple_ads (user_id, original_text, enhanced_text, category, price, location, contact_info, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, new_ads_for_db)
        
        conn.commit()
        print(f"Successfully added {len(new_ads_for_db)} ads to the database.")

        # --- Update CSV Dataset ---
        cursor.execute(f"SELECT id, enhanced_text, category, price, location, contact_info FROM simple_ads ORDER BY id DESC LIMIT {num_ads}")
        new_db_entries = cursor.fetchall()
        
        new_csv_rows = []
        for row in new_db_entries:
            ad_id, text, category, price, location, contact = row
            title = text.split('.')[0].strip()
            new_csv_rows.append({
                'id': ad_id,
                'title': title,
                'text': text,
                'category': category,
                'price': price,
                'location': location,
                'contact_info': contact
            })

        df = pd.DataFrame(new_csv_rows)
        df.to_csv(CSV_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
        print(f"Successfully appended {len(new_csv_rows)} ads to {CSV_PATH}.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Add 400 clothing ads
    add_bulk_ads(400, generate_clothing_data)
