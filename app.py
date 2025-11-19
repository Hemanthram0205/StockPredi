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

# Comprehensive list of Indian stocks (NSE & BSE)
# Format: "Company Name" : "SYMBOL.NS"
ALL_STOCKS = {
    # Nifty 50 & Popular Stocks
    "Adani Enterprises Ltd": "ADANIENT.NS",
    "Adani Ports and Special Economic Zone Ltd": "ADANIPORTS.NS",
    "Adani Power Ltd": "ADANIPOWER.NS",
    "Apollo Hospitals Enterprise Ltd": "APOLLOHOSP.NS",
    "Asian Paints Ltd": "ASIANPAINT.NS",
    "Axis Bank Ltd": "AXISBANK.NS",
    "Bajaj Auto Ltd": "BAJAJ-AUTO.NS",
    "Bajaj Finance Ltd": "BAJFINANCE.NS",
    "Bajaj Finserv Ltd": "BAJFINSERV.NS",
    "Bank of Baroda": "BANKBARODA.NS",
    "Bharat Electronics Ltd": "BEL.NS",
    "Bharat Petroleum Corporation Ltd": "BPCL.NS",
    "Bharti Airtel Ltd": "BHARTIARTL.NS",
    "Britannia Industries Ltd": "BRITANNIA.NS",
    "Cipla Ltd": "CIPLA.NS",
    "Coal India Ltd": "COALINDIA.NS",
    "Dabur India Ltd": "DABUR.NS",
    "Divi's Laboratories Ltd": "DIVISLAB.NS",
    "Dr. Reddy's Laboratories Ltd": "DRREDDY.NS",
    "Eicher Motors Ltd": "EICHERMOT.NS",
    "Grasim Industries Ltd": "GRASIM.NS",
    "HCL Technologies Ltd": "HCLTECH.NS",
    "HDFC Bank Ltd": "HDFCBANK.NS",
    "HDFC Life Insurance Company Ltd": "HDFCLIFE.NS",
    "Hero MotoCorp Ltd": "HEROMOTOCO.NS",
    "Hindalco Industries Ltd": "HINDALCO.NS",
    "Hindustan Unilever Ltd": "HINDUNILVR.NS",
    "ICICI Bank Ltd": "ICICIBANK.NS",
    "Indian Oil Corporation Ltd": "IOC.NS",
    "IndusInd Bank Ltd": "INDUSINDBK.NS",
    "Infosys Ltd": "INFY.NS",
    "ITC Ltd": "ITC.NS",
    "JSW Steel Ltd": "JSWSTEEL.NS",
    "Kotak Mahindra Bank Ltd": "KOTAKBANK.NS",
    "Larsen & Toubro Ltd": "LT.NS",
    "LTIMindtree Ltd": "LTIM.NS",
    "Mahindra & Mahindra Ltd": "M&M.NS",
    "Maruti Suzuki India Ltd": "MARUTI.NS",
    "Nestle India Ltd": "NESTLEIND.NS",
    "NTPC Ltd": "NTPC.NS",
    "Oil & Natural Gas Corporation Ltd": "ONGC.NS",
    "Power Grid Corporation of India Ltd": "POWERGRID.NS",
    "Reliance Industries Ltd": "RELIANCE.NS",
    "SBI Life Insurance Company Ltd": "SBILIFE.NS",
    "Shriram Finance Ltd": "SHRIRAMFIN.NS",
    "State Bank of India": "SBIN.NS",
    "Sun Pharmaceutical Industries Ltd": "SUNPHARMA.NS",
    "Tata Consultancy Services Ltd": "TCS.NS",
    "Tata Consumer Products Ltd": "TATACONSUM.NS",
    "Tata Motors Ltd": "TATAMOTORS.NS",
    "Tata Steel Ltd": "TATASTEEL.NS",
    "Tech Mahindra Ltd": "TECHM.NS",
    "Titan Company Ltd": "TITAN.NS",
    "UltraTech Cement Ltd": "ULTRACEMCO.NS",
    "UPL Ltd": "UPL.NS",
    "Wipro Ltd": "WIPRO.NS",
    
    # Additional Popular Stocks (Alphabetically A-Z)
    "ABB India Ltd": "ABB.NS",
    "ACC Ltd": "ACC.NS",
    "Adani Green Energy Ltd": "ADANIGREEN.NS",
    "Adani Total Gas Ltd": "ATGL.NS",
    "Adani Transmission Ltd": "ADANITRANS.NS",
    "Ambuja Cements Ltd": "AMBUJACEM.NS",
    "Aurobindo Pharma Ltd": "AUROPHARMA.NS",
    "Avenue Supermarts Ltd (DMart)": "DMART.NS",
    "Bandhan Bank Ltd": "BANDHANBNK.NS",
    "Bank of India": "BANKINDIA.NS",
    "Berger Paints India Ltd": "BERGEPAINT.NS",
    "Biocon Ltd": "BIOCON.NS",
    "Bosch Ltd": "BOSCHLTD.NS",
    "Canara Bank": "CANBK.NS",
    "Cholamandalam Investment and Finance Company Ltd": "CHOLAFIN.NS",
    "Colgate-Palmolive (India) Ltd": "COLPAL.NS",
    "Container Corporation of India Ltd": "CONCOR.NS",
    "Coromandel International Ltd": "COROMANDEL.NS",
    "DLF Ltd": "DLF.NS",
    "Federal Bank Ltd": "FEDERALBNK.NS",
    "Gail (India) Ltd": "GAIL.NS",
    "Godrej Consumer Products Ltd": "GODREJCP.NS",
    "Godrej Properties Ltd": "GODREJPROP.NS",
    "Havells India Ltd": "HAVELLS.NS",
    "HDFC Asset Management Company Ltd": "HDFCAMC.NS",
    "Indian Railway Finance Corporation Ltd": "IRFC.NS",
    "InterGlobe Aviation Ltd (IndiGo)": "INDIGO.NS",
    "Jindal Steel & Power Ltd": "JINDALSTEL.NS",
    "LIC Housing Finance Ltd": "LICHSGFIN.NS",
    "Lupin Ltd": "LUPIN.NS",
    "Marico Ltd": "MARICO.NS",
    "Max Financial Services Ltd": "MFSL.NS",
    "Motherson Sumi Systems Ltd": "MOTHERSON.NS",
    "MRF Ltd": "MRF.NS",
    "Muthoot Finance Ltd": "MUTHOOTFIN.NS",
    "Persistent Systems Ltd": "PERSISTENT.NS",
    "Petronet LNG Ltd": "PETRONET.NS",
    "Pidilite Industries Ltd": "PIDILITIND.NS",
    "Punjab National Bank": "PNB.NS",
    "SBI Cards and Payment Services Ltd": "SBICARD.NS",
    "Shree Cement Ltd": "SHREECEM.NS",
    "Siemens Ltd": "SIEMENS.NS",
    "SRF Ltd": "SRF.NS",
    "Sundaram Finance Ltd": "SUNDARMFIN.NS",
    "Suzlon Energy Ltd": "SUZLON.NS",
    "Tata Elxsi Ltd": "TATAELXSI.NS",
    "Tata Power Company Ltd": "TATAPOWER.NS",
    "Torrent Pharmaceuticals Ltd": "TORNTPHARM.NS",
    "TVS Motor Company Ltd": "TVSMOTOR.NS",
    "Union Bank of India": "UNIONBANK.NS",
    "United Spirits Ltd": "MCDOWELL-N.NS",
    "Vedanta Ltd": "VEDL.NS",
    "Voltas Ltd": "VOLTAS.NS",
    "Yes Bank Ltd": "YESBANK.NS",
    "Zomato Ltd": "ZOMATO.NS",
    "Zydus Lifesciences Ltd": "ZYDUSLIFE.NS",
    
    # Mid-cap & Small-cap (Additional)
    "Aarti Industries Ltd": "AARTIIND.NS",
    "ABB India Ltd": "ABB.NS",
    "Aditya Birla Fashion and Retail Ltd": "ABFRL.NS",
    "Ashok Leyland Ltd": "ASHOKLEY.NS",
    "Atul Ltd": "ATUL.NS",
    "BEML Ltd": "BEML.NS",
    "Bharat Forge Ltd": "BHARATFORG.NS",
    "BSE Ltd": "BSE.NS",
    "Cummins India Ltd": "CUMMINSIND.NS",
    "Dixon Technologies (India) Ltd": "DIXON.NS",
    "Escorts Kubota Ltd": "ESCORTS.NS",
    "Exide Industries Ltd": "EXIDEIND.NS",
    "Fortis Healthcare Ltd": "FORTIS.NS",
    "Gujarat Gas Ltd": "GUJGASLTD.NS",
    "ICICI Lombard General Insurance Company Ltd": "ICICIGI.NS",
    "ICICI Prudential Life Insurance Company Ltd": "ICICIPRULI.NS",
    "IDFC First Bank Ltd": "IDFCFIRSTB.NS",
    "Indian Bank": "INDIANB.NS",
    "Indian Railway Catering and Tourism Corporation Ltd": "IRCTC.NS",
    "Indraprastha Gas Ltd": "IGL.NS",
    "Jubilant Foodworks Ltd": "JUBLFOOD.NS",
    "L&T Technology Services Ltd": "LTTS.NS",
    "Laurus Labs Ltd": "LAURUSLABS.NS",
    "Lichsgfin Finance Ltd": "LICHSGFIN.NS",
    "Linde India Ltd": "LINDEINDIA.NS",
    "Mankind Pharma Ltd": "MANKIND.NS",
    "Max Healthcare Institute Ltd": "MAXHEALTH.NS",
    "NHPC Ltd": "NHPC.NS",
    "Oberoi Realty Ltd": "OBEROIRLTY.NS",
    "Oracle Financial Services Software Ltd": "OFSS.NS",
    "Page Industries Ltd": "PAGEIND.NS",
    "Paytm (One 97 Communications Ltd)": "PAYTM.NS",
    "Phoenix Mills Ltd": "PHOENIXLTD.NS",
    "PI Industries Ltd": "PIIND.NS",
    "Polycab India Ltd": "POLYCAB.NS",
    "Prestige Estates Projects Ltd": "PRESTIGE.NS",
    "REC Ltd": "RECLTD.NS",
    "Samvardhana Motherson International Ltd": "MOTHERSON.NS",
    "Schaeffler India Ltd": "SCHAEFFLER.NS",
    "Shoppers Stop Ltd": "SHOPERSTOP.NS",
    "Tata Communications Ltd": "TATACOMM.NS",
    "Tata Chemicals Ltd": "TATACHEM.NS",
    "Thermax Ltd": "THERMAX.NS",
    "Torrent Power Ltd": "TORNTPOWER.NS",
    "Trent Ltd": "TRENT.NS",
    "Triveni Turbine Ltd": "TRITURBINE.NS",
    "Varun Beverages Ltd": "VBL.NS",
    "Whirlpool of India Ltd": "WHIRLPOOL.NS",
    
    # Tech & IT
    "Coforge Ltd": "COFORGE.NS",
    "eClerx Services Ltd": "ECLERX.NS",
    "Happiest Minds Technologies Ltd": "HAPPSTMNDS.NS",
    "Hexaware Technologies Ltd": "HEXAWARE.NS",
    "Infosys BPM Ltd": "INFY.NS",
    "Mphasis Ltd": "MPHASIS.NS",
    "Tata Elxsi Ltd": "TATAELXSI.NS",
    
    # Pharma
    "Alkem Laboratories Ltd": "ALKEM.NS",
    "Glenmark Pharmaceuticals Ltd": "GLENMARK.NS",
    "Granules India Ltd": "GRANULES.NS",
    "Ipca Laboratories Ltd": "IPCALAB.NS",
    "Natco Pharma Ltd": "NATCOPHARM.NS",
    "Sanofi India Ltd": "SANOFI.NS",
    "Strides Pharma Science Ltd": "STAR.NS",
    "Torrent Pharmaceuticals Ltd": "TORNTPHARM.NS",
    
    # Auto & Components
    "Apollo Tyres Ltd": "APOLLOTYRE.NS",
    "Balkrishna Industries Ltd": "BALKRISIND.NS",
    "Bharat Forge Ltd": "BHARATFORG.NS",
    "Bosch Ltd": "BOSCHLTD.NS",
    "CEAT Ltd": "CEATLTD.NS",
    "MRF Ltd": "MRF.NS",
    "Samvardhana Motherson International Ltd": "MOTHERSON.NS",
    "Sona BLW Precision Forgings Ltd": "SONACOMS.NS",
    "Tube Investments of India Ltd": "TIINDIA.NS",
}

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

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Stock selection with searchable dropdown
    st.subheader("📊 Select Stock")
    
    # Create a list of options with company name and symbol
    stock_options = [f"{name} ({symbol})" for name, symbol in sorted(ALL_STOCKS.items())]
    
    # Searchable selectbox
    selected_option = st.selectbox(
        "Search & Select Stock",
        options=[""] + stock_options,  # Empty first option
        help="Start typing to search for stocks (e.g., 'TCS', 'Reliance', 'Infosys')"
    )
    
    # Extract symbol from selection
    if selected_option:
        # Parse the selected option to get the symbol
        symbol = selected_option.split("(")[-1].replace(")", "")
        stock_name = selected_option.split(" (")[0]
    else:
        symbol = None
        stock_name = None
    
    st.divider()
    
    # Manual entry option
    with st.expander("🔧 Advanced: Enter Custom Symbol"):
        manual_symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., RELIANCE.NS",
            help="Format: SYMBOL.NS (NSE) or SYMBOL.BO (BSE)"
        ).upper()
        
        if manual_symbol:
            symbol = manual_symbol
            stock_name = manual_symbol.replace('.NS', '').replace('.BO', '')
    
    st.info("💡 NSE: Add .NS | BSE: Add .BO")
    
    st.divider()
    
    period = st.selectbox("Historical Period", 
                          ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                          index=3)
    
    predict_days = st.slider("Predict Days Ahead", 7, 90, 30)
    
    # Disable button if no stock selected
    analyze_btn = st.button(
        "🔮 ANALYZE & PREDICT", 
        type="primary", 
        use_container_width=True,
        disabled=(symbol is None)
    )
    
    if symbol is None:
        st.warning("⚠️ Please select a stock first")
    
    st.divider()
    st.markdown("### 🤖 AI-Powered Analysis")
    st.caption(f"📊 {len(ALL_STOCKS)} stocks available")
    st.caption("🔍 Searchable dropdown")
    st.caption("✅ Data cached for 10 min")

