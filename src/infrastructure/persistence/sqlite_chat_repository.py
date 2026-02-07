"""SQLite implementation of ChatHistoryRepository.

Persists chat conversations in a SQLite database for long-term storage.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ...domain.repositories import ChatHistoryRepository
from ...domain.models import ChatMessage, MessageRole
from ..mappers import ChatMessageMapper


class SQLiteChatRepository(ChatHistoryRepository):
    """SQLite-based chat history persistence."""
    
    def __init__(self, db_path: str = "./data/chat_history.db"):
        """Initialize SQLite repository.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.mapper = ChatMessageMapper()
        self._init_database()
    
    def _init_database(self) -> None:
        """Create database schema if it doesn't exist."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster session queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON chat_messages(session_id)
        """)
        
        # Create index for timestamp ordering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp 
            ON chat_messages(session_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Save a message to the database.
        
        Args:
            session_id: Session identifier.
            message: ChatMessage to save.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Use mapper to convert domain object to persistence tuple
        role, content, timestamp = self.mapper.to_persistence(message)
        
        cursor.execute("""
            INSERT INTO chat_messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Retrieve conversation history.
        
        Args:
            session_id: Session identifier.
            limit: Maximum number of messages (most recent).
            
        Returns:
            List of ChatMessage objects in chronological order.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT role, content, timestamp 
            FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY id ASC
        """
        
        if limit:
            # Get most recent N messages
            query = f"""
                SELECT role, content, timestamp 
                FROM (
                    SELECT role, content, timestamp 
                    FROM chat_messages 
                    WHERE session_id = ? 
                    ORDER BY id DESC 
                    LIMIT {limit}
                ) 
                ORDER BY timestamp ASC
            """
        
        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to ChatMessage objects using mapper
        messages = []
        for row in rows:
            message = self.mapper.to_domain(row)
            if message:
                messages.append(message)
        
        return messages
    
    def clear_history(self, session_id: str) -> None:
        """Clear all messages for a session.
        
        Args:
            session_id: Session identifier.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM chat_messages 
            WHERE session_id = ?
        """, (session_id,))
        
        conn.commit()
        conn.close()
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session (same as clear_history for SQLite).
        
        Args:
            session_id: Session identifier.
        """
        self.clear_history(session_id)
    
    def list_sessions(self) -> List[str]:
        """List all session IDs.
        
        Returns:
            List of unique session identifiers.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id
            FROM chat_messages
            GROUP BY session_id
            ORDER BY MAX(created_at) DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_session_stats(self, session_id: str) -> dict:
        """Get statistics for a session.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            Dictionary with session statistics.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_messages,
                MIN(created_at) as first_message,
                MAX(created_at) as last_message
            FROM chat_messages 
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_messages": row[0] if row else 0,
            "first_message": row[1] if row else None,
            "last_message": row[2] if row else None
        }
