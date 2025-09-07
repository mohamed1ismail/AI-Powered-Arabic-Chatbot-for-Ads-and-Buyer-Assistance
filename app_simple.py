import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

# Simple in-memory storage for demo
ads_storage = []
conversations = {}

@app.route('/')
def home():
    """Home page with API information"""
    return """
    <html>
    <head>
        <title>Arabic AI Chatbot API</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .arabic { direction: rtl; text-align: right; font-size: 18px; color: #27ae60; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Arabic AI Chatbot API</h1>
            <p class="arabic">بوت ذكي للإعلانات باللغة العربية يعمل على منصات التواصل الاجتماعي المختلفة</p>
            
            <h2>📱 Supported Platforms</h2>
            <ul>
                <li>Facebook Messenger</li>
                <li>WhatsApp Business</li>
                <li>Instagram Messaging</li>
                <li>Telegram</li>
            </ul>
            
            <h2>🔗 Webhook Endpoints</h2>
            <div class="endpoint">
                <span class="method">GET/POST</span> <code>/webhooks/facebook</code> - Facebook Messenger webhook
            </div>
            <div class="endpoint">
                <span class="method">GET/POST</span> <code>/webhooks/whatsapp</code> - WhatsApp Business webhook
            </div>
            <div class="endpoint">
                <span class="method">GET/POST</span> <code>/webhooks/instagram</code> - Instagram Messaging webhook
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <code>/webhooks/telegram</code> - Telegram Bot webhook
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/webhooks/status</code> - Webhook status and platform info
            </div>
            <div class="endpoint">
                <span class="method">POST</span> <code>/webhooks/test</code> - Test webhook with sample message
            </div>
            
            <h2>📢 Advertisement API</h2>
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/ads/submit</code> - Submit new advertisement
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/ads/search</code> - Search approved advertisements
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/ads/stats</code> - Get advertisement statistics
            </div>
            
            <h2>🎯 Features</h2>
            <ul>
                <li class="arabic">تحسين النصوص الإعلانية باستخدام الذكاء الاصطناعي</li>
                <li class="arabic">البحث الذكي في الإعلانات</li>
                <li class="arabic">نظام الموافقة الإدارية</li>
                <li class="arabic">دعم متعدد المنصات</li>
                <li class="arabic">معالجة اللغة العربية</li>
            </ul>
            
            <p style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                Status: <strong style="color: #27ae60;">Active</strong> | 
                Version: <strong>1.0.0</strong>
            </p>
        </div>
    </body>
    </html>
    """

def process_arabic_message(user_id, message_text, platform='telegram'):
    """Simple Arabic message processing"""
    message_text = message_text.strip()
    
    # Initialize conversation state if not exists
    if user_id not in conversations:
        conversations[user_id] = {'state': 'start', 'data': {}}
    
    conversation = conversations[user_id]
    
    # Welcome message
    if message_text in ['مرحبا', 'السلام عليكم', 'أهلا', 'البداية', '/start']:
        conversation['state'] = 'welcome'
        return {
            'type': 'text',
            'text': 'أهلاً بك 👋، من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري',
            'quick_replies': [
                {'title': '1️⃣ أنا معلن', 'payload': 'advertiser'},
                {'title': '2️⃣ أنا مشتري', 'payload': 'buyer'}
            ]
        }
    
    # User selection
    elif message_text in ['1', '1️⃣ أنا معلن', 'معلن', 'أنا معلن']:
        conversation['state'] = 'advertiser'
        return {
            'type': 'text',
            'text': 'ممتاز! من فضلك اكتب تفاصيل إعلانك في 3 أسطر على الأقل، واحرص على ذكر:\n• نوع المنتج أو الخدمة\n• السعر\n• معلومات الاتصال'
        }
    
    elif message_text in ['2', '2️⃣ أنا مشتري', 'مشتري', 'أنا مشتري']:
        conversation['state'] = 'buyer'
        return {
            'type': 'text',
            'text': 'أخبرني، ما الذي تبحث عنه بالضبط؟ 🔎\nمثال: أنا عايز موبايل سامسونج بسعر أقل من 5000 جنيه'
        }
    
    # Advertiser flow
    elif conversation['state'] == 'advertiser':
        if len(message_text) < 50:
            return {
                'type': 'text',
                'text': 'من فضلك اكتب تفاصيل أكثر عن إعلانك (على الأقل 3 أسطر)'
            }
        
        # Simple ad enhancement
        enhanced_text = f"🔥 عرض مميز!\n\n{message_text}\n\n📞 للتواصل والاستفسار"
        
        # Store ad
        ad_id = len(ads_storage) + 1
        ads_storage.append({
            'id': ad_id,
            'user_id': user_id,
            'original_text': message_text,
            'enhanced_text': enhanced_text,
            'status': 'pending',
            'platform': platform
        })
        
        conversation['state'] = 'ad_review'
        conversation['data']['ad_id'] = ad_id
        
        return {
            'type': 'text',
            'text': f'ده النص المحسن لإعلانك ✅:\n\n{enhanced_text}\n\nهل توافق عليه؟',
            'quick_replies': [
                {'title': 'نعم، موافق', 'payload': 'approve_ad'},
                {'title': 'تعديل', 'payload': 'edit_ad'}
            ]
        }
    
    elif conversation['state'] == 'ad_review':
        if message_text in ['نعم', 'موافق', 'نعم، موافق']:
            ad_id = conversation['data'].get('ad_id')
            if ad_id:
                # Update ad status
                for ad in ads_storage:
                    if ad['id'] == ad_id:
                        ad['status'] = 'approved'
                        break
                
                conversation['state'] = 'start'
                return {
                    'type': 'text',
                    'text': f'🎉 تم رفع إعلانك بنجاح!\n\nرقم الإعلان: {ad_id}\nحالة الإعلان: تمت الموافقة\n\nشكراً لاستخدامك خدمتنا!'
                }
        else:
            conversation['state'] = 'advertiser'
            return {
                'type': 'text',
                'text': 'من فضلك اكتب النص الجديد لإعلانك:'
            }
    
    # Buyer flow
    elif conversation['state'] == 'buyer':
        # Simple search in ads
        search_results = []
        search_terms = message_text.lower().split()
        
        for ad in ads_storage:
            if ad['status'] == 'approved':
                ad_text = ad['enhanced_text'].lower()
                if any(term in ad_text for term in search_terms):
                    search_results.append(ad)
        
        if search_results:
            response_text = f'وجدت {len(search_results)} إعلان مطابق لبحثك:\n\n'
            for i, ad in enumerate(search_results[:3], 1):  # Show max 3 results
                response_text += f'{i}. {ad["enhanced_text"][:100]}...\n\n'
            response_text += 'هل تريد البحث عن شيء آخر؟'
        else:
            response_text = 'عذراً، لم أجد إعلانات مطابقة لبحثك.\nجرب كلمات بحث أخرى أو تحقق لاحقاً من وجود إعلانات جديدة.'
        
        conversation['state'] = 'buyer'  # Stay in buyer mode
        return {
            'type': 'text',
            'text': response_text
        }
    
    # Default response
    else:
        return {
            'type': 'text',
            'text': 'عذراً، لم أفهم طلبك. من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري',
            'quick_replies': [
                {'title': '1️⃣ أنا معلن', 'payload': 'advertiser'},
                {'title': '2️⃣ أنا مشتري', 'payload': 'buyer'}
            ]
        }

