import streamlit as st
from data import get_stock_history, get_stock_info, get_current_price, get_popular_stocks_data
from charts import index_chart, price_chart
import time
from data import get_stock_history, get_stock_info, get_current_price, get_popular_stocks_data, search_stocks
import datetime
import plotly.graph_objects as go

# Handle search navigation
params = st.query_params
if "stock" in params:
    st.session_state.page = "detail"
    st.session_state.selected_stock = params["stock"]
    st.query_params.clear()
    st.rerun()

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
        .stApp { background-color: #0a0a0a; }
        .stock-panel {
            background-color: #141414 !important;
            border: 1px solid #333333 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin-top: 10px !important;
        }
        .stAppHeader {
            display: none;
        }
        [data-testid="stDecoration"] {
            display: none;
        }
        .block-container {
            padding-top: 50px !important;
        }
        /* Fix logo size, quality and remove expand button */
        [data-testid="stImage"] img {
            width: 120px !important;
            height: auto !important;
            image-rendering: -webkit-optimize-contrast;
        }

        /* Hide the expand/enlarge button on hover */
        [data-testid="stImageContainer"] button {
            display: none !important;
        }

        /* Remove extra spacing the image adds */
        [data-testid="stImage"] {
            margin-top: -30px;
        }
        /* Remove empty space below top bar */
        [data-testid="stTextInput"] {
        margin-bottom: -20px;
        margin-top: -30px;
        }
        /* Tighten gap between top bar and divider */
        div[data-testid="stHorizontalBlock"] {
        margin-bottom: -20px;
        }
        /* Hide Streamlit top header bar */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        /* Fade animation for updating values */
        @keyframes fadeRefresh {
            0% { opacity: 0.3; }
            100% { opacity: 1; }
        }

        /* Catch everything */
        [data-testid="stMarkdown"],
        [data-testid="stMarkdown"] *,
        [data-testid="stImage"],
        .block-container * {
            animation: fadeRefresh 0.4s ease-in-out;
        }
        .search-results [data-testid="stButton"] button {
            background: #1a1a1a !important;
            border: none !important;
            border-bottom: 1px solid #222 !important;
            border-radius: 0 !important;
            width: 100% !important;
            text-align: left !important;
            padding: 10px 16px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        [data-title="Double-click to zoom back out"] {
            display: none !important;
        }
    </style>

    <div id="zoom-toast" style="
        display: none;
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #00C896, #00a876);
        color: white;
        padding: 10px 24px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 20px rgba(0, 200, 150, 0.4);
        z-index: 9999;
        pointer-events: none;
        transition: opacity 0.3s ease;
    ">
        🔍 Double-click to zoom back out
    </div>

    <script>
        function setupZoomToast() {
            const toast = document.getElementById('zoom-toast');
            if (!toast) return;

            // Find all plotly charts inside iframes
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    const plots = iframeDoc.querySelectorAll('.js-plotly-plot');
                    plots.forEach(plot => {
                        plot.on('plotly_relayout', function(eventData) {
                            const isZoomed = (
                                eventData['xaxis.range[0]'] !== undefined ||
                                eventData['yaxis.range[0]'] !== undefined
                            );
                            if (isZoomed) {
                                toast.style.display = 'block';
                                toast.style.opacity = '1';
                            }
                        });
                        plot.on('plotly_doubleclick', function() {
                            toast.style.opacity = '0';
                            setTimeout(() => { toast.style.display = 'none'; }, 300);
                        });
                    });
                } catch(e) {
                    // Cross-origin iframe access blocked, skip
                }
            });

            // Also check top-level document
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(plot => {
                if (plot.on) {
                    plot.on('plotly_relayout', function(eventData) {
                        const isZoomed = (
                            eventData['xaxis.range[0]'] !== undefined ||
                            eventData['yaxis.range[0]'] !== undefined
                        );
                        if (isZoomed) {
                            toast.style.display = 'block';
                            toast.style.opacity = '1';
                        }
                    });
                    plot.on('plotly_doubleclick', function() {
                        toast.style.opacity = '0';
                        setTimeout(() => { toast.style.display = 'none'; }, 300);
                    });
                }
            });
        }

        // Retry every 500ms for 5 seconds to catch late-loading charts
        let attempts = 0;
        const interval = setInterval(() => {
            setupZoomToast();
            attempts++;
            if (attempts >= 10) clearInterval(interval);
        }, 500);
    </script>
