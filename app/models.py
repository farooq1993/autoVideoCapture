from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class VideoChunk(Base):
    __tablename__ = 'video_chunks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to users table
    user_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    record_start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    record_end_time = Column(DateTime, nullable=False)
    duration_seconds = Column(Float, nullable=False)  # Total recording duration requested
    chunk_duration_seconds = Column(Float, nullable=False, default=180)  # Per-chunk duration
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<VideoChunk(user_name='{self.user_name}', file_name='{self.file_name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'record_start_time': self.record_start_time.isoformat(),
            'record_end_time': self.record_end_time.isoformat(),
            'duration_seconds': self.duration_seconds,
            'chunk_duration_seconds': self.chunk_duration_seconds,
            'created_at': self.created_at.isoformat()
        }