"""
QuantTrack — Price Forecast Page
"""

import streamlit as st

from data_ingestion import fetch_stock_data
from forecasting import generate_forecast

st.set_page_config(page_title="Forecast - QuantTrack", page_icon="🔮", layout="wide")

st.title("🔮 30-Day Price Forecast")
st.caption("A trend projection based on historical patterns — not a guaranteed prediction.")

forecast_ticker = st.text_input("Enter ticker for forecast", "RELIANCE.NS")
forecast_button = st.button("Generate Forecast")

if forecast_button:
    forecast_data = fetch_stock_data(forecast_ticker)

    if forecast_data is None:
        st.error(f"No data found for ticker '{forecast_ticker}'. Check the symbol.")
    else:
        with st.spinner("Generating forecast..."):
            forecast_result = generate_forecast(forecast_data)

        if forecast_result is None:
            st.warning("Not enough historical data to generate a reliable forecast for this stock.")
        else:
            forecast_chart_data = forecast_result[["ds", "yhat", "yhat_lower", "yhat_upper"]].set_index("ds").tail(30)

            st.subheader("Forecasted Price (next 30 days)")
            st.line_chart(forecast_chart_data)

            st.caption("The shaded range (yhat_lower to yhat_upper) represents genuine uncertainty — not a guarantee. Markets are affected by news and events no model can predict.")

            st.subheader("Forecast Table")
            st.dataframe(forecast_chart_data.tail(10), use_container_width=True)
else:
    st.info("Enter a ticker above, then click **Generate Forecast** to begin.")