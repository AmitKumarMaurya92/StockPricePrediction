# Stock Price Prediction

A modern web application built on Flask that predicts stock prices. The project is structured nicely for deploying machine learning pipelines.

## Project Structure
```text
Stock-Price-Prediction/
├── app/                         # Main application package
│   ├── __init__.py              # Initialize Flask app
│   ├── routes.py                # All routes (API + UI)
│   ├── utils.py                 # Helper functions
│   ├── templates/               # HTML files
│   └── static/                  # CSS, JS, images
├── data/                        # Dataset storage
├── model/                       # Saved models
├── notebooks/                   # Jupyter notebooks (optional)
├── src/                         # Core ML logic
│   ├── data_loader.py           # Fetch data (yfinance)
│   ├── preprocess.py            # Cleaning + scaling
│   ├── train_model.py           # Train model
│   ├── predict.py               # Prediction logic
│   └── visualize.py             # Graphs
├── config/                      # Configuration files
├── tests/                       # Unit tests
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
├── run.py                       # Entry point
└── .gitignore                   # Ignore unnecessary files
```

## Workflow Integration
User Input (Stock Symbol) → Flask App (`routes.py`) → `predict.py` → Load Model (`model/lstm_model.h5`) → Fetch Data (`data_loader.py` using Yahoo Finance) → Preprocess Data → Predict Output → Send Result → UI (`index.html`)

## Setup Instructions

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python run.py
   ```

3. **View the Application:**
   Open http://127.0.0.1:5000 in your browser.
