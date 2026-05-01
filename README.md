# Sentiment Analysis

Instagram comment moderation app that fetches comments from an Instagram post, analyzes sentiment, calculates toxicity, and shows a moderation decision.

## Features

- Fetch Instagram comments with Apify
- Classify comments as positive, negative, neutral, or abusive
- Show moderation stats and toxicity percentage
- Generate downloadable PDF moderation reports
- React dashboard served by Flask
- Optional Streamlit and desktop app entry points

## Project Structure

```text
.
├── server.py                 # Flask API and production frontend server
├── fetch_comments.py         # Instagram comment fetching through Apify
├── dl_predict.py             # Sentiment prediction wrapper
├── dl_model.py               # Keras model loading and prediction
├── train_model.py            # Model training script
├── report_generator.py       # PDF report generation
├── streamlit_app.py          # Streamlit UI
├── desktop_app.py            # PyWebView desktop wrapper
├── sentimentdataset.csv      # Training dataset
├── sentiment_dl_model.h5     # Trained sentiment model
├── tokenizer.pkl             # Saved tokenizer
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker deployment config
└── frontend/                 # React + Vite frontend
```

## Requirements

- Python 3.10+
- Node.js 18+ and npm
- Apify API token

Create a free Apify account, then copy your API token from Apify settings. The app asks for this token when analyzing comments.

## Python Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you plan to retrain or run the deep learning model locally, you may also need:

```bash
pip install tensorflow pandas numpy streamlit pywebview
```

## Run the Flask App

The Flask app serves the production React build from `frontend/dist`.

```bash
python server.py
```

Open:

```text
http://127.0.0.1:5000
```

API endpoint:

```text
POST /api/analyze
```

Example JSON body:

```json
{
  "apifyToken": "YOUR_APIFY_TOKEN",
  "username": "account_username",
  "url": "https://www.instagram.com/p/POST_SHORTCODE/"
}
```

## Run the React Frontend in Development

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually:

```text
http://localhost:5173
```

Build the frontend for production:

```bash
cd frontend
npm run build
```

Then run the Flask server again:

```bash
cd ..
python server.py
```

## Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

Open the local Streamlit URL shown in the terminal.

## Run the Desktop App

Install PyWebView first if needed:

```bash
pip install pywebview
```

Run:

```bash
python desktop_app.py
```

## Train the Model

The training script reads `sentimentdataset.csv` and writes `sentiment_dl_model.h5` and `tokenizer.pkl`.

```bash
python train_model.py
```

## Docker

Build the image:

```bash
docker build -t sentiment-analysis .
```

Run the container:

```bash
docker run -p 5000:5000 sentiment-analysis
```

Open:

```text
http://localhost:5000
```

## Git Commands

Check changes:

```bash
git status
```

Stage files:

```bash
git add README.md
```

Commit:

```bash
git commit -m "Add project README"
```

Push to GitHub:

```bash
git push origin main
```

If your branch is named `master`, use:

```bash
git push origin master
```

## Notes

- The app requires a valid Apify token to fetch Instagram comments.
- The React app may use a configured backend URL in `frontend/src/App.jsx`; update that URL if you want the frontend dev server to call a local Flask backend.
- Generated PDF reports are saved in the project root and can be downloaded through the Flask API.
