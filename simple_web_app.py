import sys
import os

# Set UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import json
from models.gemini_image_search import create_gemini_image_search_model
from models.product_search_engine import ProductSearchEngine
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
app.secret_key = 'demo-secret-key-change-in-production'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simple_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize platform integrations (optional)
try:
    from instagram import InstagramMessaging
    from whatsapp import WhatsAppMessaging
    from facebook import FacebookMessaging
    from telegram import TelegramBot
    
    instagram = InstagramMessaging()
    whatsapp = WhatsAppMessaging()
    facebook = FacebookMessaging()
    telegram = TelegramBot()
    
    print("Platform integrations loaded successfully")
except ImportError as e:
    print(f"Platform integrations not available: {e}")
    instagram = whatsapp = facebook = telegram = None

# Configure file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'

# Dataset and AI Model Integration
class DatasetManager:
    def __init__(self):
        self.dataset_path = 'dataset/ads_dataset.csv'
        self.model_path = 'models/'
        self.vectorizer = None
        self.ad_vectors = None
        self.dataset = None
        
        os.makedirs('dataset', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        self.load_or_create_dataset()
    
    def load_or_create_dataset(self):
        """Load existing dataset or create new one"""
        try:
            if os.path.exists(self.dataset_path):
                self.dataset = pd.read_csv(self.dataset_path)
                print(f"📊 Loaded dataset with {len(self.dataset)} records")
            else:
                # Create initial dataset from existing ads
                self.create_initial_dataset()
            
            self.train_model()
        except Exception as e:
            print(f"Dataset error: {e}")
            self.dataset = pd.DataFrame(columns=['text', 'category', 'price', 'location'])
    
    def create_initial_dataset(self):
        """Create initial dataset from existing approved ads"""
        try:
            ads = SimpleAd.query.filter_by(status='approved').all()
            data = []
            
            for ad in ads:
                data.append({
                    'text': ad.enhanced_text,
                    'category': ad.category or 'عام',
                    'price': ad.price or 0,
                    'location': ad.location or '',
                    'contact_info': ad.contact_info or ''
                })
            
            self.dataset = pd.DataFrame(data)
            self.save_dataset()
            print(f"📊 Created initial dataset with {len(self.dataset)} records")
        except Exception as e:
            print(f"Error creating initial dataset: {e}")
            self.dataset = pd.DataFrame(columns=['text', 'category', 'price', 'location'])
    
    def add_to_dataset(self, ad):
        """Add new approved ad to dataset"""
        try:
            new_row = {
                'text': ad.enhanced_text,
                'category': ad.category or 'عام',
                'price': ad.price or 0,
                'location': ad.location or '',
                'contact_info': ad.contact_info or ''
            }
            
            self.dataset = pd.concat([self.dataset, pd.DataFrame([new_row])], ignore_index=True)
            self.save_dataset()
            self.train_model()  # Retrain model with new data
            print(f"Added ad to dataset. Total records: {len(self.dataset)}")
        except Exception as e:
            print(f"Error adding to dataset: {e}")
    
    def save_dataset(self):
        """Save dataset to CSV"""
        try:
            self.dataset.to_csv(self.dataset_path, index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"Error saving dataset: {e}")
    
    def train_model(self):
        """Train TF-IDF model for similarity search"""
        try:
            if len(self.dataset) == 0:
                return
            
            # Prepare text data
            texts = self.dataset['text'].fillna('').astype(str)
            
            # Train TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,  # Arabic stop words handled in arabic_utils
                ngram_range=(1, 2)
            )
            
            self.ad_vectors = self.vectorizer.fit_transform(texts)
            
            # Save model
            with open(f'{self.model_path}vectorizer.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            with open(f'{self.model_path}ad_vectors.pkl', 'wb') as f:
                pickle.dump(self.ad_vectors, f)
            
            print(f"🤖 Trained AI model with {len(texts)} samples")
        except Exception as e:
            print(f"Error training model: {e}")
    
    def search_similar_ads(self, query, top_k=5):
        """Find similar ads using AI model"""
        try:
            if self.vectorizer is None or self.ad_vectors is None:
                return []
            
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.ad_vectors).flatten()
            
            # Get top similar ads
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    results.append({
                        'text': self.dataset.iloc[idx]['text'],
                        'category': self.dataset.iloc[idx]['category'],
                        'price': self.dataset.iloc[idx]['price'],
                        'location': self.dataset.iloc[idx]['location'],
                        'similarity': similarities[idx]
                    })
            
            return results
        except Exception as e:
            print(f"Error in AI search: {e}")
            return []

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
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)
    ad_link = db.Column(db.String(500))
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

