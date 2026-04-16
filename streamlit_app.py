import streamlit as st

st.set_page_config(page_title="AI Trading Bot Dashboard", layout="wide")

st.title("AI Trading Bot Dashboard")
st.caption("Streamlit version")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Risk Level", "MEDIUM")

with col2:
    st.metric("Profile", "NORMAL")

with col3:
    st.metric("Positions", "6")

left, right = st.columns(2)

with left:
    st.subheader("Trading Rules")
    st.write("Max Position: $2500")
    st.write("Max Positions: 8")
    st.write("Max Daily Trades: 3")
    st.write("Stop Loss: -10.0%")
    st.write("Take Profit: 20.0%")
    st.write("Trailing Stop: -7.0%")
    st.write("Max Deployed: 80%")
    st.write("VIX Threshold: 25")

with right:
    st.subheader("Approved Tickers")
    st.write(["AAPL", "NVDA", "MSFT"])

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    st.subheader("Communication Log")
    st.text("PROFILE Selected=normal Reason=MEDIUM RISK")
    st.text("NEWS Sentiment=neutral")
    st.text("MARKET_DATA VIX=18.08 SP=0.8%")

with bottom_right:
    st.subheader("Rule Change History")
    st.info("No rule changes yet")
