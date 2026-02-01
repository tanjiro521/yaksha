# How to Add Your Colab Model
Since I cannot access your private Google Colab notebook directly, I have set up the infrastructure for you to easily plug your trained model into this website.

## Step 1: Export Model from Colab
Open your Google Colab notebook and add this code at the end of your training process:

```python
import joblib

# Assuming your trained model variable is called 'model'
# Use the actual variable name of your trained classifier (e.g., clf, rf_model, etc.)
joblib.dump(model, 'fraud_detection_model.pkl')

from google.colab import files
files.download('fraud_detection_model.pkl')
```

## Step 2: Add Model to Website
1.  Download the `fraud_detection_model.pkl` file.
2.  Move it into this folder: `c:\Users\param\Desktop\web\` (same place as `app.py`).

## Step 3: Run the Server
You need to run the Python server to handle the model predictions.

1.  Open a terminal in this folder.
2.  Install dependencies (if not done):
    ```powershell
    pip install -r requirements.txt
    ```
3.  Run the server:
    ```powershell
    python app.py
    ```
4.  Open `http://localhost:5000` in your browser.

## Step 4: Final Connection (Important)
Open `app.py` in your code editor.
Look for the `predict()` function.
You might need to adjust the input features to match EXACTLY what your model expects.
For example, if your model expects `[amount, merchant_code, location_code]`, you might need to map the string values from the website (`"retail"`, `"international"`) to the numbers your model knows (`1`, `2`, etc.).

I have added comments in `app.py` to guide you!
