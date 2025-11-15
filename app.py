# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from prophet import Prophet
from prophet.plot import plot_plotly
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Stock Prediction App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("📈 Stock Price Prediction App")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Stock selection
    stock_symbol = st.text_input(
        "Enter Stock Symbol",
        value="AAPL",
        help="Enter stock ticker (e.g., AAPL, GOOGL, MSFT, TSLA)"
    ).upper()
    
    # Date range
    st.subheader("Historical Data Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365*2),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # Prediction period
    st.subheader("Prediction Settings")
    prediction_days = st.slider(
        "Days to Predict",
        min_value=7,
        max_value=365,
        value=30,
        step=7,
        help="Number of days to predict into the future"
    )
    
    # Model parameters
    with st.expander("Advanced Settings"):
        changepoint_prior_scale = st.slider(
            "Changepoint Prior Scale",
            0.001, 0.5, 0.05,
            help="Flexibility of trend changes"
        )
        seasonality_prior_scale = st.slider(
            "Seasonality Prior Scale",
            0.01, 10.0, 10.0,
            help="Strength of seasonality"
        )
    
    predict_button = st.button("🔮 Predict Stock Price", type="primary", use_container_width=True)

# Helper Functions
@st.cache_data(ttl=3600)
def load_stock_data(symbol, start, end):
    """Load stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start, end=end)
        
        if df.empty:
            return None, None
        
        info = stock.info
        return df, info
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def calculate_metrics(df):
    """Calculate stock metrics"""
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    change = current_price - prev_price
    pct_change = (change / prev_price) * 100
    
    high_52w = df['High'].tail(252).max()
    low_52w = df['Low'].tail(252).min()
    avg_volume = df['Volume'].tail(30).mean()
    
    return {
        'current_price': current_price,
        'change': change,
        'pct_change': pct_change,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'avg_volume': avg_volume
    }

def create_candlestick_chart(df):
    """Create candlestick chart with volume"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price', 'Volume')
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Volume bars
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            marker_color=colors,
            name='Volume',
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f'{stock_symbol} Stock Price',
        yaxis_title='Price (USD)',
        yaxis2_title='Volume',
        xaxis_rangeslider_visible=False,
        height=600,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def predict_stock(df, days, changepoint_scale, seasonality_scale):
    """Predict stock prices using Prophet"""
    # Prepare data for Prophet
    prophet_df = df.reset_index()[['Date', 'Close']].rename(
        columns={'Date': 'ds', 'Close': 'y'}
    )
    
    # Initialize and fit model
    model = Prophet(
        changepoint_prior_scale=changepoint_scale,
        seasonality_prior_scale=seasonality_scale,
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True
    )
    
    model.fit(prophet_df)
    
    # Make future dataframe
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    
    return model, forecast

# Main App Logic
if predict_button:
    with st.spinner(f'Loading data for {stock_symbol}...'):
        # Load data
        df, info = load_stock_data(stock_symbol, start_date, end_date)
        
        if df is None or df.empty:
            st.error(f"❌ Could not load data for {stock_symbol}. Please check the symbol and try again.")
        else:
            # Reset index to have Date as a column
            df = df.reset_index()
            
            # Company Information
            st.header(f"📊 {stock_symbol} Analysis")
            
            if info:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Company", info.get('longName', stock_symbol))
                with col2:
                    st.metric("Sector", info.get('sector', 'N/A'))
                with col3:
                    st.metric("Industry", info.get('industry', 'N/A'))
            
            st.markdown("---")
            
            # Calculate and display metrics
            metrics = calculate_metrics(df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${metrics['current_price']:.2f}",
                    f"{metrics['change']:+.2f} ({metrics['pct_change']:+.2f}%)"
                )
            
            with col2:
                st.metric(
                    "52 Week High",
                    f"${metrics['high_52w']:.2f}"
                )
            
            with col3:
                st.metric(
                    "52 Week Low",
                    f"${metrics['low_52w']:.2f}"
                )
            
            with col4:
                st.metric(
                    "Avg Volume (30d)",
                    f"{metrics['avg_volume']:,.0f}"
                )
            
            st.markdown("---")
            
            # Historical data chart
            st.subheader("📈 Historical Price Data")
            fig_historical = create_candlestick_chart(df.set_index('Date'))
            st.plotly_chart(fig_historical, use_container_width=True)
            
            st.markdown("---")
            
            # Predictions
            st.subheader("🔮 Price Predictions")
            
            with st.spinner('Generating predictions...'):
                try:
                    model, forecast = predict_stock(
                        df,
                        prediction_days,
                        changepoint_prior_scale,
                        seasonality_prior_scale
                    )
                    
                    # Plot forecast
                    fig_forecast = plot_plotly(model, forecast)
                    fig_forecast.update_layout(
                        title=f'{stock_symbol} Price Forecast ({prediction_days} days)',
                        xaxis_title='Date',
                        yaxis_title='Price (USD)',
                        height=500,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    # Forecast statistics
                    st.markdown("---")
                    st.subheader("📊 Forecast Statistics")
                    
                    future_forecast = forecast.tail(prediction_days)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Predicted Price (End)",
                            f"${future_forecast['yhat'].iloc[-1]:.2f}"
                        )
                    
                    with col2:
                        predicted_change = future_forecast['yhat'].iloc[-1] - metrics['current_price']
                        predicted_pct = (predicted_change / metrics['current_price']) * 100
                        st.metric(
                            "Expected Change",
                            f"{predicted_pct:+.2f}%",
                            f"${predicted_change:+.2f}"
                        )
                    
                    with col3:
                        st.metric(
                            "Upper Bound",
                            f"${future_forecast['yhat_upper'].iloc[-1]:.2f}"
                        )
                    
                    with col4:
                        st.metric(
                            "Lower Bound",
                            f"${future_forecast['yhat_lower'].iloc[-1]:.2f}"
                        )
                    
                    # Forecast components
                    st.markdown("---")
                    st.subheader("📉 Forecast Components")
                    
                    from prophet.plot import plot_components_plotly
                    fig_components = plot_components_plotly(model, forecast)
                    st.plotly_chart(fig_components, use_container_width=True)
                    
                    # Detailed forecast table
                    st.markdown("---")
                    st.subheader("📋 Detailed Forecast")
                    
                    forecast_display = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                    forecast_display.columns = ['Date', 'Predicted Price', 'Lower Bound', 'Upper Bound']
                    forecast_display['Date'] = forecast_display['Date'].dt.date
                    forecast_display = forecast_display.round(2)
                    
                    st.dataframe(
                        forecast_display,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Download button
                    csv = forecast_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Forecast CSV",
                        data=csv,
                        file_name=f"{stock_symbol}_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating predictions: {str(e)}")
                    st.info("Try adjusting the advanced settings or selecting a different date range.")

else:
    # Landing page
    st.info("👈 Enter a stock symbol and click 'Predict Stock Price' to get started!")
    
    st.markdown("""
    ## Welcome to the Stock Prediction App! 🚀
    
    This application uses **Facebook Prophet**, a powerful time series forecasting tool, to predict stock prices.
    
    ### Features:
    - 📊 **Real-time stock data** from Yahoo Finance
    - 📈 **Interactive charts** with historical prices
    - 🔮 **AI-powered predictions** using Prophet
    - 📉 **Detailed analysis** with trend and seasonality components
    - 💾 **Export predictions** to CSV
    
    ### How to use:
    1. Enter a stock symbol (e.g., AAPL, GOOGL, TSLA)
    2. Select the historical data range
    3. Choose how many days to predict
    4. Click "Predict Stock Price"
    
    ### Popular Stocks to Try:
    - **AAPL** - Apple Inc.
    - **GOOGL** - Alphabet Inc.
    - **MSFT** - Microsoft Corporation
    - **TSLA** - Tesla Inc.
    - **AMZN** - Amazon.com Inc.
    - **NVDA** - NVIDIA Corporation
    
    ---
    
    ⚠️ **Disclaimer**: This tool is for educational purposes only. Stock predictions are not financial advice. 
    Always do your own research before making investment decisions.
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        Made with ❤️ using Streamlit | Data from Yahoo Finance | Predictions powered by Prophet
    </div>
    """, unsafe_allow_html=True)
