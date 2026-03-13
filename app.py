from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# detection categories

risk_categories = {

"fraud":{
"keywords":[
"send money",
"transfer money",
"cashapp",
"paypal",
"urgent money",
"hospital bill",
"doctor needed",
"help urgently"
],
"score":60
},

"harassment":{
"keywords":[
"idiot",
"stupid",
"shut up",
"i hate you",
"you are useless"
],
"score":40
},

"photo_request":{
"keywords":[
"send me your photo",
"send your picture",
"send pics",
"send private pics"
],
"score":85
},

"nude_request":{
"keywords":[
"send nude",
"nude pics",
"send nudes",
"private photos",
"explicit photos"
],
"score":90
},

"blackmail":{
"keywords":[
"i will leak",
"i will post your photos",
"i will expose you",
"i will ruin your life"
],
"score":100
}

}


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/platform")
def platform():
    return render_template("platform.html")


@app.route("/evidence", methods=["POST"])
def evidence():

    platform = request.form["platform"]

    return render_template("evidence.html", platform=platform)


@app.route("/analyze", methods=["POST"])
def analyze():

    message = request.form.get("message","").lower()

    screenshot = request.files.get("screenshot")

    extracted_text = ""

    if screenshot and screenshot.filename != "":

        path = os.path.join(app.config["UPLOAD_FOLDER"], screenshot.filename)

        screenshot.save(path)

        img = Image.open(path)

        extracted_text = pytesseract.image_to_string(img).lower()


    combined_text = message + " " + extracted_text

    detected_categories = []
    detected_phrases = []

    risk_score = 0


    for category,data in risk_categories.items():

        for keyword in data["keywords"]:

            if keyword in combined_text:

                detected_categories.append(category)

                detected_phrases.append(keyword)

                risk_score += data["score"]


    if risk_score > 100:
        risk_score = 100


    if risk_score >= 60:

        risk_level = "HIGH RISK"

        advice = "Dangerous conversation detected. Do NOT send money or personal images."

    elif risk_score >= 30:

        risk_level = "MODERATE RISK"

        advice = "Suspicious conversation detected. Be cautious."

    else:

        risk_level = "LOW RISK"

        advice = "Conversation appears safe."


    return render_template(
        "result.html",
        risk_level=risk_level,
        risk_score=risk_score,
        categories=detected_categories,
        phrases=detected_phrases,
        extracted_text=extracted_text,
        advice=advice
    )


if __name__ == "__main__":
    app.run(debug=True)