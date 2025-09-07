from typing import Dict, Any, Optional, List
from facebook import FacebookMessenger
from whatsapp import WhatsAppBusiness
from instagram import InstagramMessaging
from telegram import TelegramBot

class PlatformManager:
    """Unified manager for all social media platform integrations"""
    
    def __init__(self):
        self.platforms = {
            'facebook': FacebookMessenger(),
            'whatsapp': WhatsAppBusiness(),
            'instagram': InstagramMessaging(),
            'telegram': TelegramBot()
        }
    
    def get_platform(self, platform_name: str):
        """Get platform integration by name"""
        return self.platforms.get(platform_name.lower())
    
    def verify_webhook(self, platform_name: str, **kwargs) -> Optional[str]:
        """Verify webhook for specified platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            return None
        
        if platform_name.lower() == 'facebook':
            return platform.verify_webhook(
                kwargs.get('hub_mode'),
                kwargs.get('hub_challenge'),
                kwargs.get('hub_verify_token')
            )
        elif platform_name.lower() == 'whatsapp':
            return platform.verify_webhook(
                kwargs.get('hub_mode'),
                kwargs.get('hub_challenge'),
                kwargs.get('hub_verify_token')
            )
        elif platform_name.lower() == 'instagram':
            return platform.verify_webhook(
                kwargs.get('hub_mode'),
                kwargs.get('hub_challenge'),
                kwargs.get('hub_verify_token')
            )
        elif platform_name.lower() == 'telegram':
            return str(kwargs.get('challenge', '')) if platform.verify_webhook(kwargs.get('secret_token', '')) else None
        
        return None
    
    def parse_webhook_events(self, platform_name: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse webhook events for specified platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            return []
        
        try:
            events = platform.parse_webhook_event(data)
            # Add platform information to each event
            for event in events:
                event['platform'] = platform_name.lower()
            return events
        except Exception as e:
            print(f"Error parsing {platform_name} webhook events: {e}")
            return []
    
    def send_message(self, platform_name: str, recipient_id: str, response_data: Dict[str, Any]) -> bool:
        """Send message via specified platform"""
        platform = self.get_platform(platform_name)
        if not platform:
            print(f"Platform {platform_name} not found")
            return False
        
        try:
            # Handle platform-specific recipient ID formats
            if platform_name.lower() == 'telegram':
                # For Telegram, we might need to use chat_id instead of sender_id
                chat_id = response_data.get('chat_id', recipient_id)
                return platform.send_message(chat_id, response_data)
            else:
                return platform.send_message(recipient_id, response_data)
        except Exception as e:
            print(f"Error sending message via {platform_name}: {e}")
            return False
    
    def get_user_profile(self, platform_name: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from specified platform"""
        platform = self.get_platform(platform_name)
        if not platform or not hasattr(platform, 'get_user_profile'):
            return None
        
        try:
            return platform.get_user_profile(user_id)
        except Exception as e:
            print(f"Error getting user profile from {platform_name}: {e}")
            return None
    
    def setup_platform_features(self, platform_name: str) -> bool:
        """Setup platform-specific features like welcome messages, menus, etc."""
        platform = self.get_platform(platform_name)
        if not platform:
            return False
        
        try:
            if platform_name.lower() == 'facebook':
                # Set welcome message
                welcome_text = "أهلاً بك في بوت الإعلانات العربي! 👋"
                platform.set_welcome_message(welcome_text)
                
                # Set persistent menu
                menu_items = [
                    {
                        'type': 'postback',
                        'title': 'البداية',
                        'payload': 'GET_STARTED'
                    },
                    {
                        'type': 'postback',
                        'title': 'مساعدة',
                        'payload': 'HELP'
                    }
                ]
                platform.set_persistent_menu(menu_items)
                
            elif platform_name.lower() == 'telegram':
                # Set bot commands
                commands = [
                    {'command': 'start', 'description': 'بدء محادثة جديدة'},
                    {'command': 'help', 'description': 'عرض المساعدة'},
                    {'command': 'advertiser', 'description': 'أنا معلن'},
                    {'command': 'buyer', 'description': 'أنا مشتري'}
                ]
                platform.set_my_commands(commands)
            
            return True
        except Exception as e:
            print(f"Error setting up features for {platform_name}: {e}")
            return False
    
    def normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data across different platforms"""
        platform = event.get('platform', '')
        normalized = {
            'platform': platform,
            'type': event.get('type', 'message'),
            'sender_id': event.get('sender_id', ''),
            'sender_name': event.get('sender_name', ''),
            'text': event.get('text', ''),
            'timestamp': event.get('timestamp'),
            'message_id': event.get('message_id', ''),
        }
        
        # Platform-specific normalizations
        if platform == 'telegram':
            normalized['chat_id'] = event.get('chat_id', event.get('sender_id', ''))
            
            # Handle Telegram commands
            if event.get('type') == 'command':
                command = event.get('command', '')
                if command == 'start':
                    normalized['text'] = 'البداية'
                elif command == 'help':
                    normalized['text'] = 'مساعدة'
                elif command == 'advertiser':
                    normalized['text'] = '1'
                elif command == 'buyer':
                    normalized['text'] = '2'
            
            # Handle callback queries
            elif event.get('type') == 'callback_query':
                normalized['text'] = event.get('data', '')
                normalized['callback_query_id'] = event.get('callback_query_id')
        
        elif platform == 'whatsapp':
            # Handle WhatsApp button replies
            if event.get('type') == 'button_reply':
                normalized['text'] = event.get('button_title', '')
            elif event.get('type') == 'list_reply':
                normalized['text'] = event.get('list_title', '')
        
        elif platform in ['facebook', 'instagram']:
            # Handle postbacks
            if event.get('type') == 'postback':
                payload = event.get('payload', '')
                if payload == 'GET_STARTED':
                    normalized['text'] = 'البداية'
                elif payload == 'HELP':
                    normalized['text'] = 'مساعدة'
                else:
                    normalized['text'] = event.get('title', payload)
        
        return normalized
    
    def get_platform_capabilities(self, platform_name: str) -> Dict[str, bool]:
        """Get capabilities of specified platform"""
        capabilities = {
            'quick_replies': False,
            'buttons': False,
            'images': False,
            'templates': False,
            'persistent_menu': False,
            'user_profile': False
        }
        
        platform_name = platform_name.lower()
        
        if platform_name == 'facebook':
            capabilities.update({
                'quick_replies': True,
                'buttons': True,
                'images': True,
                'persistent_menu': True,
                'user_profile': True
            })
        elif platform_name == 'whatsapp':
            capabilities.update({
                'buttons': True,
                'images': True,
                'templates': True
            })
        elif platform_name == 'instagram':
            capabilities.update({
                'quick_replies': True,
                'images': True,
                'user_profile': True
            })
        elif platform_name == 'telegram':
            capabilities.update({
                'buttons': True,
                'images': True
            })
        
        return capabilities
    
    def get_active_platforms(self) -> List[str]:
        """Get list of platforms that are properly configured"""
        active_platforms = []
        
        for platform_name, platform in self.platforms.items():
            if platform_name == 'facebook' and platform.page_access_token:
                active_platforms.append(platform_name)
            elif platform_name == 'whatsapp' and platform.access_token:
                active_platforms.append(platform_name)
            elif platform_name == 'instagram' and platform.page_access_token:
                active_platforms.append(platform_name)
            elif platform_name == 'telegram' and platform.bot_token:
                active_platforms.append(platform_name)
        
        return active_platforms

