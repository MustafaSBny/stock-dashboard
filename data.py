import yfinance as yf
import pandas as pd

def get_stock_history(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    return history

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

def get_sp500_history(period="1y"):
    return get_stock_history("^GSPC", period)