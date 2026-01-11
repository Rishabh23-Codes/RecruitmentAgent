# import streamlit as st
# from pathlib import Path
# import subprocess
# import base64
# import tempfile

# def render_latex_to_pdf(latex_code):
#     try:
#         # Define the path to your LaTeX compiler (xelatex or any other compiler)
#         xelatex_path = "/usr/local/texlive/2025basic/bin/universal-darwin/xelatex"  # Adjust this path accordingly
        
#         # Create a temporary directory to store LaTeX file and PDF output
#         with tempfile.TemporaryDirectory() as tmpdirname:
#             tex_file = Path(tmpdirname) / "resume.tex"
#             pdf_file = Path(tmpdirname) / "resume.pdf"

#             # Step 1: Write LaTeX code to a temporary .tex file
#             tex_file.write_text(latex_code)

#             # Step 2: Compile the LaTeX code using xelatex
#             result = subprocess.run(
#                 [xelatex_path, "-interaction=nonstopmode", str(tex_file)],
#                 cwd=tmpdirname,
#                 check=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )

#             # Step 3: Capture LaTeX Compilation Error (if any)
#             error = result.stderr.decode('utf-8')

#             if error:
#                 st.text_area("LaTeX Compilation Error", error)

#             # Step 4: Read the compiled PDF
#             pdf_bytes = pdf_file.read_bytes()

#             # Step 5: Convert PDF to Base64 for inline rendering in Streamlit
#             pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
#             st.markdown(
#                 f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="1200" height="1000"></iframe>',
#                 unsafe_allow_html=True
#             )

#             # Step 6: Allow the user to download the compiled PDF
#             st.download_button("Download Resume PDF", pdf_bytes, file_name="resume.pdf")

#     except subprocess.CalledProcessError as e:
#         st.error(f"Failed to compile PDF. Check your LaTeX code.\nError: {e}")
#     except FileNotFoundError:
#         st.error("xelatex not found. Make sure BasicTeX is installed and the path is correct.")

# st.title("LaTeX Resume Live Preview")

# # --------------------------
# # Text area for LaTeX code
# # --------------------------
# # default_latex = r"""
# # \documentclass{article}
# # \usepackage[margin=1in]{geometry}
# # \usepackage{lipsum}  % placeholder text

# # \begin{document}
# # \begin{center}
# # \Huge \textbf{John Doe} \\
# # \large john.doe@example.com | +1 234 567 890
# # \end{center}

# # \section*{Education}
# # \textbf{M.Sc. in Physics}, University XYZ, 2024

# # \section*{Experience}
# # \textbf{Software Engineer Intern}, ABC Corp \\
# # - Developed AI-based solutions for data analysis \\
# # - Built interactive dashboards in Python

# # \section*{Skills}
# # Python, SQL, Machine Learning, Streamlit
# # \end{document}
# # """

# default_latex=r"""
# \documentclass[a4paper,12pt]{article}
# \usepackage[margin=1in]{geometry}
# \usepackage{hyperref}
# \usepackage{enumitem}

# \begin{document}

# \vspace{-10pt}  
# \begin{center}
#     \Huge \textbf{Rishabh} \\ 
#     \small
#     \href{mailto:rishabh23032000@gmail.com}{rishabh23032000@gmail.com}
#     \texttt{|} 8851203297
#     \texttt{|} \href{https://linkedin.com/in/rishabh-503315270}{LinkedIn}
#     \texttt{|} \href{https://github.com/Rishabh23-Codes}{GitHub}
# \end{center}

# \noindent\rule{\linewidth}{0.4pt}

# \section*{Technical Skills}

# \begin{itemize}[leftmargin=*,itemsep=0pt]
#     \item Programming Languages: Python, SQL
#     \item Machine Learning \& AI: Retrieval-Augmented Generation (RAG), Transformer-based LLMs, Conversational Agents
#     \item Frameworks \& Tools: LangChain, ChatGroq API, HuggingFace Transformers, FAISS, Pydantic, Streamlit, Scikit-learn, TensorFlow, Optuna
#     \item Data Engineering: Vector Databases, Text Embeddings, Document Chunking, Data Preprocessing, Model Deployment
#     \item Other Skills: Prompt Engineering, Tool Integration, Dynamic Prompting, API Handling, Version Control (Git), Environment Management
# \end{itemize}

