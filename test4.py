import streamlit as st
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

# --------------------------------------------------
# Thread executor (global)
# --------------------------------------------------
executor = ThreadPoolExecutor(max_workers=2)

# --------------------------------------------------
# Session state initialization
# --------------------------------------------------
defaults = {
    "job_id": None,
    "active_resume_name": None,
    "preprocess_future": None,
    "analyze_requested": False,
    "analysis_running": False,
    "analysis_result": None,
    "resume_text": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------
# UI START
# --------------------------------------------------
st.title("📄 Resume Analyzer")

col1, col2 = st.columns([3, 2])

with col1:
    # --------------------------------------------------
    # Resume upload section
    # --------------------------------------------------
    st.subheader("📄 Upload Resume")

    st.markdown(
        """<div style="color:white; font-size:1rem;margin-bottom: 15px;">
        <p style="margin-bottom:1px">
        We'll analyze your resume and extract key information to help you find matching jobs
        </p>
        <p style="margin-top:1px"><i>suggested</i>: PDF, DOCX, or TXT format.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    resume_file = st.file_uploader(
        "Upload your Resume",
        type=["pdf", "txt", "docx"],
        key="resume_uploader",
    )

    # --------------------------------------------------
    # BACKGROUND PREPROCESSING (ON UPLOAD)
    # --------------------------------------------------
    if resume_file and st.session_state.active_resume_name != resume_file.name:
        new_job_id = str(uuid.uuid4())

        # Reset state for new upload
        st.session_state.job_id = new_job_id
        st.session_state.active_resume_name = resume_file.name
        st.session_state.preprocess_future = None
        st.session_state.analyze_requested = False
        st.session_state.analysis_running = False
        st.session_state.analysis_result = None
        st.session_state.resume_text = None

        resume_analyser = resources["analysis_agent"]

        # Start background preprocessing
        st.session_state.preprocess_future = executor.submit(
            resume_analyser.preprocess_resume,
            resume_file,
            new_job_id,
        )

        st.info(f"Resume uploaded: {resume_file.name} (processing started)")

# --------------------------------------------------
# Role + JD section
# --------------------------------------------------
st.markdown("---")
new_col1, new_col2 = st.columns([2, 1])

with new_col1:
    role = st.selectbox(
        "Select the role you're applying for:",
        list(role_requirements.keys()),
    )

with new_col2:
    upload_jd = st.checkbox("Upload custom job description instead")

custom_jd = None
if upload_jd:
    custom_jd_file = st.file_uploader(
        "Upload job description (PDF or TXT)",
        type=["pdf", "txt"],
    )
    if custom_jd_file:
        st.success("✅ Custom job description uploaded!")
        custom_jd = custom_jd_file
else:
    st.info(f"Required skills: {', '.join(role_requirements[role])}")
    st.markdown(
        f"""<p style="font-size: 12px;">
        Cutoff Score for selection: <b>75/100</b>
        </p>""",
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# ANALYZE BUTTON (ONE REQUEST ONLY)
# --------------------------------------------------
if st.button(
    "🔍 Analyze Resume",
    width="stretch",
    disabled=st.session_state.analyze_requested,
):
    if st.session_state.preprocess_future is None:
        st.warning("Please upload a resume first.")
    else:
        st.session_state.analyze_requested = True
        st.info("Analyze request registered. Waiting for processing if needed...")

# --------------------------------------------------
# ORCHESTRATION LOGIC
# --------------------------------------------------
if st.session_state.analyze_requested and st.session_state.analysis_result is None:

    # Wait until preprocessing finishes
    if not st.session_state.preprocess_future.done():
        with st.spinner("Waiting for resume processing to finish..."):
            time.sleep(1)
        st.experimental_rerun()

    # Preprocessing finished
    finished_job_id = st.session_state.preprocess_future.result()

    # 🔒 Ignore stale uploads
    if finished_job_id != st.session_state.job_id:
        st.warning("Old resume discarded. Please wait for the latest upload.")
        st.stop()

    # Run analysis ONCE
    if not st.session_state.analysis_running:
        st.session_state.analysis_running = True
        resume_analyser = resources["analysis_agent"]

        with st.spinner("Analyzing resume..."):
            if upload_jd:
                analysis, resume_text = resume_analyser.analyze_system(
                    custom_jd=custom_jd
                )
            else:
                analysis, resume_text = resume_analyser.analyze_system(
                    role_requirements=role_requirements[role]
                )

            st.session_state.analysis_result = analysis
            st.session_state.resume_text = resume_text

# --------------------------------------------------
# FINAL OUTPUT + VERIFICATION
# --------------------------------------------------
if st.session_state.analysis_result:
    st.success("✅ Resume analysis complete!")

    # Verification message
    st.info(
        f"✅ Verification: Analysis was performed on resume "
        f"**{st.session_state.active_resume_name}**"
    )

    # Store for downstream tabs
    st.session_state.resume_data = st.session_state.analysis_result
    st.session_state.resume_data["raw_text"] = st.session_state.resume_text

    # Reset dependent UI state
    st.session_state.latex_code = None
    st.session_state.tab4_state = "idle"






import streamlit as st

st.set_page_config(page_title="Interview Generator")

st.title("🎤 Interview Generator")

st.markdown(
    """
    <a href="http://localhost:5173/" target="_blank">
        <button style="
            padding: 0.6rem 1.2rem;
            font-size: 16px;
            cursor: pointer;
        ">
            🚀 Generate Interview
        </button>
    </a>
    """,
    unsafe_allow_html=True
)