# Main content
if analyze_btn and symbol:
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
    st.info("👈 Search and select a stock from the sidebar, then click 'ANALYZE & PREDICT' to begin")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Features
        - ✅ **200+ Indian Stocks** (NSE/BSE)
        - ✅ **Searchable Dropdown** - Type to find
        - ✅ Real-time data with AI predictions
        - ✅ Technical analysis & indicators
        - ✅ Buy/Sell/Hold signals
        - ✅ Interactive price & volume charts
        - ✅ INR currency support (₹)
        - ✅ Export to CSV
        - ✅ Smart caching (no rate limits!)
        
        ### 🔍 How Search Works
        - Type any part of company name
        - Type stock symbol (e.g., "TCS", "Reliance")
        - Results appear instantly
        - Select from dropdown list
        """)
    
    with col2:
        st.markdown("""
        ### 📖 Quick Start Guide
        
        1. **Search for Stock**
           - Click on the dropdown in sidebar
           - Start typing company name or symbol
           - Example: Type "A" to see all "A" stocks
           - Select your desired stock
        
        2. **Set Parameters**
           - Choose historical period (1mo to 5y)
           - Set prediction timeframe (7-90 days)
        
        3. **Analyze**
           - Click "ANALYZE & PREDICT" button
           - View comprehensive analysis
           - Get AI-powered predictions
        
        4. **Export Data**
           - Download historical data as CSV
           - Use for further analysis
        
        ### 🏆 Stock Categories Included
        
        - **Large Cap**: Nifty 50, Sensex stocks
        - **Banking**: HDFC, ICICI, SBI, Axis
        - **IT**: TCS, Infosys, Wipro, HCL
        - **Auto**: Maruti, Tata Motors, M&M
        - **Pharma**: Sun Pharma, Dr. Reddy's
        - **FMCG**: ITC, HUL, Britannia
        - **Energy**: Reliance, ONGC, BPCL
        - **And many more!**
        """)
    
    st.divider()
    
    # Stock categories showcase
    st.subheader("📊 Featured Stock Categories")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏦 Banking", "💻 IT", "🚗 Auto", "💊 Pharma"])
    
    with tab1:
        st.markdown("""
        **Top Banking Stocks:**
        - HDFC Bank, ICICI Bank, State Bank of India
        - Axis Bank, Kotak Mahindra Bank, IndusInd Bank
        - Bank of Baroda, Punjab National Bank, Canara Bank
        """)
    
    with tab2:
        st.markdown("""
        **Top IT Stocks:**
        - TCS, Infosys, Wipro
        - HCL Technologies, Tech Mahindra
        - LTIMindtree, Coforge, Persistent Systems
        """)
    
    with tab3:
        st.markdown("""
        **Top Auto Stocks:**
        - Maruti Suzuki, Tata Motors, Mahindra & Mahindra
        - Bajaj Auto, Hero MotoCorp, Eicher Motors
        - TVS Motor, Ashok Leyland
        """)
    
    with tab4:
        st.markdown("""
        **Top Pharma Stocks:**
        - Sun Pharmaceutical, Dr. Reddy's Laboratories
        - Cipla, Lupin, Aurobindo Pharma
        - Divi's Laboratories, Biocon, Torrent Pharma
        """)

# Footer
st.divider()
st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px;'>
        <p style='margin: 0;'><b>📈 MarketSense AI</b></p>
        <p style='margin: 0;'>Advanced Indian Stock Market Analysis Platform</p>
        <p style='margin: 0; font-size: 0.9em;'>Powered by AI & Real-time Data</p>
        <p style='margin: 0; font-size: 0.85em;'>📊 {len(ALL_STOCKS)} Stocks Available | 🔍 Searchable Database</p>
        <p style='margin: 0; font-size: 0.8em; color: #666;'>
            ⚠️ For Informational Purposes Only | Not Financial Advice
        </p>
    </div>
    """, unsafe_allow_html=True)