# \noindent\rule{\linewidth}{0.4pt}

# \section*{Projects}

# \begin{itemize}[leftmargin=*,itemsep=0pt]
#     \item \textbf{RAG-BASEDMEDICALCHATBOT(RETRIEVAL-AUGMENTEDGENERATIONSYSTEM)} \textbf{}
#     \begin{itemize}[leftmargin=*,itemsep=0pt]
#         \item Built a Retrieval-Augmented Generation (RAG) chatbot to answer medical queries using contextual retrieval and LLM-based reasoning.
#         \item Implemented document ingestion with LangChain , FAISS , and HuggingFace Embeddings (all-MiniLM-L6-v2) for semantic search across medical PDFs.
#         \item Integrated the ChatGroq (Llama-3.1-8B) model for accurate, context-aware responses with controlled temperature and token limits.
#         \item Designed an efficient text-splitting pipeline using RecursiveCharacterTextSplitter to optimize retrieval precision.
#         \item Built an interactive Streamlit app for real-time medical Q\&A with session persistence and conversation memory.
#     \end{itemize}

#     \item \textbf{CONVERSATIONALAIAGENTWITHTOOL-AUGMENTEDREASONING} \textbf{}
#     \begin{itemize}[leftmargin=*,itemsep=0pt]
#         \item Built an intelligent AI Agent using LangChain and ChatGroq (Llama-3.1-8B) capable of real-time query handling, tool use, and structured response generation.
#         \item Designed a custom Pydantic schema to parse LLM outputs into fields like topic, summary, and sources, ensuring consistent JSON formatting.
#         \item Implemented dynamic prompting middleware to adjust instructions and tone based on conversation flow and message history.
#         \item Integrated the DuckDuckGoSearch API for up-to-date information retrieval and factual grounding in responses.
#         \item Architected a modular ToolStrategy-based agent framework that supports future expansion and multi-tool integration.
#         \item Used Python-dotenv for secure environment variable management and smooth project configuration.
#     \end{itemize}
# \end{itemize}

# \noindent\rule{\linewidth}{0.4pt}

# \section*{Achievements \& Hackathons}

# \begin{itemize}[leftmargin=*,itemsep=0pt]
#     \item \textbf{CLINIQUEST - THE ACADEMIA CONCLAVE, KGMULUCKNOW} \textbf{}
#     \begin{itemize}[leftmargin=*,itemsep=0pt]
#         \item Designed a functional prototype demonstrating AI-assisted post-care monitoring and patient follow-up workflows.
#         \item Added multilingual text support and proposed future integration of AI voice reminders for broader accessibility.
#         \item Presented the solution as a scalable model for improving adherence and hospital communication efficiency.
#     \end{itemize}

#     \item \textbf{M³VISION2030AIHACKATHON,AIIMSDELHI} \textbf{}
#     \begin{itemize}[leftmargin=*,itemsep=0pt]
#         \item Selected among top teams for presenting an AI-enabled healthcare concept co-developed by AIIMS and IIT Delhi.
#         \item Outlined integration of AWS services for secure data storage, communication, and system scalability.
#         \item Highlighted roadmap for deploying D.O.S.T. as a unified platform supporting patient-centric healthcare innovation.
#     \end{itemize}
# \end{itemize}

# \noindent\rule{\linewidth}{0.4pt}

# \section*{Education}

# \begin{itemize}[leftmargin=*,itemsep=0pt]
#     \item \textbf{M.Sc. in Physics} \\ Indian Institute of Technology Delhi
#     \item \textbf{B.Sc. (Hons) in Physics} \\ Kirori Mal College, University of Delhi
# \end{itemize}

# \noindent\rule{\linewidth}{0.4pt}

# \section*{Thesis}