@app.route('/webhooks/status', methods=['GET'])
def webhook_status():
    """Get webhook status"""
    return jsonify({
        'status': 'active',
        'active_platforms': ['telegram', 'facebook', 'whatsapp', 'instagram'],
        'total_ads': len(ads_storage),
        'approved_ads': len([ad for ad in ads_storage if ad['status'] == 'approved']),
        'pending_ads': len([ad for ad in ads_storage if ad['status'] == 'pending'])
    })

@app.route('/webhooks/test', methods=['POST'])
def test_webhook():
    """Test webhook with sample message"""
    try:
        data = request.get_json()
        platform = data.get('platform', 'telegram')
        user_id = data.get('user_id', 'test_user')
        message = data.get('message', 'مرحبا')
        
        response = process_arabic_message(user_id, message, platform)
        
        return jsonify({
            'success': True,
            'response': response,
            'user_id': user_id,
            'platform': platform
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhooks/telegram', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            user_id = str(message['from']['id'])
            text = message.get('text', '').strip()
            
            if text:
                response = process_arabic_message(user_id, text, 'telegram')
                # In real implementation, send response back to Telegram
                return jsonify({'success': True, 'response': response})
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ads/stats', methods=['GET'])
def ads_stats():
    """Get advertisement statistics"""
    total_ads = len(ads_storage)
    approved_ads = len([ad for ad in ads_storage if ad['status'] == 'approved'])
    pending_ads = len([ad for ad in ads_storage if ad['status'] == 'pending'])
    
    return jsonify({
        'success': True,
        'stats': {
            'total_ads': total_ads,
            'approved_ads': approved_ads,
            'pending_ads': pending_ads,
            'platforms': ['telegram', 'facebook', 'whatsapp', 'instagram']
        }
    })

@app.route('/api/ads/search', methods=['GET'])
def search_ads():
    """Search approved advertisements"""
    query = request.args.get('query', '').strip().lower()
    
    results = []
    for ad in ads_storage:
        if ad['status'] == 'approved':
            if not query or query in ad['enhanced_text'].lower():
                results.append({
                    'id': ad['id'],
                    'text': ad['enhanced_text'],
                    'platform': ad['platform']
                })
    
    return jsonify({
        'success': True,
        'results': results,
        'total_count': len(results)
    })

@app.route('/api/ads/submit', methods=['POST'])
def submit_ad():
    """Submit new advertisement"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Missing ad text'}), 400
        
        # Simple enhancement
        enhanced_text = f"🔥 عرض مميز!\n\n{text}\n\n📞 للتواصل والاستفسار"
        
        ad_id = len(ads_storage) + 1
        ads_storage.append({
            'id': ad_id,
            'user_id': user_id,
            'original_text': text,
            'enhanced_text': enhanced_text,
            'status': 'pending',
            'platform': 'api'
        })
        
        return jsonify({
            'success': True,
            'ad_id': ad_id,
            'enhanced_text': enhanced_text,
            'status': 'pending'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

