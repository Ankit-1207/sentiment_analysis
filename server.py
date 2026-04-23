from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os

from fetch_comments import extract_shortcode, fetch_comments
from dl_predict import predict_sentiment
from report_generator import generate_report

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
CORS(app)  # Enable CORS for all domains, specifically useful for our Vite dev server

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    apify_token = data.get('apifyToken')
    username = data.get('username')
    url = data.get('url')

    if not url:
        return jsonify({"error": "Instagram URL is required"}), 400

    shortcode = extract_shortcode(url)
    if not shortcode:
        return jsonify({"error": "Invalid Instagram URL"}), 400

    comments = fetch_comments(url, apify_token=apify_token)

    if len(comments) == 1 and isinstance(comments[0], str) and (comments[0].startswith("Error") or comments[0] == "No comments found by parser."):
        return jsonify({"error": comments[0]}), 400

    positive = 0
    negative = 0
    neutral = 0
    abusive = 0
    
    analyzed_comments = []

    for c_obj in comments:
        # Support fallback in case of legacy string
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

    # Generate PDF Report
    report_filename = None
    if username:
        report_filename = generate_report(username, positive, negative, neutral, decision)

    return jsonify({
        "stats": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "abusive": abusive,
            "total": total,
            "toxicPercentage": round(percent, 2),
            "decision": decision
        },
        "comments": analyzed_comments,
        "reportUrl": f"/api/download/{report_filename}" if report_filename else None
    })

@app.route('/api/download/<filename>')
def download_report(filename):
    try:
        # Prevent path traversal
        filename = os.path.basename(filename)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
