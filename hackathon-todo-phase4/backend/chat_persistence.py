"""
Chat Persistence Module
Provides database-persisted conversations for stateless chat endpoints
"""

from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel


# Models
class ConversationCreate(BaseModel):
    user_id: Optional[str] = None
    title: Optional[str] = "New Conversation"


class ConversationResponse(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    conversation_id: str
    role: str  # "user", "assistant", "system"
    content: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


class ConversationWithMessages(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]


# Database operations
def init_chat_tables(conn):
    """Create chat-related tables if they don't exist"""
    cursor = conn.cursor()

    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36),
            title VARCHAR(255) DEFAULT 'New Conversation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id VARCHAR(36) PRIMARY KEY,
            conversation_id VARCHAR(36) REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
        ON messages(conversation_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_user_id
        ON conversations(user_id)
    """)

    conn.commit()
    cursor.close()


def create_conversation(
    conn,
    user_id: Optional[str] = None,
    title: str = "New Conversation"
) -> dict:
    """Create a new conversation"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    conversation_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO conversations (id, user_id, title)
        VALUES (%s, %s, %s)
        RETURNING id, user_id, title, created_at, updated_at
        """,
        (conversation_id, user_id, title)
    )
    conversation = cursor.fetchone()
    conn.commit()
    cursor.close()

    return dict(conversation)


def get_conversation(conn, conversation_id: str) -> Optional[dict]:
    """Get a conversation by ID"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM conversations WHERE id = %s",
        (conversation_id,)
    )
    conversation = cursor.fetchone()
    cursor.close()

    return dict(conversation) if conversation else None


def get_user_conversations(
    conn,
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[dict]:
    """Get all conversations for a user"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT * FROM conversations
        WHERE user_id = %s
        ORDER BY updated_at DESC
        LIMIT %s OFFSET %s
        """,
        (user_id, limit, offset)
    )
    conversations = cursor.fetchall()
    cursor.close()

    return [dict(c) for c in conversations]


def update_conversation_title(conn, conversation_id: str, title: str) -> dict:
    """Update conversation title"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        UPDATE conversations
        SET title = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *
        """,
        (title, conversation_id)
    )
    conversation = cursor.fetchone()
    conn.commit()
    cursor.close()

    return dict(conversation) if conversation else None


def delete_conversation(conn, conversation_id: str) -> bool:
    """Delete a conversation and all its messages"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()

    return deleted


def add_message(
    conn,
    conversation_id: str,
    role: str,
    content: str
) -> dict:
    """Add a message to a conversation"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    message_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO messages (id, conversation_id, role, content)
        VALUES (%s, %s, %s, %s)
        RETURNING id, conversation_id, role, content, created_at
        """,
        (message_id, conversation_id, role, content)
    )
    message = cursor.fetchone()

    # Update conversation's updated_at
    cursor.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (conversation_id,)
    )

    conn.commit()
    cursor.close()

    return dict(message)


def get_conversation_messages(
    conn,
    conversation_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[dict]:
    """Get all messages in a conversation"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT * FROM messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        LIMIT %s OFFSET %s
        """,
        (conversation_id, limit, offset)
    )
    messages = cursor.fetchall()
    cursor.close()

    return [dict(m) for m in messages]


def get_conversation_with_messages(conn, conversation_id: str) -> Optional[dict]:
    """Get conversation with all its messages"""
    conversation = get_conversation(conn, conversation_id)
    if not conversation:
        return None

    messages = get_conversation_messages(conn, conversation_id)

    return {
        "conversation": conversation,
        "messages": messages
    }


def get_or_create_conversation(
    conn,
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> dict:
    """Get existing conversation or create a new one"""
    if conversation_id:
        conversation = get_conversation(conn, conversation_id)
        if conversation:
            return conversation

    # Create new conversation
    return create_conversation(conn, user_id=user_id)
