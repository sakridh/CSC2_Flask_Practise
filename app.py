from flask import Flask, render_template
import json

app = Flask(__name__)

def load_data():
    with open("data/flowers.json") as file:
        flowers = json.load(file)
    return flowers

@app.route("/")
def home():
    flowers = load_data()
    return render_template("index.html", flowers=flowers)

if __name__ == "__main__":
    app.run(debug=True)