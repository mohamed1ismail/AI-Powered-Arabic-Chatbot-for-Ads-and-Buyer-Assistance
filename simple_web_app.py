from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'demo-secret-key-change-in-production'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simple_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Simple models for demo
class SimpleUser(db.Model):
    __tablename__ = 'simple_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SimpleAd(db.Model):
    __tablename__ = 'simple_ads'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('simple_users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    enhanced_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    location = db.Column(db.String(200))
    contact_info = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SimpleConversation(db.Model):
    __tablename__ = 'simple_conversations'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), default='initial')
    user_type = db.Column(db.String(20))
    context_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('simple_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create session ID
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Get or create conversation
        conversation = SimpleConversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            conversation = SimpleConversation(session_id=session_id, context_data='{}')
            db.session.add(conversation)
            db.session.commit()
        
        # Process message
        response = process_simple_message(conversation, message)
        
        return jsonify({
            'success': True,
            'response': response,
            'state': conversation.state,
            'user_type': conversation.user_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_simple_message(conversation, message):
    """Process user message with simple responses (no AI)"""
    
    if conversation.state == 'initial':
        conversation.state = 'waiting_user_type'
        db.session.commit()
        return "أهلاً بك 👋\nمن فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري"
    
    elif conversation.state == 'waiting_user_type':
        if '1' in message or 'معلن' in message:
            conversation.user_type = 'advertiser'
            conversation.state = 'advertiser_waiting_ad'
            db.session.commit()
            return "ممتاز! من فضلك اكتب تفاصيل إعلانك:\n• نوع المنتج أو الخدمة\n• السعر\n• معلومات الاتصال"
        elif '2' in message or 'مشتري' in message:
            conversation.user_type = 'buyer'
            conversation.state = 'buyer_waiting_query'
            db.session.commit()
            return "أخبرني، ما الذي تبحث عنه؟ 🔎\nمثال: أريد موبايل سامسونج بسعر أقل من 5000 جنيه"
        else:
            return "من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري"
    
    elif conversation.state == 'advertiser_waiting_ad':
        if len(message.split()) < 5:
            return "من فضلك اكتب تفاصيل أكثر عن إعلانك (على الأقل 5 كلمات)"
        
        # Simple text enhancement (demo version)
        enhanced_text = enhance_text_simple(message)
        
        # Store in context
        context = json.loads(conversation.context_data or '{}')
        context['original_ad'] = message
        context['enhanced_ad'] = enhanced_text
        conversation.context_data = json.dumps(context)
        conversation.state = 'advertiser_confirming'
        db.session.commit()
        
        return f"ده النص المحسن لإعلانك ✅:\n\n{enhanced_text}\n\nهل توافق عليه؟\nاكتب 'نعم' للموافقة أو 'تعديل' لطلب تعديلات"
    
    elif conversation.state == 'advertiser_confirming':
        if 'نعم' in message or 'موافق' in message:
            # Save the ad
            context = json.loads(conversation.context_data or '{}')
            
            # Extract basic info
            price = extract_price_simple(context.get('original_ad', ''))
            location = extract_location_simple(context.get('original_ad', ''))
            contact = extract_contact_simple(context.get('original_ad', ''))
            category = extract_category_simple(context.get('original_ad', ''))
            
            # Create user if not exists
            user = SimpleUser.query.filter_by(name=f'web_user_{conversation.session_id}').first()
            if not user:
                user = SimpleUser(name=f'web_user_{conversation.session_id}')
                db.session.add(user)
                db.session.flush()
            
            ad = SimpleAd(
                user_id=user.id,
                original_text=context.get('original_ad', ''),
                enhanced_text=context.get('enhanced_ad', ''),
                category=category,
                price=price,
                location=location,
                contact_info=contact
            )
            
            db.session.add(ad)
            db.session.commit()
            
            conversation.state = 'completed'
            db.session.commit()
            
            return f"تم حفظ إعلانك بنجاح! 🎉\nرقم الإعلان: {ad.id}\n\nيمكنك بدء محادثة جديدة للبحث عن المنتجات أو إضافة إعلان آخر"
        
        elif 'تعديل' in message:
            conversation.state = 'advertiser_waiting_ad'
            db.session.commit()
            return "من فضلك اكتب النص المحدث لإعلانك:"
        else:
            return "من فضلك اكتب 'نعم' للموافقة أو 'تعديل' لطلب تعديلات"
    
    elif conversation.state == 'buyer_waiting_query':
        if len(message.split()) < 2:
            return "من فضلك اكتب تفاصيل أكثر عما تبحث عنه"
        
        # Search for ads
        ads = search_ads_simple(message)
        
        conversation.state = 'buyer_showing_results'
        db.session.commit()
        
        if ads:
            response = "إليك أفضل النتائج التي وجدتها لك: 🔍\n\n"
            
            for i, ad in enumerate(ads[:5], 1):
                response += f"{i}. {ad.enhanced_text[:80]}...\n"
                if ad.price:
                    response += f"   💰 السعر: {ad.price} جنيه\n"
                if ad.location:
                    response += f"   📍 المكان: {ad.location}\n"
                if ad.contact_info:
                    response += f"   📞 التواصل: {ad.contact_info}\n"
                response += f"   🆔 رقم الإعلان: {ad.id}\n\n"
            
            response += "اكتب رقم الإعلان للمزيد من التفاصيل أو ابحث عن شيء آخر"
            return response
        else:
            return "عذرًا، لم أجد نتائج مطابقة لطلبك 😔\nجرب البحث بكلمات مختلفة أو قم بتوسيع نطاق البحث"
    
    elif conversation.state == 'buyer_showing_results':
        if message.isdigit():
            ad_id = int(message)
            ad = SimpleAd.query.get(ad_id)
            if ad:
                response = f"📋 تفاصيل الإعلان رقم {ad_id}:\n\n"
                response += f"{ad.enhanced_text}\n\n"
                if ad.price:
                    response += f"💰 السعر: {ad.price} جنيه\n"
                if ad.location:
                    response += f"📍 المكان: {ad.location}\n"
                if ad.contact_info:
                    response += f"📞 للتواصل: {ad.contact_info}\n"
                response += f"\n🕒 تاريخ النشر: {ad.created_at.strftime('%Y-%m-%d')}"
                return response
            else:
                return "عذراً، لم أجد إعلان بهذا الرقم"
        else:
            # New search
            conversation.state = 'buyer_waiting_query'
            db.session.commit()
            return process_simple_message(conversation, message)
    
    return "شكرًا لك! كيف يمكنني مساعدتك أكثر؟"

def enhance_text_simple(text):
    """Simple text enhancement without AI"""
    lines = text.split('\n')
    enhanced = []
    
    enhanced.append("🌟 عرض مميز 🌟")
    enhanced.append("")
    
    for line in lines:
        if line.strip():
            enhanced.append(f"✅ {line.strip()}")
    
    enhanced.append("")
    enhanced.append("📞 للاستفسار والحجز اتصل الآن!")
    enhanced.append("💯 جودة مضمونة وأسعار منافسة")
    
    return '\n'.join(enhanced)

def extract_price_simple(text):
    """Extract price from text"""
    import re
    patterns = [r'(\d+)\s*جنيه', r'(\d+)\s*ج\.م', r'(\d+)\s*ريال', r'(\d+)\s*درهم']
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    return None

def extract_location_simple(text):
    """Extract location from text"""
    locations = ['القاهرة', 'الجيزة', 'الإسكندرية', 'أسوان', 'أسيوط', 'طنطا', 'المنصورة']
    for location in locations:
        if location in text:
            return location
    return None

def extract_contact_simple(text):
    """Extract contact info from text"""
    import re
    phone_match = re.search(r'01[0-9]{9}', text)
    if phone_match:
        return phone_match.group(0)
    return None

def extract_category_simple(text):
    """Extract category from text"""
    categories = {
        'موبايل': ['موبايل', 'جوال', 'هاتف', 'تليفون'],
        'سيارات': ['سيارة', 'عربية', 'أوتوموبيل'],
        'عقارات': ['شقة', 'فيلا', 'بيت', 'منزل'],
        'إلكترونيات': ['تلفزيون', 'لابتوب', 'كمبيوتر']
    }
    
    text_lower = text.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    return 'عام'

def search_ads_simple(query):
    """Simple ad search"""
    # Search in enhanced text
    ads = SimpleAd.query.filter(SimpleAd.enhanced_text.contains(query)).order_by(SimpleAd.created_at.desc()).all()
    
    if not ads:
        # Fallback: search by category
        category = extract_category_simple(query)
        if category != 'عام':
            ads = SimpleAd.query.filter(SimpleAd.category == category).order_by(SimpleAd.created_at.desc()).all()
    
    return ads

@app.route('/api/ads', methods=['GET'])
def get_ads():
    """Get all ads"""
    try:
        ads = SimpleAd.query.order_by(SimpleAd.created_at.desc()).limit(20).all()
        return jsonify({
            'success': True,
            'ads': [{
                'id': ad.id,
                'enhanced_text': ad.enhanced_text,
                'category': ad.category,
                'price': ad.price,
                'location': ad.location,
                'contact_info': ad.contact_info,
                'created_at': ad.created_at.isoformat()
            } for ad in ads]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation state"""
    try:
        session_id = session.get('session_id')
        if session_id:
            conversation = SimpleConversation.query.filter_by(session_id=session_id).first()
            if conversation:
                conversation.state = 'initial'
                conversation.user_type = None
                conversation.context_data = '{}'
                db.session.commit()
        
        return jsonify({'success': True, 'message': 'Conversation reset'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Arabic AI Chatbot Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    print("This is a demo version that works without OpenAI API")
    print("To use full AI features, set up your OpenAI API key in .env file")
    app.run(debug=True, host='0.0.0.0', port=5000)
