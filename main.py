from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import secrets
import threading

app = Flask(__name__)
CORS(app)

# Configuration
DEV_PASSWORD = "RDbird1585"  # Updated password
news_posts = []

# Shared data lock
data_lock = threading.Lock()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_post', methods=['POST'])
def add_post():
    if request.headers.get('X-Dev-Auth') != DEV_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    post = {
        "id": secrets.token_hex(8),
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "image": data.get("image", ""),
        "timestamp": datetime.now().isoformat()
    }

    with data_lock:
        news_posts.append(post)
    return jsonify(post)

@app.route('/update_post/<post_id>', methods=['PUT'])
def update_post(post_id):
    if request.headers.get('X-Dev-Auth') != DEV_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    with data_lock:
        for post in news_posts:
            if post['id'] == post_id:
                post.update({
                    "title": data.get("title", post["title"]),
                    "content": data.get("content", post["content"]),
                    "image": data.get("image", post["image"]),
                    "timestamp": datetime.now().isoformat()
                })
                return jsonify(post)
    return jsonify({"error": "Post not found"}), 404

@app.route('/delete_post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    if request.headers.get('X-Dev-Auth') != DEV_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401

    with data_lock:
        global news_posts
        news_posts = [post for post in news_posts if post['id'] != post_id]
    return jsonify({"success": True})

@app.route('/get_posts')
def get_posts():
    with data_lock:
        return jsonify(sorted(news_posts, key=lambda x: x['timestamp'], reverse=True))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)