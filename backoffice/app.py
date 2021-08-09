from flask import Flask, send_from_directory, jsonify, request
import os, glob, yaml, subprocess, builtins, sys
from resources_analysis import site_resources, save_legal_status

builtins.proc = ''



def load_post(filename, return_content = False):
    with open(filename,"r", encoding="utf8") as f:
        content = f.read()
        header = content.split('---')[1]
        js = yaml.safe_load(header)
        js['file'] = filename.replace('../', '')
        if return_content:
            js['content'] = content.split('---\n')[-1]
        return js
        

def start_local_jekyll_server():
    shell = True # on windows
    if sys.platform.startswith('linux'):
        shell = False
    builtins.proc = subprocess.Popen(["bundle", "exec","jekyll", "serve"], cwd="../", shell=shell)
    return str(builtins.proc)

def run(*args):
    cmd = ['git'] + list(args)
    print(' '.join(cmd))
    cwd = os.getcwd().replace('/backoffice','')
    return subprocess.check_call(['git'] + list(args), cwd=cwd)

def commit_and_push(commit_message):
    try:
        run('pull')
        run('add', '../_episodes/*.*')
        run('add', '../_posts/*.*')
        run('add', '../assets/*.*')
        run('add', '.')
        run('add', '../.')
        run("commit", "-am", f'"{commit_message}"')
        run("push", "origin", "master")
    except Exception as e:
        return {'status': 'error', 'error' : str(e)}
    return {'status': 'ok'}



# -------------------------- API -------------------------
app = Flask(__name__, static_url_path='')


@app.route("/")
def post_editor():
    with open("post_editor.html","r", encoding="utf8") as f:
        return f.read()

@app.route("/resource_managment")
def resource_managment():
    with open("site_resource_managment.html","r", encoding="utf8") as f:
        return f.read()

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('../assets/', path)

@app.route('/_site/<path:path>')
def site_(path):
    return send_from_directory('../_site/', path)

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
    


@app.route('/update_post', methods=['POST'])
def update_post():
    post_data = request.get_json()
    filename = '../' + post_data['file']
    html_content = str(post_data['content'])
    del post_data['content']
    header = str(yaml.dump(post_data, allow_unicode=True))
    html_content = f'---\n{header}---\n{html_content}'
    with open(filename, 'w', encoding="utf8") as f:
        f.write(html_content)
    return jsonify({'status': 'ok', 'file': filename, 'exist' : os.path.isfile(filename)})


@app.route('/delete_post', methods=['POST'])
def delete_post():
    post_data = request.get_json()
    filename = '../' + post_data['file']
    if os.path.isfile(filename):
        os.remove(filename)
    return jsonify({'status': 'ok', 'file': filename, 'exist' : os.path.isfile(filename)})


@app.route('/push_changes')
def api_commit_and_push():
    return commit_and_push(commit_message = "pushed by backoffice")


@app.route('/site_resources')
def get_site_resources():
    return jsonify(site_resources().to_dict(orient="records"))


@app.route('/update_legal_status', methods=['POST'])
def update_legal_status():
    data = request.get_json()
    data = save_legal_status(data)
    return jsonify({"status": "success", 'data' : data})

#=============================================================
if __name__ == '__main__':
    # episodes = glob.glob('../_episodes/*.*')
    # for episode in episodes:
    #     content = load_post(episode, return_content=True)
    print(start_local_jekyll_server())