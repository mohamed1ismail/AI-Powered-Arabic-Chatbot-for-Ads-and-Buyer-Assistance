import os
import requests
import hmac
import hashlib
from typing import Dict, Any, Optional

class InstagramMessaging:
    """Instagram Messaging API integration for the chatbot"""
    
    def __init__(self):
        self.page_access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
        self.verify_token = os.environ.get('INSTAGRAM_VERIFY_TOKEN', 'arabic_chatbot_instagram')
        self.app_secret = os.environ.get('INSTAGRAM_APP_SECRET')
        self.api_version = 'v21.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def verify_webhook(self, hub_mode: str, hub_challenge: str, hub_verify_token: str) -> Optional[str]:
        """Verify Instagram webhook"""
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
        
        if data.get('object') == 'instagram':
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
        """Send message to Instagram user"""
        if not self.page_access_token:
            print("Instagram Page Access Token not configured")
            return False
        
        message_data = self._format_message(response_data)
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': message_data
        }
        
        url = f'{self.base_url}/me/messages'
        params = {'access_token': self.page_access_token}
        
        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Instagram message: {e}")
            return False
    
    def _format_message(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response data for Instagram Messaging"""
        message_type = response_data.get('type', 'text')
        
        if message_type == 'text':
            message = {'text': response_data['text']}
            
            # Add quick replies if provided (Instagram supports up to 13)
            quick_replies = response_data.get('quick_replies', [])
            if quick_replies:
                message['quick_replies'] = []
                for reply in quick_replies[:13]:
                    message['quick_replies'].append({
                        'content_type': 'text',
                        'title': reply['title'][:20],  # Instagram limit is 20 chars
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
            'fields': 'name,profile_pic',
            'access_token': self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting Instagram user profile: {e}")
            return None
    
    def send_ice_breaker(self, recipient_id: str, ice_breaker_text: str) -> bool:
        """Send ice breaker message to start conversation"""
        if not self.page_access_token:
            return False
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': ice_breaker_text},
            'messaging_type': 'MESSAGE_TAG',
            'tag': 'HUMAN_AGENT'
        }
        
        url = f'{self.base_url}/me/messages'
        params = {'access_token': self.page_access_token}
        
        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Instagram ice breaker: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> Optional[list]:
        """Get conversation history with a user"""
        if not self.page_access_token:
            return None
        
        url = f'{self.base_url}/{user_id}/conversations'
        params = {
            'fields': 'messages{message,created_time,from}',
            'limit': limit,
            'access_token': self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            conversations = []
            for conversation in data.get('data', []):
                for message in conversation.get('messages', {}).get('data', []):
                    conversations.append({
                        'text': message.get('message'),
                        'timestamp': message.get('created_time'),
                        'from_user': message.get('from', {}).get('id') == user_id
                    })
            
            return sorted(conversations, key=lambda x: x['timestamp'])
        except requests.exceptions.RequestException as e:
            print(f"Error getting Instagram conversation history: {e}")
            return None

