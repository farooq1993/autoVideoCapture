import cv2
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoRecorder:
    """
    Handles real-time video recording with automatic chunking.
    Records video in chunks of specified duration (default: 3 minutes).
    """
    
    def __init__(self, user_name, chunk_duration_seconds=180, total_duration_seconds=900, output_dir="videos"):
        """
        Initialize the video recorder.
        
        Args:
            user_name: Name of the user recording the video
            chunk_duration_seconds: Duration of each chunk in seconds (default: 180 = 3 minutes)
            total_duration_seconds: Total recording duration in seconds (default: 900 = 15 minutes)
            output_dir: Directory to save video chunks
        """
        self.user_name = user_name
        self.chunk_duration = chunk_duration_seconds
        self.total_duration = total_duration_seconds
        self.output_dir = output_dir
        self.is_recording = False
        self.video_chunks = []
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Video codec and frame rate
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480
        
    def get_chunk_filename(self, chunk_number):
        """Generate chunk filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.user_name}_{timestamp}_chunk_{chunk_number}.mp4"
    
    def record_video(self, callback=None):
        """
        Record video from webcam in chunks.
        
        Args:
            callback: Optional callback function to be called when each chunk is saved
                     callback(chunk_info) where chunk_info is a dict with chunk metadata
        """
        cap = cv2.VideoCapture(0)  # 0 for default webcam
        
        if not cap.isOpened():
            logger.error("Cannot open webcam")
            return False
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        self.is_recording = True
        recording_start_time = datetime.now()
        chunk_number = 0
        
        try:
            while self.is_recording:
                chunk_number += 1
                chunk_start_time = datetime.now()
                
                # Create video writer for this chunk
                chunk_filename = self.get_chunk_filename(chunk_number)
                chunk_path = os.path.join(self.output_dir, chunk_filename)
                
                out = cv2.VideoWriter(
                    chunk_path,
                    self.codec,
                    self.fps,
                    (self.frame_width, self.frame_height)
                )
                
                if not out.isOpened():
                    logger.error(f"Cannot create video writer for chunk {chunk_number}")
                    self.is_recording = False
                    break
                
                # Record frames for this chunk
                frame_count = 0
                target_frames = int(self.chunk_duration * self.fps)
                
                while frame_count < target_frames and self.is_recording:
                    ret, frame = cap.read()
                    
                    if not ret:
                        logger.error("Error reading frame from webcam")
                        self.is_recording = False
                        break
                    
                    # Add timestamp text to frame
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, f"User: {self.user_name}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Time: {current_time}", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    out.write(frame)
                    frame_count += 1
                    
                    # Check if total recording time exceeded
                    elapsed_time = (datetime.now() - recording_start_time).total_seconds()
                    if elapsed_time >= self.total_duration:
                        self.is_recording = False
                        break
                
                out.release()
                chunk_end_time = datetime.now()
                
                # Store chunk info
                chunk_info = {
                    'chunk_number': chunk_number,
                    'user_name': self.user_name,
                    'file_name': chunk_filename,
                    'file_path': chunk_path,
                    'record_start_time': chunk_start_time,
                    'record_end_time': chunk_end_time,
                    'duration': (chunk_end_time - chunk_start_time).total_seconds()
                }
                
                self.video_chunks.append(chunk_info)
                logger.info(f"Chunk {chunk_number} saved: {chunk_filename}")
                
                # Call callback if provided
                if callback:
                    callback(chunk_info)
                
                # Check if total duration exceeded
                elapsed_time = (datetime.now() - recording_start_time).total_seconds()
                if elapsed_time >= self.total_duration:
                    self.is_recording = False
                    break
            
            logger.info(f"Recording completed. Total chunks: {chunk_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            return False
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def start_recording_thread(self, callback=None):
        """Start recording in a separate thread"""
        thread = threading.Thread(target=self.record_video, args=(callback,))
        thread.daemon = False
        thread.start()
        return thread
    
    def stop_recording(self):
        """Stop the recording"""
        self.is_recording = False
        logger.info("Recording stop requested")
    
    def get_chunks(self):
        """Return list of recorded chunks"""
        return self.video_chunks
