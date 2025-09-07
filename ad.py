from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class AdStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Ad(db.Model):
    __tablename__ = 'ads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    enhanced_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(AdStatus), default=AdStatus.PENDING, nullable=False)
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    location = db.Column(db.String(200))
    contact_info = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_text': self.original_text,
            'enhanced_text': self.enhanced_text,
            'status': self.status.value,
            'category': self.category,
            'price': self.price,
            'location': self.location,
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'admin_notes': self.admin_notes
        }
    
    def approve(self, admin_notes=None):
        self.status = AdStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.admin_notes = admin_notes
        db.session.commit()
    
    def reject(self, admin_notes=None):
        self.status = AdStatus.REJECTED
        self.rejected_at = datetime.utcnow()
        self.admin_notes = admin_notes
        db.session.commit()
    
    @classmethod
    def search_ads(cls, query=None, category=None, min_price=None, max_price=None, location=None):
        """Search approved ads based on criteria"""
        query_obj = cls.query.filter(cls.status == AdStatus.APPROVED)
        
        if query:
            # Search in enhanced text
            query_obj = query_obj.filter(cls.enhanced_text.contains(query))
        
        if category:
            query_obj = query_obj.filter(cls.category.ilike(f'%{category}%'))
        
        if min_price is not None:
            query_obj = query_obj.filter(cls.price >= min_price)
        
        if max_price is not None:
            query_obj = query_obj.filter(cls.price <= max_price)
        
        if location:
            query_obj = query_obj.filter(cls.location.ilike(f'%{location}%'))
        
        return query_obj.order_by(cls.created_at.desc()).all()

