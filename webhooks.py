from flask import Blueprint, request, jsonify
from platform_manager import PlatformManager
from message_handler import MessageHandler
import json

webhooks_bp = Blueprint('webhooks', __name__)

# Initialize managers
platform_manager = PlatformManager()
message_handler = MessageHandler()

@webhooks_bp.route('/facebook', methods=['GET', 'POST'])
def facebook_webhook():
    """Handle Facebook Messenger webhook"""

    if request.method == 'GET':
        # Webhook verification
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')

        challenge = platform_manager.verify_webhook('facebook',
            hub_mode=hub_mode,
            hub_challenge=hub_challenge,
            hub_verify_token=hub_verify_token
        )

        if challenge:
            return challenge
        else:
            return 'Verification failed', 403

    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = request.get_json()
            events = platform_manager.parse_webhook_events('facebook', data)

            for event in events:
                normalized_event = platform_manager.normalize_event(event)

                if normalized_event['type'] in ['message', 'postback']:
                    # Process the message
                    response = message_handler.process_message(
                        platform='facebook',
                        platform_user_id=normalized_event['sender_id'],
                        message_text=normalized_event['text'],
                        user_name=normalized_event.get('sender_name')
                    )

                    if response['success']:
                        # Send response back to user
                        platform_manager.send_message(
                            'facebook',
                            normalized_event['sender_id'],
                            response['response']
                        )

            return 'OK', 200

        except Exception as e:
            print(f"Error processing Facebook webhook: {e}")
            return 'Error', 500

@webhooks_bp.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Handle WhatsApp Business webhook"""

    if request.method == 'GET':
        # Webhook verification
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')

        challenge = platform_manager.verify_webhook('whatsapp',
            hub_mode=hub_mode,
            hub_challenge=hub_challenge,
            hub_verify_token=hub_verify_token
        )

        if challenge:
            return challenge
        else:
            return 'Verification failed', 403

    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = request.get_json()
            events = platform_manager.parse_webhook_events('whatsapp', data)

            for event in events:
                normalized_event = platform_manager.normalize_event(event)

                if normalized_event['type'] in ['message', 'button_reply', 'list_reply']:
                    # Process the message
                    response = message_handler.process_message(
                        platform='whatsapp',
                        platform_user_id=normalized_event['sender_id'],
                        message_text=normalized_event['text'],
                        user_name=normalized_event.get('sender_name')
                    )

                    if response['success']:
                        # Send response back to user
                        platform_manager.send_message(
                            'whatsapp',
                            normalized_event['sender_id'],
                            response['response']
                        )

                        # Mark message as read
                        whatsapp_platform = platform_manager.get_platform('whatsapp')
                        if hasattr(whatsapp_platform, 'mark_message_as_read') and normalized_event.get('message_id'):
                            whatsapp_platform.mark_message_as_read(normalized_event['message_id'])

            return 'OK', 200

        except Exception as e:
            print(f"Error processing WhatsApp webhook: {e}")
            return 'Error', 500

@webhooks_bp.route('/instagram', methods=['GET', 'POST'])
def instagram_webhook():
    """Handle Instagram Messaging webhook"""

    if request.method == 'GET':
        # Webhook verification
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')

        challenge = platform_manager.verify_webhook('instagram',
            hub_mode=hub_mode,
            hub_challenge=hub_challenge,
            hub_verify_token=hub_verify_token
        )

        if challenge:
            return challenge
        else:
            return 'Verification failed', 403

    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = request.get_json()
            events = platform_manager.parse_webhook_events('instagram', data)

            for event in events:
                normalized_event = platform_manager.normalize_event(event)

                if normalized_event['type'] in ['message', 'postback']:
                    # Process the message
                    response = message_handler.process_message(
                        platform='instagram',
                        platform_user_id=normalized_event['sender_id'],
                        message_text=normalized_event['text'],
                        user_name=normalized_event.get('sender_name')
                    )

                    if response['success']:
                        # Send response back to user
                        platform_manager.send_message(
                            'instagram',
                            normalized_event['sender_id'],
                            response['response']
                        )

            return 'OK', 200

        except Exception as e:
            print(f"Error processing Instagram webhook: {e}")
            return 'Error', 500

@webhooks_bp.route('/telegram', methods=['POST'])
def telegram_webhook():
    """Handle Telegram Bot webhook"""

    try:
        # Verify secret token if provided
        secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        telegram_platform = platform_manager.get_platform('telegram')

        if not telegram_platform.verify_webhook(secret_token or ''):
            return 'Unauthorized', 401

        data = request.get_json()
        events = platform_manager.parse_webhook_events('telegram', data)

        for event in events:
            normalized_event = platform_manager.normalize_event(event)

            if normalized_event['type'] in ['message', 'command', 'callback_query']:
                # Process the message
                response = message_handler.process_message(
                    platform='telegram',
                    platform_user_id=normalized_event['sender_id'],
                    message_text=normalized_event['text'],
                    user_name=normalized_event.get('sender_name')
                )

                if response['success']:
                    # Add chat_id for Telegram
                    response_data = response['response']
                    response_data['chat_id'] = normalized_event.get('chat_id', normalized_event['sender_id'])

                    # Send response back to user
                    platform_manager.send_message(
                        'telegram',
                        normalized_event.get('chat_id', normalized_event['sender_id']),
                        response_data
                    )

                    # Answer callback query if it's a button press
                    if normalized_event['type'] == 'callback_query':
                        callback_query_id = normalized_event.get('callback_query_id')
                        if callback_query_id:
                            telegram_platform.answer_callback_query(callback_query_id)

        return 'OK', 200

    except Exception as e:
        print(f"Error processing Telegram webhook: {e}")
        return 'Error', 500

@webhooks_bp.route('/status', methods=['GET'])
def webhook_status():
    """Get webhook status and platform information"""
    try:
        active_platforms = platform_manager.get_active_platforms()

        status = {
            'status': 'active',
            'active_platforms': active_platforms,
            'platform_capabilities': {}
        }

        for platform in active_platforms:
            status['platform_capabilities'][platform] = platform_manager.get_platform_capabilities(platform)

        return jsonify(status), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@webhooks_bp.route('/test', methods=['POST'])
def test_webhook():
    """Test webhook with sample message"""
    try:
        data = request.get_json()
        platform = data.get('platform', 'telegram')
        user_id = data.get('user_id', 'test_user')
        message = data.get('message', 'مرحبا')
        user_name = data.get('user_name', 'Test User')

        # Process test message
        response = message_handler.process_message(
            platform=platform,
            platform_user_id=user_id,
            message_text=message,
            user_name=user_name
        )

        return jsonify({
            'success': response['success'],
            'response': response['response'],
            'user_id': response.get('user_id'),
            'conversation_id': response.get('conversation_id')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

