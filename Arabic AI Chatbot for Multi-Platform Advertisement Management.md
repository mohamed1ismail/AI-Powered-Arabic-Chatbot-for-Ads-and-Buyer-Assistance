# Arabic AI Chatbot for Multi-Platform Advertisement Management

🤖 **بوت ذكي للإعلانات باللغة العربية يعمل على منصات التواصل الاجتماعي المختلفة**

An intelligent Arabic chatbot that works across multiple social media platforms (Facebook Messenger, WhatsApp, Instagram, Telegram) to facilitate advertisement management between advertisers and buyers with AI-powered text enhancement and smart search capabilities.

## 🌟 Features

### Core Functionality
- **Multi-Platform Support**: Works seamlessly across Facebook Messenger, WhatsApp Business, Instagram Messaging, and Telegram
- **Arabic Language Processing**: Native Arabic text processing and conversation handling
- **Dual User Flow**: Separate workflows for advertisers and buyers
- **AI Text Enhancement**: Automatic improvement of advertisement text using AI
- **Smart Search**: Intelligent search functionality for buyers to find relevant ads
- **Admin Approval System**: Built-in moderation workflow for advertisement approval

### Advertiser Flow
1. **Welcome & Selection**: User selects "أنا معلن" (I am an advertiser)
2. **Ad Submission**: User writes advertisement details (minimum 3 lines)
3. **AI Enhancement**: System automatically improves the ad text with better formatting and marketing tone
4. **Review & Approval**: User reviews enhanced text and approves or requests modifications
5. **Publication**: Approved ads are submitted to admin review queue
6. **Notification**: User receives confirmation with ad ID and status

### Buyer Flow
1. **Welcome & Selection**: User selects "أنا مشتري" (I am a buyer)
2. **Search Query**: User describes what they're looking for in natural Arabic
3. **AI Analysis**: System analyzes the query to extract keywords, categories, and price ranges
4. **Results Display**: Relevant approved advertisements are shown to the user
5. **Continued Search**: User can perform additional searches or refine their criteria

## 🏗️ Architecture

### System Components
- **Flask Backend**: RESTful API server with webhook endpoints
- **Platform Integrations**: Dedicated handlers for each social media platform
- **AI Services**: Text processing and enhancement using OpenAI API
- **Database Layer**: SQLite database for storing ads, users, and conversations
- **State Management**: Conversation state tracking across platforms

### Project Structure
```
arabic-chatbot/
├── src/
│   ├── main.py                 # Main Flask application
│   ├── models/                 # Database models
│   │   ├── user.py
│   │   ├── ad.py
│   │   ├── conversation.py
│   │   └── platform.py
│   ├── routes/                 # API route handlers
│   │   ├── webhooks.py
│   │   ├── ads.py
│   │   └── user.py
│   ├── integrations/           # Social media platform integrations
│   │   ├── facebook.py
│   │   ├── whatsapp.py
│   │   ├── instagram.py
│   │   ├── telegram.py
│   │   └── platform_manager.py
│   ├── services/               # Core business logic
│   │   ├── ai_service.py
│   │   └── arabic_utils.py
│   └── utils/                  # Utility functions
│       ├── message_handler.py
│       └── state_manager.py
├── requirements.txt
├── README.md
└── DEPLOYMENT.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Flask 3.0+
- Access tokens for social media platforms
- OpenAI API key (optional, for AI enhancement)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd arabic-chatbot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export FACEBOOK_ACCESS_TOKEN="your-facebook-token"
export WHATSAPP_ACCESS_TOKEN="your-whatsapp-token"
export INSTAGRAM_ACCESS_TOKEN="your-instagram-token"
export TELEGRAM_BOT_TOKEN="your-telegram-token"
```

5. Run the application:
```bash
python src/main.py
```

The application will be available at `http://localhost:5000`

## 🔗 API Endpoints

### Webhook Endpoints
- `GET/POST /webhooks/facebook` - Facebook Messenger webhook
- `GET/POST /webhooks/whatsapp` - WhatsApp Business webhook  
- `GET/POST /webhooks/instagram` - Instagram Messaging webhook
- `POST /webhooks/telegram` - Telegram Bot webhook
- `GET /webhooks/status` - Webhook status and platform info
- `POST /webhooks/test` - Test webhook with sample message