# \begin{itemize}[leftmargin=*,itemsep=0pt]
#     \item \textbf{M.SC. THESIS WORK} \textbf{}
#     \begin{itemize}[leftmargin=*,itemsep=0pt]
#         \item Title: Analytical Study of Propagation Characteristics in Optical Fibers
#         \item Supervisor: Prof. Anurag Sharma , Department of Physics, IIT Delhi
#         \item Description: Performed analytical modeling of optical fiber propagation focusing on mode computation, dispersion, and coupling losses.
#         \item Analyzed fiber performance using simulation tools to study mode propagation and minimize transmission losses.
#         \item Presented results through detailed reports, demonstrating proficiency in optical modeling and data analysis.
#     \end{itemize}
# \end{itemize}

# \end{document}
# """

# # default_latex = r"""
# # \documentclass[a4paper,12pt]{article}
# # \usepackage[margin=1in]{geometry}
# # \usepackage{hyperref}
# # \usepackage{lipsum}  % Placeholder text

# # \begin{document}

# # \begin{center}
# # \Huge \textbf{Rishabh} \\
# # \small \href{mailto:rishabh23032000@gmail.com}{rishabh23032000@gmail.com} | +91 8851203297 \\
# # \href{https://www.linkedin.com/in/rishabh-503315270}{LinkedIn: rishabh-503315270} | 
# # \href{https://github.com/Rishabh23-Codes}{GitHub: Rishabh23-Codes}
# # \end{center}

# # \section*{Education}
# # \noindent \textbf{M.Sc. in Physics}, Indian Institute of Technology Delhi, New Delhi, India \hfill 2023 – 2025 \\
# # \noindent \textbf{B.Sc. (Hons) in Physics}, Kirori Mal College, University of Delhi, New Delhi, India \hfill 2018 – 2021

# # \section*{Experience}

# # \noindent \textbf{Software Engineer Intern}, ABC Corp \hfill 2024 - Present \\
# # \begin{itemize}
# #     \item Developed AI-based solutions for data analysis.
# #     \item Built interactive dashboards in Python using Streamlit.
# # \end{itemize}

# # \section*{Projects}

# # \noindent \textbf{RAG-based Medical Chatbot (Retrieval-Augmented Generation System)} \hfill \textit{2024} \\
# # \begin{itemize}
# #     \item Built a \textbf{Retrieval-Augmented Generation (RAG)} chatbot to answer medical queries using contextual retrieval and LLM-based reasoning.
# #     \item Implemented document ingestion with \textbf{LangChain}, \textbf{FAISS}, and \textbf{HuggingFace Embeddings (all-MiniLM-L6-v2)} for semantic search across medical PDFs.
# #     \item Integrated the \textbf{ChatGroq (Llama-3.1-8B)} model for accurate, context-aware responses.
# #     \item Built an interactive \textbf{Streamlit app} for real-time medical Q\&A with session persistence and conversation memory.
# # \end{itemize}

# # \noindent \textbf{MCP-Based LLM Agent for Mathematical Expression Solving} \hfill \textit{2024} \\
# # \begin{itemize}
# #     \item Developed an \textbf{LLM Agent} leveraging the \textbf{Model Context Protocol (MCP)} to interact with an external math computation tool via standard I/O.  
# #     \item Built a lightweight \textbf{FastMCP server} to securely evaluate mathematical expressions extracted from user queries.  
# #     \item Implemented an asynchronous pipeline using \textbf{AsyncIO} for efficient agent–server communication.
# # \end{itemize}

# # \noindent \textbf{E-commerce Product Text Classification} \hfill \textit{2023} \\
# # \begin{itemize}
# #     \item Built a multi-class text classifier to categorize product descriptions into classes like Electronics, Books, and Clothing.
# #     \item Enhanced embeddings by combining \textbf{Word2Vec} and \textbf{GloVe} for better contextual understanding.
# #     \item Achieved an \textbf{F1-score of 0.92} using a tuned Linear SVM optimized for precision and recall.
# # \end{itemize}

# # \section*{Achievements \& Hackathons}

