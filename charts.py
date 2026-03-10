import plotly.graph_objects as go

def index_chart(ticker, label, period="1d"):
    import yfinance as yf
    stock = yf.Ticker(ticker)

    interval = "5m" if period == "1d" else "1d"
    history = stock.history(period=period, interval=interval)

    if history.empty:
        return None

    prices = history['Close'].dropna()

    if len(prices) < 2:
        return None

    prices = history['Close']
    color = "#00C896" if prices.iloc[-1] >= prices.iloc[0] else "#FF4444"
    fill_color = "rgba(0, 200, 150, 0.15)" if color == "#00C896" else "rgba(255, 68, 68, 0.15)"

    # Dynamic scaling — pad 0.5% above and below the actual range
    y_min = prices.min() * 0.995
    y_max = prices.max() * 1.005

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history.index,
        y=prices,
        fill='tozeroy',
        fillcolor=fill_color,
        line=dict(color=color, width=2),
        name=label
    ))

    fig.update_layout(
        dragmode=False,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            showticklabels=True,
            tickformat="%I:%M %p",
            tickfont=dict(color="gray", size=10),
            fixedrange=True  # disables zoom
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=True,
            side='right',
            range=[y_min, y_max],
            tickfont=dict(color="gray", size=10),
            tickformat=",.0f",
            fixedrange=True  # disables zoom
        ),
        height=180,
        showlegend=False
    )

    return fig

def price_chart(history, ticker):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=history.index,
        y=history['Close'],
        name="Price",
        line=dict(color="#00C896", width=2)
    ))

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
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14,14,14,1)',
    )

    return fig