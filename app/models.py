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
    clip_id = Column(Integer, nullable=False)  # Sequential clip number
    user_id = Column(Integer, nullable=False)  # Foreign key to users table
    user_name = Column(String(255), nullable=False)
    recording_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Date of recording
    file_name = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    start_time = Column(DateTime, nullable=False)  # Per-spec naming
    end_time = Column(DateTime, nullable=False)  # Per-spec naming
    duration_seconds = Column(Integer, nullable=False)  # Duration in seconds
    chunk_duration_seconds = Column(Integer, nullable=False, default=180)  # Per-chunk duration
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<VideoChunk(user_name='{self.user_name}', file_name='{self.file_name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'clip_id': self.clip_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'recording_date': self.recording_date.isoformat(),
            'file_name': self.file_name,
            'file_path': self.file_path,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': self.duration_seconds,
            'chunk_duration_seconds': self.chunk_duration_seconds,
            'created_at': self.created_at.isoformat()
        }