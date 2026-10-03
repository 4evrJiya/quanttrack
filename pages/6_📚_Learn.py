"""
QuantTrack — Learn Page
"""

import streamlit as st

st.set_page_config(page_title="Learn - QuantTrack", page_icon="📚", layout="wide")

st.title("📚 Learn")
st.caption("New to trading or investing? Start here before using the other pages.")

with st.expander("🧪 What is backtesting?", expanded=True):
    st.write("""
    Backtesting means testing a trading rule against **past** data to see if it would have made money.
    It's not predicting the future — it's checking whether an idea would have worked historically.
    If it didn't work in the past, it's unlikely to magically work going forward either.
    """)

with st.expander("📈 Moving Average Crossover"):
    st.write("""
    Compares a fast-reacting average (last 20 days) against a slower average (last 50 days).
    When the fast one rises above the slow one, that's a **buy** signal — the stock may be starting a new upward trend.
    When it drops back below, that's a **sell** signal.
    """)

with st.expander("🚀 Momentum Strategy"):
    st.write("""
    If a stock has risen more than a set amount (e.g. 5%) over the last 20 days, this strategy buys,
    betting that stocks on a roll tend to keep rising a bit longer.
    """)

with st.expander("↩️ Mean Reversion"):
    st.write("""
    The opposite idea — if a stock drops unusually far below its normal average price, this strategy buys,
    betting it will bounce back toward its average.
    """)

with st.expander("🧭 Market Regime Detection (ADX)"):
    st.write("""
    ADX measures how strongly a stock is trending, from 0 to 100.
    Above 25 means the stock is clearly trending (Crossover/Momentum tend to work better).
    Below 25 means it's moving sideways with no clear direction (Mean Reversion tends to work better).
    """)

with st.expander("💰 Sharpe Ratio"):
    st.write("""
    The single most important number in this whole app. It measures **return per unit of risk taken**,
    not just raw profit. A strategy that makes 15% with wild swings can actually be worse than one making 10% smoothly.
    Above 1 is generally good, above 2 is very good.
    """)

with st.expander("📉 Max Drawdown"):
    st.write("""
    The biggest drop you'd have experienced from a peak before it recovered — basically, the worst pain
    you'd have felt holding this strategy. A high return with a brutal drawdown might not be worth the stress.
    """)

with st.expander("🎯 Win Rate"):
    st.write("""
    The percentage of active trading days that were profitable. Careful — a high win rate doesn't
    automatically mean a good strategy; a few big losses can outweigh many small wins.
    """)

with st.expander("🥧 Portfolio Diversification"):
    st.write("""
    Spreading money across several stocks instead of betting everything on one. You usually earn
    less than if you'd picked the single best stock — but your worst-case losses are typically much smaller.
    It's a trade-off between upside and safety, not a free win.
    """)

with st.expander("🔮 Price Forecasting"):
    st.write("""
    QuantTrack uses a tool called Prophet to project where a price trend might head over the next 30 days.
    This is **not** a guarantee — it's a reasonable projection based on historical patterns, shown with a range
    of uncertainty. No tool can reliably predict short-term stock prices.
    """)

st.divider()
st.info("💡 Once you're comfortable with these ideas, head to **Backtest** in the sidebar to try them on a real stock.")