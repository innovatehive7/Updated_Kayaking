import os
import logging
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Booking counter logic with reset option
def get_next_booking_number(reset=False):
    file_path = 'booking_counter.txt'
    try:
        if reset:
            with open(file_path, 'w') as f:
                f.write('1')
            return 'KK1'
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('1')
            return 'KK1'
        else:
            with open(file_path, 'r+') as f:
                current = int(f.read().strip())
                next_number = current + 1
                f.seek(0)
                f.write(str(next_number))
                f.truncate()
            return f'KK{next_number}'
    except (IOError, ValueError) as e:
        app.logger.error(f"Error accessing booking counter: {e}")
        return 'KK1'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    app.logger.debug("Received POST request to /book")
    if request.method == 'POST':
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

            # Parse and format date safely
            try:
                formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                app.logger.warning(f"Invalid date format: {date}")
                formatted_date = 'Not specified'

            booking_number = get_next_booking_number()

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, alignment=1, spaceAfter=12, textColor=colors.darkblue)
            company_name_style = ParagraphStyle('CompanyName', parent=styles['Heading2'], fontSize=18, alignment=1, spaceAfter=8, textColor=colors.orange)
            company_name_green_style = ParagraphStyle('CompanyNameGreen', parent=styles['Heading2'], fontSize=18, alignment=1, spaceAfter=8, textColor=colors.green)
            address_style = ParagraphStyle('Address', parent=styles['Normal'], fontSize=12, alignment=1, spaceAfter=8)
            time_style = ParagraphStyle('Time', parent=styles['Normal'], fontSize=12, alignment=1, spaceAfter=16)
            label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', spaceAfter=8)
            value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=12, spaceAfter=8)

            content = []

            # Add logo
            logo_path = os.path.join('static', 'img', 'LOGO_1.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=170, height=85)
                logo.hAlign = 'CENTER'
                content.append(logo)
                content.append(Spacer(1, 12))
            else:
                app.logger.warning("Logo file not found")
                content.append(Paragraph("Logo not available", address_style))

            # Company name
            content.append(Paragraph("Kayak Adventures", company_name_style))
            # content.append(Paragraph("Adventures", company_name_green_style))

            # Company address and hours
            content.append(Paragraph("Khavane Kayaks, Khavane, Khavaneshwar Mandir Road, Tal. Vengurla, Dist. Sindhudurg, Maharashtra 416522", address_style))
            content.append(Paragraph("Hours: Open daily 6:00 AM - 7:00 PM", time_style))

            # Title and booking number
            content.append(Paragraph("Booking Confirmation 🛶", title_style))
            content.append(Paragraph(f"<b>Sr. No.:</b> {booking_number}", value_style))
            content.append(Spacer(1, 12))

            # Booking info table
            table_data = [
                [Paragraph("Name:", label_style), Paragraph(name, value_style)],
                [Paragraph("Phone:", label_style), Paragraph(phone, value_style)],
                [Paragraph("Email:", label_style), Paragraph(email, value_style)],
                [Paragraph("Tour:", label_style), Paragraph(tour, value_style)],
                [Paragraph("Date:", label_style), Paragraph(formatted_date, value_style)],
                [Paragraph("Participants:", label_style), Paragraph(participants, value_style)],
                [Paragraph("Special Requests:", label_style), Paragraph(message, value_style)]
            ]
            table = Table(table_data, colWidths=[150, 350])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            content.append(table)

            # Top-right timestamp
            def draw_top_right(canvas, doc):
                canvas.saveState()
                canvas.setFont("Helvetica", 10)
                canvas.setFillColor(colors.black)
                timestamp = f"Issued: {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}"
                text_width = canvas.stringWidth(timestamp, "Helvetica", 10)
                canvas.drawString(doc.pagesize[0] - text_width - 0.5*inch, doc.pagesize[1] - 0.5*inch, timestamp)
                canvas.restoreState()

            app.logger.debug("Generating PDF")
            doc.build(content, onFirstPage=draw_top_right)
            pdf_data = buffer.getvalue()
            buffer.close()

            app.logger.debug("PDF generated successfully")
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=booking_confirmation_{name}.pdf'
            return response
        except Exception as e:
            app.logger.error(f"Error in /book: {str(e)}")
            return "Error submitting form or downloading PDF. Please try again.", 500
    return redirect(url_for('home'))

@app.route('/reset_booking_number', methods=['GET'])
def reset_booking_number():
    get_next_booking_number(reset=True)
    return "Booking counter has been reset to KK1."

if __name__ == '__main__':
    app.run(debug=True)
