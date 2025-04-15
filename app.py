import requests
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    if request.method == 'POST':
        # Collect form data
        name = request.form.get('entry.2005620554')
        phone = request.form.get('entry.1065046570')
        email = request.form.get('entry.1045781291', 'Not provided')
        date = request.form.get('entry.1166974658')
        tour = request.form.get('entry.839337160')
        participants = request.form.get('entry.395628407')
        message = request.form.get('entry.1051313161', 'None')

        # Format date
        if date:
            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            formatted_date = 'Not specified'

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = []

        # Add content to PDF
        content.append(Paragraph("Kayak Booking Confirmation", styles['Title']))
        content.append(Spacer(1, 12))
        content.append(Paragraph(f"Name: {name}", styles['Normal']))
        content.append(Paragraph(f"Phone: {phone}", styles['Normal']))
        content.append(Paragraph(f"Email: {email}", styles['Normal']))
        content.append(Paragraph(f"Tour: {tour}", styles['Normal']))
        content.append(Paragraph(f"Date: {formatted_date}", styles['Normal']))
        content.append(Paragraph(f"Participants: {participants}", styles['Normal']))
        content.append(Paragraph(f"Special Requests: {message}", styles['Normal']))

        doc.build(content)
        
        # Get PDF data from buffer
        pdf_data = buffer.getvalue()
        buffer.close()

        # Create response with PDF
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=booking_confirmation_{name}.pdf'
        
        return response

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
