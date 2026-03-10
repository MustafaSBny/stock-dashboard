import plotly.graph_objects as go
import pandas as pd

def price_chart(history, ticker):
    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(
        x=history.index,
        y=history['Close'],
        name="Price",
        line=dict(color="#00C896", width=2)
    ))

    # 50 day moving average
    history['MA50'] = history['Close'].rolling(window=50).mean()
    fig.add_trace(go.Scatter(
        x=history.index,
        y=history['MA50'],
        name="50 Day MA",
        line=dict(color="#FF6B6B", width=1, dash='dash')
    ))

    fig.update_layout(
        title=f"{ticker} Price History",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark"
    )

    return fig

def investment_growth_chart(ticker, amount, start_date):
    import yfinance as yf

    stock = yf.Ticker(ticker)
    history = stock.history(start=start_date)

    if history.empty:
        return None

    start_price = history['Close'].iloc[0]
    shares = amount / start_price
    history['Portfolio Value'] = history['Close'] * shares

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history.index,
        y=history['Portfolio Value'],
        fill='tozeroy',
        name="Portfolio Value",
        line=dict(color="#00C896")
    ))

    fig.update_layout(
        title="Investment Growth Over Time",
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        template="plotly_dark"
    )

    return fig