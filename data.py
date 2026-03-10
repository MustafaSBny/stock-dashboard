import yfinance as yf
import pandas as pd
import time

def get_stock_history(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "name": info.get("longName", ticker),
        "sector": info.get("sector", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
        "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
    }

def get_current_price(ticker, retries=3):
    for attempt in range(retries):
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="2d")
            if len(history) >= 2:
                current = history['Close'].iloc[-1]
                previous = history['Close'].iloc[-2]
                change_pct = ((current - previous) / previous) * 100
                return round(current, 2), round(change_pct, 2)
        except Exception:
            pass
        time.sleep(0.3)
    return None, None
    
def get_popular_stocks_data():
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META"]
    names = {
        "AAPL": "Apple",
        "MSFT": "Microsoft", 
        "NVDA": "NVIDIA",
        "TSLA": "Tesla",
        "AMZN": "Amazon",
        "GOOGL": "Google",
        "META": "Meta"
    }
    results = []
    for ticker in tickers:
        price, change_pct = get_current_price(ticker)
        if price:
            results.append({
                "ticker": ticker,
                "name": names[ticker],
                "price": f"${price:,.2f}",
                "change": f"{'+' if change_pct >= 0 else ''}{change_pct:.2f}%",
                "positive": change_pct >= 0
            })
    return results