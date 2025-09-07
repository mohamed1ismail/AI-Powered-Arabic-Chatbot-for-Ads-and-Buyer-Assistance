# API Documentation - Arabic AI Chatbot

This document provides comprehensive documentation for all API endpoints available in the Arabic AI Chatbot system.

## 🌐 Base URL

**Production**: `https://58hpi8cpzekl.manus.space`
**Local Development**: `http://localhost:5000`

## 🔐 Authentication

Most endpoints are public for webhook integration. Admin endpoints require proper authentication (to be implemented based on your security requirements).

## 📡 Webhook Endpoints

### Facebook Messenger Webhook

#### Verification (GET)
```http
GET /webhooks/facebook?hub.mode=subscribe&hub.challenge=CHALLENGE&hub.verify_token=VERIFY_TOKEN
```

**Parameters:**
- `hub.mode`: Must be "subscribe"
- `hub.challenge`: Challenge string from Facebook
- `hub.verify_token`: Your verification token

**Response:**
```
CHALLENGE (if verification successful)
```

#### Message Handling (POST)
```http
POST /webhooks/facebook
Content-Type: application/json
```

**Request Body:**
```json
{
  "object": "page",
  "entry": [
    {
      "id": "PAGE_ID",
      "time": 1458692752478,
      "messaging": [
        {
          "sender": {"id": "USER_ID"},
          "recipient": {"id": "PAGE_ID"},
          "timestamp": 1458692752478,
          "message": {
            "mid": "mid.1457764197618:41d102a3e1ae206a38",
            "text": "مرحبا"
          }
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "status": "OK"
}
```

### WhatsApp Business Webhook

#### Verification (GET)
```http
GET /webhooks/whatsapp?hub.mode=subscribe&hub.challenge=CHALLENGE&hub.verify_token=VERIFY_TOKEN
```

#### Message Handling (POST)
```http
POST /webhooks/whatsapp
Content-Type: application/json
```

