# How to Train Your Model with CSV
I have prepared a script for you to train your machine learning model using your CSV data.

## 1. Prepare your CSV
1. Name your file **`fraud_train.csv`**.
2. Make sure it has columns like:
   - `merchant`, `category`, `amt` (or `amount`), `city`, `state`, `lat`, `long`, `is_fraud` (or target column).
   - If you are missing some, the script will try to handle it or give you an error telling you what is missing.
3. Move `fraud_train.csv` into this folder: `c:\Users\param\Desktop\web\`.

## 2. Train the Model
1. Open a new terminal in this folder.
2. Run the training script:
   ```bash
   python train_model.py
   ```
3. This will create details logs. If successful, it will save two files:
   - `fraud_detection_model.pkl` (The Brain)
   - `encoders.pkl` (The Dictionary to understand text data)

## 3. Restart the App
1. Stop your running server (Ctrl+C).
2. Start it again:
   ```bash
   python app.py
   ```

Now your website is using YOUR data to make predictions!
