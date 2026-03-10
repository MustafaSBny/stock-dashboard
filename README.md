# StockDash 📈

A real-time stock market dashboard built with Python and Streamlit.
Track live market data, analyze stocks, and calculate hypothetical investment returns.

## Features
- Live Dow Jones and NASDAQ index charts with real-time data
- Dynamic price scaling for accurate chart visualization
- Popular stocks sidebar with live prices and daily % change in green/red
- Hypothetical investment calculator with S&P 500 benchmark comparison
- Investment growth chart over any custom time period
- Custom StockDash branding and dark theme UI
- Watchlist feature (in progress)
- Stock detail page with full analysis (in progress)
- Search by ticker or company name (in progress)

## Tech Stack
- Python
- Streamlit
- yfinance
- Pandas
- Plotly

## How To Run

1. Clone the repository
'''
   git clone https://github.com/MustafaSBny/stock-dashboard.git
'''

2. Create and activate virtual environment
'''
   python -m venv venv
   source venv/bin/activate
'''

3. Install dependencies
'''
   pip install -r requirements.txt
'''

4. Run the app
'''
   streamlit run app.py
'''

## Project Structure
- app.py — Main Streamlit application and page routing
- data.py — Live stock data fetching via yfinance
- calculations.py — Investment return calculations
- charts.py — Plotly chart generation
- assets/ — Logo and static assets

## Roadmap
- [ ] Stock detail page with full price history
- [ ] Hypothetical investment calculator
- [ ] Watchlist functionality
- [ ] Search by ticker or company name