# Fraud Detection Demo Webapp

Click to deploy this project on Render (one-click):

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/deploy?repo=https://github.com/USERNAME/REPO)

Deployment notes:
- Ensure `requirements.txt` includes `gunicorn` and all Python dependencies used by `app.py`.
- `Procfile` already contains `web: gunicorn app:app`.
- Don't commit sensitive Google credentials; use Render environment variables or secrets.

Replace `USERNAME/REPO` in the button URL with your GitHub repo path.
