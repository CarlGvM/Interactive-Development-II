import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# ---------------------- SETUP ------------------------
st.set_page_config(page_title="📊 Stock Dashboard", layout="wide")

st.title("📊 Stock Market Dashboard")
st.caption("Visual insights for smarter stock decisions")

# ---------------- STOCK SELECTOR + DATE RANGE ---------
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA)", value="AAPL").upper().strip()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", value=date.today())

# Input validation
if start_date > end_date or start_date > date.today() or end_date > date.today():
    st.error("Please enter a valid date range.")
    st.stop()

# --------------- FETCH & PROCESS DATA ------------------
@st.cache_data(ttl=3600)
def get_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    if data.empty:
        return None
    data["Daily Return"] = data["Close"].pct_change()
    data["Cumulative Return"] = (1 + data["Daily Return"]).cumprod() - 1
    data["Max Drawdown"] = (data["Close"] / data["Close"].cummax()) - 1
    return data

with st.spinner(f"Loading data for {ticker}..."):
    df = get_stock_data(ticker, start_date, end_date)

if df is None:
    st.error("No data found. Try a different ticker.")
    st.stop()

# ---------------- PRICE CHART -------------------------
st.subheader("📈 Stock Price Over Time")

fig = px.line(
    df,
    x=df.index,
    y="Close",
    title=f"{ticker} Closing Price",
    labels={"Close": "Price (USD)", "index": "Date"},
    template="plotly_white",
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    height=500,
)
fig.update_xaxes(rangeslider_visible=True)

st.plotly_chart(fig, use_container_width=True)

# ---------------- METRICS SECTION ---------------------
st.subheader("📊 Performance Metrics")

total_return = df["Cumulative Return"].iloc[-1]
avg_daily_return = df["Daily Return"].mean()
volatility = df["Daily Return"].std()
max_drawdown = df["Max Drawdown"].min()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📈 Total Return", f"{total_return:.2%}")
col2.metric("🔁 Avg Daily Return", f"{avg_daily_return:.3%}")
col3.metric("📉 Volatility", f"{volatility:.3%}")
col4.metric("⛔ Max Drawdown", f"{max_drawdown:.2%}")

# ----------------- TABLE WITH CONDITIONAL FORMATTING --------------
st.subheader("📅 Historical Data with Returns")

display_df = df[["Close", "Daily Return"]].copy().reset_index()
display_df.rename(columns={"Date": "Date", "Close": "Close Price"}, inplace=True)

def highlight_returns(val):
    if pd.isna(val):
        return ""
    color = "green" if val > 0 else "red"
    return f"color: {color}"

st.dataframe(
    display_df.style.format({"Close Price": "${:.2f}", "Daily Return": "{:.2%}"}).applymap(highlight_returns, subset=["Daily Return"]),
    use_container_width=True
)

# ---------------- RATIONALE (for your write-up) --------------------
with st.expander("🧠 Dashboard Design Rationale (for assignment write-up)"):
    st.markdown("""
**Cognitive & Visualization Design Choices**:

- **Line chart**: Chosen for intuitive trend recognition (supports *pattern detection* and reduces *cognitive load*).
- **Date range slider**: Helps avoid *anchoring* and allows temporal context (*focus + context*).
- **Metric cards**: Support *working memory* by chunking key info into digestible units.
- **Conditional formatting in table**: Leverages *preattentive processing* (green/red) for rapid insight.
- **Volatility & max drawdown metrics**: Introduced to emphasize *risk*, not just performance (mitigates *confirmation bias*).
- **Caching**: Improves performance and user experience.
    """)
