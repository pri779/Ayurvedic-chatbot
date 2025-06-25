from flask import Flask, request, make_response
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
import re
import os

app = Flask(__name__)
data = pd.read_csv("ayurvedic_data.csv")

def check_age_group(age_group_str, age):
    if age_group_str.lower() == "all ages":
        return True
    if '+' in age_group_str:
        return age >= int(age_group_str.split('+')[0])
    if " to " in age_group_str:
        min_age, max_age = map(int, age_group_str.split(" to "))
        return min_age <= age <= max_age
    return False

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>Ayurvedic Chatbot</title>
        <link href='https://fonts.googleapis.com/css2?family=Inter&display=swap' rel='stylesheet'>
        <style>
            body {
                background-image: url('https://img.freepik.com/free-photo/ayurvedic-medicine-natural-herbal-leaves-powder-wooden-surface-background-ai-generated_123827-24934.jpg');
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
                height: 100vh;
                margin: 0;
                font-family: 'Inter', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .overlay {
                background: rgba(0, 0, 0, 0.65);
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                color: white;
            }
            input {
                padding: 12px;
                width: 250px;
                margin: 10px 0;
                border-radius: 5px;
                border: none;
                font-size: 16px;
            }
            button {
                padding: 12px 25px;
                background-color: #e74c3c;
                border: none;
                color: white;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            }
            .loader {
                display: none;
                margin-top: 15px;
                color: #fff;
            }
        </style>
    </head>
    <body>
        <div class="overlay">
            <h3>"Health is the greatest gift, contentment the greatest wealth." - Buddha</h3>
            <h1 style='color:#ff7050;'>Ayurvedic Chatbot</h1>
            <form action="/result" method="POST" onsubmit="showLoader()">
                <input type="text" name="disease" id="disease" placeholder="Enter disease" required>
                <button type="button" onclick="startVoice()">🎤</button><br>
                <input type="number" name="age" placeholder="Enter age" required><br>
                <button type="submit">Get Remedy</button>
            </form>
            <div class="loader" id="loader">⏳ Loading remedy...</div>
        </div>
        <script>
            function startVoice() {
                var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'en-IN';
                recognition.start();
                recognition.onresult = function(event) {
                    document.getElementById('disease').value = event.results[0][0].transcript;
                };
            }
            function showLoader() {
                document.getElementById('loader').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
@app.route('/result', methods=['POST'])
def result():
    disease = request.form['disease'].strip().lower()
    age = int(request.form['age'])

    matches = data[
        (data['Disease'].str.lower() == disease) &
        data['Age Group'].apply(lambda x: check_age_group(x, age))
    ]

    if matches.empty:
        return "<h2 style='color:red;'>Sorry, no remedy found for the given disease and age.</h2>"

    html = f"""
    <html>
    <head>
        <title>Ayurvedic Remedy</title>
        <link href='https://fonts.googleapis.com/css2?family=Inter&display=swap' rel='stylesheet'>
        <style>
            body {{
                background: url('https://img.freepik.com/free-photo/top-view-natural-ayurvedic-herbs-table_23-2149187646.jpg') no-repeat center center fixed;
                background-size: cover;
                font-family: 'Inter', sans-serif;
                padding: 50px;
            }}
            .box {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                padding: 30px;
                max-width: 800px;
                margin: auto;
                box-shadow: 0 0 10px rgba(0,0,0,0.2);
            }}
            .header-buttons {{
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                margin-bottom: 20px;
            }}
            .btn {{
                background: #2e7d32;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                border: none;
            }}
            h1 {{ color: #1b5e20; }}
            .remedy-step {{
                background: #f1f8e9;
                border-left: 5px solid #66bb6a;
                margin: 10px 0;
                padding: 10px 15px;
                border-radius: 6px;
            }}
            .images img {{
                width: 130px;
                height: 130px;
                margin: 10px;
                border-radius: 10px;
                object-fit: cover;
            }}
        </style>
    </head>
    <body>
        <div class='box'>
            <div class="header-buttons">
                <a href="/" class="btn">🔙 Back</a>
                <form action="/download" method="POST">
                    <input type="hidden" name="disease" value="{disease}">
                    <input type="hidden" name="age" value="{age}">
                    <button type="submit" class="btn">📄 Download PDF</button>
                </form>
            </div>
            <h1>Ayurvedic Remedy</h1>
            <p><strong>Disease:</strong> {disease.title()}</p>
            <p><strong>Season:</strong> {matches.iloc[0]['Season']}</p>
            <h2>Remedy Steps:</h2>
    """
    step_no = 1
    for step in re.split(r'\d\)|\.', matches.iloc[0]['Remedies']):
        if step.strip():
            html += f"<div class='remedy-step'>Step {step_no}: {step.strip()}</div>"
            step_no += 1

    html += "<h2>Ingredient Images:</h2><div class='images'>"
    for img in matches.iloc[0]['Image URL'].split(';'):
        html += f"<img src='{img.strip()}' alt='ingredient'/>"
    html += "</div></div></body></html>"
    return html
@app.route('/download', methods=['POST'])
def download():
    disease = request.form['disease'].strip().lower()
    age = int(request.form['age'])

    matches = data[
        (data['Disease'].str.lower() == disease) &
        data['Age Group'].apply(lambda x: check_age_group(x, age))
    ]

    if matches.empty:
        return "<h3>No remedy found for your inputs.</h3>"

    html = f"<h1 style='color:green;'>Ayurvedic Remedy</h1>"
    html += f"<p><strong>Disease:</strong> {matches.iloc[0]['Disease']}</p>"
    html += f"<p><strong>Season:</strong> {matches.iloc[0]['Season']}</p><br>"
    html += "<b>Remedy Steps:</b><br>"
    step_no = 1
    for step in re.split(r'\d\)|\.', matches.iloc[0]['Remedies']):
        if step.strip():
            html += f"<p>Step {step_no}: {step.strip()}</p>"
            step_no += 1
    html += "<p><i>*Note: Ingredient images are available only on the website.</i></p>"

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return "Failed to create PDF", 500

    response = make_response(result.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=remedy.pdf"
    return response
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
