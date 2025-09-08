#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Models package for Arabic AI Chatbot
Contains AI models and search engines for the chatbot system
"""

from .gemini_image_search import GeminiImageSearchModel, create_gemini_image_search_model
from .product_search_engine import ProductSearchEngine, ProductMatch, create_product_search_engine

__all__ = [
    'GeminiImageSearchModel',
    'create_gemini_image_search_model',
    'ProductSearchEngine', 
    'ProductMatch',
    'create_product_search_engine'
]

__version__ = '1.0.0'
__author__ = 'Arabic AI Chatbot Team'
