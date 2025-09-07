#!/usr/bin/env python3
"""Test script for AI services"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_service import AIService
from arabic_utils import ArabicTextProcessor

def test_arabic_utils():
    """Test Arabic text processing utilities"""
    print("=== Testing Arabic Text Processing ===")
    
    processor = ArabicTextProcessor()
    
    # Test text cleaning
    test_text = "أريد موبايل سامسونج بسعر 3000 جنيه في القاهرة"
    cleaned = processor.clean_text(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned: {cleaned}")
    
    # Test keyword extraction
    keywords = processor.extract_keywords(test_text)
    print(f"Keywords: {keywords}")
    
    # Test price extraction
    price_info = processor.extract_price_info(test_text)
    print(f"Price info: {price_info}")
    
    # Test category detection
    category = processor.detect_category(test_text)
    print(f"Category: {category}")
    
    # Test location extraction
    location = processor.extract_location(test_text)
    print(f"Location: {location}")
    
    # Test search intent analysis
    intent_analysis = processor.analyze_search_intent(test_text)
    print(f"Intent analysis: {intent_analysis}")
    
    print("\n")

def test_ai_service():
    """Test AI service functionality"""
    print("=== Testing AI Service ===")
    
    ai_service = AIService()
    
    # Test ad enhancement
    print("Testing ad enhancement...")
    original_ad = """
موبايل سامسونج للبيع
السعر 3000 جنيه
حالة ممتازة
للتواصل: 01234567890
"""
    
    try:
        enhancement_result = ai_service.enhance_ad_text(original_ad)
        print(f"Enhancement success: {enhancement_result['success']}")
        if enhancement_result['success']:
            print(f"Original: {enhancement_result['original_text']}")
            print(f"Enhanced: {enhancement_result['enhanced_text']}")
            print(f"Improvement score: {enhancement_result.get('improvement_score', 'N/A')}")
        else:
            print(f"Enhancement error: {enhancement_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Exception during ad enhancement: {e}")
    
    print("\n")
    
    # Test buyer query analysis
    print("Testing buyer query analysis...")
    buyer_query = "أنا عايز موبايل سامسونج بسعر أقل من 5000 جنيه في القاهرة"
    
    try:
        analysis_result = ai_service.analyze_buyer_query(buyer_query)
        print(f"Analysis success: {analysis_result['success']}")
        print(f"Original query: {analysis_result['original_query']}")
        print(f"Basic analysis: {analysis_result['basic_analysis']}")
        print(f"Search parameters: {analysis_result['search_parameters']}")
        if not analysis_result['success']:
            print(f"Analysis error: {analysis_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Exception during query analysis: {e}")
    
    print("\n")
    
    # Test response generation
    print("Testing response generation...")
    try:
        welcome_msg = ai_service.generate_response_message("", "", "welcome")
        print(f"Welcome message: {welcome_msg}")
        
        advertiser_msg = ai_service.generate_response_message("advertiser", "", "advertiser_request_ad")
        print(f"Advertiser message: {advertiser_msg}")
        
        buyer_msg = ai_service.generate_response_message("buyer", "", "buyer_request_search")
        print(f"Buyer message: {buyer_msg}")
    except Exception as e:
        print(f"Exception during response generation: {e}")

def main():
    """Run all tests"""
    print("Starting AI Services Tests...\n")
    
    # Test Arabic utilities (no API calls)
    test_arabic_utils()
    
    # Test AI service (requires OpenAI API)
    test_ai_service()
    
    print("Tests completed!")

if __name__ == "__main__":
    main()