""", unsafe_allow_html=True)

# --- Session State ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# --- Top Bar ---
col1, col2, col3 = st.columns([0.5, 3, 1])
with col1:
    import base64
    with open("assets/stockdashlogo.png", "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <img src="data:image/png;base64,{img_data}" 
             style="height:120px; width:auto; margin-top:-60px;">
    """, unsafe_allow_html=True)
with col2:
    search = st.text_input("", placeholder="Search stocks or companies...", label_visibility="collapsed", key="search_input")

    if search and st.session_state.page == "home":
        results = search_stocks(search)
        if results:
            st.markdown('<div class="search-results">', unsafe_allow_html=True)
            for r in results:
                if st.button(f"**{r['ticker']}**  {r['name']}", key=f"result_{r['ticker']}"):
                    st.session_state.page = "detail"
                    st.session_state.selected_stock = r['ticker']
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.write("")


# --- Popular Stocks Data (defined here, before columns) ---
popular = get_popular_stocks_data()

# --- Page Routing ---
if st.session_state.page == 'home':
    st.divider()
    main, sidebar = st.columns([2.5, 1])

    with main:
        st.subheader("Markets")
        chart1, chart2 = st.columns(2)
        # Dow Jones
        dji_price, dji_change = get_current_price("^DJI")
        if dji_price is None or dji_change is None:
            dji_price, dji_change = 0, 0
        dji_color = "green" if dji_change >= 0 else "red"
        dji_arrow = "▲" if dji_change >= 0 else "▼"
        with chart1:
            st.markdown("**Dow Jones**")
            st.markdown(f"#### ${dji_price:,.2f}")
            st.markdown(f":{dji_color}[{dji_arrow} {abs(dji_change):.2f}% Today]")
            dji_fig = index_chart("^DJI", "Dow Jones")
            if dji_fig:
                st.plotly_chart(dji_fig, use_container_width=True, config={'displayModeBar': False})
        # NASDAQ
        nas_price, nas_change = get_current_price("^IXIC")
        if nas_price is None or nas_change is None:
            nas_price, nas_change = 0, 0
        nas_color = "green" if nas_change >= 0 else "red"
        nas_arrow = "▲" if nas_change >= 0 else "▼"
        with chart2:
            st.markdown("**NASDAQ**")
            st.markdown(f"#### ${nas_price:,.2f}")
            st.markdown(f":{nas_color}[{nas_arrow} {abs(nas_change):.2f}% Today]")
            nas_fig = index_chart("^IXIC", "NASDAQ")
            if nas_fig:
                st.plotly_chart(nas_fig, use_container_width=True, config={'displayModeBar': False})

    with sidebar:
        # Build the entire panel as one HTML block
        stocks_html = ""
        for stock in popular:
            color = "#00C896" if stock["positive"] else "#FF4444"
            stocks_html += (
                '<div style="display:flex; justify-content:space-between; align-items:center; padding: 10px 0px; border-bottom: 1px solid #222;">'
                f'<div><span style="font-weight:bold; font-size:15px; color:white;">{stock["ticker"]}</span>'
                f'<span style="color:gray; font-size:12px; margin-left:8px;">{stock["name"]}</span></div>'
                '<div style="text-align:right;">'
                f'<span style="font-weight:bold; font-size:14px; color:white;">{stock["price"]}</span><br>'
                f'<span style="color:' + color + f'; font-size:12px;">{stock["change"]}</span>'
                '</div></div>'
            )


        st.markdown(f"""
            <div style="
                background-color: #141414;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 20px;
                margin-top: 10px;
            ">
                <p style="font-weight:bold; font-size:16px; color:white; margin-bottom:10px;">Popular Stocks</p>
                <hr style="border-color:#333; margin-bottom:10px;">
                {stocks_html}
            </div>
        """, unsafe_allow_html=True)

    time.sleep(25)
    st.rerun()

