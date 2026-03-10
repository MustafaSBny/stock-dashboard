# Stock Market Dashboard 📈

A Python-based interactive stock market dashboard built with Streamlit.
Allows users to analyze stock performance and calculate hypothetical investment returns.

## Features
- Real-time stock price history and charts
- 50-day moving average overlay
- Key metrics — P/E ratio, market cap, 52-week high/low
- Hypothetical investment calculator with S&P 500 benchmark comparison
- Investment growth chart over any custom time period

## Tech Stack
- Python
- Streamlit
- yfinance
- Pandas
- Plotly

## How To Run

1. Clone the repository
   git clone https://github.com/MustafaSBny/stock-dashboard.git

2. Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Run the app
   streamlit run app.py

## Project Structure
- app.py — Main Streamlit application
- data.py — Stock data fetching logic
- calculations.py — Investment return calculations
- charts.py — Plotly chart generation