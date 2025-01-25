# AI Prompt Helper

## Frontend

The frontend is a simple HTML/CSS/JS application.

### Files

- `index.html`: The main HTML file.
- `styles.css`: The CSS file for styling.
- `app.js`: The JavaScript file for frontend logic.

## Backend

The backend is a Flask application.

### Files

- `app.py`: The main Flask application.
- `requirements.txt`: The dependencies for the backend.
- `.env`: The environment variables file.
- `.gitignore`: The gitignore file for the backend.

## Setup

1. Navigate to the `backend` directory and create a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the backend server:
    ```sh
    python app.py
    ```

4. Open `frontend/index.html` in your browser to view the frontend.

## Correct Setup

Frontend (Port 5500)  →  Browser (http://localhost:5500)
   ↓
Backend (Port 5001)   →  API Endpoints (http://localhost:5001/analyze)
