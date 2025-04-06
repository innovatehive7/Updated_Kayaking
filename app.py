from flask import Flask, render_template, request, redirect, url_for
import urllib.parse

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle booking form submission
@app.route('/book', methods=['POST'])
def book():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email', 'Not provided')
        date = request.form.get('date')
        tour = request.form.get('tour')
        participants = request.form.get('participants')
        message = request.form.get('message', 'None')

        # Format date for display (if provided)
        if date:
            from datetime import datetime
            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            formatted_date = 'Not specified'

        # Create WhatsApp message
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

        # URL encode the message
        encoded_message = urllib.parse.quote(whatsapp_message)

        # Your WhatsApp number
        whatsapp_number = "919322361033"

        # Construct WhatsApp URL
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

        # Redirect to WhatsApp
        return redirect(whatsapp_url)

    # Fallback for GET requests
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)