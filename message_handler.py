from typing import Dict, Any, Optional
from src.models.user import User
from src.models.conversation import Conversation, ConversationState, UserType
from src.models.ad import Ad, AdStatus
from src.services.ai_service import AIService
from src.utils.state_manager import StateManager

class MessageHandler:
    """Unified message handler for all social media platforms"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.state_manager = StateManager()
    
    def process_message(self, platform: str, platform_user_id: str, message_text: str, user_name: str = None) -> Dict[str, Any]:
        """Process incoming message from any platform"""
        try:
            # Get or create user
            user = User.get_or_create_by_platform(platform, platform_user_id, user_name)
            
            # Get or create conversation
            conversation = Conversation.get_or_create(platform, platform_user_id, user.id)
            
            # Update last message
            conversation.last_message = message_text
            
            # Process message based on current state
            response = self._handle_message_by_state(conversation, message_text)
            
            return {
                'success': True,
                'response': response,
                'user_id': user.id,
                'conversation_id': conversation.id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': self.ai_service.generate_response_message("", message_text, "error")
            }
    
    def _handle_message_by_state(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle message based on conversation state"""
        current_state = conversation.state
        
        if current_state == ConversationState.INITIAL:
            return self._handle_initial_state(conversation, message_text)
        
        elif current_state == ConversationState.WAITING_USER_TYPE:
            return self._handle_user_type_selection(conversation, message_text)
        
        elif current_state == ConversationState.ADVERTISER_WAITING_AD:
            return self._handle_advertiser_ad_input(conversation, message_text)
        
        elif current_state == ConversationState.ADVERTISER_CONFIRMING:
            return self._handle_advertiser_confirmation(conversation, message_text)
        
        elif current_state == ConversationState.BUYER_WAITING_QUERY:
            return self._handle_buyer_search_query(conversation, message_text)
        
        elif current_state == ConversationState.BUYER_SHOWING_RESULTS:
            return self._handle_buyer_results_interaction(conversation, message_text)
        
        else:
            # Default: restart conversation
            conversation.set_state(ConversationState.INITIAL)
            return self._handle_initial_state(conversation, message_text)
    
    def _handle_initial_state(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle initial welcome message"""
        welcome_message = self.ai_service.generate_response_message("", message_text, "welcome")
        conversation.set_state(ConversationState.WAITING_USER_TYPE)
        
        return {
            'text': welcome_message,
            'type': 'text',
            'quick_replies': [
                {'title': '1️⃣ أنا معلن', 'payload': 'advertiser'},
                {'title': '2️⃣ أنا مشتري', 'payload': 'buyer'}
            ]
        }
    
    def _handle_user_type_selection(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle user type selection (advertiser or buyer)"""
        message_lower = message_text.lower().strip()
        
        if any(word in message_lower for word in ['1', 'معلن', 'advertiser', 'أنا معلن']):
            conversation.set_user_type(UserType.ADVERTISER)
            conversation.set_state(ConversationState.ADVERTISER_WAITING_AD)
            
            response_text = self.ai_service.generate_response_message("advertiser", message_text, "advertiser_request_ad")
            
            return {
                'text': response_text,
                'type': 'text'
            }
        
        elif any(word in message_lower for word in ['2', 'مشتري', 'buyer', 'أنا مشتري']):
            conversation.set_user_type(UserType.BUYER)
            conversation.set_state(ConversationState.BUYER_WAITING_QUERY)
            
            response_text = self.ai_service.generate_response_message("buyer", message_text, "buyer_request_search")
            
            return {
                'text': response_text,
                'type': 'text'
            }
        
        else:
            # Invalid selection, ask again
            return {
                'text': "من فضلك اختر رقم 1 للمعلنين أو رقم 2 للمشترين",
                'type': 'text',
                'quick_replies': [
                    {'title': '1️⃣ أنا معلن', 'payload': 'advertiser'},
                    {'title': '2️⃣ أنا مشتري', 'payload': 'buyer'}
                ]
            }
    
    def _handle_advertiser_ad_input(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle advertiser ad text input"""
        # Check if ad text is sufficient (at least 3 lines or 50 characters)
        lines = message_text.strip().split('\n')
        if len(lines) < 3 and len(message_text) < 50:
            return {
                'text': "من فضلك اكتب تفاصيل أكثر عن إعلانك (على الأقل 3 أسطر)",
                'type': 'text'
            }
        
        # Enhance the ad text using AI
        enhancement_result = self.ai_service.enhance_ad_text(message_text)
        
        if enhancement_result['success']:
            enhanced_text = enhancement_result['enhanced_text']
            
            # Store the enhanced text in conversation context
            conversation.update_context('original_ad', message_text)
            conversation.update_context('enhanced_ad', enhanced_text)
            conversation.update_context('enhancement_result', enhancement_result)
            
            conversation.set_state(ConversationState.ADVERTISER_CONFIRMING)
            
            confirmation_message = self.ai_service.generate_response_message("advertiser", enhanced_text, "ad_enhanced")
            
            return {
                'text': f"{enhanced_text}\n\n---\n\n{confirmation_message}",
                'type': 'text',
                'quick_replies': [
                    {'title': '✅ نعم، موافق', 'payload': 'approve'},
                    {'title': '✏️ تعديل', 'payload': 'edit'}
                ]
            }
        else:
            # AI enhancement failed, use original text
            conversation.update_context('original_ad', message_text)
            conversation.update_context('enhanced_ad', message_text)
            conversation.set_state(ConversationState.ADVERTISER_CONFIRMING)
            
            return {
                'text': f"{message_text}\n\nهل توافق على نشر هذا الإعلان؟",
                'type': 'text',
                'quick_replies': [
                    {'title': '✅ نعم، موافق', 'payload': 'approve'},
                    {'title': '✏️ تعديل', 'payload': 'edit'}
                ]
            }
    
    def _handle_advertiser_confirmation(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle advertiser confirmation of enhanced ad"""
        message_lower = message_text.lower().strip()
        
        if any(word in message_lower for word in ['نعم', 'موافق', 'approve', 'yes', 'ok']):
            # Submit the ad
            context = conversation.get_context()
            original_ad = context.get('original_ad', '')
            enhanced_ad = context.get('enhanced_ad', original_ad)
            
            # Create ad record
            from src.models.user import db
            ad = Ad(
                user_id=conversation.user_id,
                original_text=original_ad,
                enhanced_text=enhanced_ad,
                status=AdStatus.PENDING
            )
            db.session.add(ad)
            db.session.commit()
            
            conversation.update_context('ad_id', ad.id)
            conversation.set_state(ConversationState.ADVERTISER_SUBMITTED)
            
            response_text = self.ai_service.generate_response_message("advertiser", message_text, "ad_submitted")
            
            return {
                'text': response_text,
                'type': 'text'
            }
        
        elif any(word in message_lower for word in ['تعديل', 'edit', 'لا', 'no']):
            # Go back to ad input
            conversation.set_state(ConversationState.ADVERTISER_WAITING_AD)
            
            return {
                'text': "حسناً، من فضلك اكتب النص الجديد لإعلانك:",
                'type': 'text'
            }
        
        else:
            # Invalid response
            return {
                'text': "من فضلك اختر 'نعم' للموافقة أو 'تعديل' لإعادة كتابة الإعلان",
                'type': 'text',
                'quick_replies': [
                    {'title': '✅ نعم، موافق', 'payload': 'approve'},
                    {'title': '✏️ تعديل', 'payload': 'edit'}
                ]
            }
    
    def _handle_buyer_search_query(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle buyer search query"""
        # Analyze the search query
        analysis_result = self.ai_service.analyze_buyer_query(message_text)
        
        if analysis_result['success']:
            search_params = analysis_result['search_parameters']
            
            # Search for ads
            ads = Ad.search_ads(
                query=' '.join(search_params.get('keywords', [])),
                category=search_params.get('category'),
                min_price=search_params.get('price_min'),
                max_price=search_params.get('price_max'),
                location=search_params.get('location')
            )
            
            if ads:
                # Store search results in context
                conversation.update_context('search_query', message_text)
                conversation.update_context('search_results', [ad.to_dict() for ad in ads[:5]])  # Limit to 5 results
                conversation.set_state(ConversationState.BUYER_SHOWING_RESULTS)
                
                # Format results
                results_text = self.ai_service.generate_response_message("buyer", message_text, "search_results")
                results_text += "\n\n"
                
                for i, ad in enumerate(ads[:5], 1):
                    price_text = f" - {ad.price} جنيه" if ad.price else ""
                    location_text = f" - {ad.location}" if ad.location else ""
                    results_text += f"{i}. {ad.enhanced_text[:100]}...{price_text}{location_text}\n\n"
                
                return {
                    'text': results_text,
                    'type': 'text'
                }
            else:
                # No results found
                no_results_text = self.ai_service.generate_response_message("buyer", message_text, "no_results")
                
                return {
                    'text': no_results_text,
                    'type': 'text'
                }
        else:
            # Analysis failed
            return {
                'text': "عذرًا، لم أتمكن من فهم طلبك. من فضلك أعد صياغته بوضوح أكثر.",
                'type': 'text'
            }
    
    def _handle_buyer_results_interaction(self, conversation: Conversation, message_text: str) -> Dict[str, Any]:
        """Handle buyer interaction with search results"""
        # Check if user wants to search again
        if any(word in message_text.lower() for word in ['بحث جديد', 'بحث آخر', 'search', 'جديد']):
            conversation.set_state(ConversationState.BUYER_WAITING_QUERY)
            response_text = self.ai_service.generate_response_message("buyer", message_text, "buyer_request_search")
            
            return {
                'text': response_text,
                'type': 'text'
            }
        
        # Otherwise, provide help or restart
        return {
            'text': "هل تريد البحث عن شيء آخر؟ اكتب طلبك الجديد أو اكتب 'بحث جديد'",
            'type': 'text'
        }

