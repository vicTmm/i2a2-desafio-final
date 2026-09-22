import io
from html import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="Brand", fontSize=11, textColor=colors.HexColor("#1b443a"), spaceAfter=20))
    s["Title"].alignment = TA_LEFT
    s["Title"].textColor = colors.HexColor("#183d34")
    s["BodyText"].leading = 15
    return s

def footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64736d"))
    canvas.drawString(40, 24, "InsurMinds / I2A2 - Projeto Final 2026")
    canvas.drawRightString(doc.pagesize[0] - 40, 24, str(doc.page))

def sample_pdf(pages):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=48, rightMargin=48, topMargin=45, bottomMargin=45)
    s = styles()
    story = []
    for i, page in enumerate(pages):
        if i:
            story.append(PageBreak())
        for line in page["text"].split("\n"):
            if line:
                story.extend([Paragraph(escape(line), s["BodyText"]), Spacer(1, 9)])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()

def comparison_pdf(comparison):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=42)
    s = styles()
    small = ParagraphStyle("Cell", parent=s["BodyText"], fontSize=8, leading=11)
    p = lambda text: Paragraph(escape(str(text)), small)
    story = [Paragraph("INSURMINDS / ANÁLISE COMPARATIVA", s["Brand"]), Paragraph(escape("Comparação de apólices D&O"), s["Title"]), Paragraph(escape(comparison["summary"]), s["BodyText"]), Spacer(1, 16)]
    if any(x["demo"] for x in comparison["policies"]):
        story.extend([Paragraph("DEMONSTRAÇÃO: contém documentos fictícios e dados pré-preenchidos.", s["BodyText"]), Spacer(1, 12)])
    data = [[p("Critério")] + [p(x["title"]) for x in comparison["policies"]]]
    for row in comparison["rows"]:
        data.append([p(row["label"])] + [p((f["value"] or "Não identificado") + (f" | p. {f['page']}" if f["page"] else "")) for f in row["cells"]])
    count = len(comparison["policies"])
    table = Table(data, colWidths=[135] + [(doc.width - 135) / count] * count, repeatRows=1, hAlign="LEFT", splitInRow=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8efeb")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9), ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#dde4df"))]))
    story.extend([table, Spacer(1, 18), Paragraph("Diferenças textuais não comprovam diferenças jurídicas. Campos ausentes não significam exclusão. Valide os documentos e suas condições com um especialista.", s["BodyText"]), PageBreak(), Paragraph("Evidências dos documentos", s["Title"])])
    for row in comparison["rows"]:
        story.append(Paragraph(row["label"], s["Heading3"]))
        for policy, cell in zip(comparison["policies"], row["cells"]):
            story.append(Paragraph(escape(f"{policy['title']} | página {cell['page'] or '-'} | {cell['quote'] or 'Sem evidência identificada'}"), small))
        story.append(Spacer(1, 8))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
