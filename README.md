# 🎥 Video Recording Application

A Flask-based web application for recording real-time video from a webcam with automatic chunking and storage in MySQL database.

## ⚠️ AI Usage

This project was developed with AI assistance from Claude (Anthropic). AI was used for:
- Code structure and architecture design
- API endpoint implementation
- Database schema design
- Frontend JavaScript logic
- Documentation and README

## Features

✅ **Real-time Video Recording** - Record video directly from your webcam
✅ **Automatic Chunking** - Splits 15-minute recording into 3-minute chunks
✅ **Database Storage** - Saves chunk metadata (file_name, start_time, end_time, user_name) in MySQL
✅ **Web Dashboard** - View, play, download, and delete recorded videos
✅ **User Tracking** - Each recording is associated with a user
✅ **Live Status Display** - See elapsed time and chunk progress while recording
✅ **Responsive Design** - Works on desktop and mobile browsers

## Project Structure

```
app/
├── main.py                 # Flask application entry point
├── models.py              # SQLAlchemy database models
├── database.py            # Database configuration
├── route.py               # API routes and endpoints
├── video_recorder.py      # Video recording and chunking logic
├── templates/
│   ├── index.html         # Recording interface
│   └── dashboard.html     # Video management dashboard
├── static/
│   ├── app.js             # Recording page JavaScript
│   ├── dashboard.js       # Dashboard JavaScript
│   └── style.css          # Styling
└── recordings/            # Directory to store video chunks
```

## System Requirements

- Python 3.8+
- MySQL Server
- Webcam/Camera device
- OpenCV libraries

## Installation

### 1. Install Python Dependencies

```bash
cd app
pip install -r requirements.txt
```

Or manually install:
```bash
pip install flask sqlalchemy pymysql opencv-python
```

### 2. Create MySQL Database

```sql
CREATE DATABASE videochunks;

-- The tables will be created automatically when you start the app
```

### 3. Configure Database Connection

Edit `database.py` and update the connection string if needed:
```python
DATABASE_URL = "mysql+pymysql://root:your_password@localhost/videochunks"
```

## Running the Application

### Start the Flask Server

```bash
python main.py
```

The application will be available at:
- **Recording Page**: http://localhost:5000/
- **Dashboard**: http://localhost:5000/dashboard

## Usage

### Recording Video

1. Go to http://localhost:5000/
2. Enter your name
3. Click **Start Recording**
4. Allow access to your webcam when prompted
5. Recording will run for 15 minutes and automatically chunk every 3 minutes
6. Click **Stop Recording** to end early
7. Your videos will be saved to the database

### Viewing Recorded Videos

1. Go to http://localhost:5000/dashboard
2. View all recorded videos with metadata
3. Filter videos by user name
4. Play videos directly in the browser
5. Download videos for offline storage
6. Delete videos to free up space

## API Endpoints

### Recording

- **POST** `/api/start-recording` - Start recording
  ```json
  {
    "user_name": "John Doe"
  }
  ```

- **POST** `/api/stop-recording` - Stop recording
  ```json
  {
    "user_name": "John Doe"
  }
  ```

- **GET** `/api/recording-status/<user_name>` - Get current recording status

### Video Management

- **GET** `/api/videos` - Get all video chunks
- **GET** `/api/videos/<user_name>` - Get videos by user
- **GET** `/api/video/<chunk_id>` - Get specific chunk details
- **GET** `/api/video/<chunk_id>/download` - Download a video chunk
- **DELETE** `/api/delete-video/<chunk_id>` - Delete a video chunk

### Database

- **POST** `/api/init-db` - Initialize database tables

## Database Schema

### video_chunks Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| clip_id | INTEGER | Sequential clip number |
| user_id | INTEGER | Foreign key to users table |
| user_name | VARCHAR(255) | Name of the user who recorded |
| recording_date | DATETIME | Date when recording occurred |
| file_name | VARCHAR(255) | Name of the video file |
| file_path | VARCHAR(500) | Full path to the video file |
| start_time | DATETIME | When chunk recording started |
| end_time | DATETIME | When chunk recording ended |
| duration_seconds | INTEGER | Duration of chunk in seconds |
| chunk_duration_seconds | INTEGER | Configured chunk duration |
| created_at | DATETIME | When record was created in database |

## Configuration

### Recording Parameters

In `video_recorder.py`, you can adjust:

```python
recorder = VideoRecorder(
    user_name=user_name,
    chunk_duration_seconds=180,      # 3 minutes
    total_duration_seconds=900,      # 15 minutes
    output_dir="recordings"          # Output directory
)
```

### Video Quality

In the same file, adjust camera settings:
```python
self.fps = 30                        # Frames per second
self.frame_width = 640              # Video width
self.frame_height = 480             # Video height
self.codec = cv2.VideoWriter_fourcc(*'mp4v')  # Video codec
```

## Troubleshooting

### Camera Not Detected
- Make sure you give browser permission to access webcam
- Check if another application is using the camera
- Restart the browser

### Database Connection Error
- Verify MySQL is running
- Check connection string in `database.py`
- Ensure database exists
- Check username and password

### Videos Not Saving
- Verify you have write permissions to the `recordings/` directory
- Check disk space availability
- Review application logs for errors

### Slow Performance
- Reduce video resolution in `video_recorder.py`
- Reduce FPS (frames per second)
- Close other resource-intensive applications

## Performance Tips

1. **Optimize Video Size**: Lower resolution = smaller files = faster processing
2. **Database Indexing**: Add indexes on frequently queried columns
3. **Video Cleanup**: Regularly delete old videos to save disk space
4. **Threading**: Recording runs in a separate thread to prevent UI blocking

## Security Considerations

- **Input Validation**: All user inputs are validated
- **File Upload Safety**: Only server-generated files are processed
- **Database Credentials**: Store passwords securely (use environment variables in production)
- **Authentication**: Consider adding user authentication for production use

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Live video preview while recording
- [ ] Multiple camera support
- [ ] Custom chunk duration configuration via UI
- [ ] Video thumbnail generation
- [ ] Transcoding to multiple formats
- [ ] Cloud storage integration (S3, Google Cloud, etc.)
- [ ] Advanced analytics and statistics
- [ ] Real-time notifications

## License

This project is free for educational and personal use.

## Support

For issues or questions, please check the logs:
```bash
tail -f app.log
```

## Author

Built for interview preparation | 2026

---


