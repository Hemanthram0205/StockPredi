🧠 MarketSense AI — Indian Stock Analysis & Prediction App

🔗 Live Demo: Try it here → MarketSense AI Demo (replace with your app URL)

📄 Overview

MarketSense AI is a Streamlit web application for NSE/BSE stock analysis and short-term price prediction. It fetches real market data, shows technical indicators and interactive charts, and provides an AI-driven (linear-trend prototype) prediction with buy/hold/sell guidance — all with a clean India-themed UI.

🎯 Key Features

✅ Real-time NSE/BSE support — Tickers with .NS / .BO format

📥 Select or enter symbol — Popular stock list + manual entry

📊 Interactive charts — Price history and volume visualizations

📈 Technical indicators — 10-day & 50-day moving averages, 52W high/low

🔮 AI Prediction — Trend-based forecast for 7–90 days with confidence metric

💡 Buy/Hold/Sell recommendation based on predicted return thresholds

📋 Recent trading table and CSV export for analysis/reports

⚡ Smart caching (10 min) to limit API calls and avoid rate limits

🇮🇳 INR display and India-focused UX (NSE/BSE examples)

⚙️ How It Works

Select stock (popular or manual symbol like RELIANCE.NS).

App queries market data via yfinance (cached).

Computes metrics: current price, day high/low, 52W high/low, volume.

Builds charts for price and volume (Streamlit line & bar charts).

Calculates moving averages (10d, 50d) and shows simple signals (bullish/bearish).

Runs a simple linear-trend prediction to estimate future price for chosen horizon.

Shows predicted price, expected % change, confidence (volatility-based), and recommendation.

User can download recent data as CSV.

🧰 Tech Stack
Component	Technology
Language	Python
Web UI	Streamlit
Market Data	yfinance
Data Processing	Pandas, NumPy
Caching	st.cache_data (10 min TTL)
Charts	Streamlit built-ins (line_chart, bar_chart)
Deployment	Streamlit Cloud / Heroku / any Python host
