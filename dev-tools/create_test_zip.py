"""
Create a dummy D2L submission ZIP for testing D2L-Assignment-Assistant.

Output: Quiz 3 (5.1 - 5.3) Download <date>.zip in the user's Downloads folder.
Structure matches real D2L export: one folder per student (ID - Name - Date),
PDF (or .jpg/.docx for unreadable cases) directly inside each folder, index.html at root.

Run from project root or dev-tools: python dev-tools/create_test_zip.py
"""

import io
import os
import random
import zipfile
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Second ID shared across all (like real D2L)
COURSE_ID = "2018190"
BASE_ID = 100001

# Folder date format must match D2L: "Mar 4, 2026 1227 PM"
FOLDER_DATE_FMT = "%b %d, %Y %I%M %p"
ZIP_DATE_FMT = "%b %d, %Y %I%M %p"

QUOTES = [
    "The only way to do great work is to love what you do.",
    "In the middle of difficulty lies opportunity.",
    "It is during our darkest moments that we must focus to see the light.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Strive not to be a success, but rather to be of value.",
    "The only impossible journey is the one you never begin.",
    "Everything you've ever wanted is on the other side of fear.",
    "Success is not final, failure is not fatal.",
    "What we think, we become.",
    "The best time to plant a tree was 20 years ago.",
    "You miss 100% of the shots you don't take.",
    "Whether you think you can or you think you can't, you're right.",
    "The only limit to our realization of tomorrow is our doubts of today.",
    "Do what you can, with what you have, where you are.",
    "Act as if what you do makes a difference. It does.",
]

# 13 PDF students (11 normal + 2 edge-case), 2 non-PDF (unreadable)
STUDENTS_PDF = [
    "Jordan Blake",
    "Maria Elena Santos",
    "Devon Park",
    "Samuel James Tran",
    "Priya Nair",
    "Lindsey Marie Okafor",
    "Marcus Webb",
    "Rachel Nguyen",
    "Dominic Flores",
    "Keiko Ann Watanabe",
    "Brendan O'Sullivan",
    "Ana Maria De La Cruz Reyes",
    "Jean-Baptiste Moreau-Villeneuve",
]
STUDENT_JPG = "Casey Monroe"
STUDENT_DOCX = "Derek Owens"


def folder_name(student_id: int, name: str) -> str:
    now = datetime.now()
    date_str = now.strftime(FOLDER_DATE_FMT)
    return f"{student_id}-{COURSE_ID} - {name} - {date_str}"


def make_pdf(name: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    for page in range(2):
        c.setFont("Helvetica", 14)
        c.drawString(72, height - 72, name)
        c.setFont("Helvetica", 11)
        y = height - 120
        for _ in range(2):
            quote = random.choice(QUOTES)
            c.drawString(72, y, quote[:60] + ("..." if len(quote) > 60 else ""))
            y -= 24
        c.showPage()
    c.save()
    return buf.getvalue()


def make_minimal_jpg() -> bytes:
    # Minimal valid JPEG: SOI + JFIF APP0 + EOI (many viewers accept this)
    soi = bytes([0xFF, 0xD8])
    app0 = bytes([0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00])
    eoi = bytes([0xFF, 0xD9])
    return soi + app0 + eoi


def make_minimal_docx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>',
        )
        z.writestr(
            "_rels/.rels",
            '<?xml version="1.0"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml" Id="rId1"/>'
            '</Relationships>',
        )
        z.writestr(
            "word/document.xml",
            '<?xml version="1.0"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>Test submission (dummy docx)</w:t></w:r></w:p></w:body>'
            '</w:document>',
        )
        z.writestr(
            "word/_rels/document.xml.rels",
            '<?xml version="1.0"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
        )
    return buf.getvalue()


def main() -> None:
    random.seed(42)
    downloads = os.path.expanduser("~") + os.sep + "Downloads"
    now = datetime.now()
    zip_filename = f"Quiz 3 (5.1 - 5.3) Download {now.strftime(ZIP_DATE_FMT)}.zip"
    zip_path = os.path.join(downloads, zip_filename)

    index_html = b"<!DOCTYPE html><html><head><meta charset=\"utf-8\"/></head><body></body></html>"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", index_html)

        student_id = BASE_ID
        for name in STUDENTS_PDF:
            folder = folder_name(student_id, name) + "/"
            pdf_bytes = make_pdf(name)
            pdf_name = "Quiz 3 (5.1 - 5.3).pdf" if student_id == BASE_ID else f"quiz3_{student_id}.pdf"
            z.writestr(folder + pdf_name, pdf_bytes)
            student_id += 1

        folder_jpg = folder_name(student_id, STUDENT_JPG) + "/"
        z.writestr(folder_jpg + "submission.jpg", make_minimal_jpg())
        student_id += 1

        folder_docx = folder_name(student_id, STUDENT_DOCX) + "/"
        z.writestr(folder_docx + "submission.docx", make_minimal_docx())

    print(f"Created: {zip_path}")
    print(f"  {len(STUDENTS_PDF)} PDF students, 1 image (unreadable), 1 docx (unreadable), index.html")


if __name__ == "__main__":
    main()
