from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import uuid

# Import our models and services
from user import User
from ad import Ad, AdStatus
from ai_service import AIService
from arabic_utils import ArabicTextProcessor
from conversation import Conversation, ConversationState, UserType

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize services
ai_service = AIService()
arabic_processor = ArabicTextProcessor()

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

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
        
        # Get or create user for this session
        user = User.query.filter_by(name=f'web_user_{session_id}').first()
        if not user:
            user = User(name=f'web_user_{session_id}', preferred_language='ar')
            db.session.add(user)
            db.session.commit()
        
        # Get or create conversation
        conversation = Conversation.get_or_create('web', session_id, user.id)
        
        # Process message based on conversation state
        response = process_message(conversation, message)
        
        return jsonify({
            'success': True,
            'response': response,
            'state': conversation.state.value,
            'user_type': conversation.user_type.value if conversation.user_type else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_message(conversation, message):
    """Process user message based on conversation state"""
    
    if conversation.state == ConversationState.INITIAL:
        # Welcome message
        conversation.set_state(ConversationState.WAITING_USER_TYPE)
        return ai_service.generate_response_message("", message, "welcome")
    
    elif conversation.state == ConversationState.WAITING_USER_TYPE:
        # User choosing between advertiser or buyer
        if '1' in message or 'معلن' in message or 'اعلن' in message:
            conversation.set_user_type(UserType.ADVERTISER)
            conversation.set_state(ConversationState.ADVERTISER_WAITING_AD)
            return ai_service.generate_response_message("", message, "advertiser_request_ad")
        elif '2' in message or 'مشتري' in message or 'شاري' in message:
            conversation.set_user_type(UserType.BUYER)
            conversation.set_state(ConversationState.BUYER_WAITING_QUERY)
            return ai_service.generate_response_message("", message, "buyer_request_search")
        else:
            return "من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري"
    
    elif conversation.state == ConversationState.ADVERTISER_WAITING_AD:
        # Process advertisement text
        if len(message.split()) < 5:
            return "من فضلك اكتب تفاصيل أكثر عن إعلانك (على الأقل 5 كلمات)"
        
        # Enhance the ad text
        enhancement_result = ai_service.enhance_ad_text(message)
        enhanced_text = enhancement_result.get('enhanced_text', message)
        
        # Store in conversation context
        conversation.update_context('original_ad', message)
        conversation.update_context('enhanced_ad', enhanced_text)
        conversation.update_context('enhancement_result', enhancement_result)
        
        conversation.set_state(ConversationState.ADVERTISER_CONFIRMING)
        
        return f"{ai_service.generate_response_message('', message, 'ad_enhanced')}\n\n{enhanced_text}"
    
    elif conversation.state == ConversationState.ADVERTISER_CONFIRMING:
        # User confirming or requesting changes to enhanced ad
        if 'نعم' in message or 'موافق' in message or 'اوافق' in message:
            # Save the ad to database
            context = conversation.get_context()
            
            # Analyze the ad for category, price, etc.
            analysis = arabic_processor.analyze_search_intent(context.get('original_ad', ''))
            
            ad = Ad(
                user_id=conversation.user_id,
                original_text=context.get('original_ad', ''),
                enhanced_text=context.get('enhanced_ad', ''),
                status=AdStatus.APPROVED,  # Auto-approve for demo
                category=analysis.get('category'),
                price=analysis.get('price_info', {}).get('value') if analysis.get('price_info') else None,
                location=analysis.get('location'),
                contact_info=extract_contact_info(context.get('original_ad', ''))
            )
            
            db.session.add(ad)
            db.session.commit()
            
            conversation.set_state(ConversationState.ADVERTISER_SUBMITTED)
            return f"{ai_service.generate_response_message('', message, 'ad_submitted')}\n\nرقم الإعلان: {ad.id}"
        
        elif 'تعديل' in message or 'تغيير' in message:
            conversation.set_state(ConversationState.ADVERTISER_WAITING_AD)
            return "من فضلك اكتب النص المحدث لإعلانك:"
        else:
            return "من فضلك اكتب 'نعم' للموافقة أو 'تعديل' لطلب تعديلات"
    
    elif conversation.state == ConversationState.BUYER_WAITING_QUERY:
        # Process buyer search query
        if len(message.split()) < 2:
            return "من فضلك اكتب تفاصيل أكثر عما تبحث عنه"
        
        # Analyze the search query
        analysis_result = ai_service.analyze_buyer_query(message)
        search_params = analysis_result.get('search_parameters', {})
        
        # Search for ads
        ads = Ad.search_ads(
            query=message,
            category=search_params.get('category'),
            min_price=search_params.get('price_min'),
            max_price=search_params.get('price_max'),
            location=search_params.get('location')
        )
        
        conversation.set_state(ConversationState.BUYER_SHOWING_RESULTS)
        
        if ads:
            response = ai_service.generate_response_message('', message, 'search_results')
            response += "\n\n"
            
            for i, ad in enumerate(ads[:5], 1):  # Show top 5 results
                response += f"{i}. {ad.enhanced_text[:100]}...\n"
                if ad.price:
                    response += f"   💰 السعر: {arabic_processor.format_price(ad.price)}\n"
                if ad.location:
                    response += f"   📍 المكان: {ad.location}\n"
                if ad.contact_info:
                    response += f"   📞 التواصل: {ad.contact_info}\n"
                response += f"   🆔 رقم الإعلان: {ad.id}\n\n"
            
            response += "اكتب رقم الإعلان للمزيد من التفاصيل أو ابحث عن شيء آخر"
            return response
        else:
            return ai_service.generate_response_message('', message, 'no_results')
    
    elif conversation.state == ConversationState.BUYER_SHOWING_RESULTS:
        # Handle ad selection or new search
        if message.isdigit():
            ad_id = int(message)
            ad = Ad.query.get(ad_id)
            if ad and ad.status == AdStatus.APPROVED:
                response = f"📋 تفاصيل الإعلان رقم {ad_id}:\n\n"
                response += f"{ad.enhanced_text}\n\n"
                if ad.price:
                    response += f"💰 السعر: {arabic_processor.format_price(ad.price)}\n"
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
            conversation.set_state(ConversationState.BUYER_WAITING_QUERY)
            return process_message(conversation, message)
    
    # Default response
    return ai_service.generate_response_message("", message, "default")

def extract_contact_info(text):
    """Extract contact information from text"""
    import re
    
    # Look for phone numbers
    phone_patterns = [
        r'01[0-9]{9}',  # Egyptian mobile
        r'\+20[0-9]{10}',  # Egyptian with country code
        r'[0-9]{11}'  # General 11-digit number
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    # Look for email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        return email_match.group(0)
    
    return None

@app.route('/api/ads', methods=['GET'])
def get_ads():
    """Get all approved ads"""
    try:
        ads = Ad.query.filter_by(status=AdStatus.APPROVED).order_by(Ad.created_at.desc()).limit(20).all()
        return jsonify({
            'success': True,
            'ads': [ad.to_dict() for ad in ads]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation state"""
    try:
        session_id = session.get('session_id')
        if session_id:
            user = User.query.filter_by(name=f'web_user_{session_id}').first()
            if user:
                conversation = Conversation.query.filter_by(
                    platform='web',
                    platform_user_id=session_id,
                    user_id=user.id
                ).first()
                if conversation:
                    conversation.set_state(ConversationState.INITIAL)
                    conversation.set_user_type(None)
                    conversation.set_context({})
        
        return jsonify({'success': True, 'message': 'Conversation reset'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