# Dataset manager will be initialized lazily when needed
dataset_manager = None

def get_dataset_manager():
    global dataset_manager
    if dataset_manager is None:
        dataset_manager = DatasetManager()
    return dataset_manager

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image_with_gemini(image_path):
    """Analyze image using Gemini AI to extract product information"""
    try:
        if not GEMINI_API_KEY:
            return {'success': False, 'error': 'Gemini API key not configured'}
        
        # Read and encode image
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Prepare request payload
        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": "حلل هذه الصورة واستخرج معلومات المنتج باللغة العربية. اذكر نوع المنتج، الماركة إن وجدت، اللون، والخصائص المميزة. اكتب الوصف بشكل مختصر ومفيد للبحث."
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make API request
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                description = result['candidates'][0]['content']['parts'][0]['text']
                return {'success': True, 'description': description}
            else:
                return {'success': False, 'error': 'No analysis result from Gemini'}
        else:
            return {'success': False, 'error': f'Gemini API error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Image analysis failed: {str(e)}'}

def search_products_by_image_description(description):
    """Search for products in database using image description"""
    try:
        # Get all approved ads
        ads = SimpleAd.query.filter_by(status='approved').all()
        
        if not ads:
            return []
        
        # Use AI search if available
        dataset_manager = get_dataset_manager()
        if dataset_manager:
            ai_results = dataset_manager.search_similar_ads(description, top_k=5)
            if ai_results:
                return ai_results
        
        # Fallback to simple text search
        results = []
        description_lower = description.lower()
        
        for ad in ads:
            ad_text = (ad.enhanced_text or ad.original_text or '').lower()
            category = (ad.category or '').lower()
            
            # Simple keyword matching
            if any(word in ad_text or word in category for word in description_lower.split()):
                results.append({
                    'id': ad.id,
                    'text': ad.enhanced_text or ad.original_text,
                    'price': ad.price,
                    'location': ad.location,
                    'contact': ad.contact_info,
                    'image_url': ad.image_url,
                    'similarity': 0.7  # Default similarity for fallback
                })
        
        return results[:5]  # Return top 5 matches
        
    except Exception as e:
        print(f"Error in image search: {e}")
        return []

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('simple_index.html')

@app.route('/admin')
def admin_panel():
    """Admin panel for managing ads"""
    pending_ads = SimpleAd.query.filter_by(status='pending').order_by(SimpleAd.created_at.desc()).all()
    return render_template('admin.html', ads=pending_ads)

# Platform webhook endpoints
@app.route('/webhook/instagram', methods=['GET', 'POST'])
def instagram_webhook():
    if request.method == 'GET':
        # Webhook verification
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')
        
        challenge = instagram.verify_webhook(hub_mode, hub_challenge, hub_verify_token)
        if challenge:
            return challenge
        return 'Verification failed', 403
    
    elif request.method == 'POST':
        # Process incoming messages
        data = request.get_json()
        events = instagram.parse_webhook_event(data)
        
        for event in events:
            if event['type'] == 'message':
                response = process_platform_message('instagram', event['sender_id'], event['text'])
                instagram.send_message(event['sender_id'], {'type': 'text', 'text': response})
        
        return 'OK', 200

@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')
        
        challenge = whatsapp.verify_webhook(hub_mode, hub_challenge, hub_verify_token)
        if challenge:
            return challenge
        return 'Verification failed', 403
    
    elif request.method == 'POST':
        data = request.get_json()
        events = whatsapp.parse_webhook_event(data)
        
        for event in events:
            if event['type'] == 'message':
                response = process_platform_message('whatsapp', event['sender_id'], event['text'])
                whatsapp.send_message(event['sender_id'], {'type': 'text', 'text': response})
        
        return 'OK', 200

