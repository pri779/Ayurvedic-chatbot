from flask import Flask, request, make_response
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO

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
        <style>
            body {
                background-image: url('https://img.freepik.com/premium-photo/harmony-tradition-embracing-indian-ayurveda-through-minimalistic-background-images-powerpoi_983420-27736.jpg');
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
                margin: 0;
                padding: 0;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
            }
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.6);
                z-index: 0;
            }
            .content {
                position: relative;
                z-index: 1;
                text-align: center;
                max-width: 400px;
                width: 90%;
                padding: 30px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .quote {
                font-style: italic;
                font-size: 1.1em;
                color: #d1e0e0;
                margin-bottom: 20px;
            }
            h1 {
                color: #e74c3c;
                font-size: 1.8em;
                margin-bottom: 15px;
            }
            input[type="text"], input[type="number"] {
                padding: 12px;
                margin: 8px 0;
                width: calc(100% - 24px);
                font-size: 1em;
                border-radius: 5px;
                border: 1px solid #ddd;
                box-sizing: border-box;
            }
            button {
                padding: 12px 20px;
                width: 100%;
                color: white;
                background-color: #e74c3c;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                margin-top: 15px;
                box-sizing: border-box;
            }
            button:hover {
                background-color: #c0392b;
            }
        </style>
    </head>
    <body>
        <div class="overlay"></div>
        <div class="content">
            <div class="quote">"Health is the greatest gift, contentment the greatest wealth." - Buddha</div>
            <h1>Ayurvedic Chatbot</h1>
            <form action="/result" method="POST">
                <input type="text" name="disease" placeholder="Enter disease" required>
                <input type="number" name="age" placeholder="Enter age" required>
                <button type="submit">Get Remedy</button>
            </form>
        </div>
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

    html = """
    <html>
    <head>
        <title>Ayurvedic Remedy</title>
        <style>
            body {
                background: #f0f9f4;
                font-family: Arial, sans-serif;
                padding: 30px;
                color: #333;
            }
            h2 { color: #2e7d32; }
            img {
                width: 150px;
                height: 150px;
                border-radius: 10px;
                margin: 10px;
            }
            .remedy-step {
                background: #ffffff;
                border-left: 5px solid #4caf50;
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
            }
            .refresh {
                background: #4caf50;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                position: absolute;
                top: 20px;
                right: 20px;
            }
        </style>
    </head>
    <body>
    <a class='refresh' href='/'>🔄 Refresh</a>
    <h1>Ayurvedic Remedy</h1>
    """

    for _, row in matches.iterrows():
        html += "<h2>Images:</h2>"
        images = row['Image URL'].split(';')
        for img in images:
            html += f"<img src='{img.strip()}' />"

        html += "<h2>Remedy Steps:</h2>"
        steps = row['Remedies'].split('.')
        for i, step in enumerate(steps):
            if step.strip():
                html += f"<div class='remedy-step'>Step {i+1}: {step.strip().replace('1)', '').strip()}</div>"

        html += f"<h2>Season: {row['Season']}</h2><hr>"

    # Add PDF download button form
    html += f"""
    <form action="/download" method="POST">
        <input type="hidden" name="disease" value="{disease}">
        <input type="hidden" name="age" value="{age}">
        <button type="submit" style="margin-top:20px;padding:10px 15px;">📄 Download as PDF</button>
    </form>
    """

    html += "</body></html>"
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

    html = "<h1>Ayurvedic Remedy</h1>"
    for _, row in matches.iterrows():
        html += f"<p><b>Disease:</b> {row['Disease']}</p>"
        html += f"<p><b>Season:</b> {row['Season']}</p><br>"
        html += "<b>Remedy Steps:</b><br>"
        steps = row['Remedies'].split('.')
        for i, step in enumerate(steps):
            if step.strip():
                html += f"<p>Step {i+1}: {step.strip()}</p>"

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return "Failed to create PDF", 500

    response = make_response(result.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=remedy.pdf"
    return response

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
