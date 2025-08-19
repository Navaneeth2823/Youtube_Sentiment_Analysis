

from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import requests
import os
from sklearn.model_selection import GridSearchCV


app = Flask(__name__)


from sklearn.model_selection import GridSearchCV

# Train sentiment model at startup
df = pd.read_csv('reddit.csv')

# Use correct column names
comment_col = 'clean_comment'
sentiment_col = 'category'

# Extract and preprocess data
comments = df[comment_col].astype(str)
label_map = {'1': 'positive', '0': 'neutral', '-1': 'negative'}
sentiments = df[sentiment_col].astype(str).map(label_map)

# TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2), stop_words='english')
X = vectorizer.fit_transform(comments)

# --- GridSearchCV for Logistic Regression ---
param_grid = {
    'C': [0.1, 1, 10],           # Regularization strength
    'penalty': ['l1', 'l2'],     # L1 or L2 penalty
    'solver': ['liblinear'],     # Same as original
    'max_iter': [300]            # Same as original
}

grid = GridSearchCV(
    LogisticRegression(),
    param_grid,
    cv=5,                        # 5-fold cross-validation
    scoring='accuracy',
    n_jobs=-1
)

grid.fit(X, sentiments)

# Best model from GridSearch
model = grid.best_estimator_
print(f"✅ Best Parameters: {grid.best_params_}")
print(f"📊 Best Cross-Validation Accuracy: {grid.best_score_:.4f}")




# Helper to classify a list of comments using the trained model
def classify_comments(comments_list):
    X_new = vectorizer.transform(comments_list)
    preds = model.predict(X_new)
    result = {'good': [], 'bad': [], 'neutral': []}
    for comment, sentiment in zip(comments_list, preds):
        if sentiment == 'positive':
            result['good'].append(comment)
        elif sentiment == 'negative':
            result['bad'].append(comment)
        else:
            result['neutral'].append(comment)
    return result

# Helper to fetch comments from YouTube
def fetch_youtube_comments(video_id, api_key):
    comments = []
    url = f'key={api_key}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults=100'
    while url:
        resp = requests.get(url)
        data = resp.json()
        for item in data.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        next_token = data.get('nextPageToken')
        if next_token:
            url = f'key={api_key}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults=100&pageToken={next_token}'
        else:
            url = None
    return comments

@app.route('/')
def index():
    return render_template('index.html')




@app.route('/analyze', methods=['POST'])
def analyze():
    video_url = request.form.get('video_url')
    api_key = 'AIzaSyALVbaPWk4LP_lZnxgvwxGAvfS1qlK58RE'  # User's actual API key
    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400
    
    # Extract video ID
    if 'v=' in video_url:
        video_id = video_url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in video_url:
        video_id = video_url.split('youtu.be/')[1].split('?')[0]
    else:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    comments_list = fetch_youtube_comments(video_id, api_key)
    if not comments_list:
        return jsonify({'error': 'No comments found for this video.'}), 404
    
    # Predict sentiment
    all_preds = model.predict(vectorizer.transform(comments_list))
    sentiment = classify_comments(comments_list)

    sentiment = classify_comments(comments_list)
    total = sum(len(sentiment[k]) for k in sentiment)
    

    # Prepare statistics
    total = len(comments_list)
    stats = {
        'total': total,
        'good': len(sentiment['good']),
        'bad': len(sentiment['bad']),
        'neutral': len(sentiment['neutral']),
        'good_pct': round(100 * len(sentiment['good']) / total, 2) if total else 0,
        'bad_pct': round(100 * len(sentiment['bad']) / total, 2) if total else 0,
        'neutral_pct': round(100 * len(sentiment['neutral']) / total, 2) if total else 0,
    }
    # ✅ Write to CSV only if video hasn't been analyzed before
    import os
    df_output = pd.DataFrame({
        'Comment': comments_list,
        'Sentiment': all_preds
    })
    df_output['VideoID'] = video_id
    log_file = 'sentiment_log.csv'

    if os.path.exists(log_file):
        existing_log = pd.read_csv(log_file)
        if video_id not in existing_log['VideoID'].unique():
            df_output.to_csv(log_file, mode='a', header=False, index=False)
            print(f"Appended data for video ID: {video_id}")
        else:
            print(f"Video ID {video_id} already exists — skipping.")
    else:
        df_output.to_csv(log_file, index=False)
        print(f"Created new log with video ID: {video_id}")


    return jsonify({'stats': stats, 'sentiment': sentiment})

if __name__ == '__main__':
    app.run(debug=True)

