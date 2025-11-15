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
    page_title="Indian Stock Prediction App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Indian theme
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    h1 {
        color: #FF9933;
        padding-bottom: 1rem;
    }
    h2 {
        color: #138808;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stock-header {
        background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Indian Stock Symbols Dictionary
POPULAR_STOCKS = {
    "TCS": "TCS.NS",
    "Reliance": "RELIANCE.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Wipro": "WIPRO.NS",
    "ITC": "ITC.NS",
    "SBI": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "HUL": "HINDUNILVR.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Kotak Bank": "KOTAKBANK.NS",
    "L&T": "LT.NS",
    "M&M": "M&M.NS",
    "Titan": "TITAN.NS",
    "Coal India": "COALINDIA.NS",
    "NTPC": "NTPC.NS",
    "Power Grid": "POWERGRID.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Dr Reddy's": "DRREDDY.NS",
    "Tech Mahindra": "TECHM.NS",
    "UltraTech": "ULTRACEMCO.NS",
    "Nestle India": "NESTLEIND.NS",
    "HCL Tech": "HCLTECH.NS",
    "JSW Steel": "JSWSTEEL.NS"
}

# Title with Indian flag colors
st.markdown("""
    <div class='stock-header' style='text-align: center;'>
        <h1 style='color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
            🇮🇳 Indian Stock Market Prediction App
        </h1>
        <p style='color: white; margin-top: 0.5rem; font-size: 1.2rem;'>NSE/BSE Stock Analysis & Forecasting</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Stock selection method
    selection_method = st.radio(
        "Select Stock By:",
        ["Popular Stocks", "Enter Symbol Manually"],
        help="Choose from popular Indian stocks or enter a symbol manually"
    )
    
    if selection_method == "Popular Stocks":
        stock_name = st.selectbox(
            "Select Stock",
            options=list(POPULAR_STOCKS.keys()),
            help="Choose from popular NSE stocks"
        )
        stock_symbol = POPULAR_STOCKS[stock_name]
        display_name = stock_name
    else:
        manual_symbol = st.text_input(
            "Enter Stock Symbol",
            value="RELIANCE.NS",
            help="Enter NSE symbol with .NS (e.g., TCS.NS) or BSE symbol with .BO (e.g., TCS.BO)"
        ).upper()
        stock_symbol = manual_symbol
        display_name = manual_symbol.replace('.NS', '').replace('.BO', '')
    
    st.info("💡 **NSE stocks**: Add .NS (e.g., TCS.NS)\n\n**BSE stocks**: Add .BO (e.g., TCS.BO)")
    
    # Date range
    st.subheader("📅 Historical Data Range")
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
    st.subheader("🔮 Prediction Settings")
    prediction_days = st.slider(
        "Days to Predict",
        min_value=7,
        max_value=365,
        value=30,
        step=7,
        help="Number of days to predict into the future"
    )
    
    # Model parameters
    with st.expander("⚡ Advanced Settings"):
        changepoint_prior_scale = st.slider(
            "Changepoint Prior Scale",
            0.001, 0.5, 0.05,
            help="Flexibility of trend changes (higher = more flexible)"
        )
        seasonality_prior_scale = st.slider(
            "Seasonality Prior Scale",
            0.01, 10.0, 10.0,
            help="Strength of seasonality component"
        )
        include_market_days = st.checkbox(
            "Trading Days Only",
            value=True,
            help="Predict only for market trading days"
        )
    
    predict_button = st.button("🔮 Predict Stock Price", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📚 University Project")
    st.markdown("**Indian Stock Market Analysis**")
    st.markdown("*Using AI & Machine Learning*")

# Helper Functions
@st.cache_data(ttl=3600)
def load_stock_data(symbol, start, end):
    """Load stock data from Yahoo Finance for Indian stocks"""
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

def format_inr(amount):
    """Format number in Indian currency style"""
    s = str(int(amount))
    if len(s) <= 3:
        return f"₹{s}"
    
    # Indian numbering system
    result = s[-3:]
    s = s[:-3]
    while s:
        if len(s) <= 2:
            result = s + ',' + result
            break
        result = s[-2:] + ',' + result
        s = s[:-2]
    
    return f"₹{result}"

def format_inr_decimal(amount):
    """Format decimal number in Indian currency"""
    integer_part = int(amount)
    decimal_part = amount - integer_part
    formatted_integer = format_inr(integer_part)
    return f"{formatted_integer}.{decimal_part:.2f}"[:-3] + f"{amount:.2f}"[-3:]

def calculate_metrics(df):
    """Calculate stock metrics"""
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    change = current_price - prev_price
    pct_change = (change / prev_price) * 100
    
    high_52w = df['High'].tail(252).max()
    low_52w = df['Low'].tail(252).min()
    avg_volume = df['Volume'].tail(30).mean()
    
    # Calculate moving averages
    ma_50 = df['Close'].tail(50).mean()
    ma_200 = df['Close'].tail(200).mean() if len(df) >= 200 else None
    
    return {
        'current_price': current_price,
        'change': change,
        'pct_change': pct_change,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'avg_volume': avg_volume,
        'ma_50': ma_50,
        'ma_200': ma_200
    }

def create_candlestick_chart(df, symbol_name):
    """Create candlestick chart with volume and moving averages"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol_name} Price Chart', 'Volume')
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color='#138808',
            decreasing_line_color='#FF0000'
        ),
        row=1, col=1
    )
    
    # Add 50-day MA
    if len(df) >= 50:
        ma_50 = df['Close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=ma_50,
                name='MA 50',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    # Add 200-day MA
    if len(df) >= 200:
        ma_200 = df['Close'].rolling(window=200).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=ma_200,
                name='MA 200',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
    
    # Volume bars
    colors = ['#FF0000' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#138808' 
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
        title=f'{symbol_name} Stock Price Analysis',
        yaxis_title='Price (INR ₹)',
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
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True
    )
    
    # Add Indian market holidays (you can expand this list)
    indian_holidays = pd.DataFrame({
        'holiday': 'indian_market_holiday',
        'ds': pd.to_datetime([
            '2024-01-26',  # Republic Day
            '2024-03-08',  # Maha Shivratri
            '2024-03-25',  # Holi
            '2024-03-29',  # Good Friday
            '2024-04-11',  # Id-Ul-Fitr
            '2024-04-17',  # Ram Navami
            '2024-04-21',  # Mahavir Jayanti
            '2024-05-01',  # Maharashtra Day
            '2024-06-17',  # Bakri Id
            '2024-07-17',  # Muharram
            '2024-08-15',  # Independence Day
            '2024-08-26',  # Janmashtami
            '2024-10-02',  # Gandhi Jayanti
            '2024-10-12',  # Dussehra
            '2024-11-01',  # Diwali
            '2024-11-15',  # Gurunanak Jayanti
            '2024-12-25',  # Christmas
        ]),
        'lower_window': 0,
        'upper_window': 0,
    })
    
    model = Prophet(
        holidays=indian_holidays,
        changepoint_prior_scale=changepoint_scale,
        seasonality_prior_scale=seasonality_scale,
        daily_seasonality=False,
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
    with st.spinner(f'📊 Loading data for {display_name}...'):
        # Load data
        df, info = load_stock_data(stock_symbol, start_date, end_date)
        
        if df is None or df.empty:
            st.error(f"❌ Could not load data for {stock_symbol}. Please check the symbol and try again.")
            st.info("💡 Make sure to add .NS for NSE stocks or .BO for BSE stocks")
        else:
            # Reset index to have Date as a column
            df = df.reset_index()
            
            # Company Information Header
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("### 🏢 Company")
                company_name = info.get('longName', display_name) if info else display_name
                st.markdown(f"**{company_name}**")
            
            with col2:
                st.markdown("### 📍 Exchange")
                exchange = "NSE" if ".NS" in stock_symbol else "BSE" if ".BO" in stock_symbol else "N/A"
                st.markdown(f"**{exchange}**")
            
            with col3:
                st.markdown("### 🏭 Sector")
                sector = info.get('sector', 'N/A') if info else 'N/A'
                st.markdown(f"**{sector}**")
            
            with col4:
                st.markdown("### 🏢 Industry")
                industry = info.get('industry', 'N/A') if info else 'N/A'
                st.markdown(f"**{industry}**")
            
            st.markdown("---")
            
            # Calculate and display metrics
            metrics = calculate_metrics(df)
            
            st.subheader("📊 Key Metrics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"₹{metrics['current_price']:.2f}",
                    f"{metrics['change']:+.2f} ({metrics['pct_change']:+.2f}%)",
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    "52 Week High",
                    f"₹{metrics['high_52w']:.2f}"
                )
            
            with col3:
                st.metric(
                    "52 Week Low",
                    f"₹{metrics['low_52w']:.2f}"
                )
            
            with col4:
                st.metric(
                    "50 Day MA",
                    f"₹{metrics['ma_50']:.2f}"
                )
            
            with col5:
                volume_lakhs = metrics['avg_volume'] / 100000
                st.metric(
                    "Avg Volume (30d)",
                    f"{volume_lakhs:.2f}L"
                )
            
            st.markdown("---")
            
            # Historical data chart
            st.subheader("📈 Historical Price Analysis")
            fig_historical = create_candlestick_chart(df.set_index('Date'), display_name)
            st.plotly_chart(fig_historical, use_container_width=True)
            
            # Technical Analysis
            st.markdown("---")
            st.subheader("📊 Technical Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price vs Moving Averages
                current = metrics['current_price']
                ma50 = metrics['ma_50']
                
                if current > ma50:
                    st.success(f"✅ Price is **above** 50-day MA (₹{ma50:.2f}) - **Bullish Signal**")
                else:
                    st.warning(f"⚠️ Price is **below** 50-day MA (₹{ma50:.2f}) - **Bearish Signal**")
            
            with col2:
                # 52-week range
                week_52_range = ((current - metrics['low_52w']) / (metrics['high_52w'] - metrics['low_52w'])) * 100
                st.info(f"📍 Stock is at **{week_52_range:.1f}%** of its 52-week range")
            
            st.markdown("---")
            
            # Predictions
            st.subheader("🔮 AI-Powered Price Predictions")
            
            with st.spinner('🤖 Generating predictions using Machine Learning...'):
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
                        title=f'{display_name} - {prediction_days} Days Price Forecast',
                        xaxis_title='Date',
                        yaxis_title='Price (INR ₹)',
                        height=500,
                        template='plotly_white'
                    )
                    
                    # Update colors to match Indian theme
                    fig_forecast.update_traces(
                        marker=dict(color='#FF9933'),
                        selector=dict(mode='markers')
                    )
                    
                    st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    # Forecast statistics
                    st.markdown("---")
                    st.subheader("📊 Prediction Summary")
                    
                    future_forecast = forecast[forecast['ds'] > df['Date'].max()].head(prediction_days)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        predicted_price = future_forecast['yhat'].iloc[-1]
                        st.metric(
                            "Predicted Price",
                            f"₹{predicted_price:.2f}",
                            help=f"Predicted price after {prediction_days} days"
                        )
                    
                    with col2:
                        predicted_change = predicted_price - metrics['current_price']
                        predicted_pct = (predicted_change / metrics['current_price']) * 100
                        st.metric(
                            "Expected Change",
                            f"{predicted_pct:+.2f}%",
                            f"₹{predicted_change:+.2f}",
                            delta_color="normal"
                        )
                    
                    with col3:
                        upper_bound = future_forecast['yhat_upper'].iloc[-1]
                        st.metric(
                            "Upper Bound",
                            f"₹{upper_bound:.2f}",
                            help="95% confidence upper limit"
                        )
                    
                    with col4:
                        lower_bound = future_forecast['yhat_lower'].iloc[-1]
                        st.metric(
                            "Lower Bound",
                            f"₹{lower_bound:.2f}",
                            help="95% confidence lower limit"
                        )
                    
                    # Investment Recommendation
                    st.markdown("---")
                    st.subheader("💡 AI Recommendation")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if predicted_pct > 5:
                            st.success(f"""
                            ### 🟢 STRONG BUY Signal
                            - Predicted growth: **{predicted_pct:.2f}%**
                            - Expected return: **₹{predicted_change:.2f}** per share
                            - Confidence interval: ₹{lower_bound:.2f} - ₹{upper_bound:.2f}
                            """)
                        elif predicted_pct > 0:
                            st.info(f"""
                            ### 🔵 BUY Signal
                            - Predicted growth: **{predicted_pct:.2f}%**
                            - Expected return: **₹{predicted_change:.2f}** per share
                            - Confidence interval: ₹{lower_bound:.2f} - ₹{upper_bound:.2f}
                            """)
                        elif predicted_pct > -5:
                            st.warning(f"""
                            ### 🟡 HOLD Signal
                            - Predicted change: **{predicted_pct:.2f}%**
                            - Expected change: **₹{predicted_change:.2f}** per share
                            - Confidence interval: ₹{lower_bound:.2f} - ₹{upper_bound:.2f}
                            """)
                        else:
                            st.error(f"""
                            ### 🔴 SELL Signal
                            - Predicted decline: **{predicted_pct:.2f}%**
                            - Expected loss: **₹{predicted_change:.2f}** per share
                            - Confidence interval: ₹{lower_bound:.2f} - ₹{upper_bound:.2f}
                            """)
                    
                    with col2:
                        # Risk meter
                        uncertainty = upper_bound - lower_bound
                        risk_pct = (uncertainty / predicted_price) * 100
                        
                        st.metric("Risk Level", f"{risk_pct:.1f}%")
                        
                        if risk_pct < 10:
                            st.success("Low Risk ✅")
                        elif risk_pct < 20:
                            st.info("Medium Risk ⚠️")
                        else:
                            st.warning("High Risk ⚡")
                    
                    # Forecast components
                    st.markdown("---")
                    st.subheader("📉 Trend & Seasonality Analysis")
                    
                    from prophet.plot import plot_components_plotly
                    fig_components = plot_components_plotly(model, forecast)
                    st.plotly_chart(fig_components, use_container_width=True)
                    
                    # Detailed forecast table
                    st.markdown("---")
                    st.subheader("📋 Detailed Daily Predictions")
                    
                    forecast_display = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                    forecast_display.columns = ['Date', 'Predicted Price (₹)', 'Lower Bound (₹)', 'Upper Bound (₹)']
                    forecast_display['Date'] = pd.to_datetime(forecast_display['Date']).dt.strftime('%d-%m-%Y')
                    forecast_display['Predicted Price (₹)'] = forecast_display['Predicted Price (₹)'].round(2)
                    forecast_display['Lower Bound (₹)'] = forecast_display['Lower Bound (₹)'].round(2)
                    forecast_display['Upper Bound (₹)'] = forecast_display['Upper Bound (₹)'].round(2)
                    
                    # Add day-wise change
                    forecast_display['Change (₹)'] = forecast_display['Predicted Price (₹)'].diff().round(2)
                    forecast_display['Change (%)'] = (forecast_display['Change (₹)'] / forecast_display['Predicted Price (₹)'].shift(1) * 100).round(2)
                    
                    st.dataframe(
                        forecast_display,
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                    
                    # Download buttons
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        csv = forecast_display.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Predictions (CSV)",
                            data=csv,
                            file_name=f"{display_name}_forecast_{datetime.now().strftime('%d%m%Y')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Download historical data
                        hist_csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Historical Data",
                            data=hist_csv,
                            file_name=f"{display_name}_historical_{datetime.now().strftime('%d%m%Y')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Create analysis report
                        report = f"""
STOCK ANALYSIS REPORT
{'='*50}
Stock: {company_name}
Symbol: {stock_symbol}
Exchange: {exchange}
Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}

CURRENT METRICS
{'='*50}
Current Price: ₹{metrics['current_price']:.2f}
Daily Change: ₹{metrics['change']:.2f} ({metrics['pct_change']:.2f}%)
52 Week High: ₹{metrics['high_52w']:.2f}
52 Week Low: ₹{metrics['low_52w']:.2f}
50 Day MA: ₹{metrics['ma_50']:.2f}

PREDICTION ({prediction_days} days)
{'='*50}
Predicted Price: ₹{predicted_price:.2f}
Expected Change: ₹{predicted_change:.2f} ({predicted_pct:.2f}%)
Upper Bound: ₹{upper_bound:.2f}
Lower Bound: ₹{lower_bound:.2f}
Risk Level: {risk_pct:.1f}%

RECOMMENDATION
{'='*50}
{'STRONG BUY' if predicted_pct > 5 else 'BUY' if predicted_pct > 0 else 'HOLD' if predicted_pct > -5 else 'SELL'}

Disclaimer: This is an AI-generated prediction for educational purposes only.
Not financial advice. Please do your own research before investing.

Generated by Indian Stock Prediction App
University Project
"""
                        st.download_button(
                            label="📄 Download Analysis Report",
                            data=report,
                            file_name=f"{display_name}_report_{datetime.now().strftime('%d%m%Y')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error generating predictions: {str(e)}")
                    st.info("💡 Try adjusting the advanced settings or selecting a different date range.")

else:
    # Landing page
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%); 
                padding: 2rem; border-radius: 1rem; margin: 2rem 0;'>
        <h2 style='color: white; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
            Welcome to Indian Stock Market Analysis & Prediction System! 🚀
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ## 🎯 Features
        
        - 📊 **Real-time NSE/BSE Data** from Yahoo Finance
        - 📈 **Interactive Charts** with candlesticks and volume
        - 🤖 **AI-Powered Predictions** using Facebook Prophet
        - 📉 **Technical Analysis** with moving averages
        - 💡 **Investment Recommendations** based on predictions
        - 💾 **Export Data** to CSV and generate reports
        - 🇮🇳 **Indian Currency** (₹ INR) formatting
        - 📅 **Indian Market Holidays** consideration
        
        ## 🏆 Top Indian Stocks
        
        ### IT Sector
        - **TCS** - Tata Consultancy Services
        - **Infosys** - Infosys Limited
        - **Wipro** - Wipro Limited
        - **HCL Tech** - HCL Technologies
        - **Tech Mahindra** - Tech Mahindra Ltd
        
        ### Banking & Finance
        - **HDFC Bank** - HDFC Bank Limited
        - **ICICI Bank** - ICICI Bank Limited
        - **SBI** - State Bank of India
        - **Axis Bank** - Axis Bank Limited
        - **Kotak Bank** - Kotak Mahindra Bank
        """)
    
    with col2:
        st.markdown("""
        ## 📖 How to Use
        
        1. **Select a Stock**
           - Choose from popular stocks OR
           - Enter symbol manually (e.g., RELIANCE.NS)
        
        2. **Set Date Range**
           - Choose historical data period
           - More data = better predictions
        
        3. **Configure Prediction**
           - Select prediction period (7-365 days)
           - Adjust advanced settings if needed
        
        4. **Click "Predict Stock Price"**
           - View comprehensive analysis
           - Get AI-powered recommendations
           - Download reports and data
        
        ## 💡 Stock Symbol Format
        
        - **NSE Stocks**: Add `.NS` suffix
          - Example: `TCS.NS`, `RELIANCE.NS`
        
        - **BSE Stocks**: Add `.BO` suffix
          - Example: `TCS.BO`, `RELIANCE.BO`
        
        ## 📚 University Project Details
        
        **Project Title:** AI-Based Indian Stock Market Prediction System
        
        **Technologies Used:**
        - Python & Streamlit (Frontend)
        - Facebook Prophet (ML Model)
        - Yahoo Finance API (Data Source)
        - Plotly (Visualization)
        
        **Features Implemented:**
        - Time series forecasting
        - Technical analysis
        - Risk assessment
        - Indian market customization
        """)
    
    st.markdown("---")
    
    # Popular stocks quick access
    st.subheader("🔥 Quick Access - Popular Stocks")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    quick_stocks = [
        ("Reliance", "RELIANCE.NS"),
        ("TCS", "TCS.NS"),
        ("Infosys", "INFY.NS"),
        ("HDFC Bank", "HDFCBANK.NS"),
        ("ITC", "ITC.NS")
    ]
    
    for idx, (col, (name, symbol)) in enumerate(zip([col1, col2, col3, col4, col5], quick_stocks)):
        with col:
            if st.button(f"📊 {name}", use_container_width=True, key=f"quick_{idx}"):
                st.info(f"Select '{name}' from sidebar and click 'Predict Stock Price'")
    
    st.markdown("---")
    
    # Disclaimer
    st.warning("""
    ⚠️ **Important Disclaimer**
    
    This application is developed for **educational and academic purposes only** as part of a university project.
    
    - Stock market predictions are based on historical data and AI algorithms
    - Past performance does not guarantee future results
    - This is **NOT financial advice**
    - Always consult with a qualified financial advisor before making investment decisions
    - The developers are not responsible for any financial losses incurred
    
    **Please do your own research and invest responsibly!**
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;'>
        <p style='margin: 0.5rem 0;'><b>🎓 University Project - Indian Stock Market Prediction System</b></p>
        <p style='margin: 0.5rem 0;'>Made with ❤️ using Streamlit | Data from Yahoo Finance | Predictions by Facebook Prophet</p>
        <p style='margin: 0.5rem 0;'>🇮🇳 Customized for NSE/BSE with INR Currency</p>
        <p style='margin: 0.5rem 0; font-size: 0.8rem;'>For Educational Purposes Only | Not Financial Advice</p>
    </div>
    """, unsafe_allow_html=True)
