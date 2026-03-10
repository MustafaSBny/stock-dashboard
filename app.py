import streamlit as st
from data import get_stock_history, get_stock_info
from calculations import calculate_investment, calculate_sp500_return
from charts import price_chart, investment_growth_chart

# --- Page Config ---
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📈 Stock Market Dashboard")

# --- Sidebar ---
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

# --- Stock Info Section ---
st.subheader(f"Overview — {ticker}")
info = get_stock_info(ticker)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Company", info["name"])
col2.metric("Sector", info["sector"])
col3.metric("P/E Ratio", info["pe_ratio"])
col4.metric("Market Cap", info["market_cap"])

# --- Price Chart ---
st.subheader("Price History")
history = get_stock_history(ticker, period)
st.plotly_chart(price_chart(history, ticker), use_container_width=True)

# --- Investment Calculator ---
st.subheader("💰 Hypothetical Investment Calculator")

col1, col2, col3 = st.columns(3)
amount = col1.number_input("Amount Invested ($)", min_value=100, value=1000, step=100)
start_date = col2.date_input("Start Date")
calc_button = col3.button("Calculate Returns")

if calc_button:
    result = calculate_investment(ticker, amount, str(start_date))
    sp500_return = calculate_sp500_return(amount, str(start_date))

    if result:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Value", f"${result['current_value']:,}")
        col2.metric("Total Profit", f"${result['profit']:,}")
        col3.metric("Total Return", f"{result['total_return']}%")
        col4.metric("Annualized Return", f"{result['annualized_return']}%")

        if sp500_return:
            st.metric(
                "vs S&P 500",
                f"{result['total_return']}%",
                delta=f"{round(result['total_return'] - sp500_return, 2)}% vs market"
            )

        st.plotly_chart(
            investment_growth_chart(ticker, amount, str(start_date)),
            use_container_width=True
        )
    else:
        st.error("Could not retrieve data for that ticker and date.")