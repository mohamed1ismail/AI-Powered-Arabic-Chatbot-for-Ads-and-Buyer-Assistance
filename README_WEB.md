# Arabic AI Chatbot - Web Interface

A simple web interface for testing the Arabic AI Chatbot for advertisement management and buyer assistance.

## Features

- **Arabic Language Support**: Full RTL support and Arabic text processing
- **Dual Mode Operation**: 
  - Advertiser mode: AI-enhanced ad creation
  - Buyer mode: Intelligent product search
- **Real-time Chat Interface**: Modern, responsive web UI
- **AI-Powered Text Enhancement**: Automatic ad improvement using OpenAI
- **Smart Search**: Arabic text analysis and product matching

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables
Copy `.env.example` to `.env` and add your OpenAI API key:
```bash
cp .env.example .env
```

Edit `.env` file:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Run the Application
```bash
python web_app.py
```

### 4. Open in Browser
Navigate to: http://localhost:5000

## How to Use

### For Advertisers:
1. Start a conversation
2. Choose "أنا معلن" (I'm an advertiser)
3. Write your ad text in Arabic
4. Review the AI-enhanced version
5. Confirm to publish

### For Buyers:
1. Start a conversation  
2. Choose "أنا مشتري" (I'm a buyer)
3. Describe what you're looking for in Arabic
4. Browse search results
5. Click on ad numbers for details

## Example Interactions

**Advertiser Example:**
```
User: أنا معلن
Bot: ممتاز! من فضلك اكتب تفاصيل إعلانك...
User: موبايل سامسونج للبيع بحالة ممتازة السعر 3000 جنيه للتواصل 01234567890
Bot: ده النص المحسن لإعلانك...
```

**Buyer Example:**
```
User: أنا مشتري
Bot: أخبرني، ما الذي تبحث عنه بالضبط؟
User: أريد موبايل سامسونج بسعر أقل من 5000 جنيه
Bot: إليك أفضل النتائج التي وجدتها لك...
```

## API Endpoints

- `POST /api/chat` - Send chat messages
- `GET /api/ads` - Get all approved ads
- `POST /api/reset` - Reset conversation state

## Database

The application uses SQLite database (`chatbot.db`) with the following tables:
- `users` - User information
- `ads` - Advertisement data
- `conversations` - Chat conversation states

## Troubleshooting

1. **OpenAI API Error**: Make sure your API key is valid and has credits
2. **Database Error**: Delete `chatbot.db` to reset the database
3. **Import Error**: Ensure all dependencies are installed with `pip install -r requirements.txt`

## Notes

- This is a demo/testing interface
- All ads are auto-approved for testing purposes
- The AI service requires a valid OpenAI API key
- Arabic text processing works offline
