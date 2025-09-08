# 🤖 Arabic Chatbot-smart chatbot system

A smart chatbot system in Arabic that works on multiple social media platforms, serving advertisers and buyers with an ad optimization system and smart search.

## ② Main features

### الاصطناعي artificial intelligence
- **Optimize texts**: optimize ads using GPT-4
- **Analysis of search queries**: understanding the intentions of users and extracting information
- **Smart search**: sort results by relevance and match
- **Interactive responses**: generate intelligent responses by context

### 📱 Social media platforms
- **Facebook Messenger**: support for Quick Replies and interactive messages
- **WhatsApp Business API**: support Interactive Buttons
- **Telegram Bot**: support for Inline Keyboards and commands
- **Instagram Messaging**: direct messages

### 👥 Two types of users

#### 📝 For advertisers
1. Write the details of the declaration (at least 3 lines)
2. Automatically optimize text with artificial intelligence
3. Review and approval of the improved text
4. Submit for administrative review
5. Get the announcement link upon admission

#### 🔍 For buyers
1. Describe in detail what they are looking for
2. Demand analysis and information extraction (Category, Price, Specifications)
3. Intelligent search of the advertising base
4. View results sorted by relevance

### 🛠️ Admin panel
- **Review ads**: accept or reject submitted ads
- **Comprehensive statistics**: number of ads, active sessions, etc
- **Session management**: monitor active conversations
- **Status of platforms**: monitor the status of social media platforms

## 🚀 Installation and operation

### Requirements
- Python 3.11+
- Flask
- OpenAI API Key
- Environment variables for social media platforms

### Installation steps

1. ** Reproduction of the project**
```bash
git clone <repository-url>
cd arabic-chatbot-backend
```

2. ** Activation of the virtual environment**
```bash
source venv/bin/activate
```

3. ** Installation requirements**
```bash
pip install -r requirements.txt
```

4. ** Setting environment variables**
```bash
cp .env.example .env
# Make an adjustment .env and add your own keys
```

5. ** Running the application**
```bash
python src/main.py
```

## ⚙️ Setting up social media platforms

### Facebook Messenger
```env
FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_VERIFY_TOKEN=arabic_chatbot_verify_token
```

### WhatsApp Business API
```env
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=arabic_chatbot_whatsapp_verify
```

### Telegram Bot
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Instagram Messaging API
```env
INSTAGRAM_PAGE_ACCESS_TOKEN=your_instagram_page_access_token
INSTAGRAM_APP_SECRET=your_instagram_app_secret
```

## 📡 API Endpoints

### Chatbot API
- `POST / api/chatbot / start` - start a new conversation
- `POST / api/chatbot/user-type` - specify the user type
- `POST / api/chatbot/process-ad` - processing the advertiser's ad
- `POST / api/chatbot/search` - search for buyers
- 'GET / api/chatbot/help` - help

### Ads API
- `POST / api/ads/submit` - submit a new ad
- 'GET / api/ads/search` - Search Ads
- 'GET / api/ads / <id>` - get a specific ad

### Admin API
- 'GET / api/admin` - admin panel
- 'GET / api/admin/stats` - Statistics
- 'GET / api/admin/ads` - all ads
- `POST /api/admin/ads / <id> / approve` - accept the ad
- `POST /api/admin/ads / <id>/reject` - reject an ad

### Webhooks
- `GET/POST /api/webhook/facebook` - Facebook Messenger
- `GET/POST /api/webhook/whatsapp` - WhatsApp Business
- `POST /api/webhook/telegram` - Telegram Bot
- `GET/POST /api/webhook/instagram` - Instagram Messaging
- `POST / api/webhook/test` - Test the webhook

## 🏗️ Project structure

```
arabic-chatbot-backend/
├── src/
 ξ ├-- models / # database models
】 │ - - user.py # user form
】 │ - - ad.py # advertising form
】 ├-- routes / # API paths
【 】 ├-- user.py # user paths
【 】 ├-- ads.py # advertising tracks
【 】 ├-- chatbot.py # chatbot tracks
【 】 ├-- webhooks.py # webhooks tracks
【 】 └-- admin.py # management paths
 ξ ├-- ai_services.py # artificial intelligence services
 ξ ├-- social_integrations.py # integration of communication platforms
 ξ ├-- config.py # platform settings
 ξ ├-- notification_system.py # notification system
 ξ ├-- database / # database
 ξ ├-- static / # static files
 ξ └-- main.py # starting point
├── requirements.txt # requirements
├── .env.example # example environment variables
└-- README.md # this file
```

## الاستخدام usage

### 1. Access to the admin panel
Open the browser and go to: `http://localhost:5000/api/admin`

### 2. Chatbot testing
```bash
curl -X POST http://localhost:5000/api/webhook/test \
  -H "Content-Type: application/json" \
  -d ' {"platform": "test", "user_id": "test_user", "message": "Hello"}'
```

### 3. Submit an ad for testing
```bash
curl -X POST http://localhost:5000/api/ads/submit \
  -H "Content-Type: application/json" \
  - d ' {"ad_text": "for sale iPhone 14 Mobile in excellent condition at a price of 15000 EGP to contact 01234567890"}'
```

## 🔍 Monitoring and diagnostics

### Health Check
```bash
curl http://localhost:5000/health
```

### The state of the platforms
```bash
curl http://localhost:5000/api/webhook/status
```

### System statistics
```bash
curl http://localhost:5000/api/admin/stats
```

## 🛡️ Security

- **Webhooks verification**: all webhooks are protected by verify tokens
- **CORS**: activated to allow requests from different sources
- **Error handling**: comprehensive error handling with clear messages
- **Data verification**: check and clean all inputs

## النشر publishing

### Local publishing
```bash
python src/main.py
```

### Publishing on production
1. Make sure all environment variables are set up
2. Use a WSGI server like Gunicorn
3. Set up a reverse proxy with Nginx
4. Activate HTTPS for security

## المساهمة contribution

1. Fork the project
2. Create a new branch (`git checkout-b feature/amazing-feature`)
3. Commit changes (`git commit-m 'Add amazing feature")
4. Push to Branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## الترخيص license

This project is licensed under the MIT license - see the [LICENSE](LICENSE) file for details.

## الدعم support

To get support or report problems:
- Open an Issue on GitHub
- Communication via e-mail
- Review of documents

## 🔄 Future updates

- [] Support more social media platforms
- [] Improved search algorithms
- [] Add an ad rating system
- [] Support attached photos and files
- [] Advanced analytics and reports
- [] Advanced notification system
- [] Support multiple languages

---

** Developed by ❤️ for the Arab community**