**Request Body:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "PHONE_NUMBER",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "messages": [
              {
                "from": "PHONE_NUMBER",
                "id": "wamid.ID",
                "timestamp": "TIMESTAMP",
                "text": {
                  "body": "أنا عايز موبايل سامسونج"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

### Instagram Messaging Webhook

#### Verification (GET)
```http
GET /webhooks/instagram?hub.mode=subscribe&hub.challenge=CHALLENGE&hub.verify_token=VERIFY_TOKEN
```

#### Message Handling (POST)
```http
POST /webhooks/instagram
Content-Type: application/json
```

**Request Body:**
```json
{
  "object": "instagram",
  "entry": [
    {
      "id": "INSTAGRAM_ACCOUNT_ID",
      "time": 1569262486134,
      "messaging": [
        {
          "sender": {"id": "SENDER_ID"},
          "recipient": {"id": "RECIPIENT_ID"},
          "timestamp": 1569262485349,
          "message": {
            "mid": "MESSAGE_ID",
            "text": "مرحبا"
          }
        }
      ]
    }
  ]
}
```

### Telegram Bot Webhook

#### Message Handling (POST)
```http
POST /webhooks/telegram
Content-Type: application/json
X-Telegram-Bot-Api-Secret-Token: YOUR_SECRET_TOKEN
```

**Request Body:**
```json
{
  "update_id": 10000,
  "message": {
    "date": 1441645532,
    "chat": {
      "last_name": "Test Lastname",
      "id": 1111111,
      "first_name": "Test",
      "username": "Test"
    },
    "message_id": 1365,
    "from": {
      "last_name": "Test Lastname",
      "id": 1111111,
      "first_name": "Test",
      "username": "Test"
    },
    "text": "/start"
  }
}
```

### Webhook Status

#### Get Status
```http
GET /webhooks/status
```

**Response:**
```json
{
  "status": "active",
  "active_platforms": ["telegram", "facebook", "whatsapp", "instagram"],
  "total_ads": 15,
  "approved_ads": 12,
  "pending_ads": 3
}
```

### Test Webhook

#### Test Message Processing
```http
POST /webhooks/test
Content-Type: application/json
```

**Request Body:**
```json
{
  "platform": "telegram",
  "user_id": "test_user_123",
  "message": "مرحبا",
  "user_name": "Test User"
}
```

**Response:**
```json
{
  "success": true,
  "platform": "telegram",
  "user_id": "test_user_123",
  "response": {
    "type": "text",
    "text": "أهلاً بك 👋، من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري",
    "quick_replies": [
      {"title": "1️⃣ أنا معلن", "payload": "advertiser"},
      {"title": "2️⃣ أنا مشتري", "payload": "buyer"}
    ]
  }
}
```

## 📢 Advertisement API

### Submit Advertisement

#### Create New Ad
```http
POST /api/ads/submit
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "text": "للبيع موبايل سامسونج جالاكسي S21 حالة ممتازة بسعر 8000 جنيه. للتواصل: 01234567890"
}
```

**Response:**
```json
{
  "success": true,
  "ad_id": 1,
  "enhanced_text": "🔥 عرض مميز!\n\nللبيع موبايل سامسونج جالاكسي S21 حالة ممتازة بسعر 8000 جنيه. للتواصل: 01234567890\n\n📞 للتواصل والاستفسار",
  "status": "pending"
}
```

### Search Advertisements

#### Search Approved Ads
```http
GET /api/ads/search?query=موبايل&category=electronics&min_price=1000&max_price=10000
```

**Query Parameters:**
- `query` (optional): Search text in Arabic
- `category` (optional): Advertisement category
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `location` (optional): Location filter
- `limit` (optional): Number of results (default: 10, max: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": 1,
      "text": "🔥 عرض مميز!\n\nللبيع موبايل سامسونج جالاكسي S21...",
      "platform": "telegram"
    }
  ],
  "total_count": 1
}
```

### Get Advertisement Statistics

#### Get Stats
```http
GET /api/ads/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_ads": 25,
    "approved_ads": 20,
    "pending_ads": 3,
    "rejected_ads": 2,
    "platforms": ["telegram", "facebook", "whatsapp", "instagram"]
  }
}
```

### Get Advertisement by ID

#### Get Specific Ad
```http
GET /api/ads/123
```

**Response:**
```json
{
  "success": true,
  "ad": {
    "id": 123,
    "user_id": "user_456",
    "original_text": "للبيع موبايل سامسونج...",
    "enhanced_text": "🔥 عرض مميز!\n\nللبيع موبايل سامسونج...",
    "status": "approved",
    "category": "electronics",
    "price": 8000.0,
    "location": "القاهرة",
    "created_at": "2024-01-15T10:30:00Z",
    "approved_at": "2024-01-15T11:00:00Z"
  }
}
```

### Admin Endpoints

#### Approve Advertisement
```http
PUT /api/ads/123/approve
Content-Type: application/json
```

**Request Body:**
```json
{
  "admin_notes": "إعلان مقبول - يتوافق مع الشروط"
}
```

**Response:**
```json
{
  "success": true,
  "ad_id": 123,
  "status": "approved",
  "approved_at": "2024-01-15T11:00:00Z",
  "admin_notes": "إعلان مقبول - يتوافق مع الشروط"
}
```

#### Reject Advertisement
```http
PUT /api/ads/123/reject
Content-Type: application/json
```

**Request Body:**
```json
{
  "admin_notes": "إعلان مرفوض - يحتوي على معلومات غير صحيحة"
}
```

**Response:**
```json
{
  "success": true,
  "ad_id": 123,
  "status": "rejected",
  "rejected_at": "2024-01-15T11:00:00Z",
  "admin_notes": "إعلان مرفوض - يحتوي على معلومات غير صحيحة"
}
```

#### Get Pending Advertisements
```http
GET /api/ads/pending?limit=20&offset=0
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": 124,
      "user_id": "user_789",
      "original_text": "للبيع سيارة تويوتا كامري...",
      "enhanced_text": "🔥 عرض مميز!\n\nللبيع سيارة تويوتا كامري...",
      "status": "pending",
      "created_at": "2024-01-15T12:00:00Z",
      "user": {
        "id": "user_789",
        "name": "أحمد محمد",
        "phone": "01234567890"
      }
    }
  ],
  "total_count": 5,
  "limit": 20,
  "offset": 0
}
```

## 👥 User API

### Get Users
```http
GET /api/users?platform=telegram&limit=50
```

**Query Parameters:**
- `platform` (optional): Filter by platform
- `limit` (optional): Number of results
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": "user_123",
      "name": "محمد أحمد",
      "platform": "telegram",
      "platform_id": "telegram_user_456",
      "created_at": "2024-01-10T09:00:00Z"
    }
  ],
  "total_count": 150
}
```

