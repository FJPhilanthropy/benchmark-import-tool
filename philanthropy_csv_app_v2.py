
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Philanthropy CSV Analyzer", layout="wide")

st.title("📈 Philanthropy Benchmark: CSV Upload (Improved Version)")

st.markdown("""
Upload a CSV file of your major gift prospects. This updated version cleans currency fields,
adds scoring diagnostics, and shows trend charts only when valid data is available.
""")
st.markdown("---")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV uploaded successfully!")
    st.write("### Preview of uploaded data:")
    st.dataframe(df.head())

    # --- Define relevant columns ---
    income_cols = [col for col in df.columns if "Donations" in col and "Count" not in col]
    count_cols = [col for col in df.columns if "Donations Count" in col]
    interaction_col = "No. Interactions*"
    events_col = "No Events Attended"

    def clean_currency(series):
        return pd.to_numeric(series.astype(str).str.replace(r"[£,]", "", regex=True).str.strip(), errors="coerce")

    try:
        # Clean and parse income and count columns
        income_data = df[income_cols].apply(clean_currency)
        gift_data = df[count_cols].apply(pd.to_numeric, errors="coerce")

        avg_income = income_data.mean().mean()
        avg_gifts = gift_data.mean().mean()
        avg_interactions = clean_currency(df[interaction_col]) if interaction_col in df.columns else pd.Series(dtype=float)
        avg_interactions = avg_interactions.mean() if not avg_interactions.empty else 0

        avg_events = pd.to_numeric(df[events_col], errors="coerce").mean() if events_col in df.columns else 0
    except Exception as e:
        st.error(f"Data parsing error: {e}")
        st.stop()

    # Display parsed values
    st.markdown("### 🔍 Parsed Metric Averages")
    st.write(f"**Average Income (Cleaned):** £{avg_income:,.2f}")
    st.write(f"**Average Gifts per Year:** {avg_gifts:.2f}")
    st.write(f"**Average Interactions:** {avg_interactions:.2f}")
    st.write(f"**Average Event Attendance:** {avg_events:.2f}")

    # --- Scoring Logic ---
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

    income_score = score_income(avg_income) if pd.notna(avg_income) else 0
    pipeline_score = score_pipeline(avg_gifts, avg_interactions) if pd.notna(avg_gifts) and pd.notna(avg_interactions) else 0
    team_score = score_team(1.0)  # Placeholder
    integration_score = score_integration(avg_events) if pd.notna(avg_events) else 0
    composite_score = round((income_score + pipeline_score + team_score + integration_score) / 4, 1)

    # --- Display Scores ---
    st.subheader("📊 Benchmark Scores")

    def color_box(label, score):
        if pd.isna(score):
            score_text = "N/A"
            color = "#CCCCCC"
        elif score <= 3:
            score_text = f"{score} / 10"
            color = "#FF4B4B"
        elif score < 7:
            score_text = f"{score} / 10"
            color = "#FFA500"
        else:
            score_text = f"{score} / 10"
            color = "#4CAF50"
        st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:8px;margin-bottom:10px;'>"
                    f"<strong>{label}:</strong> {score_text}</div>", unsafe_allow_html=True)

    color_box("Income Performance", income_score)
    color_box("Pipeline Quality", pipeline_score)
    color_box("Team & Systems (Placeholder)", team_score)
    color_box("Strategic Integration", integration_score)
    color_box("Overall Score", composite_score)

    # --- Charts ---
    if income_data.notna().any().any():
        st.subheader("📈 Giving Trends")
        fig1, ax1 = plt.subplots()
        income_data.mean().plot(kind="bar", ax=ax1)
        ax1.set_title("Average Income by Year")
        ax1.set_ylabel("£")
        ax1.set_xticklabels(income_data.columns, rotation=45, ha="right")
        st.pyplot(fig1)

    if gift_data.notna().any().any():
        st.subheader("🎁 Gift Count Trends")
        fig2, ax2 = plt.subplots()
        gift_data.mean().plot(kind="bar", ax=ax2, color="orange")
        ax2.set_title("Average Gift Count by Year")
        ax2.set_ylabel("Gift Count")
        ax2.set_xticklabels(gift_data.columns, rotation=45, ha="right")
        st.pyplot(fig2)

    if "Largest Gift" in df.columns:
        lg = clean_currency(df["Largest Gift"])
        if lg.notna().any():
            st.subheader("💸 Largest Gifts Distribution")
            fig3, ax3 = plt.subplots()
            lg.plot(kind="hist", bins=20, ax=ax3)
            ax3.set_title("Distribution of Largest Gifts")
            ax3.set_xlabel("£")
            st.pyplot(fig3)

else:
    st.info("Awaiting CSV upload. Please upload a file to begin analysis.")
