import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="MarketSense AI", page_icon="📈", layout="wide")

# Indian theme CSS
st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        font-weight: bold;
        background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# Cached function to fetch stock data
@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_stock_data(symbol, period):
    """Fetch stock data with caching to avoid rate limits"""
    try:
        time.sleep(1)  # Small delay to be respectful to API
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        info = ticker.info
        return df, info, None
    except Exception as e:
        return None, None, str(e)

st.markdown('<p class="big-font">📈 MarketSense AI</p>', unsafe_allow_html=True)
st.markdown("### Advanced NSE/BSE Stock Analysis & Prediction Platform")

# Popular Indian Stocks
STOCKS = {
    "TCS": "TCS.NS",
    "Reliance Industries": "RELIANCE.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Wipro": "WIPRO.NS",
    "ITC": "ITC.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "HUL": "HINDUNILVR.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "L&T": "LT.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Titan": "TITAN.NS"
}

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    selection_type = st.radio("Select By:", ["Popular Stocks", "Enter Symbol"])
    
    if selection_type == "Popular Stocks":
        stock_name = st.selectbox("Choose Stock", list(STOCKS.keys()))
        symbol = STOCKS[stock_name]
    else:
        manual = st.text_input("Stock Symbol", "RELIANCE.NS").upper()
        symbol = manual
        stock_name = manual.replace('.NS', '').replace('.BO', '')
    
    st.info("💡 NSE: Add .NS | BSE: Add .BO")
    
    st.divider()
    
    period = st.selectbox("Historical Period", 
                          ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                          index=3)
    
    predict_days = st.slider("Predict Days Ahead", 7, 90, 30)
    
    analyze_btn = st.button("🔮 ANALYZE & PREDICT", type="primary", use_container_width=True)
    
    st.divider()
    st.markdown("### 🤖 AI-Powered Analysis")
    st.caption("Real-time market insights")
    st.caption("✅ Data cached for 10 min")

# Main content
if analyze_btn:
    with st.spinner(f"📊 Fetching data for {stock_name}..."):
        # Use cached function
        df, info, error = get_stock_data(symbol, period)
        
        if error:
            st.error(f"❌ Error: {error}")
            st.info("Please check the stock symbol and try again. If you see 'Rate limited', wait 1-2 minutes.")
        elif df is None or df.empty:
            st.error(f"❌ No data found for {symbol}")
            st.info("Check symbol format: NSE stocks use .NS (e.g., TCS.NS)")
        else:
            # Display company info
            st.success(f"✅ Successfully loaded {len(df)} days of data")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Company", info.get('longName', stock_name)[:20])
            with col2:
                st.metric("Sector", info.get('sector', 'N/A')[:15])
            with col3:
                st.metric("Industry", info.get('industry', 'N/A')[:15])
            with col4:
                exchange = "NSE" if ".NS" in symbol else "BSE" if ".BO" in symbol else "N/A"
                st.metric("Exchange", exchange)
            
            st.divider()
            
            # Calculate metrics
            current = df['Close'].iloc[-1]
            previous = df['Close'].iloc[-2]
            change = current - previous
            pct_change = (change / previous) * 100
            
            high_52w = df['High'].max()
            low_52w = df['Low'].min()
            avg_vol = df['Volume'].mean()
            
            # Display current metrics
            st.subheader("📊 Current Metrics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Current Price", 
                         f"₹{current:.2f}",
                         f"{pct_change:+.2f}%",
                         delta_color="normal")
            
            with col2:
                st.metric("Day High", f"₹{df['High'].iloc[-1]:.2f}")
            
            with col3:
                st.metric("Day Low", f"₹{df['Low'].iloc[-1]:.2f}")
            
            with col4:
                st.metric("52W High", f"₹{high_52w:.2f}")
            
            with col5:
                st.metric("52W Low", f"₹{low_52w:.2f}")
            
            st.divider()
            
            # Price chart
            st.subheader("📈 Price History")
            st.line_chart(df['Close'], use_container_width=True)
            
            # Volume chart
            st.subheader("📊 Volume")
            st.bar_chart(df['Volume'], use_container_width=True)
            
            st.divider()
            
            # Simple Moving Averages
            st.subheader("📉 Technical Indicators")
            
            ma_10 = df['Close'].rolling(window=10).mean().iloc[-1]
            ma_50 = df['Close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("10-Day MA", f"₹{ma_10:.2f}")
                if current > ma_10:
                    st.success("✅ Price above 10-day MA (Bullish)")
                else:
                    st.warning("⚠️ Price below 10-day MA (Bearish)")
            
            with col2:
                if ma_50:
                    st.metric("50-Day MA", f"₹{ma_50:.2f}")
                    if current > ma_50:
                        st.success("✅ Price above 50-day MA (Bullish)")
                    else:
                        st.warning("⚠️ Price below 50-day MA (Bearish)")
            
            st.divider()
            
            # Predictions
            st.subheader("🔮 AI Prediction")
            
            # Simple prediction using linear trend
            prices = df['Close'].values
            days = list(range(len(prices)))
            
            # Calculate linear trend
            n = len(days)
            sum_x = sum(days)
            sum_y = sum(prices)
            sum_xy = sum(x * y for x, y in zip(days, prices))
            sum_x2 = sum(x * x for x in days)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict future price
            future_day = len(prices) + predict_days
            predicted_price = slope * future_day + intercept
            
            # Calculate prediction change
            pred_change = predicted_price - current
            pred_pct = (pred_change / current) * 100
            
            # Display prediction
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"Predicted Price ({predict_days}d)", 
                         f"₹{predicted_price:.2f}",
                         f"{pred_pct:+.2f}%",
                         delta_color="normal")
            
            with col2:
                st.metric("Expected Change", 
                         f"₹{pred_change:+.2f}",
                         f"{pred_pct:+.2f}%")
            
            with col3:
                # Calculate confidence based on volatility
                volatility = df['Close'].pct_change().std()
                confidence = max(0, min(100, 100 - (volatility * 1000)))
                st.metric("Confidence", f"{confidence:.0f}%")
            
            st.divider()
            
            # Recommendation
            st.subheader("💡 Investment Recommendation")
            
            if pred_pct > 5:
                st.success(f"""
                ### 🟢 STRONG BUY
                The model predicts a **{pred_pct:.2f}%** increase in {predict_days} days.
                
                **Target Price:** ₹{predicted_price:.2f}  
                **Potential Gain:** ₹{pred_change:.2f} per share
                """)
            elif pred_pct > 0:
                st.info(f"""
                ### 🔵 BUY
                The model predicts a **{pred_pct:.2f}%** increase in {predict_days} days.
                
                **Target Price:** ₹{predicted_price:.2f}  
                **Potential Gain:** ₹{pred_change:.2f} per share
                """)
            elif pred_pct > -5:
                st.warning(f"""
                ### 🟡 HOLD
                The model predicts a **{pred_pct:.2f}%** change in {predict_days} days.
                
                **Target Price:** ₹{predicted_price:.2f}  
                **Expected Change:** ₹{pred_change:.2f} per share
                """)
            else:
                st.error(f"""
                ### 🔴 SELL
                The model predicts a **{pred_pct:.2f}%** decrease in {predict_days} days.
                
                **Target Price:** ₹{predicted_price:.2f}  
                **Potential Loss:** ₹{pred_change:.2f} per share
                """)
            
            st.divider()
            
            # Recent data table
            st.subheader("📋 Recent Trading Data")
            recent_df = df.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            recent_df['Date'] = recent_df.index.strftime('%d-%m-%Y')
            recent_df = recent_df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            recent_df['Open'] = recent_df['Open'].round(2)
            recent_df['High'] = recent_df['High'].round(2)
            recent_df['Low'] = recent_df['Low'].round(2)
            recent_df['Close'] = recent_df['Close'].round(2)
            
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
            
            # Download button
            csv = recent_df.to_csv(index=False)
            st.download_button(
                "📥 Download Data (CSV)",
                csv,
                f"{stock_name}_data.csv",
                "text/csv",
                use_container_width=True
            )

