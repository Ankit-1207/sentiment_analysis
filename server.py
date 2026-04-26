from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os

from fetch_comments import extract_shortcode, fetch_comments
from dl_predict import predict_sentiment
from report_generator import generate_report

# ---------------- APP SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, "frontend", "dist")

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="")
CORS(app)

# ---------------- SERVE FRONTEND ----------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    full_path = os.path.join(app.static_folder, path)

    if path != "" and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

# ---------------- ANALYZE API ----------------
@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json

    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    apify_token = data.get("apifyToken")
    username = data.get("username")
    url = data.get("url")

    if not url:
        return jsonify({"error": "Instagram URL is required"}), 400

    shortcode = extract_shortcode(url)
    if not shortcode:
        return jsonify({"error": "Invalid Instagram URL"}), 400

    comments = fetch_comments(url, apify_token=apify_token)

    # Handle scraper errors
    if (
        isinstance(comments, list)
        and len(comments) == 1
        and isinstance(comments[0], str)
        and (comments[0].startswith("Error") or "No comments" in comments[0])
    ):
        return jsonify({"error": comments[0]}), 400

    positive = negative = neutral = abusive = 0
    analyzed_comments = []

    for c_obj in comments:
        if isinstance(c_obj, str):
            c_obj = {"text": c_obj, "username": "UnknownUser", "timestamp": ""}

        sentiment = predict_sentiment(c_obj["text"])

        enriched = {**c_obj, "sentiment": sentiment}
        analyzed_comments.append(enriched)

        if sentiment == "positive":
            positive += 1
        elif sentiment == "negative":
            negative += 1
        elif sentiment == "abusive":
            abusive += 1
        else:
            neutral += 1

    total = positive + negative + neutral + abusive
    toxic = negative + abusive
    percent = (toxic / total) * 100 if total > 0 else 0

    if percent < 30:
        decision = "SAFE"
    elif percent <= 60:
        decision = "WARNING"
    else:
        decision = "BAN"

    # ---------------- REPORT ----------------
    report_filename = None
    if username:
        try:
            report_filename = generate_report(
                username, positive, negative, neutral, decision
            )
        except Exception as e:
            print("Report generation error:", e)

    return jsonify(
        {
            "stats": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "abusive": abusive,
                "total": total,
                "toxicPercentage": round(percent, 2),
                "decision": decision,
            },
            "comments": analyzed_comments,
            "reportUrl": f"/api/download/{report_filename}" if report_filename else None,
        }
    )

# ---------------- DOWNLOAD REPORT ----------------
@app.route("/api/download/<filename>")
def download_report(filename):
    try:
        filename = os.path.basename(filename)
        file_path = os.path.join(BASE_DIR, filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- MAIN (IMPORTANT FOR RENDER) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)