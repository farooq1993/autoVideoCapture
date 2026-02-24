from flask import Blueprint, jsonify, request, send_file
from models import VideoChunk, User
from database import SessionLocal, init_db
from video_recorder import VideoRecorder
from datetime import datetime
import os
import logging
import threading

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

class RecordingSession:
    """Track recording session state"""
    def __init__(self, username, user_id, total_duration, chunk_duration):
        self.username = username
        self.user_id = user_id
        self.total_duration = total_duration
        self.chunk_duration = chunk_duration
        self.clip_count = 0
        self.is_active = True
        self.start_time = datetime.now()
        self.thread = None
        self.recorder = None

# Global variable to track recording state
recording_threads = {}


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check endpoint called.")
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# ==================== USER MANAGEMENT ====================

@api_bp.route('/users/register', methods=['POST'])
def register_user():
    """
    Register a new user.
    Request body: {
        "username": "john_doe",
        "email": "john@example.com"
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', '')
        email = data.get('email', '')
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "username must be at least 3 characters"}), 400
        
        db = SessionLocal()
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            db.close()
            return jsonify({"error": "User already exists"}), 409
        
        # Create new user
        new_user = User(
            username=username,
            email=email if email else None
        )
        
        db.add(new_user)
        db.commit()
        
        user_data = new_user.to_dict()
        db.close()
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_data
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users/login', methods=['POST'])
def login_user():
    """
    Login user - verify user exists.
    Request body: {
        "username": "john_doe"
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "message": f"Welcome {username}!",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all registered users"""
    try:
        db = SessionLocal()
        users = db.query(User).all()
        db.close()
        
        return jsonify({
            "total_users": len(users),
            "users": [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users/<username>', methods=['GET'])
def get_user(username):
    """Get a specific user by username"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== RECORDING MANAGEMENT ====================

@api_bp.route('/start-recording', methods=['POST'])
def start_recording():
    """
    Start recording video.
    Request body: {
        "username": "john_doe",
        "total_duration_seconds": 900,      (optional, default: 900 = 15 min)
        "chunk_duration_seconds": 180       (optional, default: 180 = 3 min)
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        total_duration = int(data.get('total_duration_seconds', 900))
        chunk_duration = int(data.get('chunk_duration_seconds', 180))
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        # Validate durations
        if total_duration < 60:
            return jsonify({"error": "total_duration_seconds must be at least 60 seconds"}), 400
        if chunk_duration < 30:
            return jsonify({"error": "chunk_duration_seconds must be at least 30 seconds"}), 400
        if chunk_duration > total_duration:
            return jsonify({"error": "chunk_duration_seconds cannot exceed total_duration_seconds"}), 400
        
        # Check if user exists
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        if not user:
            db.close()
            return jsonify({"error": "User not found. Please register first."}), 404
        user_id = user.id
        db.close()
        
        # Check if already recording for this user
        if username in recording_threads and recording_threads[username]['is_active']:
            return jsonify({"error": f"Recording already in progress for user {username}"}), 409
        
        # Create recorder instance
        recorder = VideoRecorder(
            user_name=username,
            chunk_duration_seconds=chunk_duration,
            total_duration_seconds=total_duration,
            output_dir="recordings"
        )

        # Create recording session to track clip count
        session = RecordingSession(username, user_id, total_duration, chunk_duration)

        def save_chunk_callback(chunk_info):
            """Callback to save chunk info to database"""
            try:
                db = SessionLocal()
                session.clip_count += 1

                video_chunk = VideoChunk(
                    clip_id=session.clip_count,
                    user_id=user_id,
                    user_name=chunk_info['user_name'],
                    recording_date=datetime.now(),
                    file_name=chunk_info['file_name'],
                    file_path=chunk_info['file_path'],
                    start_time=chunk_info['record_start_time'],
                    end_time=chunk_info['record_end_time'],
                    duration_seconds=int(chunk_info['duration']),
                    chunk_duration_seconds=chunk_duration
                )

                db.add(video_chunk)
                db.commit()
                db.close()

                logger.info(f"Chunk {session.clip_count} saved to database: {chunk_info['file_name']}")
            except Exception as e:
                logger.error(f"Error saving chunk to database: {e}")
        
        # Start recording in a separate thread
        thread = recorder.start_recording_thread(callback=save_chunk_callback)

        # Store thread reference with session
        session.thread = thread
        session.recorder = recorder
        recording_threads[username] = {
            'thread': thread,
            'recorder': recorder,
            'is_active': True,
            'start_time': datetime.now(),
            'user_id': user_id,
            'total_duration': total_duration,
            'chunk_duration': chunk_duration,
            'session': session
        }
        
        return jsonify({
            "message": f"Recording started for user {username}",
            "username": username,
            "total_duration_seconds": total_duration,
            "chunk_duration_seconds": chunk_duration,
            "expected_chunks": (total_duration + chunk_duration - 1) // chunk_duration
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return jsonify({"error": "Invalid parameter values. Make sure durations are integers."}), 400
    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/stop-recording', methods=['POST'])
def stop_recording():
    """
    Stop recording video.
    Request body: {
        "username": "john_doe"
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        if username not in recording_threads:
            return jsonify({"error": f"No active recording for user {username}"}), 404
        
        recorder = recording_threads[username]['recorder']
        recorder.stop_recording()
        
        # Wait for thread to finish
        recording_threads[username]['thread'].join(timeout=5)
        recording_threads[username]['is_active'] = False
        
        chunks = recorder.get_chunks()
        
        return jsonify({
            "message": f"Recording stopped for user {username}",
            "username": username,
            "total_chunks": len(chunks),
            "chunks": chunks
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/recording-status/<username>', methods=['GET'])
def recording_status(username):
    """Get current recording status for a user"""
    try:
        if username not in recording_threads:
            return jsonify({
                "username": username,
                "is_recording": False
            }), 200
        
        thread_info = recording_threads[username]
        elapsed = (datetime.now() - thread_info['start_time']).total_seconds()
        
        return jsonify({
            "username": username,
            "is_recording": thread_info['is_active'],
            "elapsed_seconds": elapsed,
            "total_duration_seconds": thread_info['total_duration'],
            "chunk_duration_seconds": thread_info['chunk_duration'],
            "total_chunks_so_far": len(thread_info['recorder'].get_chunks())
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recording status: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== VIDEO MANAGEMENT ====================

@api_bp.route('/videos', methods=['GET'])
def get_all_videos():
    """Get all recorded video chunks"""
    try:
        db = SessionLocal()
        chunks = db.query(VideoChunk).all()
        db.close()
        
        return jsonify({
            "total_chunks": len(chunks),
            "chunks": [chunk.to_dict() for chunk in chunks]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/videos/<username>', methods=['GET'])
def get_user_videos(username):
    """Get all video chunks for a specific user"""
    try:
        db = SessionLocal()
        chunks = db.query(VideoChunk).filter(
            VideoChunk.user_name == username
        ).all()
        db.close()
        
        return jsonify({
            "username": username,
            "total_chunks": len(chunks),
            "chunks": [chunk.to_dict() for chunk in chunks]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching videos for user {username}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/video/<int:chunk_id>/download', methods=['GET'])
def download_video(chunk_id):
    """Download a specific video chunk"""
    try:
        db = SessionLocal()
        chunk = db.query(VideoChunk).filter(VideoChunk.id == chunk_id).first()
        db.close()
        
        if not chunk:
            return jsonify({"error": "Video chunk not found"}), 404
        
        if not os.path.exists(chunk.file_path):
            return jsonify({"error": "Video file not found on disk"}), 404
        
        return send_file(
            chunk.file_path,
            as_attachment=True,
            download_name=chunk.file_name,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/video/<int:chunk_id>', methods=['GET'])
def get_video_details(chunk_id):
    """Get details of a specific video chunk"""
    try:
        db = SessionLocal()
        chunk = db.query(VideoChunk).filter(VideoChunk.id == chunk_id).first()
        db.close()
        
        if not chunk:
            return jsonify({"error": "Video chunk not found"}), 404
        
        return jsonify(chunk.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error fetching video details: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/init-db', methods=['POST'])
def initialize_database():
    """Initialize database tables"""
    try:
        init_db()
        return jsonify({"message": "Database initialized successfully"}), 200
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/delete-video/<int:chunk_id>', methods=['DELETE'])
def delete_video(chunk_id):
    """Delete a video chunk and its file"""
    try:
        db = SessionLocal()
        chunk = db.query(VideoChunk).filter(VideoChunk.id == chunk_id).first()
        
        if not chunk:
            db.close()
            return jsonify({"error": "Video chunk not found"}), 404
        
        # Delete file from disk
        try:
            if os.path.exists(chunk.file_path):
                os.remove(chunk.file_path)
        except Exception as e:
            logger.warning(f"Could not delete file {chunk.file_path}: {e}")
        
        # Delete from database
        db.delete(chunk)
        db.commit()
        db.close()
        
        return jsonify({"message": "Video chunk deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        return jsonify({"error": str(e)}), 500

