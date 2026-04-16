# 📈 Stock Price Prediction

A machine learning-based web application that predicts stock prices using historical market data and advanced algorithms. This project helps users analyze trends, visualize stock performance, and forecast future prices.

## 🚀 Project Overview

This project focuses on predicting stock prices using historical data such as Open, High, Low, Close, and Volume. It applies machine learning/deep learning techniques to identify patterns in time-series data and generate future predictions.

Stock prediction systems typically rely on models like regression, LSTM, or other time-series techniques to capture market trends and patterns.

## 🎯 Features
- 📊 Historical stock data analysis
- 📈 Data visualization (charts & graphs)
- 🤖 Machine Learning-based prediction
- 🔮 Future price forecasting
- 🧹 Data preprocessing & cleaning
- 📉 Model evaluation (accuracy metrics)
- 🌐 Simple and interactive UI 

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
- [ ] Add real-time stock data integration
- [ ] Improve accuracy using advanced models (Transformer, GRU)
- [ ] Deploy as a full-stack web app
- [ ] Add user authentication & dashboard
- [ ] Integrate news sentiment analysis

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
