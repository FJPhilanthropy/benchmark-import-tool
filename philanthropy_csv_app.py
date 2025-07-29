
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Philanthropy CSV Analyzer", layout="wide")

st.title("📈 Philanthropy Benchmark: CSV Upload Version")

st.markdown("""
Upload a CSV file of your major gift prospects to automatically analyze giving trends and calculate a high-level benchmark score.
This tool works with structured data across multiple financial years (e.g., income and gift counts per year).
""")
st.markdown("---")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully!")
    st.write("### Preview of uploaded data:")
    st.dataframe(df.head())

    # --- Extract numeric data from relevant year columns ---
    income_cols = [col for col in df.columns if "Donations" in col and "Count" not in col]
    count_cols = [col for col in df.columns if "Donations Count" in col]
    interaction_col = "No. Interactions*"
    events_col = "No Events Attended"

    # Safely calculate averages
    try:
        avg_income = df[income_cols].replace(",", "", regex=True).apply(pd.to_numeric, errors='coerce').mean().mean()
        avg_gifts = df[count_cols].apply(pd.to_numeric, errors='coerce').mean().mean()
        avg_interactions = df[interaction_col].apply(pd.to_numeric, errors='coerce').mean() if interaction_col in df.columns else 0
        avg_events = df[events_col].apply(pd.to_numeric, errors='coerce').mean() if events_col in df.columns else 0
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.stop()

    # --- Scoring Logic (same as before) ---
    def score_income(val):
        return min(round((val / 1_000_000) * 2, 1), 10)

    def score_pipeline(gifts, asks):
        if asks == 0:
            return 0
        elif gifts > asks:
            return round((asks / gifts) * 8, 1)
        else:
            return round((gifts / asks) * 10, 1)

    def score_team(fte):
        return min(round(fte * 2, 1), 10)

    def score_integration(events):
        return min(round(events / 2, 1), 10)

    # Use interactions as proxy for asks
    income_score = score_income(avg_income)
    pipeline_score = score_pipeline(avg_gifts, avg_interactions)
    team_score = score_team(1.0)  # Placeholder: not in file
    integration_score = score_integration(avg_events)
    composite_score = round((income_score + pipeline_score + team_score + integration_score) / 4, 1)

    # --- Display Scores ---
    st.subheader("📊 Benchmark Scores")

    def color_box(label, score):
        if score <= 3:
            color = "#FF4B4B"
        elif score < 7:
            color = "#FFA500"
        else:
            color = "#4CAF50"
        st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:8px;margin-bottom:10px;'>"
                    f"<strong>{label}:</strong> {score} / 10</div>", unsafe_allow_html=True)

    color_box("Income Performance", income_score)
    color_box("Pipeline Quality", pipeline_score)
    color_box("Team & Systems (Placeholder)", team_score)
    color_box("Strategic Integration", integration_score)
    st.markdown("### 🧮 Composite Score")
    color_box("Overall Score", composite_score)

    # --- Charts ---
    st.subheader("📈 Giving Trends")
    fig1, ax1 = plt.subplots()
    df[income_cols].replace(",", "", regex=True).apply(pd.to_numeric, errors='coerce').mean().plot(kind='bar', ax=ax1)
    ax1.set_title("Average Income by Year")
    ax1.set_ylabel("£")
    ax1.set_xticklabels(income_cols, rotation=45, ha="right")
    st.pyplot(fig1)

    st.subheader("🎁 Gift Count Trends")
    fig2, ax2 = plt.subplots()
    df[count_cols].apply(pd.to_numeric, errors='coerce').mean().plot(kind='bar', ax=ax2, color="orange")
    ax2.set_title("Average Gift Count by Year")
    ax2.set_ylabel("Gift Count")
    ax2.set_xticklabels(count_cols, rotation=45, ha="right")
    st.pyplot(fig2)

    if "Largest Gift" in df.columns:
        st.subheader("💸 Largest Gifts Distribution")
        fig3, ax3 = plt.subplots()
        df["Largest Gift"].replace(",", "", regex=True).apply(pd.to_numeric, errors='coerce').plot(kind="hist", bins=20, ax=ax3)
        ax3.set_title("Distribution of Largest Gifts")
        ax3.set_xlabel("£")
        st.pyplot(fig3)

else:
    st.info("Awaiting CSV upload. Please upload a file to begin analysis.")
