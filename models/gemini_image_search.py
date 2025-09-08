#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini AI Image Search Model for Arabic AI Chatbot
Handles image analysis and product search functionality
"""

import os
import base64
import requests
import json
from typing import Dict, List, Optional

class GeminiImageSearchModel:
    """
    Model for handling image analysis and product search using Gemini AI
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini Image Search Model
        
        Args:
            api_key (str): Gemini API key
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        self.api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'
        self.arabic_prompt = """
        حلل هذه الصورة واستخرج معلومات المنتج باللغة العربية بدقة.
        
        يرجى تحديد:
        1. نوع المنتج (موبايل، لابتوب، سيارة، ملابس، إلخ)
        2. الماركة أو العلامة التجارية إن كانت واضحة
        3. اللون الأساسي
        4. الخصائص المميزة والتفاصيل المهمة
        5. الحالة الظاهرة (جديد، مستعمل، إلخ)
        
        اكتب الوصف بشكل مختصر ومفيد للبحث، باستخدام كلمات مفتاحية مناسبة.
        """
        
    def analyze_image(self, image_path: str) -> Dict[str, any]:
        """
        Analyze an image using Gemini AI and extract product information
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Dict containing analysis results
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Gemini API key not configured',
                'description': '',
                'keywords': [],
                'confidence': 0.0
            }
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Get MIME type
            mime_type = self._get_mime_type(image_path)
            if not mime_type:
                return {
                    'success': False,
                    'error': 'Unsupported image format',
                    'description': '',
                    'keywords': [],
                    'confidence': 0.0
                }
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the request payload
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": self.arabic_prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 1024
                }
            }
            
            # Make API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parse the response
                    parsed_result = self._parse_gemini_response(content)
                    parsed_result['success'] = True
                    
                    return parsed_result
                else:
                    return {
                        'success': False,
                        'error': 'No response from Gemini',
                        'description': '',
                        'keywords': [],
                        'confidence': 0.0
                    }
            else:
                return {
                    'success': False,
                    'error': f'API request failed: {response.status_code}',
                    'description': '',
                    'keywords': [],
                    'confidence': 0.0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'description': '',
                'keywords': [],
                'confidence': 0.0
            }

    def extract_keywords(self, description: str) -> List[str]:
        """
        Extract search keywords from product description
        
        Args:
            description (str): Product description in Arabic
            
        Returns:
            List of search keywords
        """
        # Common Arabic stop words to filter out
        stop_words = {
            'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
            'التي', 'الذي', 'التي', 'اللذان', 'اللتان', 'الذين', 'اللواتي',
            'أن', 'إن', 'كان', 'كانت', 'يكون', 'تكون', 'أو', 'و', 'لكن',
            'لكن', 'غير', 'سوف', 'قد', 'لقد', 'كل', 'بعض', 'جميع'
        }
        
        # Split description into words and filter
        words = description.split()
        keywords = []
        
        for word in words:
            # Clean word from punctuation
            clean_word = word.strip('.,!?؟،؛:')
            
            # Skip stop words and short words
            if len(clean_word) > 2 and clean_word not in stop_words:
                keywords.append(clean_word)
        
        return keywords[:10]  # Return top 10 keywords

    def _parse_text_analysis_response(self, content: str, original_query: str) -> Dict[str, any]:
        """
        Parse Gemini's text analysis response
        
        Args:
            content (str): Response from Gemini
            original_query (str): Original user query
            
        Returns:
            Dict with parsed information
        """
        try:
            lines = content.strip().split('\n')
            result = {
                'product_type': '',
                'price_range': '',
                'location': '',
                'specifications': [],
                'keywords': original_query,
                'enhanced_query': original_query
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('نوع المنتج:'):
                    result['product_type'] = line.replace('نوع المنتج:', '').strip()
                elif line.startswith('السعر:'):
                    result['price_range'] = line.replace('السعر:', '').strip()
                elif line.startswith('الموقع:'):
                    result['location'] = line.replace('الموقع:', '').strip()
                elif line.startswith('المواصفات:'):
                    specs_text = line.replace('المواصفات:', '').strip()
                    result['specifications'] = [s.strip() for s in specs_text.split(',')]
                elif line.startswith('الكلمات المفتاحية:'):
                    keywords_text = line.replace('الكلمات المفتاحية:', '').strip()
                    result['keywords'] = keywords_text
                    result['enhanced_query'] = keywords_text
            
            return result
            
        except Exception as e:
            return {
                'product_type': '',
                'price_range': '',
                'location': '',
                'specifications': [],
                'keywords': original_query,
                'enhanced_query': original_query,
                'error': str(e)
            }
    
    def _get_mime_type(self, image_path: str) -> str:
        """
        Get MIME type based on file extension
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            MIME type string
        """
        extension = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')
    
    def _calculate_confidence(self, api_result: Dict) -> float:
        """
        Calculate confidence score from API result
        
        Args:
            api_result (Dict): Gemini API response
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Simple confidence calculation based on response length and structure
            if 'candidates' in api_result and len(api_result['candidates']) > 0:
                candidate = api_result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text = candidate['content']['parts'][0].get('text', '')
                    # Higher confidence for longer, more detailed descriptions
                    base_confidence = min(len(text) / 200, 1.0)
                    return max(0.5, base_confidence)  # Minimum 50% confidence
            return 0.5
        except:
            return 0.5
    
    def validate_api_key(self) -> bool:
        """
        Validate if Gemini API key is configured and working
        
        Returns:
            True if API key is valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Simple test request
            payload = {
                "contents": [{
                    "parts": [{"text": "Hello"}]
                }]
            }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        except:
            return False

# Factory function for easy instantiation
def create_gemini_image_search_model(api_key: str = None) -> GeminiImageSearchModel:
    """
    Factory function to create GeminiImageSearchModel instance
    
    Args:
        api_key (str): Optional API key
        
    Returns:
        GeminiImageSearchModel instance
    """
    return GeminiImageSearchModel(api_key)

# Example usage and testing
if __name__ == "__main__":
    # Test the model
    model = create_gemini_image_search_model()
    
    if model.validate_api_key():
        print("✅ Gemini API key is valid")
    else:
        print("❌ Gemini API key is invalid or not configured")
        print("Please set GEMINI_API_KEY environment variable")
