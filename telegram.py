import os
import requests
from typing import Dict, Any, Optional

class TelegramBot:
    """Telegram Bot API integration for the chatbot"""
    
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.webhook_secret = os.environ.get('TELEGRAM_WEBHOOK_SECRET', 'arabic_chatbot_telegram')
        self.base_url = f'https://api.telegram.org/bot{self.bot_token}' if self.bot_token else None
    
    def verify_webhook(self, secret_token: str) -> bool:
        """Verify Telegram webhook secret token"""
        return secret_token == self.webhook_secret
    
    def parse_webhook_event(self, data: Dict[str, Any]) -> list:
        """Parse incoming webhook events"""
        events = []
        
        # Handle regular messages
        if 'message' in data:
            event = self._extract_message_event(data['message'])
            if event:
                events.append(event)
        
        # Handle callback queries (inline keyboard buttons)
        elif 'callback_query' in data:
            event = self._extract_callback_query_event(data['callback_query'])
            if event:
                events.append(event)
        
        # Handle inline queries
        elif 'inline_query' in data:
            event = self._extract_inline_query_event(data['inline_query'])
            if event:
                events.append(event)
        
        return events
    
    def _extract_message_event(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract message event from Telegram message"""
        user = message.get('from', {})
        chat = message.get('chat', {})
        
        user_id = user.get('id')
        chat_id = chat.get('id')
        message_id = message.get('message_id')
        date = message.get('date')
        
        # Get user name
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')
        username = user.get('username', '')
        user_name = f"{first_name} {last_name}".strip() or username or str(user_id)
        
        # Handle text messages
        if 'text' in message:
            text = message['text'].strip()
            
            # Handle commands
            if text.startswith('/'):
                return {
                    'type': 'command',
                    'sender_id': str(user_id),
                    'chat_id': str(chat_id),
                    'sender_name': user_name,
                    'message_id': message_id,
                    'timestamp': date,
                    'command': text.split()[0][1:],  # Remove '/' prefix
                    'text': text
                }
            else:
                return {
                    'type': 'message',
                    'sender_id': str(user_id),
                    'chat_id': str(chat_id),
                    'sender_name': user_name,
                    'message_id': message_id,
                    'timestamp': date,
                    'text': text
                }
        
        # Handle other message types
        elif any(key in message for key in ['photo', 'document', 'audio', 'video', 'voice', 'sticker']):
            return {
                'type': 'attachment',
                'sender_id': str(user_id),
                'chat_id': str(chat_id),
                'sender_name': user_name,
                'message_id': message_id,
                'timestamp': date,
                'message': 'عذرًا، لا يمكنني معالجة المرفقات حالياً. من فضلك أرسل رسالة نصية.'
            }
        
        return None
    
    def _extract_callback_query_event(self, callback_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract callback query event from inline keyboard button press"""
        user = callback_query.get('from', {})
        message = callback_query.get('message', {})
        
        user_id = user.get('id')
        chat_id = message.get('chat', {}).get('id')
        
        # Get user name
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')
        username = user.get('username', '')
        user_name = f"{first_name} {last_name}".strip() or username or str(user_id)
        
        return {
            'type': 'callback_query',
            'sender_id': str(user_id),
            'chat_id': str(chat_id),
            'sender_name': user_name,
            'callback_query_id': callback_query.get('id'),
            'data': callback_query.get('data'),
            'message_id': message.get('message_id')
        }
    
    def _extract_inline_query_event(self, inline_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract inline query event"""
        user = inline_query.get('from', {})
        user_id = user.get('id')
        
        # Get user name
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')
        username = user.get('username', '')
        user_name = f"{first_name} {last_name}".strip() or username or str(user_id)
        
        return {
            'type': 'inline_query',
            'sender_id': str(user_id),
            'sender_name': user_name,
            'query_id': inline_query.get('id'),
            'query': inline_query.get('query', '').strip()
        }
    
    def send_message(self, chat_id: str, response_data: Dict[str, Any]) -> bool:
        """Send message to Telegram user"""
        if not self.base_url:
            print("Telegram Bot Token not configured")
            return False
        
        message_data = self._format_message(response_data)
        message_data['chat_id'] = chat_id
        
        url = f'{self.base_url}/sendMessage'
        
        try:
            response = requests.post(url, json=message_data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def _format_message(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response data for Telegram"""
        message_type = response_data.get('type', 'text')
        
        if message_type == 'text':
            message = {
                'text': response_data['text'],
                'parse_mode': 'HTML'  # Support HTML formatting
            }
            
            # Add inline keyboard if quick replies are provided
            quick_replies = response_data.get('quick_replies', [])
            if quick_replies:
                keyboard = []
                row = []
                
                for i, reply in enumerate(quick_replies):
                    button = {
                        'text': reply['title'],
                        'callback_data': reply.get('payload', reply['title'])[:64]  # Telegram limit is 64 bytes
                    }
                    row.append(button)
                    
                    # Create new row every 2 buttons or at the end
                    if len(row) == 2 or i == len(quick_replies) - 1:
                        keyboard.append(row)
                        row = []
                
                message['reply_markup'] = {
                    'inline_keyboard': keyboard
                }
            
            return message
        
        elif message_type == 'image':
            return {
                'photo': response_data['image_url'],
                'caption': response_data.get('text', '')
            }
        
        else:
            # Fallback to text
            return {
                'text': response_data.get('text', 'رسالة غير مدعومة'),
                'parse_mode': 'HTML'
            }
    
    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False) -> bool:
        """Answer callback query from inline keyboard"""
        if not self.base_url:
            return False
        
        payload = {
            'callback_query_id': callback_query_id,
            'show_alert': show_alert
        }
        
        if text:
            payload['text'] = text
        
        url = f'{self.base_url}/answerCallbackQuery'
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error answering Telegram callback query: {e}")
            return False
    
    def set_webhook(self, webhook_url: str, secret_token: str = None) -> bool:
        """Set webhook URL for the bot"""
        if not self.base_url:
            return False
        
        payload = {
            'url': webhook_url,
            'allowed_updates': ['message', 'callback_query', 'inline_query']
        }
        
        if secret_token:
            payload['secret_token'] = secret_token
        
        url = f'{self.base_url}/setWebhook'
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error setting Telegram webhook: {e}")
            return False
    
    def get_webhook_info(self) -> Optional[Dict[str, Any]]:
        """Get current webhook information"""
        if not self.base_url:
            return None
        
        url = f'{self.base_url}/getWebhookInfo'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting Telegram webhook info: {e}")
            return None
    
    def set_my_commands(self, commands: list) -> bool:
        """Set bot commands menu"""
        if not self.base_url:
            return False
        
        payload = {'commands': commands}
        url = f'{self.base_url}/setMyCommands'
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error setting Telegram commands: {e}")
            return False

