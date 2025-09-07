# Deployment Guide - Arabic AI Chatbot

This guide provides step-by-step instructions for deploying the Arabic AI Chatbot across different social media platforms and hosting environments.

## 🏗️ Infrastructure Setup

### Server Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: 3.11 or higher
- **Memory**: Minimum 1GB RAM (2GB+ recommended)
- **Storage**: 10GB+ available space
- **Network**: Public IP address with HTTPS support

### Domain and SSL
1. **Domain Setup**: Point your domain to the server IP
2. **SSL Certificate**: Use Let's Encrypt or similar for HTTPS
3. **Webhook URLs**: Must use HTTPS for all social media platforms

## 🔧 Application Deployment

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip nginx -y

# Create application directory
sudo mkdir -p /opt/arabic-chatbot
sudo chown $USER:$USER /opt/arabic-chatbot
```

### 2. Application Setup
```bash
# Clone repository
cd /opt/arabic-chatbot
git clone <repository-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `/opt/arabic-chatbot/.env`:
```bash
# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:///app.db

# Social Media Platform Tokens
FACEBOOK_ACCESS_TOKEN=your-facebook-page-access-token
WHATSAPP_ACCESS_TOKEN=your-whatsapp-business-token
INSTAGRAM_ACCESS_TOKEN=your-instagram-business-token
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Webhook Verification Tokens
FACEBOOK_VERIFY_TOKEN=your-facebook-verify-token
WHATSAPP_VERIFY_TOKEN=your-whatsapp-verify-token
INSTAGRAM_VERIFY_TOKEN=your-instagram-verify-token
TELEGRAM_WEBHOOK_SECRET=your-telegram-webhook-secret

# AI Services (Optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
```

### 4. Systemd Service Setup
Create `/etc/systemd/system/arabic-chatbot.service`:
```ini
[Unit]
Description=Arabic AI Chatbot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/arabic-chatbot
Environment=PATH=/opt/arabic-chatbot/venv/bin
EnvironmentFile=/opt/arabic-chatbot/.env
ExecStart=/opt/arabic-chatbot/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable arabic-chatbot
sudo systemctl start arabic-chatbot
sudo systemctl status arabic-chatbot
```

### 5. Nginx Configuration
Create `/etc/nginx/sites-available/arabic-chatbot`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/arabic-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📱 Platform Configuration

### Facebook Messenger Setup

#### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app → Business → Continue
3. Add Messenger product to your app

#### 2. Configure Webhook
1. In Messenger settings, add webhook URL:
   ```
   https://your-domain.com/webhooks/facebook
   ```
2. Set verify token (same as in your .env file)
3. Subscribe to webhook fields:
   - `messages`
   - `messaging_postbacks`
   - `messaging_optins`

#### 3. Page Access Token
1. Create or select a Facebook Page
2. Generate Page Access Token
3. Add token to your .env file

#### 4. Test Configuration
```bash
curl -X GET "https://your-domain.com/webhooks/facebook?hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=CHALLENGE_ACCEPTED&hub.mode=subscribe"
```

### WhatsApp Business Setup

#### 1. WhatsApp Business Account
1. Create WhatsApp Business Account
2. Add phone number and verify
3. Get access token from Meta Business

#### 2. Configure Webhook
1. Set webhook URL:
   ```
   https://your-domain.com/webhooks/whatsapp
   ```
2. Subscribe to webhook fields:
   - `messages`
   - `message_deliveries`
   - `message_reads`

#### 3. Test Configuration
```bash
curl -X POST "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "YOUR_TEST_NUMBER",
    "type": "text",
    "text": {"body": "Hello from Arabic Chatbot!"}
  }'
```

### Instagram Messaging Setup

#### 1. Instagram Business Account
1. Convert Instagram account to Business
2. Connect to Facebook Page
3. Enable messaging in Instagram settings

#### 2. Configure Webhook
1. Use same webhook as Facebook Messenger:
   ```
   https://your-domain.com/webhooks/instagram
   ```
2. Subscribe to Instagram messaging events

