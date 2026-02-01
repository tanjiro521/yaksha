# How to Run Yaksha Locally (Without Agent Help)

Follow these steps to run your project on any computer (simulating the competition environment).

## 1. Prerequisites
Ensure you have **Python** installed. You can check by opening a terminal (Command Prompt or PowerShell) and typing:
```bash
python --version
```
If it says "Python 3.x.x", you are good.

## 2. Setup (One-Time Only)
Open your terminal in the project folder (`web`) and run this command to install the required libraries:

```bash
pip install -r requirements.txt
```
*(If `pip` is not recognized, try `pip3` or `python -m pip`)*

### Troubleshooting Installation
If you get errors about missing libraries, manually install the core ones:
```bash
pip install flask flask-cors pandas numpy joblib scikit-learn gspread google-auth
```

## 3. Running the App
Whenever you want to start the website:

1.  **Open Terminal** in your project folder.
2.  **Run the Server** by typing:
    ```bash
    python app.py
    ```
3.  You should see a message like:
    ```
    * Running on http://127.0.0.1:5000
    ```
4.  **Open Browser**: Go to `http://localhost:5000`.

## 4. Closing the App
To stop the server, go back to the terminal and press `Ctrl + C`.

---
**Good Luck! 🏆**
