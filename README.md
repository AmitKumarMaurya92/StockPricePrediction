# 📈 Stock Price Prediction

A machine learning-based web application that predicts stock prices using historical market data and advanced algorithms. This project helps users analyze trends, visualize stock performance, and forecast future prices.

## 🚀 Project Overview

This project focuses on predicting stock prices using historical data such as Open, High, Low, Close, and Volume. It applies machine learning/deep learning techniques to identify patterns in time-series data and generate future predictions.

Stock prediction systems typically rely on models like regression, LSTM, or other time-series techniques to capture market trends and patterns.

## 🎯 Features
- **🤖 AI-Powered Neural Forecasting**: Multivariate LSTM model trained on OHLCV data providing next-day predictive projections.
- **🚥 Actionable Trading Signals**: AI Intelligence HUD computing automated "Strong Buy", "Buy", "Hold", and "Sell" signals alongside intelligently calculated Stop-Loss & Target Profit metrics.
- **📈 Advanced Interactive Charting**: Professional-grade, high-performance Plotly charts with real-time toggleable overlays for 50 DMA, 200 DMA, and Volume histograms.
- **📅 Multi-Interval Timeframes**: Analyze stock structures across diverse historical snapshots (1M, 6M, 1Yr, 3Yr).
- **📂 Custom Dataset Validation**: Flexibility to upload proprietary, offline `.csv` or `.xlsx` datasets to bypass live APIs and run custom offline predictions.
- **🔎 Live Search & Autocomplete**: Intuitive ticker lookup seamlessly bridging between Indian Market (NSE/BSE) and US Market stock identifiers.
- **📊 Fundamental Deep-Dive**: Screener-style dashboard displaying Key Statistics such as P/E Ratios, Trailing Twelve Month (TTM) EPS, ROCE, ROE, Dividend Yield, and Market Cap.
- **🎨 Glassmorphism & Theme Toggling**: Premium, aesthetic modern interface adapting beautifully between custom Dark and Light modes.
- **☁️ Robust Cloud Data Polling**: Hardened backend deployment architecture designed to bypass standard rate limiting via fallback mechanisms and execution timeouts.

## 🛠️ Technologies Used

### 👨‍💻 Programming Language
- Python

### 📚 Libraries & Frameworks
- NumPy
- Pandas
- Scikit-learn
- TensorFlow / Keras 
- yfinance (for stock data)
- Plotly
- Flask

### 📊 Machine Learning Models
- LSTM (Long Short-Term Memory) 

### 🌐 Tools / Platforms
- VS Code
- Git & GitHub

## 📂 Project Structure
```text
StockPricePrediction/
│── data/                # Dataset files
│── notebooks/           # Jupyter notebooks
│── model/               # Trained models
│── src/                 # Source code (ML Pipeline)
│── app/                 # Flask Backend & Frontend Assets
│── run.py               # Main application
│── requirements.txt     # Dependencies
│── README.md            # Project documentation
```

## ⚙️ How It Works
1. 📥 Collect historical stock data (Yahoo Finance API)
2. 🧹 Preprocess the data (handle null values, multivariate scaling)
3. 📊 Perform exploratory data analysis (EDA)
4. 🔧 Train machine learning model
5. 📉 Evaluate model performance
6. 🔮 Predict future stock prices
7. 📈 Visualize results dynamically on the web UI

## 🧪 Installation & Setup

1️⃣ **Clone the Repository**
```bash
git clone https://github.com/AmitKumarMaurya92/StockPricePrediction.git
cd StockPricePrediction
```

2️⃣ **Create a Virtual Environment (Optional but Recommended)**
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/MacOS:
source .venv/bin/activate
```

3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

4️⃣ **Train the Model**
You must train the machine learning model before running the application. This will fetch historical data, process it, and save the model to the `model/` directory.
```bash
python -m src.train_model
```

5️⃣ **Run the Project**
```bash
python run.py
```
*(The application will be live at `http://127.0.0.1:5000`)*

## 📊 Dataset
**Source**: Yahoo Finance API
**Features Used**:
- Open
- High
- Low
- Close
- Volume
- Technical Indicators (RSI, MACD, Bollinger Bands)

## 📈 Results
- The model learns complex non-linear patterns from historical data
- Generates predictions for future stock prices
- Seamless visual comparison between actual vs predicted values via interactive Candlesticks.

## 🔥 Future Improvements
- [x] Add real-time stock data integration
- [x] Deploy as a full-stack web app
- [ ] Improve accuracy using advanced models (Transformer, GRU)
- [ ] Implement user portfolio tracking & authentication
- [ ] Integrate deep real-time news sentiment analysis

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is open-source and available under the MIT License.

## 👤 Author

**Amit Kumar Maurya**

- **GitHub**: [AmitKumarMaurya92](https://github.com/AmitKumarMaurya92)
- **LinkedIn**: [Amit Kumar Maurya](https://www.linkedin.com/in/amit-kumar-maurya-b2a103295)