#### 3. Permissions
Ensure your app has these permissions:
- `instagram_basic`
- `instagram_manage_messages`
- `pages_messaging`

### Telegram Bot Setup

#### 1. Create Bot
1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Choose bot name and username
4. Save the bot token

#### 2. Set Webhook
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/webhooks/telegram",
    "secret_token": "YOUR_WEBHOOK_SECRET"
  }'
```

#### 3. Configure Bot Commands
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command": "start", "description": "بدء محادثة جديدة"},
      {"command": "help", "description": "عرض المساعدة"},
      {"command": "advertiser", "description": "أنا معلن"},
      {"command": "buyer", "description": "أنا مشتري"}
    ]
  }'
```

## 🔍 Testing & Verification

### 1. Health Check
```bash
curl https://your-domain.com/webhooks/status
```

Expected response:
```json
{
  "status": "active",
  "active_platforms": ["telegram", "facebook", "whatsapp", "instagram"],
  "total_ads": 0,
  "approved_ads": 0,
  "pending_ads": 0
}
```

### 2. Webhook Testing
```bash
curl -X POST https://your-domain.com/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "telegram",
    "user_id": "test_user",
    "message": "مرحبا"
  }'
```

### 3. Platform-Specific Tests

#### Facebook Messenger
Send a message to your Facebook Page and verify the bot responds.

#### WhatsApp Business
Send a WhatsApp message to your business number.

#### Instagram
Send a direct message to your Instagram business account.

#### Telegram
Start a conversation with your bot using `/start` command.

## 📊 Monitoring & Maintenance

### 1. Log Monitoring
```bash
# Application logs
sudo journalctl -u arabic-chatbot -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Database Backup
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /opt/arabic-chatbot/src/database/app.db /opt/backups/app_${DATE}.db

# Add to crontab for daily backups
0 2 * * * /opt/scripts/backup_db.sh
```

### 3. SSL Certificate Renewal
```bash
# If using Let's Encrypt
sudo certbot renew --dry-run

# Add to crontab for automatic renewal
0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. Performance Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check application status
sudo systemctl status arabic-chatbot
curl -s https://your-domain.com/webhooks/status | jq
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Webhook Verification Failed
- Check verify tokens match in .env and platform settings
- Ensure HTTPS is properly configured
- Verify webhook URL is accessible

#### 2. Bot Not Responding
- Check application logs: `sudo journalctl -u arabic-chatbot -f`
- Verify platform tokens are valid
- Test webhook endpoints manually

#### 3. SSL Certificate Issues
- Ensure certificate is valid and not expired
- Check certificate chain is complete
- Verify domain name matches certificate

#### 4. Database Connection Errors
- Check database file permissions
- Verify database path in configuration
- Ensure sufficient disk space

### Debug Commands
```bash
# Test webhook connectivity
curl -I https://your-domain.com/webhooks/status

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Verify environment variables
sudo systemctl show arabic-chatbot --property=Environment

# Test database connectivity
sqlite3 /opt/arabic-chatbot/src/database/app.db ".tables"
```

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Stop service
sudo systemctl stop arabic-chatbot

# Backup current version
cp -r /opt/arabic-chatbot /opt/arabic-chatbot-backup-$(date +%Y%m%d)

# Pull latest changes
cd /opt/arabic-chatbot
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl start arabic-chatbot
sudo systemctl status arabic-chatbot
```

### Database Migrations
```bash
# If database schema changes are needed
cd /opt/arabic-chatbot
source venv/bin/activate
python -c "
from src.models.user import db
from src.main import app
with app.app_context():
    db.create_all()
"
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Deploy multiple application instances
- Implement session sharing via Redis
- Use external database (PostgreSQL, MySQL)

### Performance Optimization
- Enable nginx caching for static content
- Use CDN for global distribution
- Implement database connection pooling
- Add Redis for conversation state caching

### High Availability
- Set up multiple server instances
- Use database replication
- Implement health checks
- Configure automatic failover

---

This deployment guide ensures your Arabic AI Chatbot is properly configured and running across all supported platforms. For additional support, refer to the main README.md or create an issue in the repository.

