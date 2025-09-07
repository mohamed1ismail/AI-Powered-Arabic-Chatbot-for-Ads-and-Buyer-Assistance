from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PlatformUser(db.Model):
    __tablename__ = 'platform_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # facebook, whatsapp, instagram, telegram
    platform_user_id = db.Column(db.String(200), nullable=False)  # Platform-specific user ID
    platform_name = db.Column(db.String(200))  # User's name on the platform
    platform_username = db.Column(db.String(100))  # Username on the platform (if available)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate platform users
    __table_args__ = (db.UniqueConstraint('platform', 'platform_user_id', name='unique_platform_user'),)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('platform_users', lazy=True))
    
    def __repr__(self):
        return f'<PlatformUser {self.platform}:{self.platform_user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'platform_user_id': self.platform_user_id,
            'platform_name': self.platform_name,
            'platform_username': self.platform_username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_platform_id(cls, platform, platform_user_id):
        """Get platform user by platform and platform user ID"""
        return cls.query.filter_by(
            platform=platform,
            platform_user_id=platform_user_id
        ).first()
    
    @classmethod
    def create_or_update(cls, user_id, platform, platform_user_id, platform_name=None, platform_username=None):
        """Create or update platform user"""
        platform_user = cls.get_by_platform_id(platform, platform_user_id)
        
        if platform_user:
            # Update existing
            if platform_name:
                platform_user.platform_name = platform_name
            if platform_username:
                platform_user.platform_username = platform_username
            platform_user.updated_at = datetime.utcnow()
        else:
            # Create new
            platform_user = cls(
                user_id=user_id,
                platform=platform,
                platform_user_id=platform_user_id,
                platform_name=platform_name,
                platform_username=platform_username
            )
            db.session.add(platform_user)
        
        db.session.commit()
        return platform_user

