import os
import logging
import threading
import re
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Thread-safe booking counter
class BookingCounter:
    def __init__(self, file_path='booking_counter.txt'):
        self.file_path = file_path
        self.lock = threading.Lock()
        self._initialize_counter()

    def _initialize_counter(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write('1')

    def get_next(self, reset=False):
        with self.lock:
            try:
                if reset:
                    with open(self.file_path, 'w') as f:
                        f.write('1')
                    return 'KK1'
                with open(self.file_path, 'r+') as f:
                    current = int(f.read().strip())
                    next_number = current + 1
                    f.seek(0)
                    f.write(str(next_number))
                    f.truncate()
                return f'KK{next_number}'
            except (IOError, ValueError) as e:
                app.logger.error(f"Error accessing booking counter: {e}")
                return 'KK1'

booking_counter = BookingCounter()

def get_next_booking_number(reset=False):
    return booking_counter.get_next(reset)

def validate_form(name, phone, email, participants):
    if not re.match(r'^\+?\d{10,15}$', phone):
        return False, "Invalid phone number"
    if email != 'Not provided' and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return False, "Invalid email address"
    if not participants.isdigit() or int(participants) <= 0:
        return False, "Invalid number of participants"
    return True, ""

def create_pdf(name, phone, email, date, tour, participants, message, booking_number):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          leftMargin=0.5*inch, 
                          rightMargin=0.5*inch, 
                          topMargin=0.75*inch, 
                          bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    # Custom styles with adjusted spacing
    title_style = ParagraphStyle('Title', parent=styles['Title'], 
                               fontSize=20, alignment=1, 
                               spaceAfter=8, textColor=colors.darkblue)  # Reduced spaceAfter
    company_style = ParagraphStyle('Company', parent=styles['Normal'], 
                                 fontSize=14, alignment=1, 
                                 spaceAfter=1, textColor=colors.orange)  # Reduced spaceAfter
    address_style = ParagraphStyle('Address', parent=styles['Normal'], 
                                 fontSize=10, alignment=1, 
                                 spaceAfter=4)  # Reduced spaceAfter
    label_style = ParagraphStyle('Label', parent=styles['Normal'], 
                               fontSize=11, fontName='Helvetica-Bold')
    value_style = ParagraphStyle('Value', parent=styles['Normal'], 
                               fontSize=11)

    content = []

    # Add logo with minimal spacing
    logo_path = os.path.join('static', 'img', 'LOGO_6.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=180, height=150)
        logo.hAlign = 'CENTER'
        content.append(logo)
        content.append(Spacer(1, 1))  # Minimal space after logo
    else:
        app.logger.warning("Logo file not found")
        content.append(Paragraph("Logo not available", address_style))

    # Company details with tight spacing
    content.append(Paragraph("KHAVANE KAYAKS", company_style))
    content.append(Paragraph("Khavane Kayaks, Khavane, Khavaneshwar Mandir Road, Tal. Vengurla, Dist. Sindhudurg, Maharashtra 416522", address_style))
    content.append(Paragraph("Hours: Open daily 6:00 AM - 7:00 PM", address_style))
    content.append(Spacer(1, 12))  # Reduced spacing

    # Title and booking number
    content.append(Paragraph("Booking Confirmation", title_style))
    content.append(Paragraph(f"Sr. No.: {booking_number}", value_style))
    content.append(Spacer(1, 12))  # Reduced spacing

    # Booking info table
    table_data = [
        [Paragraph("Name:", label_style), Paragraph(name, value_style)],
        [Paragraph("Phone:", label_style), Paragraph(phone, value_style)],
        [Paragraph("Email:", label_style), Paragraph(email, value_style)],
        [Paragraph("Tour:", label_style), Paragraph(tour, value_style)],
        [Paragraph("Date:", label_style), Paragraph(date, value_style)],
        [Paragraph("Participants:", label_style), Paragraph(participants, value_style)],
        [Paragraph("Special Requests:", label_style), Paragraph(message, value_style)]
    ]
    table = Table(table_data, colWidths=[120, 380])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(table)

    # Page template with timestamp
    def page_template(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        timestamp = f"Issued: {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}"
        text_width = canvas.stringWidth(timestamp, "Helvetica", 9)
        canvas.drawString(doc.pagesize[0] - text_width - 0.5*inch, doc.pagesize[1] - 0.5*inch, timestamp)
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='template', frames=frame, onPage=page_template)
    doc.addPageTemplates([template])

    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    app.logger.debug("Received POST request to /book")
    try:
        app.logger.debug(f"Form data: {request.form}")
        name = request.form.get('entry.2005620554')
        phone = request.form.get('entry.1065046570')
        email = request.form.get('entry.1045781291', 'Not provided')
        date = request.form.get('entry.1166974658')
        tour = request.form.get('entry.839337160')
        participants = request.form.get('entry.395628407')
        message = request.form.get('entry.1051313161', 'None')

        # Validate required fields
        if not all([name, phone, date, tour, participants]):
            app.logger.warning("Missing required form fields")
            return "Error: Required form fields are missing.", 400

        # Validate form inputs
        is_valid, error_msg = validate_form(name, phone, email, participants)
        if not is_valid:
            app.logger.warning(f"Form validation failed: {error_msg}")
            return f"Error: {error_msg}", 400

        # Parse and format date
        try:
            formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            app.logger.warning(f"Invalid date format: {date}")
            formatted_date = 'Not specified'

        booking_number = get_next_booking_number()

        # Generate PDF
        pdf_data = create_pdf(name, phone, email, formatted_date, tour, participants, message, booking_number)

        # Create response
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=booking_confirmation_{name}.pdf'
        return response
    except Exception as e:
        app.logger.error(f"Error in /book: {str(e)}")
        return "Error submitting form or downloading PDF. Please try again.", 500

@app.route('/reset_booking_number', methods=['GET'])
def reset_booking_number():
    get_next_booking_number(reset=True)
    return "Booking counter has been reset to KK1."

if __name__ == '__main__':
    app.run(debug=True)
