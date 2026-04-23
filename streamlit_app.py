import streamlit as st
from fetch_comments import extract_shortcode, fetch_comments
from dl_predict import predict_sentiment
from report_generator import generate_report

# Page setup
st.set_page_config(page_title="Instagram Moderation System", layout="centered")

st.title("📸 Instagram Comment Moderation System")
st.markdown("Analyze comments using ML + DL + NLP")

# Inputs
st.markdown("### Authentication (Required to bypass Instagram blocks)")
apify_token = st.text_input("Your Apify API Token (Get one for free at apify.com)", type="password")

st.markdown("### Post Details")
username = st.text_input("Enter Account Owner's Username (for Report)")
url = st.text_input("Enter Instagram Post URL")

# Analyze button
if st.button("Analyze Comments"):

    shortcode = extract_shortcode(url)

    if not shortcode:
        st.error("❌ Invalid Instagram URL. Example: https://www.instagram.com/p/ABC123/")
    else:

        comments = fetch_comments(url, apify_token=apify_token)

        if len(comments) == 1 and (comments[0].startswith("Error") or comments[0] == "No comments found"):
            st.warning(f"⚠️ {comments[0]}")
            st.stop()

        positive = 0
        negative = 0
        neutral = 0
        abusive = 0

        st.subheader("💬 Comment Analysis")

        for comment in comments:

            sentiment = predict_sentiment(comment)

            st.write(f"➡️ {comment}")
            st.write(f"   🔎 Sentiment: {sentiment}")
            st.write("---")

            if sentiment == "positive":
                positive += 1
            elif sentiment == "negative":
                negative += 1
            elif sentiment == "abusive":
                abusive += 1
            else:
                neutral += 1

        # Totals
        total = positive + negative + neutral + abusive
        toxic = negative + abusive

        percent = (toxic / total) * 100 if total > 0 else 0

        # Moderation logic
        if percent < 30:
            decision = "SAFE"
            status_color = "green"
        elif percent <= 60:
            decision = "WARNING"
            status_color = "orange"
        else:
            decision = "BAN"
            status_color = "red"

        # Display Results
        st.subheader("📊 Statistics")

        col1, col2 = st.columns(2)

        col1.metric("Positive", positive)
        col1.metric("Negative", negative)

        col2.metric("Neutral", neutral)
        col2.metric("Abusive", abusive)

        st.markdown(f"### ⚠️ Toxic Percentage: {round(percent,2)}%")

        # Decision
        st.subheader("🚨 Moderation Decision")

        if decision == "SAFE":
            st.success("User Status: SAFE")
        elif decision == "WARNING":
            st.warning("User Status: WARNING")
        else:
            st.error("User Status: ACCOUNT SHOULD BE BANNED")

        # Simple Bar Chart
        st.subheader("📈 Sentiment Distribution")

        st.bar_chart({
            "Positive": positive,
            "Negative": negative,
            "Neutral": neutral,
            "Abusive": abusive
        })

        # Generate PDF Report
        st.subheader("📄 Moderation Report")

        if username:

            file = generate_report(username, total, toxic, percent, decision)

            with open(file, "rb") as f:
                st.download_button(
                    label="Download Report",
                    data=f,
                    file_name=file,
                    mime="application/pdf"
                )

        else:
            st.warning("Enter username to generate report")