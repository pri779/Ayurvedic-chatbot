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
        <link href="https://fonts.googleapis.com/css2?family=Inter&family=Dancing+Script&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
                background-image: url('https://img.freepik.com/premium-photo/harmony-tradition-embracing-indian-ayurveda-through-minimalistic-background-images-powerpoi_983420-27736.jpg');
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: 'Inter', sans-serif;
            }

            .overlay {
    background-color: rgba(0, 0, 0, 0.6);
    padding: 40px 30px;
    border-radius: 18px;
    color: white;
    text-align: left;
    width: 430px;
    min-height: 440px;     /* ✅ more space */
    display: flex;
    flex-direction: column;
    justify-content: center;
}

            .quote {
                font-family: 'Dancing Script', cursive;
                font-size: 20px;
                text-align: center;
                margin-bottom: 10px;
            }

            h1 {
                text-align: center;
                color: #ff4d4d;
                margin-bottom: 25px;
            }

  form {
    display: flex;
    flex-direction: column;
    gap: 20px;               /* ✅ more gap between fields */
    align-items: center;
}



 .input-group {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 280px;
    margin-left: 10px;  /* ✅ slight right shift */
}

.input-group input[type="text"],
.input-group input[type="number"],
input[type="number"] {
    flex: 1;
    padding: 12px;
    font-size: 14px;
    border-radius: 6px;
    border: none;
    box-shadow: 0 0 4px rgba(255,255,255,0.2);
}



            input[type="text"], input[type="number"] {
                width: 260px;
                padding: 11px;
                font-size: 14px;
                border-radius: 6px;
                border: none;
                box-shadow: 0 0 4px rgba(255,255,255,0.2);
            }

            .voice-btn {
                padding: 12px;
                background-color: #e74c3c;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                color: white;
                height: 40px;
                width: 40px;
            }

            button[type="submit"] {
                width: 180px;
                padding: 12px;
                background-color: #e74c3c;
                color: white;
                border: none;
                font-size: 15px;
                border-radius: 6px;
                cursor: pointer;
                align-self: center;
                margin-top: 10px;
            }

            .loader {
                display: none;
                color: white;
                margin-top: 12px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="overlay">
            <div class="quote">"Health is the greatest gift, contentment the greatest wealth."</div>
            <h1>Ayurvedic Chatbot</h1>
            <form action="/result" method="POST" onsubmit="showLoader()">
                <div class="input-group">
    <input type="text" name="disease" id="disease" placeholder="Enter Your Disease..." required>
    <button type="button" class="voice-btn" onclick="startVoice()">🎤</button>
</div>
<div class="input-group">
    <input type="number" name="age" placeholder="Enter Your Age..." required>
</div>

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
                background: url('https://t3.ftcdn.net/jpg/12/15/65/08/360_F_1215650842_rsCDeAP7zfX9go3kQTcWYq8fjyVhfhQX.jpgs') no-repeat center center fixed;
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
