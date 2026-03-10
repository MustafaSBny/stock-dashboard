import yfinance as yf

def calculate_investment(ticker, amount, start_date):
    stock = yf.Ticker(ticker)
    history = stock.history(start=start_date)

    if history.empty:
        return None

    start_price = history['Close'].iloc[0]
    current_price = history['Close'].iloc[-1]

    shares = amount / start_price
    current_value = round(shares * current_price, 2)
    profit = round(current_value - amount, 2)
    total_return = round(((current_value - amount) / amount) * 100, 2)

    # Annualized return
    days_held = (history.index[-1] - history.index[0]).days
    years_held = days_held / 365
    annualized_return = round(((current_value / amount) ** (1 / years_held) - 1) * 100, 2)

    return {
        "current_value": current_value,
        "profit": profit,
        "total_return": total_return,
        "annualized_return": annualized_return,
        "shares": round(shares, 4),
        "start_price": round(start_price, 2),
        "current_price": round(current_price, 2),
    }

def calculate_sp500_return(amount, start_date):
    result = calculate_investment("^GSPC", amount, start_date)
    return result["total_return"] if result else None