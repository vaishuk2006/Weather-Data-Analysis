
import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Weather Data Analysis",
    page_icon="🌦️",
    layout="wide"
)

# ---------------- CUSTOM DASHBOARD DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071526, #102D49);
    color: #FFFFFF;
}
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3, p, label {
    color: #FFFFFF !important;
}
[data-testid="stMetric"] {
    background: #163B5A;
    border: 1px solid #28658A;
    padding: 18px;
    border-radius: 14px;
}
[data-testid="stMetricLabel"] {
    color: #C7E9FF !important;
}
[data-testid="stMetricValue"] {
    color: #55E6FF !important;
}
[data-testid="stSidebar"] {
    background: #0D2238;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DASHBOARD HEADER ----------------
st.title("🌦️ Weather Data Analysis Dashboard")
st.write(
    "Explore weather patterns, compare cities, "
    "and understand temperature, humidity, rainfall and wind speed."
)

st.markdown("---")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("weather_data.csv")
    data["date"] = pd.to_datetime(data["date"], errors="coerce")

    numeric_columns = [
        "temperature", "humidity", "rainfall", "wind_speed"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["city"] = data["city"].astype("string")
    data = data.dropna(
        subset=[
            "date", "city", "temperature",
            "humidity", "rainfall", "wind_speed"
        ]
    )

    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Cannot find weather_data.csv. "
        "Make sure it is saved in the same folder as app.py."
    )
    st.stop()
except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

if df.empty:
    st.error("The dataset contains no valid weather records.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🔎 Dashboard Filters")

city_options = sorted(df["city"].unique().tolist())

selected_cities = st.sidebar.multiselect(
    "Select cities",
    options=city_options,
    default=city_options
)


min_date = pd.to_datetime("2026-01-01").date()
max_date = pd.to_datetime("2026-12-31").date()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


if not selected_cities:
    st.warning("Select at least one city in the sidebar.")
    st.stop()

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("Please select a start date and an end date.")
    st.stop()

start_date, end_date = selected_dates

filtered = df[
    df["city"].isin(selected_cities)
    & df["date"].dt.date.between(start_date, end_date)
].copy()

if filtered.empty:
    st.warning("No weather records match these filters.")
    st.stop()

# ---------------- SUMMARY CARDS ----------------
st.subheader("📊 Weather Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🌡️ Average Temperature",
    f"{filtered['temperature'].mean():.1f} °C"
)

c2.metric(
    "🌧️ Total Rainfall",
    f"{filtered['rainfall'].sum():.1f} mm"
)

c3.metric(
    "💧 Average Humidity",
    f"{filtered['humidity'].mean():.1f}%"
)

c4.metric(
    "💨 Average Wind Speed",
    f"{filtered['wind_speed'].mean():.1f} km/h"
)

st.markdown("---")

# ---------------- TEMPERATURE CHART ----------------
st.subheader("🌡️ Temperature Trends")

temperature_chart = filtered.pivot_table(
    index="date",
    columns="city",
    values="temperature",
    aggfunc="mean"
)

st.line_chart(temperature_chart)

# ---------------- RAINFALL CHART ----------------
st.subheader("🌧️ Monthly Rainfall Analysis")

rainfall_data = filtered.copy()
rainfall_data["month"] = (
    rainfall_data["date"].dt.to_period("M").astype(str)
)

monthly_rainfall = rainfall_data.pivot_table(
    index="month",
    columns="city",
    values="rainfall",
    aggfunc="sum",
    fill_value=0
)

st.bar_chart(monthly_rainfall)

# ---------------- CITY COMPARISON ----------------
st.markdown("---")
st.subheader("🏙️ Compare Cities")

left, right = st.columns(2)

with left:
    st.write("**Average Humidity (%)**")
    humidity_data = filtered.groupby("city")["humidity"].mean()
    st.bar_chart(humidity_data)

with right:
    st.write("**Average Wind Speed (km/h)**")
    wind_data = filtered.groupby("city")["wind_speed"].mean()
    st.bar_chart(wind_data)

# ---------------- AUTOMATIC INSIGHTS ----------------
st.markdown("---")
st.subheader("💡 Key Weather Insights")

hottest = filtered.loc[filtered["temperature"].idxmax()]
wettest = filtered.loc[filtered["rainfall"].idxmax()]

st.info(
    f"🌡️ Highest temperature: {hottest['temperature']:.1f} °C "
    f"in {hottest['city']} on {hottest['date'].date()}."
)

st.info(
    f"🌧️ Highest rainfall in a single record: "
    f"{wettest['rainfall']:.1f} mm in {wettest['city']} "
    f"on {wettest['date'].date()}."
)

st.success(
    f"💧 Average humidity across the selected records is "
    f"{filtered['humidity'].mean():.1f}%."
)

# ---------------- DATA TABLE ----------------
st.markdown("---")
st.subheader("📋 Weather Records")

st.dataframe(
    filtered.sort_values(["date", "city"]),
    use_container_width=True,
    hide_index=True
)

# ---------------- DOWNLOAD BUTTON ----------------
csv_file = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_file,
    file_name="weather_analysis_results.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(
    "Weather Data Analysis | Built with Python, Pandas and Streamlit"
)