### Create User
```http
POST /api/users
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "سارة محمود",
  "phone": "01098765432",
  "email": "sara@example.com",
  "platform": "whatsapp",
  "platform_id": "whatsapp_201098765432"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "user_124",
    "name": "سارة محمود",
    "phone": "01098765432",
    "email": "sara@example.com",
    "platform": "whatsapp",
    "platform_id": "whatsapp_201098765432",
    "created_at": "2024-01-15T14:00:00Z"
  }
}
```

## 🔄 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message in English",
  "error_code": "ERROR_CODE",
  "details": { /* additional error details */ }
}
```

### Chatbot Response Format
```json
{
  "type": "text",
  "text": "النص المراد إرساله للمستخدم",
  "quick_replies": [
    {
      "title": "عنوان الزر",
      "payload": "button_payload"
    }
  ]
}
```

## 📊 Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## 🔍 Error Codes

### Common Errors
- `INVALID_REQUEST`: Request format is invalid
- `MISSING_PARAMETER`: Required parameter is missing
- `INVALID_PLATFORM`: Unsupported platform specified
- `USER_NOT_FOUND`: User does not exist
- `AD_NOT_FOUND`: Advertisement does not exist
- `WEBHOOK_VERIFICATION_FAILED`: Webhook verification failed
- `RATE_LIMIT_EXCEEDED`: Too many requests

### Platform-Specific Errors
- `FACEBOOK_TOKEN_INVALID`: Facebook access token is invalid
- `WHATSAPP_TOKEN_INVALID`: WhatsApp access token is invalid
- `TELEGRAM_TOKEN_INVALID`: Telegram bot token is invalid
- `INSTAGRAM_TOKEN_INVALID`: Instagram access token is invalid

## 📝 Usage Examples

### Complete Advertiser Flow
```bash
# 1. User starts conversation
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "advertiser_123", "message": "مرحبا"}'

# 2. User selects advertiser option
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "advertiser_123", "message": "1"}'

# 3. User submits ad text
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "advertiser_123", "message": "للبيع موبايل آيفون 13 حالة ممتازة بسعر 15000 جنيه. الجهاز نظيف جداً ومعاه الكرتونة والشاحن الأصلي. للتواصل: 01234567890"}'

# 4. User approves enhanced text
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "advertiser_123", "message": "نعم، موافق"}'
```

### Complete Buyer Flow
```bash
# 1. User starts conversation
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "buyer_456", "message": "مرحبا"}'

# 2. User selects buyer option
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "buyer_456", "message": "2"}'

# 3. User searches for products
curl -X POST https://58hpi8cpzekl.manus.space/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"platform": "telegram", "user_id": "buyer_456", "message": "أنا عايز موبايل آيفون بسعر أقل من 20000 جنيه"}'
```

## 🔒 Security Considerations

### Webhook Security
- All webhooks must use HTTPS
- Verify webhook signatures/tokens
- Implement rate limiting
- Validate all input data

### Data Protection
- Sanitize user inputs
- Encrypt sensitive data
- Implement proper access controls
- Log security events

### API Security
- Use HTTPS for all API calls
- Implement authentication for admin endpoints
- Rate limit API requests
- Validate and sanitize all inputs

---

This API documentation provides comprehensive information for integrating with the Arabic AI Chatbot system. For additional support or questions, please refer to the main README.md or create an issue in the repository.

