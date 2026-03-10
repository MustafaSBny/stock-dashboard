import streamlit as st
from data import get_stock_history, get_stock_info, get_current_price, get_popular_stocks_data
from charts import index_chart, price_chart

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
        margin-bottom: -65px;
        }
        /* Hide Streamlit top header bar */
        header[data-testid="stHeader"] {
            display: none !important;
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
    search = st.text_input("", placeholder="Search stocks or companies...", label_visibility="collapsed")
with col3:
    st.write("")

st.divider()

# --- Popular Stocks Data (defined here, before columns) ---
popular = get_popular_stocks_data()

# --- Page Routing ---
if st.session_state.page == 'home':

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

elif st.session_state.page == 'detail':
    st.button("← Back", on_click=lambda: setattr(st.session_state, 'page', 'home'))
    st.subheader(f"Detail view for {st.session_state.selected_stock}")
    st.write("Chart and details coming soon...")