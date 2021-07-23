from flask import Flask, send_from_directory, jsonify, request
import os, glob, yaml, subprocess, builtins

builtins.proc = ''




def load_post(filename, return_content = False):
    with open(filename,"r") as f:
        content = f.read()
        header = content.split('---')[1]
        js = yaml.safe_load(header)
        js['file'] = filename.replace('../', '')
        if return_content:
            js['content'] = content.split('---\n')[-1]
        return js
        

def start_local_jekyll_server():
    builtins.proc = subprocess.Popen(["bundle", "exec","jekyll", "serve"], cwd="../")
    return str(builtins.proc)

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

@app.route('/get_assets_list')
def get_assets_list():
    assets = glob.glob('../assets/*.*')
    return jsonify(assets)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filename = os.path.join('../assets/', uploaded_file.filename)
            print(filename)
            if os.path.isfile(filename):
                return jsonify({'status': 'exist', 'reason' : 'filename already exist'})
            else:
                uploaded_file.save(filename)
            return jsonify({'status': 'ok'})
    except:
        return jsonify({'status': 'error', 'reason' : 'no file'})


@app.route('/start_jakyll_server')
def start_jakyll():
    return jsonify({'process': start_local_jekyll_server(), 'address': 'http://localhost:4000'})
    

#=============================================================
if __name__ == '__main__':
    # episodes = glob.glob('../_episodes/*.*')
    # for episode in episodes:
    #     content = load_post(episode, return_content=True)
    print(start_local_jekyll_server())