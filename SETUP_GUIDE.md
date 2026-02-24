# 🚀 Setup Guide - Video Recording Flask App

## Step-by-Step Setup Instructions

### Step 1: Ensure You Have MySQL Running

**Windows:**
1. Open Services (services.msc)
2. Search for "MySQL"
3. Make sure MySQL service is running (status shows "Started")

Or start it from Command Prompt (as Administrator):
```bash
net start MySQL80
```

### Step 2: Create the Database

Open MySQL Command Line Client or MySQL Workbench:

```sql
CREATE DATABASE IF NOT EXISTS videochunks;
USE videochunks;
```

That's it! Tables will be created automatically when you run the app.

### Step 3: Activate Virtual Environment

```bash
# Navigate to your project directory
cd d:\videochunks

# Activate the virtual environment
env\Scripts\activate
```

You should see `(env)` in your terminal prompt.

### Step 4: Verify Python Dependencies

Check that all packages are installed:

```bash
pip list
```

Required packages:
- Flask
- SQLAlchemy
- PyMySQL
- opencv-python
- Werkzeug

If any are missing:
```bash
pip install -r requirements.txt
```

### Step 5: Test Database Connection

Create a test file to verify database connection:

```python
# test_connection.py
from app.database import engine, init_db

try:
    init_db()
    print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
python test_connection.py
```

### Step 6: Start the Application

From the project root directory:

```bash
python app/main.py
```

You should see:
```
 * Serving Flask app 'main'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### Step 7: Access the Application

**Recording Page:**
- Open your browser and go to: http://localhost:5000/

**Dashboard (View Videos):**
- Open your browser and go to: http://localhost:5000/dashboard

---

## Quick Test

### Test Recording

1. Go to http://localhost:5000/
2. Enter your name (e.g., "Test User")
3. Click **Start Recording**
4. Allow browser to access your webcam
5. Let it record for 10-20 seconds
6. Click **Stop Recording**
7. Go to http://localhost:5000/dashboard to see the video

---

## Common Issues & Fixes

### ❌ "Module not found" Error

**Solution:**
```bash
# Make sure virtual environment is activated
env\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### ❌ "Can't connect to MySQL"

**Solution:**
1. Check if MySQL is running: `net start MySQL80`
2. Verify username/password in `app/database.py`
3. Open MySQL and run: `SHOW DATABASES;` to test

### ❌ "Webcam not detected"

**Solution:**
1. Check browser permissions (allow camera access)
2. Make sure no other app is using the camera
3. Try a different browser (Chrome, Firefox)
4. Restart your computer

### ❌ "Port 5000 already in use"

**Solution:**
```bash
# Either kill the process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change the port in app/main.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### ❌ "Videos directory not created"

**Solution:**
1. The app creates it automatically, but if not:
2. Create manually: `app\videos\folder`
3. Make sure the app has write permissions

---

## Project Structure After Setup

```
d:\videochunks\
├── app/
│   ├── __init__.py
│   ├── main.py                 (Start here!)
│   ├── models.py               (Database models)
│   ├── database.py             (DB config)
│   ├── route.py                (API endpoints)
│   ├── video_recorder.py       (Recording logic)
│   ├── templates/
│   │   ├── index.html          (Recording page)
│   │   └── dashboard.html      (Videos page)
│   ├── static/
│   │   ├── app.js              (Recording logic)
│   │   ├── dashboard.js        (Dashboard logic)
│   │   └── style.css           (Styling)
│   ├── recordings/             (Saved videos - auto-created)
│   └── __pycache__/
├── env/                        (Virtual environment)
├── README.md                   (Full documentation)
├── requirements.txt            (Dependencies list)
└── .gitignore
```

---

## Development vs Production

### Development Mode (Current)

Suitable for testing and development:
- Debug mode enabled
- Hot reload on code changes
- Detailed error messages

### For Production

Before deploying, update `app/main.py`:

```python
if __name__ == '__main__':
    # Change debug=False and add proper config
    app.run(debug=False, host='0.0.0.0', port=5000)
```

Additional recommendations:
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up proper logging
- Use environment variables for sensitive data
- Add user authentication
- Enable HTTPS/SSL

---

## What The App Does

When you start recording:

1. **Backend (Python/Flask):**
   - Opens your webcam
   - Records 3-minute video chunks
   - Saves each chunk as an MP4 file
   - Records metadata in MySQL database

2. **Database Stores:**
   - Username
   - Filename
   - File path
   - Start time
   - End time

3. **Frontend (Web Browser):**
   - Shows recording status (elapsed time, chunks recorded)
   - Displays progress bar
   - Allows stop recording anytime

4. **Dashboard:**
   - Lists all videos
   - Shows user stats
   - Allows play/download/delete

---

## Recording Parameters (Can Be Changed)

In `app/video_recorder.py`, line 17:

```python
recorder = VideoRecorder(
    user_name=user_name,
    chunk_duration_seconds=180,      # Change to adjust chunk size
    total_duration_seconds=900,      # Change total recording time
    output_dir="recordings"
)
```

Examples:
- 2-minute chunks: `chunk_duration_seconds=120`
- 30-minute total: `total_duration_seconds=1800`

---

## Next Steps After Setup

✅ Test the app with different users
✅ Try recording multiple videos
✅ Download and check the video files
✅ Delete some videos and check database
✅ Modify parameters to experiment
✅ Practice explaining the code for interview!

---

## Ready to Interview?

Your app is now ready! Practice:
1. Starting and stopping recording
2. Viewing the dashboard
3. Explaining the chunking algorithm
4. Discussing database design
5. Answering questions about concurrency, file handling, etc.

**Good luck! 🎉**
