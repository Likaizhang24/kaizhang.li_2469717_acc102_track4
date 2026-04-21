 Listed Company Financial Performance Analysis Tool
student ID:2469717
name: kaizhang li
## 1. Problem and Users
The tool helps investors quickly access stock data, calculate key financial indicators, and support investment decisions through visualization.

## 2. Data
- **Data Source**: Yahoo Finance API
- **Key Fields**: Closing price, trading volume, daily return, cumulative return, volatility, Sharpe ratio
- **Example Stocks**: AAPL (Apple), MSFT (Microsoft), GOOGL (Alphabet)
- **Data Retrieval Date**: Dynamically generated

## 3. Methodology
Main Python steps:
1. Use the yfinance library to retrieve historical stock price data from Yahoo Finance
2. Use pandas for data cleaning (handling missing values) and data transformation
3. Calculate financial metrics: daily returns, cumulative returns, annualised volatility, Sharpe ratio
4. Create interactive visualisations using plotly
5. Build a user-friendly web interface via Streamlit

## 4. Key Findings
- Different stocks exhibit varying performance in terms of returns and risk; selection should align with investment objectives
- The Sharpe ratio is an effective metric for assessing risk-adjusted returns
- Volatility analysis helps identify stock stability
- Comprehensive multi-dimensional metrics provide a more accurate reflection of true stock performance than single indicators
- Real-time data acquisition makes analysis results more timely and valuable for reference

## 5. Running Instructions

### Running the Streamlit Application Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Running the Jupyter Notebook
```bash
# Launch Jupyter
jupyter notebook notebook.ipynb
```

## 6. Product Links
- **GitHub Repository**: https://github.com/codekey163/acc102-financial-analysis.git
- **Streamlit Application**: https://acc102-financial-analysis-gsugbacordsssvgmcd3rrr.streamlit.app



## 7. Limitations and Future Optimisation

### Current Limitations
- Only uses price data; does not include financial statement data (such as PE ratio, EPS, etc.)
- Limited technical analysis indicators; does not include professional indicators such as MACD and RSI
- Does not consider the impact of macroeconomic factors on stocks
- Sharpe ratio calculation assumes a fixed risk-free rate of 2%

### Future Optimisation Directions
- Integrate additional financial metrics (price-to-earnings ratio, price-to-book ratio, ROE, etc.)
- Add technical indicator analysis functionality
- Introduce machine learning models for price prediction
- Incorporate industry comparison features
- Support exporting analysis reports in PDF format
- Add real-time price alert functionality

## 8. Project Structure
```
/
├── app.py                  # Main Streamlit application file
├── notebook.ipynb          # Analysis workflow (English)
├── notebook_CN.ipynb       # Analysis workflow (Chinese)
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── figures/               # Generated charts (produced by notebook)
```

## 9. Technology Stack
- **Python 3.8+**
- **Streamlit**: Web application framework
- **yfinance**: Financial data retrieval
- **pandas**: Data processing and analysis
- **numpy**: Numerical computation
- **plotly**: Interactive visualisation
- **matplotlib**: Static chart generation

