# YouTube Comment Sentiment Analyzer

This web application analyzes the sentiment of comments from any public YouTube video using a machine learning model trained on Reddit comments. It fetches comments via the YouTube Data API, classifies them as positive, negative, or neutral, and displays the results with interactive charts.

## Features
- Paste a YouTube video link to analyze its comments.
- Sentiment analysis using a Logistic Regression model with TF-IDF features.
- Interactive histogram and comment breakdown.
- Keeps a log of analyzed videos and their sentiment results.

## How it Works
1. **Model Training:**
   - Trains a Logistic Regression model on startup using `reddit.csv` (with columns `clean_comment` and `category`).
   - Uses TF-IDF vectorization for text features.
2. **User Input:**
   - User submits a YouTube video URL via the web interface.
3. **Fetching Comments:**
   - The app fetches up to 100 top-level comments using the YouTube Data API.
4. **Sentiment Analysis:**
   - Each comment is classified as positive, negative, or neutral.
   - Results are shown as a histogram and comment lists.
5. **Logging:**
   - Results are saved to `sentiment_log.csv` (one entry per video).

## Setup Instructions

1. **Clone the repository and navigate to the project folder.**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Obtain a YouTube Data API key:**
   - [Get an API key here](https://console.developers.google.com/apis/credentials)
   - Replace the API key in `app.py` with your own for production use.
4. **Prepare the training data:**
   - Ensure `reddit.csv` is present in the root directory with columns `clean_comment` and `category`.
5. **Run the app:**
   ```bash
   python app.py
   ```
6. **Open your browser and go to:**
   - [http://127.0.0.1:5000](http://127.0.0.1:5000)

## File Structure
- `app.py` — Main Flask application and ML logic
- `reddit.csv` — Training data (Reddit comments)
- `sentiment_log.csv` — Log of analyzed YouTube videos
- `static/` — main.js and style.js
- `templates/` —index.html

## Notes
- The provided API key in `app.py` is for demonstration. Use your own for production.
- The model is retrained on every app start. For large datasets, consider saving/loading the model.
- Only public YouTube videos with comments are supported.


