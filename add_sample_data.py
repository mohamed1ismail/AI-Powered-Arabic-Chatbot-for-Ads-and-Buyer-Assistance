#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to add sample data with images to the Arabic AI Chatbot database
"""

import sys
import os
from datetime import datetime, timedelta
from simple_web_app import app, db, SimpleUser, SimpleAd

# Sample ad data with images
sample_ads = [
    {
        'original_text': 'موبايل سامسونج جالاكسي للبيع',
        'enhanced_text': '📱 موبايل سامسونج جالاكسي S23 للبيع - حالة ممتازة\n\n✨ المواصفات:\n• شاشة 6.1 بوصة Dynamic AMOLED\n• معالج Snapdragon 8 Gen 2\n• ذاكرة 256 جيجا\n• كاميرا 50 ميجابكسل\n• بطارية 3900 مللي أمبير\n\n💰 السعر: 15000 جنيه (قابل للتفاوض)\n📍 الموقع: القاهرة - مدينة نصر\n📞 للتواصل: 01012345678',
        'category': 'إلكترونيات',
        'price': 15000.0,
        'location': 'القاهرة - مدينة نصر',
        'contact_info': '01012345678',
        'image_url': 'sample_images/samsung_phone.jpg',
        'status': 'approved'
    },
    {
        'original_text': 'سيارة تويوتا كورولا 2020',
        'enhanced_text': '🚗 سيارة تويوتا كورولا 2020 للبيع - فرصة ذهبية!\n\n🔥 المميزات:\n• موديل 2020 - استعمال خفيف\n• محرك 1.6 لتر اقتصادي\n• ناقل حركة أوتوماتيك\n• مكيف هواء - نوافذ كهربائية\n• عداد: 45,000 كم فقط\n\n💵 السعر: 320,000 جنيه\n📍 الموقع: الإسكندرية\n📱 للاستفسار: 01098765432',
        'category': 'سيارات',
        'price': 320000.0,
        'location': 'الإسكندرية',
        'contact_info': '01098765432',
        'image_url': 'sample_images/toyota_corolla.jpg',
        'status': 'approved'
    },
    {
        'original_text': 'شقة للإيجار في المعادي',
        'enhanced_text': '🏠 شقة مفروشة للإيجار في المعادي - إطلالة رائعة!\n\n🌟 التفاصيل:\n• 3 غرف نوم + 2 حمام\n• مساحة 150 متر مربع\n• الدور الخامس - أسانسير\n• مفروشة بالكامل\n• قريبة من المترو والخدمات\n\n💰 الإيجار: 8,000 جنيه شهرياً\n📍 الموقع: المعادي - شارع 9\n☎️ للتواصل: 01155443322',
        'category': 'عقارات',
        'price': 8000.0,
        'location': 'المعادي - شارع 9',
        'contact_info': '01155443322',
        'image_url': 'sample_images/apartment_maadi.jpg',
        'status': 'approved'
    },
    {
        'original_text': 'لابتوب ديل للبيع',
        'enhanced_text': '💻 لابتوب ديل Inspiron 15 للبيع - مثالي للعمل والدراسة!\n\n⚡ المواصفات:\n• معالج Intel Core i5 الجيل العاشر\n• ذاكرة عشوائية 8 جيجا DDR4\n• قرص صلب SSD 256 جيجا\n• شاشة 15.6 بوصة Full HD\n• كارت شاشة Intel UHD\n\n💲 السعر: 12,000 جنيه\n📍 الموقع: الجيزة - المهندسين\n📞 اتصل بنا: 01077889900',
        'category': 'إلكترونيات',
        'price': 12000.0,
        'location': 'الجيزة - المهندسين',
        'contact_info': '01077889900',
        'image_url': 'sample_images/dell_laptop.jpg',
        'status': 'approved'
    },
    {
        'original_text': 'دراجة هوائية للبيع',
        'enhanced_text': '🚴‍♂️ دراجة هوائية جبلية للبيع - حالة ممتازة!\n\n🏔️ المميزات:\n• دراجة جبلية 21 سرعة\n• إطار ألومنيوم خفيف\n• فرامل قرصية أمامية وخلفية\n• عجلات 26 بوصة\n• مناسبة للطرق الوعرة والمدينة\n\n💰 السعر: 2,500 جنيه\n📍 الموقع: القاهرة - مصر الجديدة\n📱 للتواصل: 01066778899',
        'category': 'رياضة',
        'price': 2500.0,
        'location': 'القاهرة - مصر الجديدة',
        'contact_info': '01066778899',
        'image_url': 'sample_images/mountain_bike.jpg',
        'status': 'approved'
    }
]

def add_sample_data():
    """Add sample users and ads to the database"""
    
    with app.app_context():
        # Create a sample user if not exists
        user = SimpleUser.query.filter_by(name='مستخدم تجريبي').first()
        if not user:
            user = SimpleUser(
                name='مستخدم تجريبي'
            )
            db.session.add(user)
            db.session.commit()
            print("Created sample user")
        
        # Add sample ads
        for ad_data in sample_ads:
            # Check if ad already exists
            existing_ad = SimpleAd.query.filter_by(
                original_text=ad_data['original_text']
            ).first()
            
            if not existing_ad:
                ad = SimpleAd(
                    user_id=user.id,
                    original_text=ad_data['original_text'],
                    enhanced_text=ad_data['enhanced_text'],
                    category=ad_data['category'],
                    price=ad_data['price'],
                    location=ad_data['location'],
                    contact_info=ad_data['contact_info'],
                    image_url=ad_data['image_url'],
                    status=ad_data['status'],
                    approved_at=datetime.utcnow(),
                    ad_link=f"/ad/{hash(ad_data['original_text']) % 10000}"
                )
                db.session.add(ad)
                print("Added ad successfully")
        
        db.session.commit()
        print(f"\nAdded {len(sample_ads)} sample ads successfully!")
        
        # Print summary
        total_ads = SimpleAd.query.count()
        approved_ads = SimpleAd.query.filter_by(status='approved').count()
        print(f"Total ads: {total_ads}")
        print(f"Approved ads: {approved_ads}")

if __name__ == '__main__':
    add_sample_data()
