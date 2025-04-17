import fitz  # PyMuPDF
import streamlit as st
import os
from io import BytesIO

# Setup upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# PDF Processing Function
def highlight_large_qty(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in doc:
        text_blocks = page.get_text("blocks")
        in_table = False

        for block in text_blocks:
            x0, y0, x1, y1, text, *_ = block

            # Check for the start of the table
            if "Description" in text and "Qty" in text:
                in_table = True
                continue

            # If in the table, look for quantities
            if in_table:
                if not any(char.isdigit() for char in text):
                    continue
                if "Qty" in text or "Unit Price" in text or "Total" in text:
                    continue

                values = text.split()
                for val in values:
                    if val.isdigit() and int(val) > 1:
                        highlight_box = fitz.Rect(x0, y0, x1, y1)
                        page.draw_rect(highlight_box, color=(1, 0, 0), fill_opacity=0.4)
                        break

            # End of table detection
            if "TOTAL" in text:
                in_table = False

    output_buffer = BytesIO()
    doc.save(output_buffer)
    output_buffer.seek(0)
    return output_buffer

# Streamlit UI
st.set_page_config(page_title="PDF Highlighter", layout="centered")
st.title("🔍 Highlight Large Qty in PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    st.success(f"Uploaded file: {uploaded_file.name}")
    with st.spinner("Processing PDF..."):
        output_pdf = highlight_large_qty(uploaded_file.read())

    st.download_button(
        label="📥 Download Highlighted PDF",
        data=output_pdf,
        file_name=f"highlighted_{uploaded_file.name}",
        mime="application/pdf"
    )
