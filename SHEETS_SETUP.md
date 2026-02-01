# Google Sheets Integration Setup

To enable the sign-in page to save data to your Google Sheet, follow these steps:

## 1. Create Google Cloud Project & Enable APIs
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "FraudGuard-Login").
3. Enable the **Google Sheets API** and **Google Drive API** for that project.

## 2. Create Service Account & Credentials
1. In the Google Cloud Console, go to **APIs & Services > Credentials**.
2. Click **Create Credentials** > **Service Account**.
3. Name it (e.g., "sheet-editor") and click **Create**.
4. Click **Done** (skipping the role assignment is fine for now, or give it "Editor" access to the project).
5. Click on the newly created Service Account (email address).
6. Go to the **Keys** tab -> **Add Key** -> **Create new key** -> **JSON**.
7. A JSON file will download. **Rename this file to `credentials.json`**.
8. **Move this `credentials.json` file into your project folder** (same folder as `app.py`).

## 3. Share the Sheet
1. The app will try to create a sheet called "FraudGuard Members" if it doesn't exist.
2. However, it's easier if *you* create a blank Google Sheet.
3. Name it **"FraudGuard Members"**.
4. Open the `credentials.json` file and look for the `"client_email"` field.
5. Copy that email address (it ends in `@...iam.gserviceaccount.com`).
6. Go to your Google Sheet, click **Share**, and paste that email address. Give it **Editor** access.

## 4. Run the App
1. Install new requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Go to the Sign In page and test it!

## Troubleshooting
- If you see "Error: credentials.json not found", make sure the file is in the right folder.
- If you see "SpreadsheetNotFound", make sure you shared the sheet with the Service Account email.
