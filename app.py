import requests
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    if request.method == 'POST':
        # Collect form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email', 'Not provided')
        date = request.form.get('date')
        tour = request.form.get('tour')
        participants = request.form.get('participants')
        message = request.form.get('message', 'None')

        # Format date
        if date:
            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            formatted_date = 'Not specified'

        # 1️⃣ Send data to Google Form
        google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe_1WwyJTXHmIkZXg7ggaf_Ete24td50HSeksejhhW-C-LwUg/formResponse"

        form_data = {
            "entry.2005620554": name,
            "entry.1045781291": email,
            "entry.1065046570": phone,
            "entry.1166974658": date,
            "entry.839337160": tour,
            "entry.395628407": participants,
            "entry.1051313161": message,
        }

        try:
            requests.post(google_form_url, data=form_data)
        except Exception as e:
            print("Error submitting to Google Form:", e)

        # 2️⃣ Generate WhatsApp message
        whatsapp_message = (
            "New Kayak Booking Request:\n\n"
            f"*Name:* {name}\n"
            f"*Phone:* {phone}\n"
            f"*Email:* {email}\n"
            f"*Tour:* {tour}\n"
            f"*Date:* {formatted_date}\n"
            f"*Participants:* {participants}\n"
            f"*Special Requests:* {message}"
        )

        encoded_message = urllib.parse.quote(whatsapp_message)
        whatsapp_number = "9137083019"
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

        return redirect(whatsapp_url)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

