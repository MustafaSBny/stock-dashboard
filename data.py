import yfinance as yf
import pandas as pd
import time

def get_stock_history(ticker, period="1d"):
    try:
        stock = yf.Ticker(ticker)
        if period == "1d":
            history = stock.history(period="1d", interval="5m")
        elif period == "1w":
            history = stock.history(period="5d", interval="15m")
        elif period == "1m":
            history = stock.history(period="1mo", interval="1d")
        elif period == "1y":
            history = stock.history(period="1y", interval="1d")
        return history
    except Exception:
        return None

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "volume": info.get("volume", "N/A"),
        }
    except Exception:
        return None

def search_stocks(query):
    if not query or len(query)< 1:
        return []
    try:
        ticker = yf.Ticker(query)
        search = yf.Search(query, max_results=6)
        results = []
        for quote in search.quotes:
            if 'symbol' in quote and ('longname' in quote or 'shortname' in quote):
                ticker = quote.get("symbol", "")
                if "." not in ticker:  # filter out foreign exchange tickers
                    results.append({
                        "ticker": ticker,
                        "name": quote.get("longname") or quote.get("shortname", "")
            })
            if len(results) >= 5:
                break
        return results
    except Exception:
        return []

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