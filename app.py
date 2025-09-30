import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(
    page_title="COVID-19 Data Visualization Assignment",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. डेटा लोडिंग और प्रोसेसिंग (कैशिंग के साथ) ---

@st.cache_data
def load_data(file_path):
    """Loads and preprocesses the COVID-19 dataset."""
    try:
        df = pd.read_csv(file_path)
        # Convert Date to datetime object
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        # यह एरर तब आएगी जब Streamlit Cloud को डेटा फ़ाइल नहीं मिलेगी
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it is in the same directory as app.py in your GitHub repo.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        st.stop()

# सुनिश्चित करें कि यह फ़ाइल app.py के साथ एक ही फ़ोल्डर में है
DATA_FILE = 'covid_19_clean_complete.csv'
df = load_data(DATA_FILE)

# --- डेटा समरी कैलकुलेशन ---
# 1. Confirmed cases के आधार पर Top 10 देशों को ग्रुप करना
top10_story = df.groupby("Country/Region")[["Confirmed", "Deaths", "Recovered"]].max().reset_index().nlargest(10, "Confirmed")
# Melted data for the combined bar chart (from Page 3 of your PDF)
top10_melt = top10_story.melt(id_vars=["Country/Region"], value_vars=["Confirmed", "Recovered", "Deaths"])

# 2. Latest data (for Scatter Plot and Heatmap)
latest = df.groupby("Country/Region")[["Confirmed", "Deaths"]].max().reset_index()

# 3. Global trend over time
cases_over_time = df.groupby("Date")[["Confirmed", "Deaths", "Recovered"]].sum().reset_index()


# --- 3. Streamlit UI/Display शुरू करना ---

st.sidebar.title("Assignment Objectives")
st.sidebar.markdown("""
- **1. Basic Visualizations**
- **2. Misleading Visualization & Fix**
- **3. Storytelling (Global Trends)**
""")

st.title("COVID-19 Data Visualization Assignment")
st.markdown("Name: **Dhruv Singhal** | Dataset: `covid_19_clean_complete.csv`")
st.markdown("---")


# --- A. Basic Visualizations ---
st.header("1. Basic Visualizations")

# 1. Bar plot: Top 10 Countries by Confirmed Cases (Page 1)
st.subheader("1.1 Top 10 Countries by Confirmed Cases")
col1, col2 = st.columns(2)

with col1:
    st.info("Top 10 Countries by Confirmed Cases (Bar Plot)")
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    sns.barplot(x="Confirmed", y="Country/Region", data=top10_story.nlargest(10, 'Confirmed'), color="red", ax=ax_bar)
    ax_bar.set_title("Top 10 Countries by Confirmed Cases (Seaborn)")
    ax_bar.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    st.pyplot(fig_bar)
    plt.close(fig_bar)

# 2. Scatter plot: Confirmed vs Deaths (Page 2)
with col2:
    st.info("Confirmed vs Deaths (Log Scale Scatter Plot)")
    fig_scatter, ax_scatter = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x="Confirmed", y="Deaths", data=latest, alpha=0.6, ax=ax_scatter)
    ax_scatter.set_xscale("log")
    ax_scatter.set_yscale("log")
    ax_scatter.set_title("Confirmed vs Deaths (Log Scale)")
    st.pyplot(fig_scatter)
    plt.close(fig_scatter)


# 3. Heatmap: Correlation between key metrics (Page 2)
st.subheader("1.2 Correlation Heatmap")
fig_heatmap, ax_heatmap = plt.subplots(figsize=(8, 6))
# Only include the two columns used in your PDF's heatmap
sns.heatmap(latest[["Confirmed", "Deaths"]].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax_heatmap)
ax_heatmap.set_title("Correlation Heatmap (Confirmed vs Deaths)")
st.pyplot(fig_heatmap)
plt.close(fig_heatmap)

st.markdown("---")

# --- B. Misleading Visualization Example ---
st.header("2. Misleading Visualization & Corrected Plot")

# Misleading Plot (Page 2-3)
st.subheader("2.1 Misleading Plot: Truncated Y-axis")
col_misleading, col_corrected = st.columns(2)

with col_misleading:
    st.warning("Misleading Plot: Y-axis does NOT start from 0 (Exaggerates differences)")
    fig_misleading, ax_misleading = plt.subplots(figsize=(8, 5))
    sns.barplot(x="Country/Region", y="Confirmed", data=top10_story, color="red", ax=ax_misleading)
    # Truncate Y-axis as shown in your PDF
    ax_misleading.set_ylim(500000, top10_story["Confirmed"].max() * 1.05)
    ax_misleading.set_title("Misleading Plot: Truncated Y-axis")
    ax_misleading.tick_params(axis='x', rotation=45)
    ax_misleading.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    st.pyplot(fig_misleading)
    plt.close(fig_misleading)

# Corrected Plot (Page 3)
with col_corrected:
    st.success("Corrected Plot: Y-axis starts from 0 (Accurate representation)")
    fig_corrected, ax_corrected = plt.subplots(figsize=(8, 5))
    sns.barplot(x="Country/Region", y="Confirmed", data=top10_story, color="red", ax=ax_corrected)
    ax_corrected.set_title("Corrected Plot: Full Y-axis")
    ax_corrected.tick_params(axis='x', rotation=45)
    ax_corrected.set_ylim(0, top10_story["Confirmed"].max() * 1.05) # Ensure Y-axis starts from 0
    ax_corrected.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    st.pyplot(fig_corrected)
    plt.close(fig_corrected)

st.markdown("---")

# --- C. Storytelling with COVID-19 Dataset ---
st.header("3. Storytelling: Global and Top Country Trends")

# 1. Comparing Confirmed, Deaths and Recoveries (Page 3-4)
st.subheader("3.1 COVID-19 Cases, Recoveries & Deaths (Top 10 Countries)")
st.info("Insight: Confirmed cases dominate, with high Recovered counts in top countries.")

fig_story1, ax_story1 = plt.subplots(figsize=(12, 6))
sns.barplot(x="Country/Region", y="value", hue="variable", data=top10_melt, ax=ax_story1)
ax_story1.set_title("COVID-19 Cases, Recoveries & Deaths (Top 10 Countries)")
ax_story1.tick_params(axis='x', rotation=45)
ax_story1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
st.pyplot(fig_story1)
plt.close(fig_story1)


# 2. Global trend over time (Page 4)
st.subheader("3.2 Global Trend Over Time")
st.info("Insight: The trend plot clearly shows an exponential growth in cases after March 2020.")

fig_story2, ax_story2 = plt.subplots(figsize=(12, 6))
ax_story2.plot(cases_over_time["Date"], cases_over_time["Confirmed"], label="Confirmed")
ax_story2.plot(cases_over_time["Date"], cases_over_time["Deaths"], label="Deaths")
ax_story2.plot(cases_over_time["Date"], cases_over_time["Recovered"], label="Recovered")

ax_story2.legend()
ax_story2.set_title("COVID-19 Global Trend Over Time")
ax_story2.set_xlabel("Date")
ax_story2.set_ylabel("Cases")
ax_story2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
st.pyplot(fig_story2)
plt.close(fig_story2)

st.markdown("---")
st.success("App deployment complete! Now upload this app.py, requirements.txt, and your data file to GitHub.")
