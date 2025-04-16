import requests
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
import os

app = Flask(__name__)

# Function to get next booking number
def get_next_booking_number():
    file_path = 'booking_counter.txt'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('1')
        return 1
    else:
        with open(file_path, 'r+') as f:
            current = int(f.read().strip())
            next_number = current + 1
            f.seek(0)
            f.write(str(next_number))
            f.truncate()
        return next_number

# Custom Flowable for top-right timestamp
class TopRightText(Flowable):
    def __init__(self, text, style):
        Flowable.__init__(self)
        self.text = Paragraph(text, style)
    
    def wrap(self, availWidth, availHeight):
        return self.text.wrap(availWidth, availHeight)

    def draw(self):
        w, h = self.text.wrap(self.canv._pagesize[0], self.canv._pagesize[1])
        self.text.drawOn(self.canv, self.canv._pagesize[0] - w - 40, self.canv._pagesize[1] - 40)

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

        # Get booking number
        booking_number = get_next_booking_number()

        # Get current submission timestamp
        submission_time = datetime.now().strftime("Submitted on: %d/%m/%Y at %I:%M %p")

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        # Define custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=22,
            spaceAfter=20,
            alignment=1,
            textColor=colors.darkblue
        )
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            textColor=colors.black
        )
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8
        )
        timestamp_style = ParagraphStyle(
            'Time',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=2  # right align
        )

        content = []

        # Add timestamp to top-right corner
        content.append(TopRightText(submission_time, timestamp_style))

        # Add logo image
        logo_path = os.path.join('static', 'LOGO_1.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=150, height=75)
            logo.hAlign = 'CENTER'
            content.append(logo)
            content.append(Spacer(1, 12))

        # Add title and booking number
        content.append(Paragraph("Kayak Booking Confirmation🛶", title_style))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"<b>Booking Number:</b> #{booking_number:04}", value_style))
        content.append(Spacer(1, 18))

        # Create table data
        table_data = [
            [Paragraph("Name:", label_style), Paragraph(name, value_style)],
            [Paragraph("Phone:", label_style), Paragraph(phone, value_style)],
            [Paragraph("Email:", label_style), Paragraph(email, value_style)],
            [Paragraph("Tour:", label_style), Paragraph(tour, value_style)],
            [Paragraph("Date:", label_style), Paragraph(formatted_date, value_style)],
            [Paragraph("Participants:", label_style), Paragraph(participants, value_style)],
            [Paragraph("Special Requests:", label_style), Paragraph(message, value_style)]
        ]

        # Create table
        table = Table(table_data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
        ]))

        content.append(table)

        # Build PDF
        doc.build(content)

        # Send PDF as response
        pdf_data = buffer.getvalue()
        buffer.close()

        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=booking_confirmation_{name}.pdf'

        return response

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
