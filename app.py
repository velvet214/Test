from flask import Flask, render_template, request
import check

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def upload_file():
    uploaded_file = request.files["email"]
    if uploaded_file.filename != "":
        uploaded_file.save("./uploadedEmail.eml")
    urls, files, plainText = check.extractEmail("./uploadedEmail.eml")

    urlsText = ""
    if urls:
        for url in urls:
            urlsText += url + "\n"
    else:
        urlsText += "None\n"

    filesText = ""
    if files:
        for file in files:
            filesText += file + "\n"
    else:
        filesText += "None\n"

    response = check.chatbotResponse(plainText + 
    "Determine the nature of this email, and whether it should be considered as a phishing email.")
    return render_template("result.html", urlsText=urlsText, filesText=filesText, response=response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)