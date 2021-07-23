from flask import Flask, send_from_directory, jsonify, request
import os, glob, yaml



def load_post(filename, return_content = False):
    with open(filename,"r") as f:
        content = f.read()
        header = content.split('---')[1]
        js = yaml.safe_load(header)
        js['file'] = filename.replace('../', '')
        if return_content:
            js['content'] = content.split('---\n')[-1]
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


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('../assets/', path)

@app.route('/get_posts')
def get_posts():
    posts = glob.glob('../_posts/*.*')
    episodes = glob.glob('../_episodes/*.*')
    files = episodes + posts
    posts = [load_post(file) for file in files]
    return jsonify(posts)


@app.route('/get_post_data/<path:filepath>')
def get_post_data(filepath):    
    if not filepath.startswith('../'): 
        filepath = '../' + filepath
    return load_post(filepath, return_content=True)




#=============================================================
if __name__ == '__main__':
    episodes = glob.glob('../_episodes/*.*')
    for episode in episodes:
        content = load_post(episode, return_content=True)
        print(content)