elif st.session_state.page == "detail":
    ticker = st.session_state.selected_stock
    price, change = get_current_price(ticker)
    info = get_stock_info(ticker)
    if price is None: price, change = 0, 0
    if info is None: info = {"name": ticker, "sector": "N/A", "market_cap": "N/A", "pe_ratio": "N/A", "52_week_high": "N/A", "52_week_low": "N/A", "volume": "N/A"}

    color = "#00C896" if change >= 0 else "#FF4444"
    arrow = "▲" if change >= 0 else "▼"

    # --- Header ---
    h1, h2, h3 = st.columns([0.5, 4, 1])
    with h1:
        if st.button("← Back"):
            st.session_state.page = "home"
            st.rerun()
    with h2:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:16px; padding-top:6px;">
                <span style="font-size:22px; font-weight:700;">{ticker}</span>
                <span style="color:gray; font-size:16px;">{info['name']}</span>
                <span style="font-size:22px; font-weight:700;">${price:,.2f}</span>
                <span style="color:{color}; font-size:16px;">{arrow} {abs(change):.2f}%</span>
            </div>
        """, unsafe_allow_html=True)
    with h3:
        if st.button("+ Watchlist"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.success(f"{ticker} added to watchlist")

    st.markdown("---")

    # --- Period Selector ---
    period_options = {"1D": "1d", "1W": "1w", "1M": "1m", "1Y": "1y"}
    selected_period = st.radio("", list(period_options.keys()), horizontal=True, label_visibility="collapsed")
    history = get_stock_history(ticker, period_options[selected_period])

    # --- Main Layout ---
    left, right = st.columns([3, 1])

    with left:
        if history is not None and not history.empty:
            prices = history["Close"].dropna()
            is_positive = prices.iloc[-1] >= prices.iloc[0]
            line_color = "#00C896" if is_positive else "#FF4444"
            fill_color = "rgba(0,200,150,0.1)" if is_positive else "rgba(255,68,68,0.1)"

            y_min = prices.min() * 0.995
            y_max = prices.max() * 1.005

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history.index,
                y=prices,
                fill="tozeroy",
                fillcolor=fill_color,
                line=dict(color=line_color, width=2),
                name=ticker
            ))
            fig.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, tickfont=dict(color="gray", size=10)),
                    yaxis=dict(
                        showgrid=False, 
                        side="right", 
                        tickfont=dict(color="gray", size=10), 
                        tickformat=",.2f",
                        range=[y_min, y_max]
                    ),
                    height=350,
                    showlegend=False,
                    dragmode="zoom"
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.error("Could not load chart data.")

    with right:
        def fmt(val, prefix="", suffix=""):
            if val == "N/A" or val is None: return "N/A"
            if isinstance(val, float): return f"{prefix}{val:,.2f}{suffix}"
            if isinstance(val, int): return f"{prefix}{val:,}{suffix}"
            return str(val)

        def fmt_mcap(val):
            if val == "N/A" or val is None: return "N/A"
            if val >= 1_000_000_000_000: return f"${val/1_000_000_000_000:.2f}T"
            if val >= 1_000_000_000: return f"${val/1_000_000_000:.2f}B"
            if val >= 1_000_000: return f"${val/1_000_000:.2f}M"
            return f"${val:,}"

        st.markdown(f"""
            <div style="background:#141414; border:1px solid #333; border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:14px;">
                <div><span style="color:gray;font-size:12px;">MARKET CAP</span><br><span style="font-size:16px;font-weight:600;">{fmt_mcap(info['market_cap'])}</span></div>
                <div><span style="color:gray;font-size:12px;">P/E RATIO</span><br><span style="font-size:16px;font-weight:600;">{fmt(info['pe_ratio'])}</span></div>
                <div><span style="color:gray;font-size:12px;">52W HIGH</span><br><span style="font-size:16px;font-weight:600;">{fmt(info['52_week_high'], "$")}</span></div>
                <div><span style="color:gray;font-size:12px;">52W LOW</span><br><span style="font-size:16px;font-weight:600;">{fmt(info['52_week_low'], "$")}</span></div>
                <div><span style="color:gray;font-size:12px;">VOLUME</span><br><span style="font-size:16px;font-weight:600;">{fmt(info['volume'])}</span></div>
                <div style="margin-top:10px;padding-top:14px;border-top:1px solid #333;"><span style="color:gray;font-size:12px;">🔮 PREDICTION MODEL</span><br><span style="color:#555;font-size:13px;">Coming in Phase 2</span></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Investment Calculator ---
    st.markdown("### 💰 Hypothetical Investment Calculator")
    calc1, calc2 = st.columns(2)
    with calc1:
        amount = st.number_input("Amount Invested ($)", min_value=1.0, value=1000.0, step=100.0)
    with calc2:
        start_date = st.date_input("Start Date", value=datetime.date(2020, 1, 1))

    if st.button("Calculate"):
        from calculations import calculate_investment
        result = calculate_investment(ticker, amount, str(start_date))
        if result:
            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("Current Value", f"${result['current_value']:,.2f}")
            with r2:
                st.metric("Profit / Loss", f"${result['profit']:,.2f}")
            with r3:
                st.metric("Total Return", f"{result['total_return']:.2f}%")