else:
    # Landing page
    st.info("👈 Select a stock from the sidebar and click 'ANALYZE & PREDICT' to begin")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Features
        - ✅ Real-time NSE/BSE data
        - ✅ AI-powered predictions
        - ✅ Technical analysis
        - ✅ Buy/Sell signals
        - ✅ Interactive charts
        - ✅ INR currency (₹)
        - ✅ Export to CSV
        - ✅ Smart caching (no rate limits!)
        
        ### 🏆 Popular Stocks Available
        - **IT**: TCS, Infosys, Wipro
        - **Banking**: HDFC, ICICI, SBI, Axis
        - **Auto**: Maruti, Tata Motors, M&M
        - **FMCG**: ITC, HUL
        - **Energy**: Reliance, Adani
        """)
    
    with col2:
        st.markdown("""
        ### 📖 How to Use
        
        1. **Select Stock**
           - Choose from popular stocks
           - OR enter symbol manually
        
        2. **Set Parameters**
           - Historical period
           - Prediction timeframe
        
        3. **Analyze**
           - Click the predict button
           - View analysis & predictions
        
        4. **Download**
           - Export data as CSV
        
        ### 💡 Stock Symbol Guide
        
        **NSE Format:** `SYMBOL.NS`
        - Example: `TCS.NS`, `RELIANCE.NS`
        
        **BSE Format:** `SYMBOL.BO`
        - Example: `TCS.BO`, `RELIANCE.BO`
        """)
    
    st.divider()
    
    # Quick access buttons
    st.subheader("🔥 Quick Access")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    quick = [("TCS", "TCS.NS"), ("Reliance", "RELIANCE.NS"), 
             ("Infosys", "INFY.NS"), ("HDFC", "HDFCBANK.NS"), 
             ("ITC", "ITC.NS")]
    
    for col, (name, sym) in zip([col1, col2, col3, col4, col5], quick):
        with col:
            if st.button(f"📊 {name}", use_container_width=True):
                st.info(f"Select '{name}' from sidebar and click Analyze")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px;'>
        <p style='margin: 0;'><b>📈 MarketSense AI</b></p>
        <p style='margin: 0;'>Advanced Indian Stock Market Analysis Platform</p>
        <p style='margin: 0; font-size: 0.9em;'>Powered by AI & Real-time Data</p>
        <p style='margin: 0; font-size: 0.8em; color: #666;'>
            ⚠️ For Informational Purposes Only | Not Financial Advice
        </p>
    </div>
    """, unsafe_allow_html=True)
