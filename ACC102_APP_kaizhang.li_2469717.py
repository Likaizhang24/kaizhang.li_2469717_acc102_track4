import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import io
import contextlib
import logging
from datetime import datetime, timedelta
import time

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("peewee").setLevel(logging.CRITICAL)



st.sidebar.header("⚙️ Analysis Settings")

stocks_input = st.sidebar.text_input(
    "Enter ticker symbols (comma-separated)",
    value="AAPL,MSFT,GOOGL",
    help="Example: AAPL,MSFT,GOOGL"
)
stock_list = [s.strip() for s in stocks_input.split(",") if s.strip()]

col1, col2 = st.sidebar.columns(2)
with col1:
    end_date = datetime.now()
with col2:
    start_date = end_date - timedelta(days=365 * 2)

start_date_input = st.sidebar.date_input("Start Date", start_date)
end_date_input = st.sidebar.date_input("End Date", end_date)

analysis_type = st.sidebar.radio(
    "Select Analysis Type",
    ["Price Trend Analysis", "Return Analysis", "Volatility Analysis", "Comprehensive Comparison"]
)

analyze_button = st.sidebar.button("🚀 Start Analysis", type="primary", use_container_width=True)

if analyze_button and stock_list:
    try:
        if start_date_input >= end_date_input:
            st.error("The start date must be earlier than the end date.")
            st.stop()

        # Fetch data
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_data = {}
        failed_stocks = []
        total_stocks = len(stock_list)

        for idx, stock in enumerate(stock_list):
            try:
                status_text.text(f"Fetching data for {stock}... ({idx + 1}/{total_stocks})")
                
                # Retry data fetching several times
                max_retries = 3
                success = False
                
                for attempt in range(max_retries):
                    try:
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            stock_data = yf.Ticker(stock)
                            hist = stock_data.history(start=start_date_input, end=end_date_input)

                        if not hist.empty and 'Close' in hist.columns:
                            series = hist['Close'].copy()
                            series.name = stock
                            all_data[stock] = series
                            success = True
                            break
                        else:
                            if attempt < max_retries - 1:
                                time.sleep(1)  # Wait 1 second before retrying
                    except Exception:
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Wait 1 second before retrying
                
                if not success:
                    failed_stocks.append(stock)
                    
            except Exception as e:
                failed_stocks.append(stock)
            
            # Update the progress bar
            progress_bar.progress((idx + 1) / total_stocks)
            time.sleep(0.5)  # Avoid sending requests too quickly
        
        status_text.empty()
        progress_bar.empty()

        if not all_data:
            st.error(
                "❌ Unable to retrieve any stock data.\n\n"
                "Possible reasons:\n"
                "1. 🌐 Network issue - The Streamlit Cloud server may not be able to access Yahoo Finance reliably.\n"
                "2. 📝 Invalid ticker symbols - Please confirm the symbol format (for example: AAPL, MSFT, GOOGL).\n"
                "3. 🚫 API limits - Yahoo Finance may be restricting frequent requests.\n\n"
                "💡 Suggestions:\n"
                "• Try again later\n"
                "• Reduce the number of tickers queried at the same time\n"
                "• Check whether the ticker symbols are correct"
            )
            st.stop()

        data = pd.DataFrame(all_data)
        close_prices = data

        if failed_stocks:
            st.warning(f"⚠️ Failed to retrieve data for: {', '.join(failed_stocks)}")

        if data.empty or len(data.columns) == 0:
            st.error("No data was retrieved. Please check whether the ticker symbols are correct.")
        else:
            st.success(f"✅ Successfully retrieved data for {len(data.columns)} U.S. stocks.")

            with st.expander("📋 View Raw Data"):
                st.dataframe(close_prices.tail(10))

            close_prices = data

            if analysis_type == "Price Trend Analysis":
                st.header("📊 Price Trend Analysis")

                fig = go.Figure()
                for stock in stock_list:
                    if stock in close_prices.columns:
                        fig.add_trace(go.Scatter(
                            x=close_prices.index,
                            y=close_prices[stock],
                            name=stock,
                            line=dict(width=2)
                        ))

                fig.update_layout(
                    title="Stock Closing Price Trend",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    hovermode='x unified',
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📈 Price Statistics Summary")
                stats_df = pd.DataFrame({
                    'Current Price': [close_prices[stock].iloc[-1] for stock in stock_list if stock in close_prices.columns],
                    'Highest Price': [close_prices[stock].max() for stock in stock_list if stock in close_prices.columns],
                    'Lowest Price': [close_prices[stock].min() for stock in stock_list if stock in close_prices.columns],
                    'Average Price': [close_prices[stock].mean() for stock in stock_list if stock in close_prices.columns]
                }, index=stock_list)
                st.dataframe(stats_df.round(2))

            elif analysis_type == "Return Analysis":
                st.header("💰 Return Analysis")

                returns = close_prices.pct_change().dropna()
                cumulative_returns = (1 + returns).cumprod()

                fig = go.Figure()
                for stock in stock_list:
                    if stock in cumulative_returns.columns:
                        fig.add_trace(go.Scatter(
                            x=cumulative_returns.index,
                            y=cumulative_returns[stock],
                            name=stock,
                            line=dict(width=2)
                        ))

                fig.update_layout(
                    title="Cumulative Return Comparison",
                    xaxis_title="Date",
                    yaxis_title="Cumulative Return",
                    hovermode='x unified',
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📊 Return Statistics")
                total_returns = ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100
                annual_returns = total_returns / 2

                return_stats = pd.DataFrame({
                    'Total Return (%)': total_returns.round(2),
                    'Annualized Return (%)': annual_returns.round(2),
                    'Average Daily Return (%)': (returns.mean() * 100).round(4),
                    'Return Standard Deviation (%)': (returns.std() * 100).round(4)
                })
                st.dataframe(return_stats)

            elif analysis_type == "Volatility Analysis":
                st.header("📉 Volatility Analysis")

                returns = close_prices.pct_change().dropna()
                rolling_vol = returns.rolling(window=30).std() * np.sqrt(252) * 100

                fig = go.Figure()
                for stock in stock_list:
                    if stock in rolling_vol.columns:
                        fig.add_trace(go.Scatter(
                            x=rolling_vol.index,
                            y=rolling_vol[stock],
                            name=stock,
                            line=dict(width=2)
                        ))

                fig.update_layout(
                    title="30-Day Rolling Volatility (Annualized)",
                    xaxis_title="Date",
                    yaxis_title="Volatility (%)",
                    hovermode='x unified',
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("🔍 Volatility Statistics")
                vol_stats = pd.DataFrame({
                    'Average Volatility (%)': rolling_vol.mean().round(2),
                    'Maximum Volatility (%)': rolling_vol.max().round(2),
                    'Minimum Volatility (%)': rolling_vol.min().round(2),
                    'Current Volatility (%)': rolling_vol.iloc[-1].round(2)
                })
                st.dataframe(vol_stats)

            else:
                st.header("🎯 Comprehensive Financial Metric Comparison")

                returns = close_prices.pct_change().dropna()
                total_returns = ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100

                metrics_df = pd.DataFrame({
                    'Ticker': stock_list,
                    'Current Price': [close_prices[s].iloc[-1] for s in stock_list if s in close_prices.columns],
                    'Total Return (%)': [total_returns[s] for s in stock_list if s in total_returns.index],
                    'Annualized Volatility (%)': [(returns[s].std() * np.sqrt(252) * 100) for s in stock_list if
                                       s in returns.columns],
                    'Sharpe Ratio': [
                        (returns[s].mean() / returns[s].std() * np.sqrt(252))
                        for s in stock_list if s in returns.columns and returns[s].std() != 0
                    ]
                })

                st.dataframe(metrics_df.round(2), use_container_width=True)

                if len(stock_list) >= 2:
                    st.subheader("🕸️ Multi-Dimensional Comparison Radar Chart")

                    categories = ['Return', 'Risk-Adjusted Return', 'Price Stability']

                    fig = go.Figure()
                    for stock in stock_list:
                        if stock in returns.columns:
                            ret_score = min(total_returns[stock] / 100, 1) if total_returns[stock] > 0 else 0
                            sharpe = abs(returns[stock].mean() / returns[stock].std() * np.sqrt(252)) if returns[
                                                                                                             stock].std() != 0 else 0
                            sharpe_score = min(sharpe / 2, 1)
                            vol_score = 1 - min(returns[stock].std() * np.sqrt(252), 1)

                            values = [ret_score, sharpe_score, vol_score]
                            values.append(values[0])

                            fig.add_trace(go.Scatterpolar(
                                r=values,
                                theta=categories + [categories[0]],
                                fill='toself',
                                name=stock
                            ))

                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=True,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.header("💡 Key Insights")
            returns = close_prices.pct_change().dropna()
            total_returns = ((close_prices.iloc[-1] / close_prices.iloc[0]) - 1) * 100

            best_performer = total_returns.idxmax()
            worst_performer = total_returns.idxmin()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Best Performer",
                    f"{best_performer}",
                    f"{total_returns[best_performer]:.2f}%"
                )
            with col2:
                st.metric(
                    "Needs Attention",
                    f"{worst_performer}",
                    f"{total_returns[worst_performer]:.2f}%"
                )
            with col3:
                avg_vol = returns.std() * np.sqrt(252) * 100
                st.metric(
                    "Average Volatility",
                    f"{avg_vol.mean():.2f}%",
                    "Annualized"
                )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your network connection or ticker symbol format.")

elif analyze_button:
    st.info("👈 Enter ticker symbols and click Analyze.")

else:
    st.info("👈 Configure the parameters on the left, then click the Start Analysis button.")
    
    # Show usage tips
    st.markdown("""
    ### 💡 Usage Tips
    
    **Supported stock market:**
    - 🇺🇸 U.S. stocks: AAPL, MSFT, GOOGL, AMZN, TSLA, etc.
    
    **Main features:**
    - 📊 Price Trend Analysis - View stock price movements
    - 💰 Return Analysis - Calculate cumulative returns and summary metrics
    - 📉 Volatility Analysis - Evaluate stock risk levels
    - 🎯 Comprehensive Comparison - Compare different stocks across multiple dimensions
    
    **Notes:**
    - Data comes from Yahoo Finance and may be delayed
    - For the best experience, analyze 2-5 stocks at a time
    - If data retrieval fails, please try again later
    """)

st.markdown("---")
st.markdown("**Data Source**: Yahoo Finance | **Update Time**: Real-time")
st.markdown("**Note**: This tool is for educational purposes only and does not constitute investment advice.")