# # \noindent \textbf{CliniQuest – The Academia Conclave, KGMU Lucknow} \hfill \textit{3rd Position | Oct 2025} \\
# # \textbf{Event:} National-level Hackathon (Syncytium 2025) \\
# # \begin{itemize}
# #     \item Designed a functional prototype demonstrating AI-assisted post-care monitoring and patient follow-up workflows.  
# #     \item Proposed future integration of AI voice reminders for broader accessibility.  
# # \end{itemize}

# # \noindent \textbf{M\textsuperscript{3} Vision 2030 AI Hackathon, AIIMS Delhi} \hfill \textit{Idea Pitching Round Selection | Sept 2025} \\
# # \textbf{Event:} Innovation Hackathon by AIIMS Delhi \& AWS Cloud \\
# # \begin{itemize}
# #     \item Selected among top teams for presenting an AI-enabled healthcare concept co-developed by AIIMS and IIT Delhi.
# #     \item Outlined integration of AWS services for secure data storage, communication, and system scalability.
# # \end{itemize}

# # \section*{Skills}
# # \noindent \textbf{Programming Languages:} Python, SQL \\
# # \noindent \textbf{Machine Learning \& AI:} Retrieval-Augmented Generation (RAG), Transformer-based LLMs, Conversational Agents \\
# # \noindent \textbf{Frameworks \& Tools:} LangChain, ChatGroq API, HuggingFace Transformers, FAISS, Pydantic, Streamlit, Scikit-learn, TensorFlow, Optuna \\
# # \noindent \textbf{Data Engineering:} Vector Databases, Text Embeddings, Document Chunking, Data Preprocessing, Model Deployment \\
# # \noindent \textbf{Other Skills:} Prompt Engineering, Tool Integration, Dynamic Prompting, API Handling, Version Control (Git), Environment Management

# # \section*{IIT Thesis}

# # \noindent \textbf{M.Sc. Thesis Work} \hfill \textit{2024} \\
# # \textbf{Title:} Analytical Study of Propagation Characteristics in Optical Fibers \\
# # \textbf{Supervisor:} \textit{Prof. Anurag Sharma}, Department of Physics, IIT Delhi \\
# # \begin{itemize}
# #     \item Analyzed fiber performance using simulation tools to study mode propagation and minimize transmission losses.
# # \end{itemize}

# # \end{document}
# # """

# # latex_code_input = st.text_area(
# #     "Enter your LaTeX resume code here:",
# #     value=default_latex,
# #     height=400
# # )

# # --------------------------
# # Compile and render PDF
# # --------------------------
# if st.button("Render Resume PDF"):
#     render_latex_to_pdf(default_latex)
#     # Absolute path to xelatex binary (adjust if yours is different)
#     # xelatex_path = "/usr/local/texlive/2025basic/bin/universal-darwin/xelatex"

#     # with tempfile.TemporaryDirectory() as tmpdirname:
#     #     tex_file = Path(tmpdirname) / "resume.tex"
#     #     pdf_file = Path(tmpdirname) / "resume.pdf"

#     #     # Save LaTeX code to file
#     #     tex_file.write_text(latex_code_input)

#     #     try:
#     #         # Compile with xelatex
#     #         result = subprocess.run(
#     #             [xelatex_path, "-interaction=nonstopmode", str(tex_file)],
#     #             cwd=tmpdirname,
#     #             check=True,
#     #             stdout=subprocess.PIPE,
#     #             stderr=subprocess.PIPE
#     #         )

#     #         # Capture error stream
#     #         error = result.stderr.decode('utf-8')

#     #         # Display only LaTeX Compilation Error
#     #         if error:
#     #             st.text_area("LaTeX Compilation Error", error)

#     #         # Read compiled PDF
#     #         pdf_bytes = pdf_file.read_bytes()

#     #         # Display PDF inline
#     #         pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
#     #         st.markdown(
#     #             f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="1200" height="1000"></iframe>',
#     #             unsafe_allow_html=True
#     #         )

#     #         # Download button
#     #         st.download_button("Download Resume PDF", pdf_bytes, file_name="resume.pdf")

