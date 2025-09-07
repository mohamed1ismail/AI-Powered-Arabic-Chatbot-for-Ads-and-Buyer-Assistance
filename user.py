from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    preferred_language = db.Column(db.String(10), default='ar')  # Arabic by default
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name or self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'preferred_language': self.preferred_language,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_or_create_by_platform(cls, platform, platform_user_id, name=None):
        """Get or create user by platform identity"""
        from app_platform import PlatformUser
        
        platform_user = PlatformUser.query.filter_by(
            platform=platform,
            platform_user_id=platform_user_id
        ).first()
        
        if platform_user:
            return platform_user.user
        
        # Create new user
        user = cls(name=name)
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create platform mapping
        platform_user = PlatformUser(
            user_id=user.id,
            platform=platform,
            platform_user_id=platform_user_id,
            platform_name=name
        )
        db.session.add(platform_user)
        db.session.commit()
        
        return user
