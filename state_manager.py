from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class StateManager:
    """Manages conversation state and session data"""
    
    def __init__(self):
        # In-memory storage for development (use Redis in production)
        self._sessions = {}
        self._session_timeout = timedelta(hours=24)  # 24 hour session timeout
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            # Check if session has expired
            if datetime.now() - session['last_accessed'] < self._session_timeout:
                session['last_accessed'] = datetime.now()
                return session['data']
            else:
                # Session expired, remove it
                del self._sessions[session_id]
        
        return None
    
    def set_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Set session data"""
        self._sessions[session_id] = {
            'data': data,
            'created_at': datetime.now(),
            'last_accessed': datetime.now()
        }
    
    def update_session(self, session_id: str, key: str, value: Any) -> None:
        """Update a specific key in session data"""
        session = self.get_session(session_id)
        if session is None:
            session = {}
        
        session[key] = value
        self.set_session(session_id, session)
    
    def delete_session(self, session_id: str) -> None:
        """Delete session data"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of removed sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if current_time - session['last_accessed'] >= self._session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self._sessions)
    
    def create_session_id(self, platform: str, platform_user_id: str) -> str:
        """Create a unique session ID for platform and user"""
        return f"{platform}:{platform_user_id}"
    
    def store_conversation_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Store conversation context in session"""
        self.update_session(session_id, 'conversation_context', context)
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context from session"""
        session = self.get_session(session_id)
        if session:
            return session.get('conversation_context', {})
        return {}
    
    def store_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> None:
        """Store user preferences in session"""
        self.update_session(session_id, 'user_preferences', preferences)
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences from session"""
        session = self.get_session(session_id)
        if session:
            return session.get('user_preferences', {})
        return {}
    
    def store_search_history(self, session_id: str, search_query: str, results_count: int) -> None:
        """Store search history in session"""
        session = self.get_session(session_id)
        if session is None:
            session = {}
        
        if 'search_history' not in session:
            session['search_history'] = []
        
        session['search_history'].append({
            'query': search_query,
            'results_count': results_count,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 searches
        session['search_history'] = session['search_history'][-10:]
        
        self.set_session(session_id, session)
    
    def get_search_history(self, session_id: str) -> list:
        """Get search history from session"""
        session = self.get_session(session_id)
        if session:
            return session.get('search_history', [])
        return []
    
    def store_ad_draft(self, session_id: str, ad_data: Dict[str, Any]) -> None:
        """Store ad draft in session"""
        self.update_session(session_id, 'ad_draft', ad_data)
    
    def get_ad_draft(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get ad draft from session"""
        session = self.get_session(session_id)
        if session:
            return session.get('ad_draft')
        return None
    
    def clear_ad_draft(self, session_id: str) -> None:
        """Clear ad draft from session"""
        session = self.get_session(session_id)
        if session and 'ad_draft' in session:
            del session['ad_draft']
            self.set_session(session_id, session)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        current_time = datetime.now()
        active_sessions = 0
        expired_sessions = 0
        
        for session in self._sessions.values():
            if current_time - session['last_accessed'] < self._session_timeout:
                active_sessions += 1
            else:
                expired_sessions += 1
        
        return {
            'total_sessions': len(self._sessions),
            'active_sessions': active_sessions,
            'expired_sessions': expired_sessions,
            'session_timeout_hours': self._session_timeout.total_seconds() / 3600
        }
    
    def export_session_data(self, session_id: str) -> Optional[str]:
        """Export session data as JSON string"""
        session = self.get_session(session_id)
        if session:
            # Convert datetime objects to strings for JSON serialization
            exportable_data = {}
            for key, value in session.items():
                if isinstance(value, datetime):
                    exportable_data[key] = value.isoformat()
                else:
                    exportable_data[key] = value
            
            return json.dumps(exportable_data, ensure_ascii=False, indent=2)
        return None
    
    def import_session_data(self, session_id: str, json_data: str) -> bool:
        """Import session data from JSON string"""
        try:
            data = json.loads(json_data)
            self.set_session(session_id, data)
            return True
        except (json.JSONDecodeError, Exception):
            return False

