import os
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    if request.method == 'POST':
        name = request.form.get('entry.2005620554')
        phone = request.form.get('entry.1065046570')
        email = request.form.get('entry.1045781291', 'Not provided')
        date = request.form.get('entry.1166974658')
        tour = request.form.get('entry.839337160')
        participants = request.form.get('entry.395628407')
        message = request.form.get('entry.1051313161', 'None')

        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y') if date else 'Not specified'

        # Generate booking number based on timestamp
        booking_number = f"KK{datetime.now().strftime('%Y%m%d%H%M%S')}"

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=22,
            alignment=1,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8
        )

        content = []

        logo_path = os.path.join('static', 'img', 'LOGO_1.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=170, height=85)
            logo.hAlign = 'CENTER'
            content.append(logo)
            content.append(Spacer(1, 14))

        content.append(Paragraph("Kayak Booking Confirmation🛶", title_style))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"<b>Booking Number:</b> {booking_number}", value_style))
        content.append(Spacer(1, 18))

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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
        ]))
        content.append(table)

        def draw_top_right(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica-Bold", 10)
            canvas.setFillColor(colors.black)
            timestamp = f"Submitted on: {datetime.now().strftime('%d/%m/%Y at %I:%M %p')}"
            text_width = canvas.stringWidth(timestamp, "Helvetica-Bold", 10)
            canvas.drawString(doc.pagesize[0] - text_width - 40, doc.pagesize[1] - 40, timestamp)
            canvas.restoreState()

        doc.build(content, onFirstPage=draw_top_right)

        pdf_data = buffer.getvalue()
        buffer.close()

        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=booking_confirmation_{name}.pdf'

        return response

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
