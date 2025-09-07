from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import json

db = SQLAlchemy()

class ConversationState(Enum):
    INITIAL = "initial"
    WAITING_USER_TYPE = "waiting_user_type"
    ADVERTISER_WAITING_AD = "advertiser_waiting_ad"
    ADVERTISER_CONFIRMING = "advertiser_confirming"
    ADVERTISER_SUBMITTED = "advertiser_submitted"
    BUYER_WAITING_QUERY = "buyer_waiting_query"
    BUYER_SHOWING_RESULTS = "buyer_showing_results"
    COMPLETED = "completed"

class UserType(Enum):
    ADVERTISER = "advertiser"  # معلن
    BUYER = "buyer"  # مشتري

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # facebook, whatsapp, instagram, telegram
    platform_user_id = db.Column(db.String(200), nullable=False)
    state = db.Column(db.Enum(ConversationState), default=ConversationState.INITIAL, nullable=False)
    user_type = db.Column(db.Enum(UserType))
    context_data = db.Column(db.Text)  # JSON string for storing conversation context
    last_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.context_data is None:
            self.context_data = json.dumps({})
    
    def get_context(self):
        """Get conversation context as dictionary"""
        if self.context_data:
            return json.loads(self.context_data)
        return {}
    
    def set_context(self, context_dict):
        """Set conversation context from dictionary"""
        self.context_data = json.dumps(context_dict)
        db.session.commit()
    
    def update_context(self, key, value):
        """Update a specific key in conversation context"""
        context = self.get_context()
        context[key] = value
        self.set_context(context)
    
    def set_state(self, new_state):
        """Update conversation state"""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def set_user_type(self, user_type):
        """Set user type (advertiser or buyer)"""
        self.user_type = user_type
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'platform_user_id': self.platform_user_id,
            'state': self.state.value,
            'user_type': self.user_type.value if self.user_type else None,
            'context_data': self.get_context(),
            'last_message': self.last_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_or_create(cls, platform, platform_user_id, user_id):
        """Get existing conversation or create new one"""
        conversation = cls.query.filter_by(
            platform=platform,
            platform_user_id=platform_user_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            conversation = cls(
                platform=platform,
                platform_user_id=platform_user_id,
                user_id=user_id,
                state=ConversationState.INITIAL
            )
            db.session.add(conversation)
            db.session.commit()
        
        return conversation

