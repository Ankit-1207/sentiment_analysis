from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(username, positive, negative, neutral, decision):

    total = positive + negative + neutral

    negative_percent = (negative / total) * 100 if total > 0 else 0

    filename = f"{username}_moderation_report.pdf"

    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Instagram Moderation Report", styles['Title']))
    content.append(Spacer(1,20))

    content.append(Paragraph(f"Username: {username}", styles['Normal']))
    content.append(Paragraph(f"Total Comments: {total}", styles['Normal']))
    content.append(Paragraph(f"Positive Comments: {positive}", styles['Normal']))
    content.append(Paragraph(f"Negative Comments: {negative}", styles['Normal']))
    content.append(Paragraph(f"Neutral Comments: {neutral}", styles['Normal']))
    content.append(Paragraph(f"Negative Percentage: {round(negative_percent,2)}%", styles['Normal']))

    content.append(Spacer(1,20))

    content.append(Paragraph(f"Moderation Decision: {decision}", styles['Heading2']))

    pdf = SimpleDocTemplate(filename)

    pdf.build(content)

    return filename