@app.route('/webhook/facebook', methods=['GET', 'POST'])
def facebook_webhook():
    if request.method == 'GET':
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')
        
        challenge = facebook.verify_webhook(hub_mode, hub_challenge, hub_verify_token)
        if challenge:
            return challenge
        return 'Verification failed', 403
    
    elif request.method == 'POST':
        data = request.get_json()
        events = facebook.parse_webhook_event(data)
        
        for event in events:
            if event['type'] == 'message':
                response = process_platform_message('facebook', event['sender_id'], event['text'])
                facebook.send_message(event['sender_id'], {'type': 'text', 'text': response})
        
        return 'OK', 200

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload for ads and buyer image search"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Get session ID
            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'error': 'Session not found'}), 400
            
            # Get conversation
            conversation = SimpleConversation.query.filter_by(session_id=session_id).first()
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 400
            
            # Save file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Handle different states
            if conversation.state == 'advertiser_waiting_image':
                # Advertiser uploading product image
                context = json.loads(conversation.context_data or '{}')
                context['image_url'] = f"uploads/{unique_filename}"
                conversation.context_data = json.dumps(context)
                conversation.state = 'advertiser_confirming'
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'تم رفع الصورة بنجاح! ✅\n\nهل توافق على نشر الإعلان؟\nاكتب "نعم" للموافقة أو "تعديل" لطلب تعديلات',
                    'image_url': f"uploads/{unique_filename}"
                })
                
            elif conversation.state == 'buyer_waiting_image':
                # Buyer uploading image for search
                # Analyze image with Gemini AI
                analysis_result = analyze_image_with_gemini(file_path)
                
                if analysis_result['success']:
                    description = analysis_result['description']
                    
                    # Search for similar products
                    search_results = search_products_by_image_description(description)
                    
                    if search_results:
                        response = f"🔍 تم تحليل الصورة بنجاح!\n\n📝 وصف المنتج: {description}\n\n🛍️ وجدت هذه المنتجات المشابهة:\n\n"
                        
                        for i, result in enumerate(search_results, 1):
                            price_text = f"💰 {result['price']} جنيه" if result['price'] else "السعر غير محدد"
                            location_text = f"📍 {result['location']}" if result['location'] else ""
                            contact_text = f"📞 {result['contact']}" if result['contact'] else ""
                            
                            response += f"{i}. {result['text'][:100]}...\n"
                            response += f"{price_text}\n"
                            if location_text:
                                response += f"{location_text}\n"
                            if contact_text:
                                response += f"{contact_text}\n"
                            response += f"🔗 /ad/{result['id']}\n\n"
                    else:
                        response = f"🔍 تم تحليل الصورة:\n\n📝 وصف المنتج: {description}\n\n❌ لم أجد منتجات مشابهة في قاعدة البيانات حالياً"
                else:
                    response = f"❌ خطأ في تحليل الصورة: {analysis_result['error']}\nيرجى المحاولة مرة أخرى أو كتابة وصف نصي للمنتج"
                
                # Update conversation state
                conversation.state = 'buyer_waiting_query'
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': response,
                    'image_url': f"uploads/{unique_filename}"
                })
            else:
                return jsonify({'error': 'Invalid state for image upload'}), 400
        else:
            return jsonify({'error': 'نوع الملف غير مدعوم. يرجى رفع صورة (PNG, JPG, JPEG, GIF)'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        return "من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري"
    
    elif conversation.state == 'waiting_user_type':
        if message == '1' or 'معلن' in message:
            conversation.user_type = 'advertiser'
            conversation.state = 'advertiser_waiting_ad'
            db.session.commit()
            return "ممتاز! من فضلك اكتب تفاصيل إعلانك:\n• نوع المنتج أو الخدمة\n• السعر\n• معلومات الاتصال"
        elif message == '2' or 'مشتري' in message:
            conversation.user_type = 'buyer'
            conversation.state = 'buyer_waiting_query'
            db.session.commit()
            return "أخبرني، ما الذي تبحث عنه؟ \n\n يمكنك:\n• كتابة وصف نصي للمنتج\n• رفع صورة للمنتج الذي تبحث عنه \n\nمثال: أريد موبايل سامسونج بسعر أقل من 5000 جنيه"
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
        conversation.state = 'advertiser_waiting_image'
        db.session.commit()
        
        return f"ده النص المحسن لإعلانك ✅:\n\n{enhanced_text}\n\n📸 الآن من فضلك ارفع صورة للمنتج أو الخدمة\n(الصورة مطلوبة لنشر الإعلان)"
    
    elif conversation.state == 'advertiser_waiting_image':
        return "📸 من فضلك ارفع صورة للمنتج أو الخدمة من خلال الواجهة\n(لا يمكن رفع الصور من خلال النص)"
    
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
            
            # Check if image is uploaded
            image_url = context.get('image_url')
            if not image_url:
                return "❌ يجب رفع صورة للمنتج أولاً قبل نشر الإعلان"
            
            ad = SimpleAd(
                user_id=user.id,
                original_text=context.get('original_ad', ''),
                enhanced_text=context.get('enhanced_ad', ''),
                category=category,
                price=price,
                location=location,
                contact_info=contact,
                image_url=image_url,
                status='pending'  # Requires admin approval
            )
            
            db.session.add(ad)
            db.session.commit()
            
            conversation.state = 'completed'
            db.session.commit()
            
            # Notify admin about new ad
            notify_admin_new_ad(ad.id)
            
            return f"تم إرسال إعلانك للمراجعة! \nرقم الإعلان: {ad.id}\nسيتم إشعارك بالنتيجة خلال 24 ساعة"
        
        elif 'تعديل' in message:
            conversation.state = 'advertiser_waiting_ad'
            db.session.commit()
            return "من فضلك اكتب النص المحدث لإعلانك:"
        else:
            return "من فضلك اكتب 'نعم' للموافقة أو 'تعديل' لطلب تعديلات"
    
    elif conversation.state == 'buyer_waiting_query':
        # Check if user wants to upload image
        if 'صورة' in message or 'صوره' in message or 'رفع' in message or '📸' in message:
            conversation.state = 'buyer_waiting_image'
            db.session.commit()
            return "📸 ممتاز! ارفع صورة المنتج الذي تبحث عنه وسأحللها باستخدام الذكاء الاصطناعي للعثور على منتجات مشابهة"
        
        if len(message.split()) < 2:
            return "من فضلك اكتب تفاصيل أكثر عما تبحث عنه أو ارفع صورة للمنتج 📸"
        
        # Handle buyer search query with Gemini AI enhancement as the primary method
        try:
            search_text = message  # Default to original message
            try:
                # Attempt to enhance the query with Gemini AI first
                gemini_model = create_gemini_image_search_model()
                enhanced_query = gemini_model.analyze_text_query(message)
                
                if enhanced_query and enhanced_query.get('keywords'):
                    search_text = enhanced_query['keywords']
                    print(f"Using enhanced search query: {search_text}")
                else:
                    print("Gemini did not provide keywords, using original query.")
            except Exception as gemini_error:
                print(f"Gemini AI error, falling back to basic search: {gemini_error}")
            
            # Perform the search using the determined search text
            search_engine = ProductSearchEngine()
            results = search_engine.search_by_text(search_text)
            
            if results:
                response = "وجدت هذه النتائج:\n\n"
                for i, result in enumerate(results[:5], 1):
                    response += f"{i}. {result['title']}\n"
                    response += f"السعر: {result['price']}\n"
                    response += f"الموقع: {result['location']}\n"
                    response += f"التواصل: {result['contact']}\n"
                    if result.get('match_type'):
                        response += f"نوع المطابقة: {result['match_type']}\n"
                    response += f"رابط الإعلان: /ad/{result['id']}\n\n"
                
                response += "هل تريد البحث عن شيء آخر؟"
            else:
                response = "لم أجد إعلانات مطابقة لبحثك حالياً.\n\n"
                response += "جرب كلمات مختلفة أو ارفع صورة للمنتج\n\n"
                response += "أو اكتب استعلام جديد:"
            
            return response
            
        except Exception as e:
            print(f"Error in buyer search: {e}")
            # Fallback to regular search if Gemini fails
            try:
                search_engine = ProductSearchEngine()
                results = search_engine.search_by_text(message)
                
                if results:
                    response = "وجدت هذه النتائج:\n\n"
                    for i, result in enumerate(results[:5], 1):
                        response += f"{i}. {result['title']}\n"
                        response += f"السعر: {result['price']}\n"
                        response += f"الموقع: {result['location']}\n"
                        response += f"التواصل: {result['contact']}\n"
                        response += f"رابط الإعلان: /ad/{result['id']}\n\n"
                    
                    response += "هل تريد البحث عن شيء آخر؟"
                    return response
                else:
                    return "لم أجد إعلانات مطابقة لبحثك حالياً.\n\nجرب كلمات مختلفة أو ارفع صورة للمنتج"
            except:
                return "حدث خطأ في البحث. من فضلك حاول مرة أخرى."
    
    elif conversation.state == 'buyer_waiting_image':
        return "من فضلك ارفع صورة المنتج من خلال الواجهة\n(لا يمكن رفع الصور من خلال النص)"
    
    elif conversation.state == 'buyer_showing_results':
        if message.isdigit():
            ad_id = int(message)
            ad = SimpleAd.query.get(ad_id)
            if ad:
                response = f"تفاصيل الإعلان رقم {ad_id}:\n\n"
                response += f"{ad.enhanced_text}\n\n"
                if ad.price:
                    response += f"السعر: {ad.price} جنيه\n"
                if ad.location:
                    response += f"المكان: {ad.location}\n"
                if ad.contact_info:
                    response += f"للتواصل: {ad.contact_info}\n"
                response += f"\nتاريخ النشر: {ad.created_at.strftime('%Y-%m-%d')}"
                return response
            else:
                return "عذراً، لم أجد إعلان بهذا الرقم"
        else:
            # New search
            conversation.state = 'buyer_waiting_query'
            db.session.commit()
            return process_simple_message(conversation, message)
    
    elif conversation.state == 'completed':
        # After completing a flow, reset to initial to start over
        conversation.state = 'initial'
        conversation.user_type = None
        conversation.context_data = None
        db.session.commit()
        # Greet the user again to start a new flow
        return "شكرًا لك! كيف يمكنني مساعدتك الآن؟\n\n1️⃣ أنا معلن\n2️⃣ أنا مشتري"
    
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

def process_platform_message(platform, sender_id, message):
    """Process message from any platform"""
    # Get or create conversation for platform user
    conversation = SimpleConversation.query.filter_by(session_id=f"{platform}_{sender_id}").first()
    if not conversation:
        conversation = SimpleConversation(session_id=f"{platform}_{sender_id}", context_data='{}')
        db.session.add(conversation)
        db.session.commit()
    
    return process_simple_message(conversation, message)

def notify_admin_new_ad(ad_id):
    """Notify admin about new ad (placeholder for email/SMS notification)"""
    print(f"🔔 New ad #{ad_id} requires approval - Admin notification sent")
    # TODO: Implement actual notification (email, SMS, etc.)

def notify_advertiser_approval(ad_id, approved=True):
    """Notify advertiser about ad approval status"""
    ad = SimpleAd.query.get(ad_id)
    if ad:
        message = f"تم قبول إعلانك رقم {ad_id}! 🎉\nرابط الإعلان: {request.url_root}ad/{ad_id}" if approved else f"عذراً، لم يتم قبول إعلانك رقم {ad_id} ❌"
        print(f"📱 Notification sent to advertiser: {message}")
        # TODO: Send actual notification via platform

def search_ads_simple(query):
    """Simple ad search - only approved ads"""
    # Search in enhanced text for approved ads only
    ads = SimpleAd.query.filter(
        SimpleAd.enhanced_text.contains(query),
        SimpleAd.status == 'approved'
    ).order_by(SimpleAd.created_at.desc()).all()
    
    if not ads:
        # Fallback: search by category for approved ads only
        category = extract_category_simple(query)
        if category != 'عام':
            ads = SimpleAd.query.filter(
                SimpleAd.category == category,
                SimpleAd.status == 'approved'
            ).order_by(SimpleAd.created_at.desc()).all()
    
    return ads

# Admin approval endpoints
@app.route('/api/admin/approve/<int:ad_id>', methods=['POST'])
def approve_ad(ad_id):
    """Approve an ad"""
    try:
        ad = SimpleAd.query.get(ad_id)
        if not ad:
            return jsonify({'error': 'Ad not found'}), 404
        
        ad.status = 'approved'
        ad.approved_at = datetime.utcnow()
        ad.ad_link = f"{request.url_root}ad/{ad_id}"
        
        data = request.get_json() or {}
        ad.admin_notes = data.get('notes', '')
        
        db.session.commit()
        
        # Add to dataset for AI training
        get_dataset_manager().add_to_dataset(ad)
        
        # Notify advertiser
        notify_advertiser_approval(ad_id, approved=True)
        
        return jsonify({'success': True, 'message': 'Ad approved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/reject/<int:ad_id>', methods=['POST'])
def reject_ad(ad_id):
    """Reject an ad"""
    try:
        ad = SimpleAd.query.get(ad_id)
        if not ad:
            return jsonify({'error': 'Ad not found'}), 404
        
        ad.status = 'rejected'
        
        data = request.get_json() or {}
        ad.admin_notes = data.get('notes', 'Ad rejected by admin')
        
        db.session.commit()
        
        # Notify advertiser
        notify_advertiser_approval(ad_id, approved=False)
        
        return jsonify({'success': True, 'message': 'Ad rejected successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Public ad view
@app.route('/ad/<int:ad_id>')
def view_ad(ad_id):
    """View individual ad"""
    ad = SimpleAd.query.filter_by(id=ad_id, status='approved').first()
    if not ad:
        return "Ad not found or not approved", 404
    ad.text = ad.text.replace('\x00', '')
    return render_template('ad_view.html', ad=ad)

@app.route('/api/ads', methods=['GET'])
def get_ads():
    """Get all approved ads"""
    try:
        ads = SimpleAd.query.filter_by(status='approved').order_by(SimpleAd.created_at.desc()).limit(20).all()
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
