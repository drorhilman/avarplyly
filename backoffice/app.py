from flask import Flask, send_from_directory, jsonify, request
import os, glob, yaml



def load_post(filename):
    with open(filename,"r") as f:
        content = f.read().split('---')[1]
        js = yaml.load(content)
        js['file'] = filename
        return js
        


# -------------------------- API -------------------------
app = Flask(__name__, static_url_path='')

@app.route("/")
def post_editor():
    with open("post_editor.html","r") as f:
        return f.read()

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/get_posts')
def get_posts():
    posts = glob.glob('../_posts/*.*')
    episodes = glob.glob('../_episodes/*.*')
    files = episodes + posts
    posts = [load_post(file) for file in files]
    return jsonify(posts)


if __name__ == '__main__':
    episodes = glob.glob('../_episodes/*.*')
    for episode in episodes:
        content = load_post(episode)
        print(content)