#     #     except subprocess.CalledProcessError as e:
#     #         st.error(f"Failed to compile PDF. Check your LaTeX code.\nError: {e}")
#     #     except FileNotFoundError:
#     #         st.error("xelatex not found. Make sure BasicTeX is installed and the path is correct.")
# import os

# os.environ["BROWSER_USE_CONFIG_DIR"] = "./browser_use_config" 
    


# from browser_use import Agent, ChatOllama,Browser
# import asyncio



# async def example():
   
#     browser = Browser(
#         # use_cloud=True,  # Uncomment to use a stealth browser on Browser Use Cloud
#     )

#     llm = ChatOllama(model="llama3.2:3b-instruct-q2_K")

#     agent = Agent(
#         task="Search for OpenAI on Google",
#         browser=browser,
#         llm=llm,
#         max_steps=2,
#         max_failures=1,
#     )

#     history = await agent.run()
#     return history

# if __name__ == "__main__":
#     history = asyncio.run(example())

# # qwen3:4b-instruct
# # lama3.2:3b-instruct-q2_K

# jobspy_scraper.py
# jobspy_scraper_console.py

import time
import pandas as pd
from jobspy import scrape_jobs
import logging
from datetime import datetime, date


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_jobs(search_term="python developer", location="New York, NY", results_wanted=2, wait_seconds=2):
    """
    Scrape job listings using python-jobspy with verbose logging and delay.
    """
    params = {
        "site_name": ["indeed", "linkedin", "glassdoor"],
        "search_term": search_term,
        "location": location,
        "results_wanted": results_wanted,
        "hours_old": 48,
    }

    logging.info(f"Starting scraping for '{search_term}' jobs in '{location}'...")

    try:
        jobs_df = scrape_jobs(**params)
        logging.info("Scraping finished.")

        # Wait a few seconds to reduce risk of being blocked
        logging.info(f"Waiting {wait_seconds} seconds before processing results...")
        time.sleep(wait_seconds)

        if jobs_df is None or jobs_df.empty:
            logging.warning("No jobs found.")
            return pd.DataFrame()

        # Dynamically select available columns
        available_cols = [col for col in ["title", "company_name", "company", "job_url","date_posted"] if col in jobs_df.columns]
        jobs_df = jobs_df[available_cols]

        logging.info(f"Columns available in scraped data: {available_cols}")
        logging.info(f"Number of jobs scraped: {len(jobs_df)}")

        return jobs_df

    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return pd.DataFrame()



def relative_date(value):
    """
    Convert date/datetime/string to 'X days ago'
    """
    if not value:
        return "N/A"

    # If already relative text
    if isinstance(value, str) and "day" in value.lower():
        return value

    try:
        # Handle datetime / date
        if isinstance(value, (datetime, date)):
            posted_date = value.date() if isinstance(value, datetime) else value
        else:
            # Handle string date
            posted_date = datetime.strptime(str(value), "%Y-%m-%d").date()

        delta_days = (date.today() - posted_date).days

        if delta_days <= 0:
            return "Today"
        elif delta_days == 1:
            return "1 day ago"
        else:
            return f"{delta_days} days ago"

    except Exception:
        return "N/A"


def main():
    # Scrape jobs
    jobs = get_jobs(search_term="AI Engineer", location="India", results_wanted=5, wait_seconds=3)

    # Display results in console
    if not jobs.empty:
        print("\n===== Scraped Jobs =====\n")
        for idx, row in jobs.iterrows():
            title = row.get("title", "N/A")
            company = row.get("company_name", row.get("company", "N/A"))
            # date=row.get("date_posted","Recent")
            date=relative_date(row.get("date_posted",None))
            url = row.get("job_url", "N/A")

            print(f"Job #{idx+1}")
            print(f"Title  : {title}")
            print(f"Company: {company}")
            print(f"Date:{date}")
            print(f"URL    : {url}")
            print("-" * 50)
    else:
        print("No jobs scraped.")


if __name__ == "__main__":
    main()
