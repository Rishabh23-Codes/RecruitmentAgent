import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import time
import uuid

executor = ThreadPoolExecutor(max_workers=2)

# -----------------------------
# Session state initialization
# -----------------------------
defaults = {
    "job_id": None,
    "active_file_name": None,
    "upload_future": None,
    "upload_result": None,
    "analyze_requested": False,
    "analysis_running": False,
    "analysis_result": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("Safe Upload → Process → Analyze (With Verification)")

# -----------------------------
# Backend tasks
# -----------------------------
def preprocess_file(file_name, job_id):
    time.sleep(8)  # simulate long preprocessing
    return job_id, file_name, f"Preprocessed {file_name}"

def analyze_file(preprocessed_data):
    time.sleep(5)  # simulate analysis
    return f"Analysis completed for: {preprocessed_data}"

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader("Upload file", key="uploader")

if uploaded_file:
    # Detect new upload (or re-upload)
    if st.session_state.active_file_name != uploaded_file.name:
        new_job_id = str(uuid.uuid4())

        # Register new job
        st.session_state.job_id = new_job_id
        st.session_state.active_file_name = uploaded_file.name
        st.session_state.upload_future = executor.submit(
            preprocess_file, uploaded_file.name, new_job_id
        )

        # Reset analysis state
        st.session_state.upload_result = None
        st.session_state.analysis_result = None
        st.session_state.analyze_requested = False
        st.session_state.analysis_running = False

        st.info(f"File uploaded: {uploaded_file.name} (processing started)")

# -----------------------------
# Analyze button (ONE request only)
# -----------------------------
if st.button("Analyze", disabled=st.session_state.analyze_requested):
    if st.session_state.upload_future is None:
        st.warning("Upload a file first.")
    else:
        st.session_state.analyze_requested = True
        st.info("Analyze request registered.")

# -----------------------------
# Orchestration
# -----------------------------
if st.session_state.analyze_requested and st.session_state.analysis_result is None:

    # Wait for preprocessing
    if not st.session_state.upload_future.done():
        with st.spinner("Waiting for preprocessing to finish..."):
            time.sleep(1)
        st.rerun()

    # Preprocessing finished
    job_id, file_name, result = st.session_state.upload_future.result()

    # 🔒 Ignore stale job
    if job_id != st.session_state.job_id:
        st.warning("Old upload discarded. Waiting for new file.")
        st.stop()

    # Run analysis once
    if not st.session_state.analysis_running:
        st.session_state.analysis_running = True
        with st.spinner("Running analysis..."):
            st.session_state.upload_result = result
            st.session_state.analysis_result = analyze_file(result)

# -----------------------------
# Final output + verification
# -----------------------------
if st.session_state.analysis_result:
    st.success(st.session_state.analysis_result)

    # ✅ VERIFICATION MESSAGE
    st.info(
        f"✅ Verification: Analysis was performed on file "
        f"**{st.session_state.active_file_name}**"
    )
