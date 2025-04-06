import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🚀 Crypto Intraday Scanner", layout="wide")

st.title("Crypto Intraday Scanner Dashboard")
st.markdown("Get top volatile crypto coins based on 24h movement, volume, and volatility.")

# Filters
st.sidebar.header("🔎 Filters")
min_volume = st.sidebar.slider("Minimum Volume (in million USD)", 1, 100, 10)
min_change = st.sidebar.slider("Minimum 24h Price Change (%)", 1, 50, 3)
min_volatility = st.sidebar.slider("Minimum Volatility (%)", 1, 50, 5)

@st.cache_data(ttl=300)
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'volume_desc',
        'per_page': 100,
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '1h,24h'
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data)

    df = df[['symbol', 'name', 'current_price', 'price_change_percentage_1h_in_currency',
             'price_change_percentage_24h_in_currency', 'total_volume', 'high_24h', 'low_24h']]

    df['volatility_%'] = ((df['high_24h'] - df['low_24h']) / df['current_price']) * 100
    df['total_volume_m'] = df['total_volume'] / 1e6  # in millions

    return df

# Refresh button
if st.button("🔄 Refresh Now"):
    st.cache_data.clear()

df = get_crypto_data()

# Apply filters
filtered = df[
    (df['total_volume_m'] > min_volume) &
    (df['price_change_percentage_24h_in_currency'].abs() > min_change) &
    (df['volatility_%'] > min_volatility)
]

# Show table
st.subheader("📊 Top Movers")
st.dataframe(
    filtered[['symbol', 'name', 'current_price',
              'price_change_percentage_1h_in_currency',
              'price_change_percentage_24h_in_currency',
              'total_volume_m', 'volatility_%']]
    .sort_values(by='volatility_%', ascending=False)
    .head(10)
    .style.format({
        'current_price': '${:,.2f}',
        'price_change_percentage_1h_in_currency': '{:+.2f}%',
        'price_change_percentage_24h_in_currency': '{:+.2f}%',
        'total_volume_m': '{:.2f}M',
        'volatility_%': '{:.2f}%'
    })
)

# Optional: Chart
st.subheader("📈 Volatility Comparison")
if not filtered.empty:
    fig = px.bar(
        filtered.sort_values(by='volatility_%', ascending=False).head(10),
        x='name',
        y='volatility_%',
        color='price_change_percentage_24h_in_currency',
        color_continuous_scale='RdYlGn',
        labels={'volatility_%': 'Volatility (%)', 'name': 'Coin Name'},
        title="Top Volatile Coins"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No coins match your filter criteria.")

