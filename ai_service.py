import os
import openai
from typing import Dict, List, Optional
from arabic_utils import ArabicTextProcessor

class AIService:
    """AI service for text enhancement and analysis using OpenAI API"""
    
    def __init__(self):
        # OpenAI API is already configured via environment variables
        self.client = openai.OpenAI()
        self.arabic_processor = ArabicTextProcessor()
    
    def enhance_ad_text(self, original_text: str) -> Dict[str, any]:
        """Enhance Arabic advertisement text using AI"""
        try:
            # Create a prompt for ad enhancement
            prompt = f"""
أنت خبير في كتابة الإعلانات باللغة العربية. قم بتحسين النص التالي ليصبح إعلاناً جذاباً ومقنعاً:

النص الأصلي:
{original_text}

المطلوب:
1. أعد صياغة النص بطريقة تسويقية جذابة
2. أضف عناصر تسويقية مثل المميزات والفوائد
3. استخدم لغة واضحة ومقنعة
4. احتفظ بجميع المعلومات المهمة (السعر، المواصفات، معلومات الاتصال)
5. اجعل النص منظماً وسهل القراءة

النص المحسن:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "أنت خبير في التسويق والإعلانات باللغة العربية. تخصصك هو تحسين النصوص الإعلانية لتصبح أكثر جاذبية وفعالية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            
            # Extract information from both original and enhanced text
            original_analysis = self.arabic_processor.analyze_search_intent(original_text)
            enhanced_analysis = self.arabic_processor.analyze_search_intent(enhanced_text)
            
            return {
                'success': True,
                'original_text': original_text,
                'enhanced_text': enhanced_text,
                'original_analysis': original_analysis,
                'enhanced_analysis': enhanced_analysis,
                'improvement_score': self._calculate_improvement_score(original_text, enhanced_text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_text': original_text,
                'enhanced_text': original_text  # Fallback to original
            }
    
    def analyze_buyer_query(self, query: str) -> Dict[str, any]:
        """Analyze buyer search query and extract structured information"""
        try:
            # First, use our Arabic processor for basic analysis
            basic_analysis = self.arabic_processor.analyze_search_intent(query)
            
            # Then use AI for more sophisticated analysis
            prompt = f"""
قم بتحليل طلب البحث التالي واستخراج المعلومات المهمة:

طلب البحث: {query}

استخرج المعلومات التالية في شكل JSON:
{{
    "product_type": "نوع المنتج المطلوب",
    "brand": "العلامة التجارية إن وجدت",
    "price_range": {{
        "min": الحد الأدنى للسعر,
        "max": الحد الأقصى للسعر
    }},
    "specifications": ["قائمة بالمواصفات المطلوبة"],
    "location": "المنطقة المطلوبة إن وجدت",
    "urgency": "مستوى الاستعجال (عالي/متوسط/منخفض)",
    "search_keywords": ["كلمات البحث المناسبة"]
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "أنت خبير في تحليل طلبات البحث باللغة العربية واستخراج المعلومات المهمة منها."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            ai_analysis = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'original_query': query,
                'basic_analysis': basic_analysis,
                'ai_analysis': ai_analysis,
                'search_parameters': self._extract_search_parameters(basic_analysis, ai_analysis)
            }
            
        except Exception as e:
            # Fallback to basic analysis only
            return {
                'success': False,
                'error': str(e),
                'original_query': query,
                'basic_analysis': basic_analysis,
                'search_parameters': self._extract_search_parameters(basic_analysis, None)
            }
    
    def generate_response_message(self, context: str, user_message: str, response_type: str) -> str:
        """Generate appropriate Arabic response message"""
        try:
            if response_type == "welcome":
                return "أهلاً بك 👋، من فضلك اختر:\n1️⃣ أنا معلن\n2️⃣ أنا مشتري"
            
            elif response_type == "advertiser_request_ad":
                return "ممتاز! من فضلك اكتب تفاصيل إعلانك في 3 أسطر على الأقل، واحرص على ذكر:\n• نوع المنتج أو الخدمة\n• السعر\n• معلومات الاتصال"
            
            elif response_type == "buyer_request_search":
                return "أخبرني، ما الذي تبحث عنه بالضبط؟ 🔎\nمثال: أنا عايز موبايل سامسونج بسعر أقل من 5000 جنيه"
            
            elif response_type == "ad_enhanced":
                return "ده النص المحسن لإعلانك ✅، هل توافق عليه؟\n\nاكتب 'نعم' للموافقة أو 'تعديل' لطلب تعديلات"
            
            elif response_type == "ad_submitted":
                return "تم إرسال إعلانك للمراجعة 📋\nسيتم إشعارك بالنتيجة خلال 24 ساعة"
            
            elif response_type == "ad_approved":
                return "🎉 تم رفع إعلانك بنجاح، وهذا هو الرابط الخاص به:"
            
            elif response_type == "ad_rejected":
                return "❌ عذرًا، لم يتم قبول إعلانك، برجاء التواصل مع الدعم."
            
            elif response_type == "search_results":
                return "إليك أفضل النتائج التي وجدتها لك:"
            
            elif response_type == "no_results":
                return "عذرًا، لم أجد نتائج مطابقة لطلبك 😔\nجرب البحث بكلمات مختلفة أو قم بتوسيع نطاق البحث"
            
            else:
                # Generate custom response using AI
                prompt = f"""
السياق: {context}
رسالة المستخدم: {user_message}
نوع الرد المطلوب: {response_type}

اكتب رداً مناسباً باللغة العربية:
"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "أنت مساعد ذكي للدردشة باللغة العربية. اكتب ردود مفيدة ومهذبة."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            # Fallback responses
            fallback_responses = {
                "welcome": "أهلاً بك! كيف يمكنني مساعدتك؟",
                "error": "عذرًا، حدث خطأ. من فضلك حاول مرة أخرى.",
                "default": "شكرًا لك! كيف يمكنني مساعدتك أكثر؟"
            }
            return fallback_responses.get(response_type, fallback_responses["default"])
    
    def _calculate_improvement_score(self, original: str, enhanced: str) -> float:
        """Calculate improvement score between original and enhanced text"""
        # Simple scoring based on length and structure
        original_words = len(original.split())
        enhanced_words = len(enhanced.split())
        
        # Score based on length improvement (but not too long)
        length_score = min(enhanced_words / max(original_words, 1), 2.0)
        
        # Score based on structure (presence of formatting)
        structure_score = 1.0
        if any(char in enhanced for char in ['•', '-', '\n', ':']):
            structure_score = 1.5
        
        return min(length_score * structure_score, 5.0)
    
    def _extract_search_parameters(self, basic_analysis: Dict, ai_analysis: Optional[str]) -> Dict:
        """Extract search parameters from analysis results"""
        params = {
            'keywords': basic_analysis.get('keywords', []),
            'category': basic_analysis.get('category'),
            'location': basic_analysis.get('location'),
            'price_min': None,
            'price_max': None
        }
        
        # Extract price range from basic analysis
        price_info = basic_analysis.get('price_info')
        if price_info:
            params['price_max'] = price_info['value']
        
        # Try to parse AI analysis for more details
        if ai_analysis:
            try:
                import json
                ai_data = json.loads(ai_analysis)
                if 'price_range' in ai_data:
                    params['price_min'] = ai_data['price_range'].get('min')
                    params['price_max'] = ai_data['price_range'].get('max')
                if 'search_keywords' in ai_data:
                    params['keywords'].extend(ai_data['search_keywords'])
            except:
                pass  # Ignore JSON parsing errors
        
        return params

