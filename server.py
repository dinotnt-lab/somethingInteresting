from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from pushbullet import Pushbullet

app = Flask(__name__)
with open("key.txt", "r") as f:
    x = f.readlines()
    pb = Pushbullet(x[0])

def sendNotifi(message):
    pb.push_note("Something Important Alert", message)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/getgames')
def get_games():
    sendNotifi("Homepage visited")
    games = []
    links = []
    templates_dir = os.path.join(app.root_path, 'templates/games')
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and filename not in ('index.html', 'upload.html'):
            game = filename[:-5]
            games.append({"name": game})
    links_file = os.path.join(app.root_path, "links.txt")
    with open(links_file, "r") as f:
        for link in f:
            link = link.strip()
            if link:
                links.append({"name": link})
    return jsonify({"games": games, "links": links})

@app.route('/opengame')
def opengame():
    game = request.args.get('x')
    sendNotifi(f"{game} opened")
    if not game:
        return "No game specified", 400
    try:
        return render_template("games/" + game)
    except Exception:
        return "Game not found", 404

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template("upload.html", message="No file part")
    file = request.files['file']
    if file.filename == '':
        return render_template("upload.html", message="No selected file")
    if not file.filename.endswith('.html'):
        return render_template("upload.html", message="Only .html files allowed")
    filename = secure_filename(file.filename)
    sendNotifi("File recived")
    save_path = os.path.join(app.root_path, 'templates/games', filename)
    file.save(save_path)
    return render_template("upload.html", message="File uploaded successfully!")


@app.route('/upload', methods=['GET'])
def upload_form():
    sendNotifi("Upload page opened")
    return render_template("upload.html")

@app.route('/upload_link', methods=['POST'])
def upload_link():
    links = request.form.get('links', '')
    sendNotifi(f"link to {links} recived")
    links_file = os.path.join(app.root_path, "links.txt")
    added = 0
    if links:
        with open(links_file, "a", encoding="utf-8") as f:
            for link in links.splitlines():
                link = link.strip()
                if link and not link.startswith("//"):
                    f.write(link + "\n")
                    added += 1
    msg = f"Added {added} link(s)." if added else "No valid links provided."
    return render_template("upload.html", message=msg)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)