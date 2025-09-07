from flask import Blueprint, request, jsonify
from ad import Ad, AdStatus
from user import User
from ai_service import AIService
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ads_bp = Blueprint('ads', __name__)
ai_service = AIService()

@ads_bp.route('/submit', methods=['POST'])
def submit_ad():
    """Submit a new advertisement"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'original_text']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        user_id = data['user_id']
        original_text = data['original_text']
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Enhance ad text using AI
        enhancement_result = ai_service.enhance_ad_text(original_text)
        enhanced_text = enhancement_result.get('enhanced_text', original_text)
        
        # Create ad record
        ad = Ad(
            user_id=user_id,
            original_text=original_text,
            enhanced_text=enhanced_text,
            status=AdStatus.PENDING,
            category=data.get('category'),
            price=data.get('price'),
            location=data.get('location'),
            contact_info=data.get('contact_info')
        )
        
        db.session.add(ad)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'ad_id': ad.id,
            'status': ad.status.value,
            'enhanced_text': enhanced_text,
            'improvement_score': enhancement_result.get('improvement_score')
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/search', methods=['GET'])
def search_ads():
    """Search approved advertisements"""
    try:
        # Get query parameters
        query = request.args.get('query', '').strip()
        category = request.args.get('category', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        location = request.args.get('location', '').strip()
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Limit the number of results
        limit = min(limit, 50)  # Max 50 results per request
        
        # Search ads
        ads = Ad.search_ads(
            query=query if query else None,
            category=category if category else None,
            min_price=min_price,
            max_price=max_price,
            location=location if location else None
        )
        
        # Apply pagination
        total_count = len(ads)
        ads = ads[offset:offset + limit]
        
        # Convert to dict format
        results = []
        for ad in ads:
            ad_dict = ad.to_dict()
            # Add user information
            ad_dict['user'] = {
                'id': ad.user.id,
                'name': ad.user.name
            }
            results.append(ad_dict)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'search_params': {
                'query': query,
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'location': location
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    """Get advertisement by ID"""
    try:
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({'error': 'Advertisement not found'}), 404
        
        ad_dict = ad.to_dict()
        ad_dict['user'] = {
            'id': ad.user.id,
            'name': ad.user.name,
            'phone': ad.user.phone,
            'email': ad.user.email
        }
        
        return jsonify({
            'success': True,
            'ad': ad_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/<int:ad_id>/approve', methods=['PUT'])
def approve_ad(ad_id):
    """Approve advertisement (Admin only)"""
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({'error': 'Advertisement not found'}), 404
        
        if ad.status != AdStatus.PENDING:
            return jsonify({'error': 'Advertisement is not pending approval'}), 400
        
        # Approve the ad
        ad.approve(admin_notes)
        
        # TODO: Send notification to user about approval
        # This would typically involve sending a message via the platform they used
        
        return jsonify({
            'success': True,
            'ad_id': ad.id,
            'status': ad.status.value,
            'approved_at': ad.approved_at.isoformat() if ad.approved_at else None,
            'admin_notes': ad.admin_notes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/<int:ad_id>/reject', methods=['PUT'])
def reject_ad(ad_id):
    """Reject advertisement (Admin only)"""
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({'error': 'Advertisement not found'}), 404
        
        if ad.status != AdStatus.PENDING:
            return jsonify({'error': 'Advertisement is not pending approval'}), 400
        
        # Reject the ad
        ad.reject(admin_notes)
        
        # TODO: Send notification to user about rejection
        # This would typically involve sending a message via the platform they used
        
        return jsonify({
            'success': True,
            'ad_id': ad.id,
            'status': ad.status.value,
            'rejected_at': ad.rejected_at.isoformat() if ad.rejected_at else None,
            'admin_notes': ad.admin_notes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/pending', methods=['GET'])
def get_pending_ads():
    """Get all pending advertisements for admin review"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Limit the number of results
        limit = min(limit, 100)  # Max 100 results per request
        
        # Get pending ads
        query = Ad.query.filter(Ad.status == AdStatus.PENDING).order_by(Ad.created_at.desc())
        total_count = query.count()
        ads = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        results = []
        for ad in ads:
            ad_dict = ad.to_dict()
            ad_dict['user'] = {
                'id': ad.user.id,
                'name': ad.user.name,
                'phone': ad.user.phone,
                'email': ad.user.email
            }
            results.append(ad_dict)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/stats', methods=['GET'])
def get_ads_stats():
    """Get advertisement statistics"""
    try:
        total_ads = Ad.query.count()
        pending_ads = Ad.query.filter(Ad.status == AdStatus.PENDING).count()
        approved_ads = Ad.query.filter(Ad.status == AdStatus.APPROVED).count()
        rejected_ads = Ad.query.filter(Ad.status == AdStatus.REJECTED).count()
        
        # Get recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_ads = Ad.query.filter(Ad.created_at >= week_ago).count()
        
        # Get category breakdown
        category_stats = {}
        ads_with_category = Ad.query.filter(Ad.category.isnot(None)).all()
        for ad in ads_with_category:
            category = ad.category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_ads': total_ads,
                'pending_ads': pending_ads,
                'approved_ads': approved_ads,
                'rejected_ads': rejected_ads,
                'recent_ads_7_days': recent_ads,
                'category_breakdown': category_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ads_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_ads(user_id):
    """Get all advertisements by a specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        status_filter = request.args.get('status', '').strip()
        
        # Build query
        query = Ad.query.filter(Ad.user_id == user_id).order_by(Ad.created_at.desc())
        
        if status_filter:
            try:
                status_enum = AdStatus(status_filter.lower())
                query = query.filter(Ad.status == status_enum)
            except ValueError:
                return jsonify({'error': f'Invalid status: {status_filter}'}), 400
        
        total_count = query.count()
        ads = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        results = [ad.to_dict() for ad in ads]
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

