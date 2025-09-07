import os
import requests
import hmac
import hashlib
from typing import Dict, Any, Optional
from flask import request, jsonify

class FacebookMessenger:
    """Facebook Messenger integration for the chatbot"""
    
    def __init__(self):
        self.page_access_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.verify_token = os.environ.get('FACEBOOK_VERIFY_TOKEN', 'arabic_chatbot_verify')
        self.app_secret = os.environ.get('FACEBOOK_APP_SECRET')
        self.api_version = 'v21.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def verify_webhook(self, hub_mode: str, hub_challenge: str, hub_verify_token: str) -> Optional[str]:
        """Verify Facebook webhook"""
        if hub_mode == 'subscribe' and hub_verify_token == self.verify_token:
            return hub_challenge
        return None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security"""
        if not self.app_secret:
            return True  # Skip verification if no app secret is set
        
        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f'sha256={expected_signature}', signature)
    
    def parse_webhook_event(self, data: Dict[str, Any]) -> list:
        """Parse incoming webhook events"""
        events = []
        
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for messaging_event in entry.get('messaging', []):
                    event = self._extract_message_event(messaging_event)
                    if event:
                        events.append(event)
        
        return events
    
    def _extract_message_event(self, messaging_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract message event from messaging event"""
        sender_id = messaging_event.get('sender', {}).get('id')
        recipient_id = messaging_event.get('recipient', {}).get('id')
        
        if 'message' in messaging_event:
            message = messaging_event['message']
            
            # Skip messages with attachments for now
            if 'attachments' in message:
                return {
                    'type': 'attachment',
                    'sender_id': sender_id,
                    'recipient_id': recipient_id,
                    'timestamp': messaging_event.get('timestamp'),
                    'message': 'عذرًا، لا يمكنني معالجة المرفقات حالياً. من فضلك أرسل رسالة نصية.'
                }
            
            text = message.get('text', '').strip()
            if text:
                return {
                    'type': 'message',
                    'sender_id': sender_id,
                    'recipient_id': recipient_id,
                    'timestamp': messaging_event.get('timestamp'),
                    'text': text
                }
        
        elif 'postback' in messaging_event:
            postback = messaging_event['postback']
            return {
                'type': 'postback',
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'timestamp': messaging_event.get('timestamp'),
                'payload': postback.get('payload'),
                'title': postback.get('title')
            }
        
        return None
    
    def send_message(self, recipient_id: str, response_data: Dict[str, Any]) -> bool:
        """Send message to Facebook Messenger user"""
        if not self.page_access_token:
            print("Facebook Page Access Token not configured")
            return False
        
        message_data = self._format_message(response_data)
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': message_data,
            'messaging_type': 'RESPONSE'
        }
        
        url = f'{self.base_url}/me/messages'
        params = {'access_token': self.page_access_token}
        
        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Facebook message: {e}")
            return False
    
    def _format_message(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response data for Facebook Messenger"""
        message_type = response_data.get('type', 'text')
        
        if message_type == 'text':
            message = {'text': response_data['text']}
            
            # Add quick replies if provided
            quick_replies = response_data.get('quick_replies', [])
            if quick_replies:
                message['quick_replies'] = []
                for reply in quick_replies[:13]:  # Facebook limit is 13
                    message['quick_replies'].append({
                        'content_type': 'text',
                        'title': reply['title'][:20],  # Facebook limit is 20 chars
                        'payload': reply.get('payload', reply['title'])
                    })
            
            return message
        
        elif message_type == 'image':
            return {
                'attachment': {
                    'type': 'image',
                    'payload': {
                        'url': response_data['image_url'],
                        'is_reusable': True
                    }
                }
            }
        
        else:
            # Fallback to text
            return {'text': response_data.get('text', 'رسالة غير مدعومة')}
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        if not self.page_access_token:
            return None
        
        url = f'{self.base_url}/{user_id}'
        params = {
            'fields': 'first_name,last_name,profile_pic',
            'access_token': self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting Facebook user profile: {e}")
            return None
    
    def set_persistent_menu(self, menu_items: list) -> bool:
        """Set persistent menu for the bot"""
        if not self.page_access_token:
            return False
        
        payload = {
            'persistent_menu': [
                {
                    'locale': 'default',
                    'composer_input_disabled': False,
                    'call_to_actions': menu_items
                }
            ]
        }
        
        url = f'{self.base_url}/me/messenger_profile'
        params = {'access_token': self.page_access_token}
        
        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error setting persistent menu: {e}")
            return False
    
    def set_welcome_message(self, welcome_text: str) -> bool:
        """Set welcome message for new users"""
        if not self.page_access_token:
            return False
        
        payload = {
            'greeting': [
                {
                    'locale': 'default',
                    'text': welcome_text
                }
            ]
        }
        
        url = f'{self.base_url}/me/messenger_profile'
        params = {'access_token': self.page_access_token}
        
        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error setting welcome message: {e}")
            return False

