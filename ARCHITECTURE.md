# Arabic AI Chatbot - System Architecture

## Overview
This is an AI-powered Arabic chatbot system that works across multiple social media platforms (Facebook Messenger, WhatsApp, Instagram, Telegram) with two main user flows: Advertisers and Buyers.

## System Components

### 1. Core Flask Application
- **Main Entry Point**: `src/main.py`
- **Database**: SQLite with SQLAlchemy ORM
- **Configuration**: Environment-based configuration
- **CORS**: Enabled for cross-origin requests

### 2. Database Models
- **User Model**: Store user information and conversation state
- **Ad Model**: Store advertisement data with approval status
- **Conversation Model**: Track conversation history and state
- **Platform Model**: Store platform-specific user identifiers

### 3. AI Services
- **Text Enhancement Service**: Uses OpenAI API to improve Arabic ad text
- **Search Analysis Service**: Extracts keywords and intent from buyer queries
- **Language Processing**: Arabic text processing utilities
- **Intent Recognition**: Classify user messages and determine appropriate responses

### 4. Social Media Integrations
- **Facebook Messenger**: Webhook handler for Messenger API
- **WhatsApp Business**: Integration with WhatsApp Business API
- **Instagram Messaging**: Handler for Instagram Direct Messages
- **Telegram Bot**: Telegram Bot API integration
- **Unified Message Handler**: Common interface for all platforms

### 5. API Endpoints

#### Webhook Endpoints
- `POST /webhooks/facebook` - Facebook Messenger webhook
- `POST /webhooks/whatsapp` - WhatsApp Business webhook
- `POST /webhooks/instagram` - Instagram Messaging webhook
- `POST /webhooks/telegram` - Telegram Bot webhook

#### Ad Management APIs
- `POST /api/ads/submit` - Submit new advertisement
- `GET /api/ads/search` - Search advertisements
- `PUT /api/ads/{id}/approve` - Admin approve advertisement
- `PUT /api/ads/{id}/reject` - Admin reject advertisement

#### User Management APIs
- `POST /api/users` - Create/update user
- `GET /api/users/{id}/conversations` - Get user conversation history

## Conversation Flow

### Advertiser Flow (معلن)
1. **Welcome Message**: "أهلاً بك 👋، من فضلك اختر: 1️⃣ أنا معلن 2️⃣ أنا مشتري"
2. **Ad Input**: Request ad details (minimum 3 lines)
3. **AI Enhancement**: Improve ad text using OpenAI API
4. **Confirmation**: Show enhanced text and ask for approval
5. **Submission**: Send to backend API for admin review
6. **Admin Review**: Wait for admin approval/rejection
7. **Result**: Send success message with link or rejection notice

### Buyer Flow (مشتري)
1. **Welcome Message**: Same as advertiser
2. **Search Query**: "أخبرني، ما الذي تبحث عنه بالضبط؟ 🔎"
3. **AI Analysis**: Extract keywords, category, price range, intent
4. **API Query**: Search ads database with refined parameters
5. **Results Display**: Show matching ads with title, price, link, image

## State Management
- **Session Storage**: Redis or in-memory storage for conversation state
- **User Context**: Track current conversation step and user type
- **Platform Mapping**: Map platform-specific user IDs to internal user IDs

## Security & Configuration
- **Environment Variables**: API keys and secrets
- **Webhook Verification**: Verify incoming webhook requests
- **Rate Limiting**: Prevent abuse of API endpoints
- **Input Validation**: Sanitize and validate all user inputs

## Deployment Architecture
- **Flask Application**: Main backend service
- **Database**: SQLite for development, PostgreSQL for production
- **External APIs**: OpenAI API for text processing
- **Social Media APIs**: Platform-specific API integrations
- **Admin Interface**: Web interface for ad approval (optional)

## File Structure
```
arabic-chatbot/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   ├── ad.py
│   │   ├── conversation.py
│   │   └── platform.py
│   ├── routes/
│   │   ├── webhooks.py
│   │   ├── ads.py
│   │   └── users.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── text_enhancer.py
│   │   ├── search_analyzer.py
│   │   └── arabic_utils.py
│   ├── integrations/
│   │   ├── facebook.py
│   │   ├── whatsapp.py
│   │   ├── instagram.py
│   │   └── telegram.py
│   ├── utils/
│   │   ├── message_handler.py
│   │   ├── state_manager.py
│   │   └── validators.py
│   └── main.py
├── config/
│   └── settings.py
├── requirements.txt
└── README.md
```

## Environment Variables Required
- `OPENAI_API_KEY`: OpenAI API key for text processing
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Facebook page access token
- `FACEBOOK_VERIFY_TOKEN`: Facebook webhook verification token
- `WHATSAPP_ACCESS_TOKEN`: WhatsApp Business API token
- `INSTAGRAM_ACCESS_TOKEN`: Instagram messaging access token
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Flask secret key for sessions

