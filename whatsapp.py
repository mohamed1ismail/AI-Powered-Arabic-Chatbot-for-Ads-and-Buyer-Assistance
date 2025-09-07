import os
import requests
import hmac
import hashlib
from typing import Dict, Any, Optional
from flask import request

class WhatsAppBusiness:
    """WhatsApp Business API integration for the chatbot"""
    
    def __init__(self):
        self.access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        self.webhook_verify_token = os.environ.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'arabic_chatbot_whatsapp')
        self.api_version = 'v21.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def verify_webhook(self, hub_mode: str, hub_challenge: str, hub_verify_token: str) -> Optional[str]:
        """Verify WhatsApp webhook"""
        if hub_mode == 'subscribe' and hub_verify_token == self.webhook_verify_token:
            return hub_challenge
        return None
    
    def parse_webhook_event(self, data: Dict[str, Any]) -> list:
        """Parse incoming webhook events"""
        events = []
        
        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        
                        # Process incoming messages
                        for message in value.get('messages', []):
                            event = self._extract_message_event(message, value)
                            if event:
                                events.append(event)
                        
                        # Process message status updates
                        for status in value.get('statuses', []):
                            event = self._extract_status_event(status)
                            if event:
                                events.append(event)
        
        return events
    
    def _extract_message_event(self, message: Dict[str, Any], value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract message event from WhatsApp message"""
        sender_phone = message.get('from')
        message_id = message.get('id')
        timestamp = message.get('timestamp')
        message_type = message.get('type')
        
        # Get contact info
        contacts = value.get('contacts', [])
        sender_name = None
        for contact in contacts:
            if contact.get('wa_id') == sender_phone:
                profile = contact.get('profile', {})
                sender_name = profile.get('name')
                break
        
        if message_type == 'text':
            text_body = message.get('text', {}).get('body', '').strip()
            if text_body:
                return {
                    'type': 'message',
                    'sender_id': sender_phone,
                    'sender_name': sender_name,
                    'message_id': message_id,
                    'timestamp': timestamp,
                    'text': text_body
                }
        
        elif message_type == 'interactive':
            interactive = message.get('interactive', {})
            if interactive.get('type') == 'button_reply':
                button_reply = interactive.get('button_reply', {})
                return {
                    'type': 'button_reply',
                    'sender_id': sender_phone,
                    'sender_name': sender_name,
                    'message_id': message_id,
                    'timestamp': timestamp,
                    'button_id': button_reply.get('id'),
                    'button_title': button_reply.get('title')
                }
            elif interactive.get('type') == 'list_reply':
                list_reply = interactive.get('list_reply', {})
                return {
                    'type': 'list_reply',
                    'sender_id': sender_phone,
                    'sender_name': sender_name,
                    'message_id': message_id,
                    'timestamp': timestamp,
                    'list_id': list_reply.get('id'),
                    'list_title': list_reply.get('title')
                }
        
        elif message_type in ['image', 'document', 'audio', 'video']:
            return {
                'type': 'attachment',
                'sender_id': sender_phone,
                'sender_name': sender_name,
                'message_id': message_id,
                'timestamp': timestamp,
                'attachment_type': message_type,
                'message': 'عذرًا، لا يمكنني معالجة المرفقات حالياً. من فضلك أرسل رسالة نصية.'
            }
        
        return None
    
    def _extract_status_event(self, status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract status event from WhatsApp status update"""
        return {
            'type': 'status',
            'message_id': status.get('id'),
            'recipient_id': status.get('recipient_id'),
            'status': status.get('status'),
            'timestamp': status.get('timestamp')
        }
    
    def send_message(self, recipient_phone: str, response_data: Dict[str, Any]) -> bool:
        """Send message to WhatsApp user"""
        if not self.access_token or not self.phone_number_id:
            print("WhatsApp access token or phone number ID not configured")
            return False
        
        message_data = self._format_message(response_data)
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            **message_data
        }
        
        url = f'{self.base_url}/{self.phone_number_id}/messages'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def _format_message(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response data for WhatsApp"""
        message_type = response_data.get('type', 'text')
        
        if message_type == 'text':
            message = {
                'type': 'text',
                'text': {'body': response_data['text']}
            }
            
            # Add interactive buttons if quick replies are provided
            quick_replies = response_data.get('quick_replies', [])
            if quick_replies and len(quick_replies) <= 3:  # WhatsApp limit is 3 buttons
                message = {
                    'type': 'interactive',
                    'interactive': {
                        'type': 'button',
                        'body': {'text': response_data['text']},
                        'action': {
                            'buttons': []
                        }
                    }
                }
                
                for i, reply in enumerate(quick_replies[:3]):
                    message['interactive']['action']['buttons'].append({
                        'type': 'reply',
                        'reply': {
                            'id': f'btn_{i}_{reply.get("payload", reply["title"])}',
                            'title': reply['title'][:20]  # WhatsApp limit is 20 chars
                        }
                    })
            
            return message
        
        elif message_type == 'image':
            return {
                'type': 'image',
                'image': {
                    'link': response_data['image_url']
                }
            }
        
        else:
            # Fallback to text
            return {
                'type': 'text',
                'text': {'body': response_data.get('text', 'رسالة غير مدعومة')}
            }
    
    def send_template_message(self, recipient_phone: str, template_name: str, language_code: str = 'ar', components: list = None) -> bool:
        """Send WhatsApp template message"""
        if not self.access_token or not self.phone_number_id:
            return False
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language_code}
            }
        }
        
        if components:
            payload['template']['components'] = components
        
        url = f'{self.base_url}/{self.phone_number_id}/messages'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending WhatsApp template: {e}")
            return False
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """Mark message as read"""
        if not self.access_token or not self.phone_number_id:
            return False
        
        payload = {
            'messaging_product': 'whatsapp',
            'status': 'read',
            'message_id': message_id
        }
        
        url = f'{self.base_url}/{self.phone_number_id}/messages'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error marking message as read: {e}")
            return False

