import re
import unicodedata
from typing import List, Dict, Optional

class ArabicTextProcessor:
    """Utility class for processing Arabic text"""
    
    # Common Arabic stop words
    STOP_WORDS = {
        'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
        'التي', 'الذي', 'التي', 'اللذان', 'اللتان', 'اللاتي', 'اللواتي',
        'هو', 'هي', 'هم', 'هن', 'أنا', 'أنت', 'أنتم', 'أنتن', 'نحن',
        'لا', 'لم', 'لن', 'ما', 'لكن', 'لكن', 'غير', 'سوى', 'إلا',
        'كل', 'بعض', 'جميع', 'كان', 'كانت', 'يكون', 'تكون', 'أكون',
        'أن', 'إن', 'كي', 'لكي', 'حتى', 'لو', 'لولا', 'لوما', 'إذا',
        'عند', 'عندما', 'بينما', 'أثناء', 'خلال', 'أمام', 'وراء', 'فوق',
        'تحت', 'يمين', 'يسار', 'شمال', 'وسط', 'بين', 'ضد', 'نحو'
    }
    
    # Arabic price patterns
    PRICE_PATTERNS = [
        r'(\d+)\s*جنيه',
        r'(\d+)\s*ج\.م',
        r'(\d+)\s*ريال',
        r'(\d+)\s*درهم',
        r'(\d+)\s*دولار',
        r'(\d+)\s*يورو',
        r'(\d+)\s*ألف',
        r'(\d+)\s*مليون'
    ]
    
    # Common product categories in Arabic
    CATEGORIES = {
        'موبايل': ['موبايل', 'جوال', 'هاتف', 'تليفون', 'سامسونج', 'آيفون', 'هواوي', 'شاومي'],
        'سيارات': ['سيارة', 'عربية', 'أوتوموبيل', 'تويوتا', 'نيسان', 'هيونداي', 'كيا'],
        'عقارات': ['شقة', 'فيلا', 'بيت', 'منزل', 'أرض', 'محل', 'مكتب', 'عقار'],
        'أثاث': ['أثاث', 'كنبة', 'سرير', 'طاولة', 'كرسي', 'دولاب', 'مكتب'],
        'إلكترونيات': ['تلفزيون', 'لابتوب', 'كمبيوتر', 'تابلت', 'سماعات', 'كاميرا'],
        'ملابس': ['ملابس', 'فستان', 'قميص', 'بنطلون', 'جاكيت', 'حذاء', 'شنطة'],
        'خدمات': ['خدمة', 'تنظيف', 'صيانة', 'تدريس', 'ترجمة', 'تصميم', 'برمجة']
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize Arabic text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize Arabic characters
        text = unicodedata.normalize('NFKC', text)
        
        # Remove diacritics (tashkeel)
        text = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', text)
        
        # Normalize Alef variations
        text = re.sub(r'[آأإ]', 'ا', text)
        
        # Normalize Teh Marbuta
        text = re.sub(r'ة', 'ه', text)
        
        # Normalize Yeh variations
        text = re.sub(r'[يى]', 'ي', text)
        
        return text
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract meaningful keywords from Arabic text"""
        cleaned_text = ArabicTextProcessor.clean_text(text)
        
        # Split into words
        words = re.findall(r'[\u0600-\u06FF\u0750-\u077F]+', cleaned_text)
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in ArabicTextProcessor.STOP_WORDS and len(word) > 2
        ]
        
        return list(set(keywords))  # Remove duplicates
    
    @staticmethod
    def extract_price_info(text: str) -> Optional[Dict[str, any]]:
        """Extract price information from Arabic text"""
        text = ArabicTextProcessor.clean_text(text)
        
        for pattern in ArabicTextProcessor.PRICE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                price_value = int(match.group(1))
                price_text = match.group(0)
                
                # Convert to standard currency (Egyptian Pounds)
                if 'ألف' in price_text:
                    price_value *= 1000
                elif 'مليون' in price_text:
                    price_value *= 1000000
                
                return {
                    'value': price_value,
                    'text': price_text,
                    'currency': 'EGP'  # Default to Egyptian Pounds
                }
        
        return None
    
    @staticmethod
    def detect_category(text: str) -> Optional[str]:
        """Detect product category from Arabic text"""
        text = ArabicTextProcessor.clean_text(text).lower()
        
        for category, keywords in ArabicTextProcessor.CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return None
    
    @staticmethod
    def extract_location(text: str) -> Optional[str]:
        """Extract location information from Arabic text"""
        # Common Egyptian governorates and cities
        locations = [
            'القاهرة', 'الجيزة', 'الإسكندرية', 'أسوان', 'أسيوط', 'البحر الأحمر',
            'البحيرة', 'بني سويف', 'جنوب سيناء', 'الدقهلية', 'دمياط', 'الفيوم',
            'الغربية', 'الإسماعيلية', 'كفر الشيخ', 'الأقصر', 'مطروح', 'المنيا',
            'المنوفية', 'الوادي الجديد', 'شمال سيناء', 'بورسعيد', 'القليوبية',
            'قنا', 'البحر الأحمر', 'الشرقية', 'سوهاج', 'السويس', 'طنطا',
            'المنصورة', 'الزقازيق', 'شبرا الخيمة', 'بورسعيد', 'السويس',
            'مدينة نصر', 'مصر الجديدة', 'الزمالك', 'المعادي', 'حلوان'
        ]
        
        text = ArabicTextProcessor.clean_text(text)
        
        for location in locations:
            if location in text:
                return location
        
        return None
    
    @staticmethod
    def is_arabic_text(text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not text:
            return False
        
        arabic_chars = re.findall(r'[\u0600-\u06FF\u0750-\u077F]', text)
        return len(arabic_chars) > len(text) * 0.3  # At least 30% Arabic characters
    
    @staticmethod
    def format_price(price: float, currency: str = 'EGP') -> str:
        """Format price in Arabic"""
        if price >= 1000000:
            return f"{price/1000000:.1f} مليون {currency}"
        elif price >= 1000:
            return f"{price/1000:.0f} ألف {currency}"
        else:
            return f"{price:.0f} {currency}"
    
    @staticmethod
    def analyze_search_intent(text: str) -> Dict[str, any]:
        """Analyze search intent from Arabic text"""
        keywords = ArabicTextProcessor.extract_keywords(text)
        price_info = ArabicTextProcessor.extract_price_info(text)
        category = ArabicTextProcessor.detect_category(text)
        location = ArabicTextProcessor.extract_location(text)
        
        # Determine search intent
        intent = "general"
        if any(word in text for word in ['أريد', 'عايز', 'محتاج', 'بدور على', 'أبحث عن']):
            intent = "buying"
        elif any(word in text for word in ['أبيع', 'للبيع', 'متاح', 'عرض']):
            intent = "selling"
        
        return {
            'keywords': keywords,
            'price_info': price_info,
            'category': category,
            'location': location,
            'intent': intent,
            'original_text': text
        }

