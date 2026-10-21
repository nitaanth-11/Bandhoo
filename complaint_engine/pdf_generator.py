"""
Professional PDF Document Generation for Bandhoo Complaints (Checkpoint P2.5).

Produces formal, paginated, cleanly styled legal draft PDFs:
- General incident complaints
- Dedicated missing-person report template
Includes "Page X of Y" pagination, official disclaimers, tables, and officer sign-off sections.
"""

import io
import os
import hashlib
from typing import Optional, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y'."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        # Header banner
        self.drawString(54, 800, "BANDHOO CITIZEN REPORT DRAFT — NOT AN OFFICIAL FIR")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)
        # Footer
        self.line(54, 45, 541, 45)
        self.drawString(54, 32, "Prepared for human review. Unverified citizen statement.")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 32, page_text)
        self.restoreState()


def generate_complaint_pdf(
    compiled_record: dict,
    output_dir: Optional[str] = None
) -> Tuple[bytes, str, int, str]:
    """
    Generates a formal PDF document from a compiled complaint record.
    Returns: (pdf_bytes, filename, file_size_bytes, sha256_hash)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "NormalBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748")
    )
    disclaimer_style = ParagraphStyle(
        "NoticeBox",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#742A2A")
    )

    story = []

    # Title & Metadata
    complaint_no = compiled_record.get("complaint_number", "DRAFT-RECORD")
    is_missing_person = compiled_record.get("report_type") == "missing_person_report"
    doc_heading = "MISSING PERSON CITIZEN REPORT" if is_missing_person else "COMPLAINT INCIDENT REPORT DRAFT"

    story.append(Paragraph(doc_heading, title_style))
    story.append(Paragraph(f"Reference: <b>{complaint_no}</b> | Date: {compiled_record.get('header', {}).get('compiled_at', '')[:10]}", body_style))
    story.append(Spacer(1, 8))

    # Prominent Disclaimer Notice Box
    notice_text = (
        "<b>LEGAL NOTICE:</b> This document is a structured citizen report draft prepared for "
        "police review and complaint filing. <b>IT IS NOT AN FIR</b> and does not constitute "
        "an official police registration until examined and accepted by an authorised officer."
    )
    if is_missing_person:
        notice_text += (
            "<br/><br/><b>STATUTORY MANDATE (Bachpan Bachao Andolan v. Union of India):</b> "
            "Under Supreme Court directives and missing person SOPs, <b>NO 48-HOUR OR 24-HOUR WAITING PERIOD IS APPLICABLE</b>. "
            "Details must be recorded immediately in the Station General Diary."
        )

    notice_table = Table([[Paragraph(notice_text, disclaimer_style)]], colWidths=[487])
    notice_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF5F5")),
        ("BORDER", (0, 0), (-1, -1), 1, colors.HexColor("#FEB2B2")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(notice_table)
    story.append(Spacer(1, 10))

    # Complainant Section
    story.append(Paragraph("1. Complainant Information", section_style))
    c = compiled_record.get("complainant") or {}
    c_data = [
        ["Full Name:", c.get("full_name") or "Not provided", "Contact Phone:", c.get("phone") or "Not provided"],
        ["Email Address:", c.get("email") or "Not provided", "Address:", c.get("address") or "Not provided"]
    ]
    c_table = Table([[Paragraph(f"<b>{cell}</b>" if i % 2 == 0 else str(cell), body_style) for i, cell in enumerate(row)] for row in c_data], colWidths=[100, 143, 100, 144])
    c_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(c_table)

    # Missing Person Dedicated Block (if applicable)
    if is_missing_person:
        story.append(Spacer(1, 8))
        story.append(Paragraph("2. Missing Person Physical Profile", section_style))
        mp = compiled_record.get("missing_person_details") or {}
        age_disp = f"{mp.get('age')} years" if mp.get('age') is not None else "Not stated"
        if mp.get('age') is not None and mp.get('age') < 18:
            age_disp += " (MINOR - Section 137 BNS applies)"

        mp_data = [
            ["Full Name:", mp.get("full_name") or "Unknown", "Age / Category:", age_disp],
            ["Gender:", mp.get("gender") or "Not stated", "Height / Complexion:", f"{mp.get('height_cm') or '?'} cm / {mp.get('complexion') or 'Not stated'}"],
            ["Last Seen Date/Time:", mp.get("last_seen_datetime") or "Not stated", "Last Seen Place:", mp.get("last_seen_location") or "Not stated"],
            ["Clothing Last Seen:", mp.get("clothing_last_seen") or "Not stated", "Identifying Marks:", mp.get("identifying_marks") or "None"],
            ["Medical Vulnerability:", mp.get("medical_conditions_or_vulnerabilities") or "None stated", "Relationship to Informant:", mp.get("relationship_to_complainant") or "Not stated"],
        ]
        mp_table = Table([[Paragraph(f"<b>{cell}</b>" if i % 2 == 0 else str(cell), body_style) for i, cell in enumerate(row)] for row in mp_data], colWidths=[110, 133, 110, 134])
        mp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(mp_table)

    # Verbatim Narrative
    story.append(Paragraph("3. Verbatim Statement of Occurrence", section_style))
    orig_text = compiled_record.get("original_narration", {}).get("verbatim_text", "")
    story.append(Paragraph(f"<i>“{orig_text}”</i>", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<font size='7' color='#718096'>Cryptographic Hash: SHA-256 {compiled_record.get('original_narration', {}).get('sha256', '')}</font>", body_style))

    # Chronological Incident Timeline
    timeline = compiled_record.get("chronological_timeline") or []
    if timeline:
        story.append(Spacer(1, 8))
        story.append(Paragraph("4. Sequence of Alleged Events", section_style))
        t_rows = [["Time / Timing Mention", "Event / Action Allegation", "Source Quote"]]
        for t in timeline[:8]:
            t_rows.append([
                t.get("time_expression", ""),
                t.get("event_description", ""),
                f"“{t.get('source_span', {}).get('quote', '')}”"
            ])
        t_table = Table([[Paragraph(f"<b>{c}</b>" if idx == 0 else str(c), body_style) for c in r] for idx, r in enumerate(t_rows)], colWidths=[120, 217, 150])
        t_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("PADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t_table)

    # Jurisdiction
    story.append(Spacer(1, 8))
    story.append(Paragraph("5. Police Jurisdiction Assessment", section_style))
    j = compiled_record.get("jurisdiction_assessment") or {}
    j_station = j.get("station") or "Requires Police Confirmation"
    j_status = j.get("status") or "unconfirmed"
    story.append(Paragraph(f"Assigned Police Station: <b>{j_station}</b> (containment status: <i>{j_status}</i>)", body_style))

    # Statutory Candidates
    candidates = compiled_record.get("potential_bns_sections") or []
    if candidates:
        story.append(Spacer(1, 8))
        story.append(Paragraph("6. Potential BNS Statutory Provisions (Machine-Assisted Legal Reference)", section_style))
        cand_text = []
        for c in candidates:
            if c.get("bns_section"):
                cand_text.append(f"• <b>Section {c['bns_section']} BNS</b> ({c.get('title', '')}): {c.get('punishment', '')}")
        if cand_text:
            story.append(Paragraph("<br/>".join(cand_text), body_style))
            story.append(Paragraph("<font size='7' color='#718096'>Note: Statutory citations are non-binding machine candidate suggestions provided for officer guidance. The police officer determines the actual offences.</font>", body_style))

    # Police Verification Checklist & Sign-Off Block
    story.append(Spacer(1, 10))
    story.append(KeepTogether([
        Paragraph("7. Receiving Officer Action Checklist & Sign-Off", section_style),
        Paragraph("• [ ] Verify complainant identification and contact numbers.<br/>"
                  "• [ ] Enter report in Station General Diary (GD).<br/>"
                  "• [ ] Inspect and acknowledge supporting evidence supplied.<br/>"
                  "• [ ] Issue official GD acknowledgment receipt to complainant.", body_style),
        Spacer(1, 14),
        Table([
            ["Received by (Officer Name & PIN): _______________________", "Rank & Station: _______________________"],
            ["General Diary (GD) Reference No.: _______________________", "Date & Time: _______________________"],
            ["Signature of Receiving Officer: _______________________", "Complainant Signature: _______________________"]
        ], colWidths=[243, 244])
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    file_size = len(pdf_bytes)
    sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    filename = f"{complaint_no.replace(' ', '_')}_{sha256[:8]}.pdf"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes, filename, file_size, sha256
