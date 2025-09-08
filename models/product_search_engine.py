#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Product Search Engine Model for Arabic AI Chatbot
Handles advanced product matching and similarity search
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

@dataclass
class ProductMatch:
    """Data class for product search results"""
    id: int
    text: str
    price: Optional[float]
    location: Optional[str]
    contact: Optional[str]
    image_url: Optional[str]
    similarity: float
    match_type: str  # 'exact', 'partial', 'semantic', 'image'

class ProductSearchEngine:
    """
    Advanced product search engine with multiple matching strategies
    """
    
    def __init__(self):
        """Initialize the search engine"""
        self.arabic_numbers = {
            'صفر': 0, 'واحد': 1, 'اثنان': 2, 'ثلاثة': 3, 'أربعة': 4,
            'خمسة': 5, 'ستة': 6, 'سبعة': 7, 'ثمانية': 8, 'تسعة': 9,
            'عشرة': 10, 'عشرون': 20, 'ثلاثون': 30, 'أربعون': 40,
            'خمسون': 50, 'ستون': 60, 'سبعون': 70, 'ثمانون': 80,
            'تسعون': 90, 'مئة': 100, 'ألف': 1000, 'مليون': 1000000
        }
        
        self.product_categories = {
            'إلكترونيات': ['موبايل', 'هاتف', 'لابتوب', 'كمبيوتر', 'تلفزيون', 'تابلت', 'ساعة ذكية'],
            'سيارات': ['سيارة', 'عربية', 'أوتوموبيل', 'مركبة', 'شاحنة', 'دراجة نارية'],
            'عقارات': ['شقة', 'بيت', 'منزل', 'فيلا', 'أرض', 'محل', 'مكتب'],
            'ملابس': ['قميص', 'بنطلون', 'فستان', 'حذاء', 'جاكيت', 'تيشيرت'],
            'أثاث': ['كرسي', 'طاولة', 'سرير', 'خزانة', 'أريكة', 'مكتب'],
            'رياضة': ['دراجة', 'كرة', 'جهاز رياضي', 'ملعب', 'نادي']
        }
        
    def search_by_image_description(self, description: str, products: List[Dict]) -> List[ProductMatch]:
        """
        Search products using image-generated description
        
        Args:
            description (str): Product description from image analysis
            products (List[Dict]): List of available products
            
        Returns:
            List of ProductMatch objects
        """
        matches = []
        description_keywords = self._extract_keywords(description)
        
        for product in products:
            similarity = self._calculate_image_similarity(description_keywords, product)
            if similarity > 0.3:  # Minimum threshold
                matches.append(ProductMatch(
                    id=product.get('id', 0),
                    text=product.get('text', ''),
                    price=product.get('price'),
                    location=product.get('location'),
                    contact=product.get('contact'),
                    image_url=product.get('image_url'),
                    similarity=similarity,
                    match_type='image'
                ))
        
        # Sort by similarity score
        matches.sort(key=lambda x: x.similarity, reverse=True)
        return matches[:5]  # Return top 5 matches
    
    def search_by_text(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search products using text query
        
        Args:
            query (str): Search query in Arabic
            max_results (int): Maximum number of results to return
            
        Returns:
            List of product dictionaries
        """
        # Load products from database
        products = self._load_products_from_db()
        
        matches = []
        query_keywords = self._extract_keywords(query)
        price_range = self._extract_price_range(query)
        
        for product in products:
            similarity = self._calculate_text_similarity(query_keywords, product)
            
            # Apply price filter if specified
            if price_range and product.get('price'):
                if not (price_range[0] <= product['price'] <= price_range[1]):
                    continue
            
            if similarity > 0.2:  # Minimum threshold
                match_type = 'exact' if similarity > 0.8 else 'partial'
                matches.append({
                    'id': product.get('id'),
                    'title': product.get('title', product.get('text', '')[:50]),
                    'price': product.get('price'),
                    'location': product.get('location'),
                    'contact': product.get('contact_info'),
                    'image_url': product.get('image_url'),
                    'similarity': similarity,
                    'match_type': match_type
                })
        
        # Sort by similarity score
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches[:max_results]
    
    def _load_products_from_db(self) -> List[Dict]:
        """Load products from database"""
        try:
            import pandas as pd
            df = pd.read_csv('dataset/ads_dataset.csv')
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading products: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from Arabic text"""
        # Remove punctuation and normalize
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Arabic stop words
        stop_words = {
            'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
            'التي', 'الذي', 'أن', 'إن', 'كان', 'كانت', 'يكون', 'تكون', 'سوف',
            'قد', 'لقد', 'بعد', 'قبل', 'أثناء', 'خلال', 'عند', 'لدى', 'حول'
        }
        
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def _extract_price_range(self, query: str) -> Optional[Tuple[float, float]]:
        """Extract price range from query"""
        # Look for price patterns
        price_patterns = [
            r'أقل من (\d+)',
            r'أكثر من (\d+)',
            r'بين (\d+) و (\d+)',
            r'من (\d+) إلى (\d+)',
            r'سعر (\d+)',
            r'بـ?(\d+) جنيه?'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query)
            if match:
                numbers = [float(x) for x in match.groups()]
                if len(numbers) == 1:
                    if 'أقل' in pattern:
                        return (0, numbers[0])
                    elif 'أكثر' in pattern:
                        return (numbers[0], float('inf'))
                    else:
                        return (numbers[0] * 0.8, numbers[0] * 1.2)  # ±20%
                elif len(numbers) == 2:
                    return (min(numbers), max(numbers))
        
        return None
    
    def _calculate_image_similarity(self, description_keywords: List[str], product: Dict) -> float:
        """Calculate similarity between image description and product"""
        product_text = (product.get('text', '') + ' ' + 
                       product.get('category', '')).lower()
        
        matches = 0
        total_keywords = len(description_keywords)
        
        if total_keywords == 0:
            return 0.0
        
        for keyword in description_keywords:
            if keyword.lower() in product_text:
                matches += 1
        
        base_similarity = matches / total_keywords
        
        # Boost similarity for category matches
        category_boost = self._get_category_boost(description_keywords, product)
        
        return min(1.0, base_similarity + category_boost)
    
    def _calculate_text_similarity(self, query_keywords: List[str], product: Dict) -> float:
        """Calculate similarity between text query and product"""
        product_text = (product.get('text', '') + ' ' + 
                       product.get('category', '')).lower()
        
        matches = 0
        total_keywords = len(query_keywords)
        
        if total_keywords == 0:
            return 0.0
        
        for keyword in query_keywords:
            if keyword.lower() in product_text:
                matches += 1
        
        base_similarity = matches / total_keywords
        
        # Boost for exact phrase matches
        query_phrase = ' '.join(query_keywords).lower()
        if query_phrase in product_text:
            base_similarity += 0.3
        
        return min(1.0, base_similarity)
    
    def _get_category_boost(self, keywords: List[str], product: Dict) -> float:
        """Get category-based similarity boost"""
        product_category = product.get('category', '').lower()
        
        for category, category_keywords in self.product_categories.items():
            if category.lower() == product_category:
                for keyword in keywords:
                    if any(cat_keyword in keyword.lower() for cat_keyword in category_keywords):
                        return 0.2  # 20% boost for category match
        
        return 0.0
    
    def format_search_results(self, matches: List[ProductMatch]) -> str:
        """Format search results for display"""
        if not matches:
            return "😔 لم أجد منتجات مطابقة لبحثك حالياً"
        
        response = f"🔍 وجدت {len(matches)} منتجات مطابقة:\n\n"
        
        for i, match in enumerate(matches, 1):
            # Truncate long descriptions
            description = match.text[:120] + "..." if len(match.text) > 120 else match.text
            
            response += f"{i}. {description}\n"
            
            if match.price:
                response += f"💰 السعر: {match.price:,.0f} جنيه\n"
            
            if match.location:
                response += f"📍 الموقع: {match.location}\n"
            
            if match.contact:
                response += f"📞 التواصل: {match.contact}\n"
            
            response += f"🔗 رابط الإعلان: /ad/{match.id}\n"
            response += f"📊 نسبة التطابق: {match.similarity:.0%}\n"
            
            # Add match type indicator
            match_icons = {
                'exact': '🎯',
                'partial': '🔍',
                'semantic': '🧠',
                'image': '📸'
            }
            response += f"{match_icons.get(match.match_type, '🔍')} نوع المطابقة: {match.match_type}\n\n"
        
        return response
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on query"""
        suggestions = []
        
        # Category-based suggestions
        for category, keywords in self.product_categories.items():
            for keyword in keywords:
                if keyword in query.lower():
                    suggestions.extend([
                        f"{keyword} جديد",
                        f"{keyword} مستعمل",
                        f"{keyword} رخيص",
                        f"{keyword} بحالة ممتازة"
                    ])
                    break
        
        return suggestions[:5]  # Return top 5 suggestions

# Factory function
def create_product_search_engine() -> ProductSearchEngine:
    """Create ProductSearchEngine instance"""
    return ProductSearchEngine()

# Example usage
if __name__ == "__main__":
    engine = create_product_search_engine()
    
    # Test search functionality
    sample_products = [
        {
            'id': 1,
            'text': 'موبايل سامسونج جالاكسي S23 للبيع - حالة ممتازة',
            'category': 'إلكترونيات',
            'price': 15000.0,
            'location': 'القاهرة',
            'contact': '01012345678'
        }
    ]
    
    # Test text search
    results = engine.search_by_text_query('موبايل سامسونج', sample_products)
    print("Text search results:", len(results))
    
    # Test image search
    image_results = engine.search_by_image_description('موبايل ذكي أسود اللون', sample_products)
    print("Image search results:", len(image_results))
