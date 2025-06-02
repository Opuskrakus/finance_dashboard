import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openai import OpenAI
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def calculate_rsi(data, periods=14):
    """Calculate Relative Strength Index."""
    close_data = data['Close'] if 'Close' in data.columns else data[('Close', data.columns.get_level_values('Ticker')[0])]
    delta = close_data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ma(data, window):
    """Calculate Moving Average."""
    close_data = data['Close'] if 'Close' in data.columns else data[('Close', data.columns.get_level_values('Ticker')[0])]
    return close_data.rolling(window=window).mean()

def get_stock_data(symbol, start_date, end_date):   
    """Fetch data from Yahoo Finance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values('Price')
        return df
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_market_commentary(symbol, data, rsi_value):
    """Generate market commentary using OpenAI."""
    try:
        close_data = data['Close'] if 'Close' in data.columns else data[('Close', symbol)]
        price_change = ((close_data.iloc[-1] - close_data.iloc[0]) / close_data.iloc[0]) * 100
        
        prompt = f"""Stock: {symbol}
        Price Change: {price_change:.2f}%
        RSI: {rsi_value:.2f}
        Current Price: ${close_data.iloc[-1]:.2f}
        
        Analyze this data and provide 3-5 sentences about the stock's performance and technical indicators."""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

st.set_page_config(page_title="Finance Dashboard", layout="wide")

st.sidebar.title("Settings")
symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
days = st.sidebar.selectbox("Time Period (Days)", [30, 90, 180, 365], index=1)

st.sidebar.subheader("Chart Options")
show_candlestick = st.sidebar.checkbox("Show Candlestick Chart", value=True)
show_ma = st.sidebar.checkbox("Show Moving Average (20-day)", value=True)
show_rsi = st.sidebar.checkbox("Show RSI Indicator", value=True)
ma_period = st.sidebar.slider("Moving Average Period", min_value=5, max_value=50, value=20)

end_date = datetime.now()
start_date = end_date - timedelta(days=days)
data = get_stock_data(symbol, start_date, end_date)

if data is not None and not data.empty:
    # Calculate indicators
    data[f'MA{ma_period}'] = calculate_ma(data, ma_period)
    data['RSI'] = calculate_rsi(data)

    # Determine subplot configuration based on selections
    if show_rsi:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.3, 
                           row_heights=[0.7, 0.3])
    else:
        fig = make_subplots(rows=1, cols=1)

    # Add candlestick chart if selected
    if show_candlestick:
        fig.add_trace(go.Candlestick(x=data.index,
                                    open=data['Open'],
                                    high=data['High'],
                                    low=data['Low'],
                                    close=data['Close'],
                                    name='Price'),
                      row=1, col=1)

    # Add moving average if selected
    if show_ma:
        fig.add_trace(go.Scatter(x=data.index, 
                                y=data[f'MA{ma_period}'],
                                name=f'MA({ma_period})',
                                line=dict(color='orange')),
                      row=1, col=1)

    # Add RSI if selected
    if show_rsi:
        fig.add_trace(go.Scatter(x=data.index,
                                y=data['RSI'],
                                name='RSI',
                                line=dict(color='purple')),
                      row=2, col=1)

        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # Adjust height based on RSI selection
    chart_height = 600 if show_rsi else 400
    fig.update_layout(height=chart_height, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Display current price
    current_price = data['Close'].iloc[-1]
    st.metric("Current Price", f"${current_price:.2f}")

    #generate commentary
    if st.button("Get AI Commentary"):
        comment = generate_market_commentary(symbol, data, data['RSI'].iloc[-1])
        st.write(comment)
else:
    st.error("No data available") 