import streamlit as st
import base64

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    st.markdown(
        f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0" '
        f'width="100%" height="700"></iframe>',
        unsafe_allow_html=True
    )
