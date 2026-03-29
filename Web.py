from flask import Flask, request, render_template_string
import json

app = Flask(__name__)
CONFIG_FILE = "config.json"

HTML = """
<h2>🏠 Radar Immobilier</h2>

<form method="post">
Profil:
<select name="profile">
  <option value="toi">Toi</option>
  <option value="femme">Femme</option>
</select><br><br>

Pièces min: <input name="rooms"><br>
Loyer max: <input name="rent"><br>
Zip min: <input name="zip_min"><br>
Zip max: <input name="zip_max"><br>

<input type="checkbox" name="charges"> Charges incluses<br>
<input type="checkbox" name="availability"> Dispo requise<br><br>

<button type="submit">Sauvegarder</button>
</form>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        with open(CONFIG_FILE) as f:
            config = json.load(f)

        p = request.form["profile"]

        config["profiles"][p]["min_rooms"] = float(request.form["rooms"])
        config["profiles"][p]["max_rent"] = int(request.form["rent"])
        config["profiles"][p]["zip_min"] = int(request.form["zip_min"])
        config["profiles"][p]["zip_max"] = int(request.form["zip_max"])
        config["profiles"][p]["charges"] = "charges" in request.form
        config["profiles"][p]["availability"] = "availability" in request.form

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)