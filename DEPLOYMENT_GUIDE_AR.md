# دليل نشر بوت الدردشة العربي

## المتطلبات الأساسية
1. خادم VPS مع Ubuntu 20.04/22.04
2. Python 3.8 أو أحدث
3. MySQL أو SQLite
4. نطاق (Domain) مؤشر على عنوان IP الخادم

## خطوات النشر

### 1. تثبيت المتطلبات الأساسية

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت حزم النظام المطلوبة
sudo apt install -y python3-pip python3-venv nginx git

# تثبيت إدارة العمليات
sudo apt install -y supervisor
```

### 2. إعداد بيئة بايثون

```bash
# إنشاء مجلد للتطبيق
sudo mkdir -p /var/www/arabic-ai-chatbot
sudo chown -R $USER:$USER /var/www/arabic-ai-chatbot
cd /var/www/arabic-ai-chatbot

# إنشاء وتفعيل البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# نسخ الكود المصدري
git clone <رابط-المستودع> .

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

إنشاء ملف `.env` في مجلد المشروع:

```bash
FLASK_APP=simple_web_app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:////var/www/arabic-ai-chatbot/instance/simple_chatbot.db
UPLOAD_FOLDER=/var/www/arabic-ai-chatbot/static/uploads
```

### 4. إعداد قاعدة البيانات

```bash
# تهيئة قاعدة البيانات
flask db upgrade

# إنشاء المجلدات المطلوبة
mkdir -p /var/www/arabic-ai-chatbot/static/uploads
mkdir -p /var/www/arabic-ai-chatbot/static/sample_images
mkdir -p /var/www/arabic-ai-chatbot/dataset
mkdir -p /var/www/arabic-ai-chatbot/models
```

### 5. تكوين Gunicorn

إنشاء ملف `wsgi.py`:

```python
from simple_web_app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
```

تثبيت Gunicorn:
```bash
pip install gunicorn
```

### 6. تكوين Supervisor

إنشاء ملف `/etc/supervisor/conf.d/arabic-ai-chatbot.conf`:

```ini
[program:arabic-ai-chatbot]
directory=/var/www/arabic-ai-chatbot
command=/var/www/arabic-ai-chatbot/venv/bin/gunicorn --workers 3 --bind unix:arabic-ai-chatbot.sock -m 007 wsgi:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/arabic-ai-chatbot/arabic-ai-chatbot.err.log
stdout_logfile=/var/log/arabic-ai-chatbot/arabic-ai-chatbot.out.log
```

إنشاء مجلد السجلات:
```bash
sudo mkdir -p /var/log/arabic-ai-chatbot
sudo touch /var/log/arabic-ai-chatbot/arabic-ai-chatbot.{err,out}.log
sudo chown -R www-data:www-data /var/log/arabic-ai-chatbot
```

إعادة تشغيل Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start arabic-ai-chatbot
```

### 7. تكوين Nginx

إنشاء ملف `/etc/nginx/sites-available/arabic-ai-chatbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/arabic-ai-chatbot/arabic-ai-chatbot.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /var/www/arabic-ai-chatbot/static/;
        expires 30d;
    }

    location /uploads/ {
        alias /var/www/arabic-ai-chatbot/static/uploads/;
        expires 30d;
    }
}
```

تفعيل الموقع:
```bash
sudo ln -s /etc/nginx/sites-available/arabic-ai-chatbot /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 8. إعداد جدار الحماية

```bash
# السماح لحركة المرور على المنافذ المطلوبة
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw enable
```

### 9. تحديثات SSL (اختياري)

```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# إعداد تجديد تلقائي للشهادة
sudo systemctl status certbot.timer
```

## صيانة التطبيق

### تحديث التطبيق

```bash
cd /var/www/arabic-ai-chatbot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo supervisorctl restart arabic-ai-chatbot
```
### مراقبة السجلات

```bash
# سجلات التطبيق
sudo tail -f /var/log/arabic-ai-chatbot/arabic-ai-chatbot.out.log

# سجلات الأخطاء
sudo tail -f /var/log/arabic-ai-chatbot/arabic-ai-chatbot.err.log

# سجلات Nginx
sudo tail -f /var/log/nginx/error.log
```

## استكشاف الأخطاء وإصلاحها

1. **التطبيق لا يعمل**:
   ```bash
   # التحقق من حالة Supervisor
   sudo supervisorctl status
   
   # إعادة تشغيل الخدمة
   sudo supervisorctl restart arabic-ai-chatbot
   ```

2. **مشاكل في قاعدة البيانات**:
   ```bash
   # فحص قاعدة البيانات
   sqlite3 /var/www/arabic-ai-chatbot/instance/simple_chatbot.db ".tables"
   ```

3. **مشاكل في الأذونات**:
   ```bash
   # إصلاح أذونات الملفات
   sudo chown -R www-data:www-data /var/www/arabic-ai-chatbot
   sudo chmod -R 755 /var/www/arabic-ai-chatbot
   ```

## النسخ الاحتياطي

يوصى بإعداد نسخ احتياطي تلقائي لقاعدة البيانات والملفات المهمة:

```bash
# إنشاء سكربت النسخ الاحتياطي
cat > /usr/local/bin/backup-chatbot.sh << 'EOL'
#!/bin/bash
BACKUP_DIR="/var/backups/arabic-ai-chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
cp /var/www/arabic-ai-chatbot/instance/simple_chatbot.db "$BACKUP_DIR/chatbot_db_$DATE.db"

# نسخ احتياطي للملفات المهمة
tar -czf "$BACKUP_DIR/chatbot_files_$DATE.tar.gz" /var/www/arabic-ai-chatbot/static/uploads

# حذف النسخ القديمة (احتفظ بآخر 7 أيام)
find $BACKUP_DIR -type f -mtime +7 -delete
EOL

# جعل السكربت قابلاً للتنفيذ
chmod +x /usr/local/bin/backup-chatbot.sh

# جدولة النسخ الاحتياطي اليومي
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-chatbot.sh") | crontab -
```

## الترقية إلى خادم إنتاجي

لتحسين الأداء في بيئة الإنتاج، يمكنك:

1. **استخدام قاعدة بيانات MySQL/PostgreSQL** بدلاً من SQLite
2. تكوين Redis للتخزين المؤقت
3. ضبط إعدادات Gunicorn بناءً على موارد الخادم
4. إعداد CDN للملفات الثابتة
5. تكوين موازن تحميل (Load Balancer) إذا لزم الأمر

## الدعم الفني

في حالة مواجهة أي مشاكل، يرجى فتح مشكلة (issue) في مستودع GitHub الخاص بالمشروع مع تفاصيل المشكلة وسجلات الأخطاء.
