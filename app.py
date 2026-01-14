import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="India Air Quality Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/air_quality_india.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    # Fill missing numeric values with mean (to avoid graph issues)
    num_cols = df.select_dtypes('number').columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
    return df

df = load_data()

st.title("🌫️ India Air Quality Visualization Dashboard")
st.markdown("Visualizing Indian Air Quality Data (CPCB style)")

# Sidebar Filters
cities = sorted(df['City'].dropna().unique())
selected_city = st.sidebar.selectbox("Select City", cities)

filtered = df[df['City'] == selected_city]

# AQI approximation (if not present)
# Using PM2.5 as proxy for visualization
if 'AQI' not in df.columns:
    df['AQI'] = df['PM2.5'].apply(lambda x: x * 1.2 if pd.notnull(x) else 0)

# --- 1. PM2.5 Trend ---
st.header(f"📈 PM2.5 Trend in {selected_city}")
fig1 = px.line(filtered, x='Date', y='PM2.5', title=f"PM2.5 Over Time in {selected_city}", template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

# --- 2. Pollutant Distribution ---
st.header(f"🌫️ Pollutant Concentrations in {selected_city}")
pollutants = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'SO2', 'O3', 'CO']
pollutants_in_data = [p for p in pollutants if p in df.columns]

latest = filtered.sort_values('Date').tail(1)[pollutants_in_data].T.reset_index()
latest.columns = ['Pollutant', 'Concentration']
fig2 = px.bar(latest, x='Pollutant', y='Concentration', color='Concentration',
              title=f"Latest Pollutant Levels in {selected_city}",
              color_continuous_scale='YlOrRd', template="plotly_white")
st.plotly_chart(fig2, use_container_width=True)

# --- 3. Yearly Average Trend ---
yearly_avg = df.groupby(['City', 'Year'])[['PM2.5', 'PM10']].mean().reset_index()
fig3 = px.line(yearly_avg[yearly_avg['City'] == selected_city],
               x='Year', y='PM2.5', title=f"Average PM2.5 Over Years in {selected_city}",
               markers=True, template="plotly_white")
st.plotly_chart(fig3, use_container_width=True)

# --- 4. Correlation Heatmap ---
st.header("📊 Pollutant Correlation Matrix")
corr = filtered[pollutants_in_data].corr()
st.dataframe(corr.style.background_gradient(cmap='coolwarm', axis=None))

st.markdown("---")
st.markdown("✅ *Data Source:* Central Pollution Control Board (CPCB), India")

# --- 5. Monthly Average Trend ---
st.header(f"📅 Monthly Average PM2.5 Levels in {selected_city}")
filtered['Month'] = filtered['Date'].dt.month
monthly_avg = filtered.groupby('Month')['PM2.5'].mean().reset_index()
fig4 = px.bar(monthly_avg, x='Month', y='PM2.5',
              title=f"Average PM2.5 by Month in {selected_city}",
              labels={'Month': 'Month (1=Jan, 12=Dec)', 'PM2.5': 'Average PM2.5'},
              color='PM2.5', color_continuous_scale='Plasma',
              template="plotly_white")
st.plotly_chart(fig4, use_container_width=True)

# --- 6. PM2.5 vs PM10 Relationship ---
if 'PM2.5' in df.columns and 'PM10' in df.columns:
    st.header(f"⚖️ PM2.5 vs PM10 Correlation in {selected_city}")
    fig5 = px.scatter(filtered, x='PM10', y='PM2.5',
                      color='Year',
                      title=f"PM2.5 vs PM10 Scatter Plot ({selected_city})",
                      template="plotly_white")
    st.plotly_chart(fig5, use_container_width=True)

# --- 7. Multi-Pollutant Yearly Trend ---
st.header(f"📆 Yearly Trends of Major Pollutants in {selected_city}")
pollutants_for_trend = [p for p in ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3'] if p in df.columns]
yearly_multi = df.groupby(['City', 'Year'])[pollutants_for_trend].mean().reset_index()
fig6 = px.line(yearly_multi[yearly_multi['City'] == selected_city],
               x='Year', y=pollutants_for_trend,
               title=f"Yearly Pollutant Trends in {selected_city}",
               markers=True, template="plotly_white")
st.plotly_chart(fig6, use_container_width=True)

# --- 8. AQI Distribution ---
st.header(f"🏙️ AQI Distribution in {selected_city}")
fig7 = px.histogram(filtered, x='AQI', nbins=30,
                    title=f"Distribution of AQI in {selected_city}",
                    template="plotly_white", color_discrete_sequence=['teal'])
st.plotly_chart(fig7, use_container_width=True)

# --- 9. Top 10 Most Polluted Cities (PM2.5 Average) ---
st.header("🔥 Top 10 Most Polluted Cities (Based on PM2.5)")
top_cities = df.groupby('City')['PM2.5'].mean().sort_values(ascending=False).head(10).reset_index()
fig8 = px.bar(top_cities, x='City', y='PM2.5', color='PM2.5',
              title="Top 10 Polluted Cities (Average PM2.5)",
              color_continuous_scale='Reds', template="plotly_white")
st.plotly_chart(fig8, use_container_width=True)