### Advertisement API
- `POST /api/ads/submit` - Submit new advertisement
- `GET /api/ads/search` - Search approved advertisements
- `GET /api/ads/stats` - Get advertisement statistics
- `GET /api/ads/{id}` - Get advertisement by ID
- `PUT /api/ads/{id}/approve` - Approve advertisement (Admin)
- `PUT /api/ads/{id}/reject` - Reject advertisement (Admin)
- `GET /api/ads/pending` - Get pending advertisements (Admin)

### User API
- `GET/POST /api/users` - User management

## 🌐 Platform Configuration

### Facebook Messenger
1. Create a Facebook App and Page
2. Set up Messenger webhook with your domain
3. Configure page access token
4. Set webhook verify token

### WhatsApp Business
1. Set up WhatsApp Business API account
2. Configure webhook URL
3. Get access token and phone number ID
4. Verify webhook with challenge

### Instagram Messaging
1. Connect Instagram Business account to Facebook Page
2. Configure Instagram messaging webhook
3. Set up page access token with Instagram permissions

### Telegram
1. Create bot using @BotFather
2. Get bot token
3. Set webhook URL using Telegram API
4. Configure bot commands and menu

## 💬 Conversation Examples

### Arabic Conversation Flow

**User**: مرحبا
**Bot**: أهلاً بك 👋، من فضلك اختر:
1️⃣ أنا معلن
2️⃣ أنا مشتري

**Advertiser Flow**:
**User**: 1
**Bot**: ممتاز! من فضلك اكتب تفاصيل إعلانك في 3 أسطر على الأقل...

**Buyer Flow**:
**User**: 2  
**Bot**: أخبرني، ما الذي تبحث عنه بالضبط؟ 🔎

## 🔧 Configuration

### Environment Variables
```bash
# Required
FLASK_SECRET_KEY=your-secret-key

# Social Media Tokens
FACEBOOK_ACCESS_TOKEN=your-facebook-token
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token  
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
TELEGRAM_BOT_TOKEN=your-telegram-token

# Optional AI Enhancement
OPENAI_API_KEY=your-openai-key
OPENAI_API_BASE=https://api.openai.com/v1

# Webhook Verification
FACEBOOK_VERIFY_TOKEN=your-verify-token
WHATSAPP_VERIFY_TOKEN=your-verify-token
INSTAGRAM_VERIFY_TOKEN=your-verify-token
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
```

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `name`: User full name
- `phone`: Phone number
- `email`: Email address
- `platform_id`: Platform-specific user ID
- `platform`: Platform name (telegram, facebook, etc.)

### Ads Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `original_text`: Original ad text from user
- `enhanced_text`: AI-enhanced ad text
- `status`: pending/approved/rejected
- `category`: Ad category
- `price`: Product/service price
- `location`: Geographic location
- `created_at`: Creation timestamp

### Conversations Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `platform`: Platform name
- `state`: Current conversation state
- `data`: JSON data for conversation context

## 🚀 Deployment

The application is deployed and accessible at:
**https://58hpi8cpzekl.manus.space**

### Testing the Deployed API

Test the webhook status:
```bash
curl https://58hpi8cpzekl.manus.space/webhooks/status
```

Test chatbot conversation:
```bash
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "test_user", "message": "مرحبا"}'
```

## 🔒 Security Features

- **Webhook Verification**: All platforms use verification tokens/secrets
- **CORS Protection**: Cross-origin requests properly configured
- **Input Validation**: All user inputs are validated and sanitized
- **Admin Controls**: Advertisement approval workflow prevents spam
- **Rate Limiting**: Built-in protection against abuse

## 🌍 Internationalization

- **Primary Language**: Arabic (العربية)
- **Text Direction**: Right-to-left (RTL) support
- **Character Encoding**: UTF-8 throughout the system
- **Arabic Text Processing**: Native Arabic text analysis and keyword extraction

## 📈 Monitoring & Analytics

- **Real-time Statistics**: Track ads, users, and conversations
- **Platform Analytics**: Monitor performance across different platforms
- **Conversation Tracking**: Analyze user interaction patterns
- **Error Logging**: Comprehensive error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation in the `/docs` folder

## 🔄 Version History

- **v1.0.0** - Initial release with full multi-platform support
- Core Arabic chatbot functionality
- AI-powered text enhancement
- Complete advertiser/buyer workflows
- Admin approval system
- Production deployment

---

**Made with ❤️ for the Arabic-speaking community**

