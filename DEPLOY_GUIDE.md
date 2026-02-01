# Deployment Guide

## Option 1: Temporary Link (Right Now)
I have generated a live link for you using a secure tunnel:
**[Live Demo Link (Tunnel)](https://dry-toes-kneel.loca.lt)**

*Note: If you see a "Bypass-Tunnel-Reminder" page, simply click "Click to Continue" or enter the IP `5000` if asked (usually not needed).*

## Option 2: Permanent Deployment (Render/Heroku/Railway)
I have prepared the files for a permanent deployment.

### 1. Files Created
- **Procfile**: Instructs the cloud server how to run the app (`gunicorn app:app`).
- **requirements.txt**: Updated with `gunicorn`.

### 2. Steps to Deploy on Render (Free)
1. Push this code to **GitHub**.
2. Go to [dashboard.render.com](https://dashboard.render.com/).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click **Deploy**.

Your app will be live 24/7!
