import re
import PyPDF2
import io
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os
import json
import time
from config import GROQ_API_KEY,LLM_MODEL
import docx
from docling.document_converter import DocumentConverter
from langchain_ollama.chat_models import ChatOllama
from ui_utils import role_requirements as require
from pathlib import Path


def safe_llm_invoke(llm, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                sleep_time = 1 + attempt * 1.5
                time.sleep(sleep_time)
                continue
            raise e
    raise RuntimeError("Groq API failed after multiple retries")


class ResumeAnalysisAgent:
    def __init__(self):
        self.api_key=GROQ_API_KEY
        self.cutoff_score=75
        self.resume_text=None
        self.rag_vectorstore=None
        self.analysis_result=None
        self.jd_text=None
        self.extracted_skills=None
        self.resume_weaknesses=[]
        self.resume_strengths=[]
        self.improvement_suggestions={}
        self.resume_skills=[]
        self.education=[]
        self.experience=[]
        self.contact_info={"email":"","phone":""}
        # self.llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY)
        self.llm=ChatOllama(model=LLM_MODEL,temperature=0)


    # def extract_text_from_pdf(self,pdf_file):
    #     """Extract text from a PDF file"""
    #     try:
    #         if hasattr(pdf_file,'getvalue'):
    #             pdf_data=pdf_file.getvalue()
    #             pdf_file_like=io.BytesIO(pdf_data)
    #             reader=PyPDF2.PdfReader(pdf_file_like)
    #         else:
    #             reader=PyPDF2.PdfReader(pdf_file)
    #         text=""
    #         for page in reader.pages:
    #             text+=page.extract_text()

    #         return text
    #     except Exception as e:
    #         print(f"Error extracting text from PDF: {e}")
    #         return ""
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file using Docling"""
        try:
            converter = DocumentConverter()

            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                # Write the PDF content to the temp file
                if hasattr(pdf_file, "getvalue"):
                    temp_file.write(pdf_file.getvalue())
                else:
                    # In case pdf_file is already bytes
                    temp_file.write(pdf_file)
                temp_path = temp_file.name
            
            # Convert the PDF to text
            result = converter.convert(temp_path).document
            response=result.export_to_text()
            return response

        except Exception as e:
            print(f"Error extracting text from PDF with Docling: {e}")
            return ""
        
    def extract_text_from_docx(self,docx_file):
        """Extract text from a docx file"""
        try:
            if hasattr(docx_file, "getvalue"):
                file_stream = io.BytesIO(docx_file.getvalue())
                doc = docx.Document(file_stream)
            else:
                doc = docx.Document(docx_file)
            extracted_text = "\n".join([p.text for p in doc.paragraphs])
            return extracted_text
        except Exception as e:
            print(f"Error extracting text from docx file: {e}")
            return ""

        

    def extract_text_from_txt(self,txt_file):
        """Extract text from a text file"""
        try:
            if hasattr(txt_file,'getvalue'):
                return txt_file.getvalue().decode('utf-8')
            else:
                with open(txt_file,'r',encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error extracting text from text file: {e}")
            return ""
        

        
    def extract_text_from_file(self,file):
        """Extract text from a file (PDF or TXT)"""
        if hasattr(file,'name'):
            file_extension=file.name.split('.')[-1].lower()
        else:
            file_extension=file.split('.')[-1].lower()

        if file_extension=='pdf':
            return self.extract_text_from_pdf(file)
        elif file_extension=='txt':
            return self.extract_text_from_txt(file)
        elif file_extension=='docx':
            return self.extract_text_from_docx(file)
        else:
            print(f"Unsupported file extension: {file_extension}")
            return "" 
        
    def create_rag_vector_store(self,text):
        """Create a vector store for RAG"""
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks=text_splitter.split_text(text)
        embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vectorstore=FAISS.from_texts(chunks,embeddings)
        return vectorstore
    
    def create_vector_store(self,text):
        """Create a simpler vector store for skill analysis"""
        embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vectorstore=FAISS.from_texts([text],embeddings)
        return vectorstore
    

    def analyze_skill(self, skill, retriever):
        """Analyze a skill in the resume"""
    
        # Step 1: Create the query
        query = f"On a scale of 0-10, how clearly does the candidate mention proficiency in {skill}? "
        
        # Step 2: Retrieve relevant resume content
        docs = retriever.invoke(query)
        
        # Step 3: Build context from retrieved documents
        context = "\n".join([doc.page_content for doc in docs]) ###########
        # context = "\n".join(doc.page_content for doc in docs)
        
        # Step 4: Create analysis prompt
        prompt = f"""
        You are strict prompt follower and analyze carefully the prompt and do what only that prompt say,
        Evaluate how well the resume demonstrates skill: {skill}.
        
        Resume Content:
        {context}
        
        Question: {query}
        
        Provide your response starting with a numeric score (0-10), followed by your reasoning.
        Format: "[SCORE]. [REASONING]"
        """
        
        # Step 5: Get LLM response (replaces qa_chain.run())
        # response = llm.invoke(prompt)
        # response_text = response.content.strip()
        response_text = safe_llm_invoke(self.llm, prompt).content.strip()
        
        # Step 6: Parse score from response
        match = re.search(r"(\d{1,2})", response_text)
        score = int(match.group(1)) if match else 0
        
        # Step 7: Extract reasoning
        reasoning = ""
        if '.' in response_text:
            parts = response_text.split('.', 1)
            if len(parts) > 1:
                reasoning = parts[1].strip()
        
        return skill, min(score, 10), reasoning
    





    def analyze_resume_weaknesses(self,analysis_result):
        """Analyze specific weaknesses in the reason based on missing skills"""        
        skill=analysis_result.get("missing_skills",[])[:5]
        # llm=ChatGroq(model='llama-3.1-8b-instant',api_key=self.api_key)
        prompt=f"""
        Follow the prompt exactly and do iteratively for each and every skill mentioned in the "{skill}" and 
        Analyze why the resume is weak in demonstrating proficiency in that skill.
        
        For your analysis consider:
        1. What's missing from the resume regarding this skill?
        2. How could it be improved with specific examples?
        3. What specific action items would make this skill stand out?

        Resume Context:
        {self.resume_text[:3000]}...

        Provide your response in this JSON format:
        [
            {{
                "skill": "<skill name>",
                "weakness":"A concise description of what's missing or problematic(1-2 sentences)",
                "improvement_suggestions": [
                    "Specific suggestion 1",
                    "Specific suggestion 2",
                    "Specific suggestion 3"
                ],
                "example addition":"A specific bullet point that could be added to showcase this skill"
            }}
        ]

        Return only valid JSON, no other text.            
        """

        # response=llm.invoke(prompt)
        # weakness_content=response.content.strip() ##########
        weakness_content = safe_llm_invoke(self.llm, prompt).content.strip()
        # strip code fences if any
        weakness_content = weakness_content.strip("```json").strip("```").strip()

        try:
            weakness_data=json.loads(weakness_content)
            weaknesses=[]

            for item in weakness_data:
                weaknesses.append({
                    "skill": item.get("skill"),
                    "detail": item.get("weakness"),
                    "suggestions": item.get("improvement_suggestions", []),
                    "example": item.get("example_addition", "")
                })

                self.improvement_suggestions[item.get("skill")] = {
                    "suggestions": item.get("improvement_suggestions", []),
                    "example": item.get("example_addition", "")
                }

            self.resume_weaknesses = weaknesses
            print("✅ weakness addresed properly")
            return weaknesses

        except json.JSONDecodeError as e:
            print("❌LLM returned invalid JSON:", e)
            return [{
                "skill": "unknown",
                "detail": weakness_content[:300]
            }]
    
    # def extract_skills_from_resume(self, rag_vectorstore):
    #     """Extract technical skills from a resume using RAG and LLM."""
    #     skills = []

    #     try:
    #         # Create retriever from vectorstore
    #         retriever = rag_vectorstore.as_retriever()
    #         query = "Extract all technical skills, programming languages, frameworks, tools, cloud platforms, and technologies mentioned in this resume."
    #         relevant_chunks = retriever.invoke(query)
    #         context_text = "\n".join([doc.page_content for doc in relevant_chunks])

    #         # Prompt to extract technical skills in strict JSON format
    #         prompt = f"""
    #         You are strict prompt follower and analyze carefully the prompt and do what only that prompt say,
    #         Extract all technical skills strictly and only from the following resume context. 
    #         Include programming languages, frameworks, libraries, tools, platforms, cloud services, databases, and ML/AI tools.
    #         Avoid non-technical or soft skills. 
    #         Return in strict JSON format with a single key "technical_skills" as a list of strings.

    #         Example output:
    #         {{
    #             "technical_skills": ["Python", "Java", "TensorFlow", "PyTorch", "AWS", "Docker", "Kubernetes"]
    #         }}

    #         Resume Context:
    #         {context_text}
    #         """

    #         # Call LLM
    #         response_text = safe_llm_invoke(self.llm, prompt).content.strip()

    #         # Parse JSON from response
    #         match = re.search(r'\{.*\}', response_text, re.DOTALL)
    #         if match:
    #             data = json.loads(match.group())
    #             skills = data.get("technical_skills", [])

    #     except Exception as e:
    #         print(f"Error extracting technical skills via RAG: {e}")

    #     return skills
    


####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------
####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------




    def extract_info_from_resume(self,resume_text):
        try:
            prompt = f"""
            System: You are a resume parsing expert.
            Task: Extract all valid information of the following fields (skills, education, experience) from the variable "Resume Content" Only. Only extract information present in "Resume Content". Do NOT hallucinate. Each field's value must be a list of strings. If no information is found, return ["Not found"].
            Note: Use {resume_text} wherever the "Resume Content" needs to be referenced.

            Fields to extract:

            1. Skills: Technical tools, programming languages, frameworks, and domain knowledge. Example: ["Python", "JavaScript", "React.js", "Node.js", "SQL", "Docker", "LangChain", "Machine Learning", "llama3:1b", "RAG", "AI-Agent"]
            2. Education: Degree, major/subject, institution, and explicitlty graduation year . Example: ["B.Tech in Computer Science, Stanford University (2020–2024)", "B.Sc in Data Science, University of California, Berkeley (2021–2024)", "B.E in IT, IIT Bombay (2019–2023)"]
            3. Experience: Hands-on experience from projects, internships, hackathons, open-source contributions, competitions, or work experience. Example: ["Built an AI agent using LangChain and ChatGroq (Llama-3.1-8B) for real-time query handling and structured responses.", "Developed a recommendation system with Python and Scikit-learn to provide personalized product suggestions.", "Created an NLP pipeline with SpaCy and Transformers for sentiment analysis and entity recognition on large datasets.", "Implemented a serverless REST API using FastAPI and AWS Lambda for high-volume requests with low latency.", "Designed an interactive dashboard with Streamlit and Plotly to visualize real-time sales data and key metrics."]

            Expected Output example:
            {{
                "skills": ["Python", "React.js", "Docker"],
                "education": ["B.Tech in Computer Science, Stanford University (2020–2024)"],
                "experience": ["Hackathon Experience (college or national-level events)", "Open-Source Contribution Experience (GitHub projects)"]
            }}

                **RULES:**
                - Only use information explicitly mentioned in the Resume
                - If no information found in any field: ["None found"]
                - Return ONLY valid JSON - no explanations!

            """
            response_text = safe_llm_invoke(self.llm, prompt).content.strip()
            print(f"📄 Resume LLM response preview: {response_text[:10]}...") 
            try:
                llm_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: extract JSON block safely
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    llm_data = json.loads(response_text[json_start:json_end])
                else:
                    print("❌ LLM response does not contain JSON")
                    llm_data = {}

            skills = llm_data.get("skills", ["Not found"])
            education = llm_data.get("education", ["Not found"])
            experience = llm_data.get("experience", ["Not found"])
            print(f"✅ Extracted: {len(skills)} skills, {len(education)} education, {len(experience)} experience")
            return skills, education, experience

        except Exception as e:
            print(f"Error extracting skills/education/experience : {e}")

         # Fallback
        return ["Not found"], ["Not found"], ["Not found"]
    




####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------
####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------


    # def extract_skill_from_text(self,text):
    #     """Extract skills from a job description"""
    #     try:
    #         # llm=ChatGroq(model="llama-3.1-8b-instant",api_key=self.api_key)
    #         prompt=f"""
    #         You are strict prompt follower and analyze carefully the prompt and do what only that prompt say,
    #         Extract a comprehensive list of technical skills,technologies, and 
    #         competencies required from this job description,
    #         Format the output as a Python list of strings. Only includes the list,
    #         nothing else.

    #         Job Description:
    #         {text}
    #         """
    #         # response=llm.invoke(prompt)
    #         # skills_text=str(response.content) ########################################################

    #         skills_text = safe_llm_invoke(self.llm, prompt).content


    #         match=re.search(r'\[(.*?)\]',skills_text,re.DOTALL)
    #         if match:
    #             skills_text=match.group(0)

    #         try:
    #             skills_list=eval(skills_text)
    #             if isinstance(skills_list,list):
    #                 return skills_list
    #         except:
    #             pass
                
    #         skills=[]
    #         for line in skills_text.split('\n'):
    #             line=line.strip()
    #             if line.startswith('- ') or line.startswith('* '):
    #                 skill=line[2:].strip()
    #                 if skill:
    #                     skills.append(skill)
    #             elif line.startswith('"') and line.endswith('"'):
    #                 skill=line.strip('"')
    #                 if skill:
    #                     skills.append(skill)
    #         return skills
    #     except Exception as e:
    #         print(f"Error extracting skills from job description: {e}")
    #         return []
        

####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------
####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------







        
    def compare_resume_jd(self,skills,experience,education,role_requirements=None,custom_jd=None):
        try:
            context_text=""
            experiences=",".join(experience)[:2000]
            skill=",".join(skills)
            role=None
            if custom_jd:
                jd_text=self.extract_text_from_file(custom_jd)
                jd_vectorstore=self.create_rag_vector_store(jd_text)
                retriever=jd_vectorstore.as_retriever(search_kwargs={"k": 5})
                query="Extract all technical skills, programming languages, frameworks, tools, cloud platforms, databases, and relevant technologies mentioned in this job description. Include both mandatory and optional skills.For example: ['Python', 'JavaScript', 'React.js', 'Node.js', 'SQL', 'Docker', 'AWS', 'Machine Learning', 'LangChain']."
                relevant_chunks = retriever.invoke(query)
                context_text = "\n".join([doc.page_content for doc in relevant_chunks])[:5000]
                print(f"✅ JD context: {len(relevant_chunks)} chunks")
            elif role_requirements:
                role = next((key for key, values in require.items() if any(v in values for v in role_requirements)), None)
                context_text=",".join(role_requirements)
                print(f"✅ Role requirements: {len(role_requirements)} skills")

            if not context_text:
                print("❌ NO JD CONTEXT - Returning empty!")

            # Prompt to extract technical skills in strict JSON format
            prompt = f"""
            System: You are a resume parsing expert.

            Task: Compare the candidate's skills ("resume skill")=>{skill} and ("experience")->{experiences} with the job description context ("context_text")=>{context_text} and extract the following fields. Only extract valid information from the context text and resume skills. Do NOT hallucinate. Each field's value must be a list of strings. If no information is found, return ["Not found"].  

            Fields to extract:

            1. Matching Skills: List of skills that are present both in the resume ("resume skill") also ("experience") and mentioned in the ("context_text").  
            2. Skill Reasoning: For each matching skill, provide reasoning on how well the resume demonstrates the required skill.  
            3. Missing Skills: List skills explicitly mentioned in the job description (context_text) that do not appear in the resume skills or experience, ordered in decreasing priority based on their importance in the job description.  
            4. Extracted Skills: All skills explicitly mentioned in the job description ("context_text") irrespective of whether they match the resume.  
            5. Job Role:{role if role else "extract the job role from context_text"}
            6. Job Description: generate a professional detailed Job description based on {"extracting the skills from: "+role if role else "context_text"}

            Example:  

            Resume Skills: "Python, React.js, SQL, Docker"  
            Job Description Context: "Looking for candidates with Python, JavaScript, React.js, Node.js, SQL, AWS, Docker, and CI/CD experience."  

            Expected Output example:
            {{
                "Matching Skills": ["Python", "React.js", "SQL", "Docker"],
                "Skill Reasoning": [
                    "Python: Strong experience indicated in multiple projects",
                    "React.js: Used in personal web development projects",
                    "SQL: Demonstrated through database management tasks",
                    "Docker: Used for containerizing projects"
                ],
                "Missing Skills": ["JavaScript", "Node.js", "AWS", "CI/CD"],
                "Extracted Skills": ["Python", "JavaScript", "React.js", "Node.js", "SQL", "AWS", "Docker", "CI/CD"]
                "Job Role": "Web Developer",
                "Job Description": "Looking for candidates with Python, JavaScript, React.js, Node.js, SQL, AWS, Docker, and CI/CD experience."  
            }}

            **RULES:**
            - Only use skills explicitly mentioned
            - Skill Reasoning must match exactly 1:1 with Matching Skills order
            - If no matches: ["None found"]
            - Return ONLY valid JSON - no explanations!

            """

            response_text = safe_llm_invoke(self.llm, prompt).content.strip()
        
                        # ---------- SAFE LLM JSON PARSING ----------
            print(f"📄 JD Match LLM response preview:\n{response_text[:10]}\n")

            try:
                # 1️⃣ Try direct JSON parse
                llm_data = json.loads(response_text)

            except json.JSONDecodeError:
                # 2️⃣ Fallback: extract JSON block manually
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1

                if json_start != -1 and json_end != -1:
                    try:
                        llm_data = json.loads(response_text[json_start:json_end])
                    except json.JSONDecodeError as e:
                        print("❌ JD Match JSON extraction failed:", e)
                        llm_data = {}
                else:
                    print("❌ No JSON found in JD Match LLM response")
                    llm_data = {}

            # ---------- SAFE FIELD EXTRACTION ----------
            matching_skills = llm_data.get("Matching Skills", [])
            skill_reasoning = llm_data.get("Skill Reasoning", [])
            missing_skills = llm_data.get("Missing Skills", [])
            extracted_skills = llm_data.get("Extracted Skills", [])
            job_role=llm_data.get("Job Role","")
            job_description=llm_data.get("Job Description","")

            print(
                f"✅ LLM Parsed → "
                f"Matches: {len(matching_skills)}, "
                f"JD Skills: {len(extracted_skills)}, "
                f"Gaps: {len(missing_skills)}",
                f"role: {job_role}",
                f"jd: {len(job_description)}"
)

            
            # ✅ RULE-BASED CALCULATIONS (No semantic analysis needed)
            total_jd_skills = len(extracted_skills)
            match_count = len(matching_skills)
            overall_score = int((match_count / max(1, total_jd_skills)) * 100)
            
            # Strengths = matching_skills (as requested)
            strengths = matching_skills.copy()
            improvement_area = missing_skills if overall_score < self.cutoff_score else []
            
            # PERFECT OUTPUT STRUCTURE (Exactly as requested)
            result = {
                "resume_skills": skills,   
                "experience": experience,
                "education": education,           # Input parameter
                "matching_skills": matching_skills,          # LLM + strengths
                "strengths": strengths,                      # = matching_skills
                "skill_reasoning": skill_reasoning,          # LLM
                "missing_skills": missing_skills,            # LLM
                "extracted_skills": extracted_skills,        # LLM (JD skills)
                "overall_score": overall_score,              # = match_percentage
                "improvement_area":improvement_area,
                "selected": overall_score >= self.cutoff_score,
                "job_role": job_role,
                "job_description":job_description
            }
            
            print(f"✅ Analysis: {overall_score}% | Strengths: {len(strengths)} | Gaps: {len(missing_skills)}")
            return result
            
        except Exception as e:
            print(f"❌ compare_resume_jd error: {e}")
            return {
                "resume_skills": skills,
                "experience": experience,
                "education": education,
                "matching_skills": [],
                "strengths": [],
                "skill_reasoning": [],
                "missing_skills": [],
                "extracted_skills": [],
                "overall_score": 0,
                "improvement_area": [],
                "selected": False,
                "job_role": "",
                "job_description":"",
                "error": str(e)
            }




####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------
####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------





    def analyze_system(self,resume_file,role_requirements=None,custom_jd=None):
        """Analyze a resume against role requirements or a custom JD"""
        latex_code=""
        self.resume_text=self.extract_text_from_file(resume_file)
        self.rag_vectorstore=self.create_rag_vector_store(self.resume_text)

        skills,education,experience=self.extract_info_from_resume(self.resume_text)
        print(f"🔍 Raw extraction: {len(skills)} skills") 

        analysis=self.compare_resume_jd(skills=skills,experience=experience,education=education,role_requirements=role_requirements,custom_jd=custom_jd)

        analysis["contact_info"]=self.extract_contact_info(self.resume_text)
        print("✅ contact info add")

        if analysis and "missing_skills" in analysis and analysis["missing_skills"]:
            self.resume_weaknesses=self.analyze_resume_weaknesses(analysis)

            analysis["detailed_weaknesses"]=self.resume_weaknesses
        if analysis:
            latex_code = self.get_improved_resume(analysis)
            if not latex_code:
                print("Error: Latex code generation failed.")
            else:
                print("✅ all necessary requirement complete for latex code generation")            

        print("✅ done everything in analyze_system")
        
        return analysis,self.resume_text,latex_code







####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------
####-------------------------------------------####-------------------------------------------####-------------------------------------------####-------------------------------------------






    def semantic_skill_analysis(self, resume_text, skills):
        """Analysis skills semantically"""
        vectorstore = self.create_vector_store(resume_text)
        retriever = vectorstore.as_retriever()
        
        skill_scores = {}
        skill_reasoning = {}
        missing_skills = []
        total_score = 0

        # Thread pool to analyze skills in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                lambda skill: self.analyze_skill(skill, retriever),
                skills
            ))

        for skill, score, reasoning in results:
            skill_scores[skill] = score
            skill_reasoning[skill] = reasoning
            total_score += score
            if score <= 5:
                missing_skills.append(skill)
        
        overall_score = int((total_score / (10 * len(skills))) * 100)
        selected = overall_score >= self.cutoff_score

        reasoning = "Candidate evaluated based on explicit resume content using semantic similarity and clear numeric scoring."
        strengths = [skill for skill, score in skill_scores.items() if score >= 6]
        improvement_areas = missing_skills if not selected else []

        self.resume_strengths = strengths

        return {
            "overall_score": overall_score,
            "skill_scores": skill_scores,
            "skill_reasoning": skill_reasoning,
            "selected": selected,
            "reasoning": reasoning,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "improvement_areas": improvement_areas
        }

    def extract_contact_info(self,text):
        # Extract email and phone using regex
        email_pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails=re.findall(email_pattern,text)
        if emails:
            self.contact_info["email"]=emails[0]

        phone_pattern=r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phones=re.findall(phone_pattern,text)
        if phones:
            self.contact_info["phone"]=phones[0]
        
        return self.contact_info

        
    # def extract_education_experience_from_resume_text(self, resume_text,rag_vectorstore):
    #     """
    #     Extract education and work experience from resume text in a single LLM call.

    #     Args:
    #         resume_text (str): The full text of the resume

    #     Returns:
    #         education (list): List of education entries
    #         experience (list): List of work experience entries
    #     """
    #     education = []
    #     experience = []

    #     try:
    #         prompt = f"""
    #         Extract education and work experience from the following resume.

    #         1. Education: (string)->"Degree, field of study, Include institution and graduation dates" and all details must be stored in string format inside list.
    #         2. Work Experience: (string)->"Include company name, job title, employment dates, ,competitions, hackathons ,apply skills in real-world projects, key responsibilities" and all details must be stored in string format inside list.

    #         Return the output in "strict JSON" format as:
    #         example:-{{
    #             "education": ["B.Tech in Computer Science from Delhi Technical Unniversity 2020-2024",....],
    #             "experience": ["Technical excutive in XYZ company","Developing prototype for tesla inovation"]
    #         }}

    #         Resume:
    #         {resume_text}
    #         """

    #         response_text = safe_llm_invoke(self.llm, prompt).content.strip()

    #         # Parse JSON safely
    #         match = re.search(r'\{.*\}', response_text, re.DOTALL)
    #         if match:
    #             data = json.loads(match.group())
    #             education = data.get("education", [])
    #             experience = data.get("experience", [])

    #     except Exception as e:
    #         print(f"Error extracting education/experience: {e}")

    #     return education, experience

    # def extract_education_experience_from_rag(self, rag_vectorstore):
    #     education, experience = [], []

    #     try:
    #         retriever = rag_vectorstore.as_retriever(search_kwargs={"k": 5})
    #         query = "Extract all education and work/project experience details from this resume"
    #         relevant_chunks = retriever.invoke(query)
    #         context_text = "\n".join([doc.page_content for doc in relevant_chunks])

    #         prompt = f"""
    #         You are strict prompt follower and analyze carefully the prompt and do what only that prompt say,
    #         Extract education and work experience from the following resume context.

    #         1. Education: Include degree, subject/major, institution, graduation date. Return as list of strings.
    #         2. Work Experience: Include company, job title, employment dates, ,competitions, hackathons ,apply skills in real-world projects, key responsibilities. Return as list of strings.

    #         Return in strict JSON format:
    #         example:-
    #         {{
    #             "education": ["B.Tech in Computer Science from Delhi Technical Unniversity 2020-2024",....],
    #             "experience": ["Developed a cutting-edge prototype for Tesla innovation"]
    #         }}

    #         Output should be valid education and experience mentioned in context only
    #         Resume Context:
    #         {context_text}
    #         """

    #         response_text = safe_llm_invoke(self.llm, prompt).content.strip()
    #         match = re.search(r'\{.*\}', response_text, re.DOTALL)
    #         if match:
    #             data = json.loads(match.group())
    #             education = data.get("education", [])
    #             experience = data.get("experience", [])

    #     except Exception as e:
    #         print(f"Error extracting education/experience via RAG: {e}")

    #     return education, experience


    # def analyze_resume_llm(self,resume_file,role_requirements=None,custom_jd=None):
    #     """Analyze a resume against role requirements or a custom JD"""
    #     self.resume_text=self.extract_text_from_file(resume_file)

    #     with tempfile.NamedTemporaryFile(delete=False,suffix='.txt',mode='w',encoding='utf-8') as tmp:
    #         tmp.write(self.resume_text)
    #         self.resume_file_path=tmp.name

    #     self.rag_vectorstore=self.create_rag_vector_store(self.resume_text)
    
    #     self.education,self.experience=self.extract_education_experience_from_rag(self.rag_vectorstore)

    #     if custom_jd:
    #         self.jd_text=self.extract_text_from_file(custom_jd)
    #         self.extracted_skills=self.extract_skill_from_text(self.jd_text)

    #         self.analysis_result=self.semantic_skill_analysis(self.resume_text,self.extracted_skills)
    #     elif role_requirements:
    #         self.extracted_skills=role_requirements

    #         self.analysis_result=self.semantic_skill_analysis(self.resume_text,role_requirements)
        
    #     if self.analysis_result and "missing_skills" in self.analysis_result and self.analysis_result["missing_skills"]:
    #         self.analyze_resume_weaknesses()

    #         self.analysis_result["detailed_weaknesses"]=self.resume_weaknesses
        
    #     if self.analysis_result and "resume_skill" not in self.analysis_result:
    #         self.resume_skill=self.extract_skills_from_resume(self.resume_text)
    #         self.analysis_result["resume_skill"]=self.resume_skill
        
    #     if self.analysis_result and "education" not in self.analysis_result:
    #         self.analysis_result["education"]=self.education
        
    #     if self.analysis_result and "experience" not in self.analysis_result:
    #         self.analysis_result["experience"]=self.experience

    #     if self.analysis_result and "contact_info" not in self.analysis_result:
    #         self.analysis_result["contact_info"]=self.extract_contact_info(self.resume_text)
        
    #     if self.analysis_result and self.resume_strengths:
    #         self.analysis_result["strengths"]=self.resume_strengths


    #     return self.analysis_result,self.resume_text


    def ask_question(self, question):
        """Ask a question about the resume"""
        if not self.rag_vectorstore or not self.resume_text:
            return "Please analyze a resume first"
        
        retriever = self.rag_vectorstore.as_retriever(search_kwargs={"k": 3})
        # llm = ChatGroq(
        #     model='llama-3.1-8b-instant',
        #     api_key=GROQ_API_KEY
        # )

        
        docs = retriever.invoke(question)
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = f""" You are strict prompt follower and analyze carefully the prompt and do what only that prompt say,
        You are a helpful assistant answering questions about a resume.
        
        Based on the following resume content only, answer the user's question accurately and concisely.
        
        Resume Content:
        {context}
        
        Question: {question}
        
        Answer:
        """
        
        response = self.llm.invoke(prompt)
        return response.content.strip() #######################
        
    def generate_interview_questions(self,question_types,difficulty,num_questions):
        """Generate interview questions based on the resume"""
        if not self.resume_text or not self.extracted_skills:
            return []
        try:
            # llm=ChatGroq(model='llama-3.1-8b-instant',api_key=self.api_key)

            context=f"""
                Resume Context:
                {self.resume_text[:2000]}...

                Skills to focus on: {', '.join(self.extracted_skills)}
                Strengths: {', '.join(self.analysis_result.get('strengths',[]))}
                Areas of improvement: {', '.join(self.analysis_result.get('missing_skills',[]))}
                """
            prompt=f"""
                You are strict prompt follower and do what only that prompt say,
                    Generate {num_questions} personalized {difficulty.lower()} level
                    interview questions for this candidate based on their resume and skills.Include only the following question
                    types: {', '.join(question_types)}.

                    For each question:
                    1. Clearly label the question type
                    3. Make the question specific to their background and skills
                    3. For coding questions,include a clear problem statement

                    {context}

                    Format the response as a list of tuples with the question type and the question itself.
                    Each tuple should be in the format: ("Question Type","Full Question Text")
                    """
            
            # response=llm.invoke(prompt)
            # questions_text=response.content################################
            questions_text = safe_llm_invoke(self.llm, prompt).content

            questions=[]
            pattern=r'[("]([^"]+)[",)\s]+[(",\s]+([^"]+)[")\s]+'
            matches=re.findall(pattern,questions_text,re.DOTALL)

            for match in matches:
                if len(match)>=2:
                    question_type=match[0].strip()
                    question=match[1].strip()

                    for requested_type in question_types:
                        if requested_type.lower() in question_type.lower():
                            questions.append((requested_type,question))
                            break

            if not questions:
                lines=questions_text.split('\n')
                current_type=None
                current_question=""

                for line in lines:
                    line=line.strip()
                    if any(t.lower() in line.lower() for t in question_types) and not current_question:
                        current_type=next((t for t in question_types if t.lower() in line.lower()),None)
                        if ":" in line:
                            current_question=line.split(":",1)[1].strip()
                    elif current_type and line:
                        current_question+=" "+line
                    elif current_type and current_question:
                        questions.append((current_type,current_question))
                        current_type=None
                        current_question=""

            questions=questions[:num_questions]

            return questions
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            return []
        
    def improve_resume(self,improvement_areas,target_role=""):
        """Generate suggestions to improve the resume"""
        if not self.resume_text:
            return {}
        
        try:
            improvements={}
            for area in improvement_areas:
                if area=="Skills Highlighting" and self.resume_weaknesses:
                    skill_improvements={
                        "description":"Your resume needs to better highlight key skills that are important for the role.",
                        "specific":[] 
                    }

                    before_after_examples={}
                    for weakness in self.resume_weaknesses:
                        skill_name=weakness.get("skill","")
                        if "suggestions" in weakness and weakness["suggestions"]:
                            for suggestion in weakness["suggestions"]:
                                skill_improvements["specific"].append(f"**{skill_name}**: {suggestion}")

                        if "example" in weakness and weakness["example"]:
                            resume_chunks=self.resume_text.split('\n\n')
                            relevant_chunk=""

                            for chunk in resume_chunks:
                                if skill_name.lower() in chunk.lower() or "experience" in chunk.lower():
                                    relevant_chunk=chunk
                                    break
                            if relevant_chunk:
                                before_after_examples={
                                    "before":relevant_chunk.strip(),
                                    "after":relevant_chunk.strip()+"\n· "+weakness["example"]
                                }
                    if before_after_examples:
                        skill_improvements["before_after"]=before_after_examples
                    improvements["Skills Highlighting"]=skill_improvements
            remaining_areas=[area for area in improvement_areas if area not in improvements]

            if remaining_areas:
                # llm=ChatGroq(model='llama-3.1-8b-instant',api_key=self.api_key)

                # Create a context with resume analysis and weakness
                weaknesses_text=""
                if self.resume_weaknesses:
                    weaknesses_text="Resume Weaknesses:\n"
                    for i,weakness in enumerate(self.resume_weaknesses):
                        weaknesses_text+=f"{i+1}. {weakness['skill']}: {weakness['detail']}\n"
                        if "suggestions" in weakness:
                            for j,sugg in enumerate(weakness["suggestions"]):
                                weaknesses_text+=f"  - {sugg}\n"
                context=f"""
                Resume Content:
                {self.resume_text}

                Skills to focus on: {', '.join(self.extracted_skills)}
                Strengths: {', '.join(self.analysis_result.get('strengths',[]))}
                Areas for improvement: {', '.join(self.analysis_result.get('missing_skills',[]))}

                {weaknesses_text}

                Target role: {target_role if target_role else "Not specified"}

                """

                prompt=f"""
                You are strict prompt follower and do what only that prompt say,
                Provide detailed suggestions to improve this resume in the following areas: {', '.join(remaining_areas)}.
                
                {context}

                For each improvement area,provide:
                1. A general description of what needs improvement
                2. 3-5 specific actionable suggestions
                3. Where relevant,provide a before/after example

                Format the response as a JSON onject with improvement areaa as keys ,each containing:
                - "description":general description
                - "specific": list of specific suggestions
                - "before_after": (where applicable) a dict with "before" and "after" examples

                Only include the requested improvement area that aren't already covered.
                Focus particularly on addressing the resume weaknesses identified. 
                """

                # response=llm.invoke(prompt)
                response = safe_llm_invoke(self.llm, prompt)

                # Try to parse JSON from the response
                ai_improvements={}

                #Extract from markdown code blocks if present
                json_match=re.search(r'```(?:json)?\s*([\s\S]+?)\s*```',response.content)
                if json_match:
                    try:
                        ai_improvements=json.loads(json_match.group(1))
                        # Merge with existing improvements
                        improvements.update(ai_improvements)
                    except json.JSONDecodeError:
                        pass

                # If json parsing failed , create structured output manually
                if not ai_improvements:
                    sections=response.content.split("##")

                    for section in  sections:
                        if not section.strip():
                            continue
                        lines=section.strip().split("\n")
                        area=None

                        for line in lines:
                            if not area and line.strip():
                                area=line.strip()
                                improvements[area]={
                                    "description":"",
                                    "specific":[]
                                }
                            elif area and "specific" in improvements[area]:
                                if line.strip().startswith("- "):
                                    improvements[area]["specific"].append(line.strip()[2:])
                                elif not improvements[area]["description"]:
                                    improvements[area]["description"]+=line.strip()
            # Ensure all requested area are included
            for area in improvement_areas:
                if area not in improvements:
                    improvements[area]={
                        "description":f"Improvements needed in {area}",
                        "specific":["Review and enhance this section"]
                    }
            return improvements
        except Exception as e:
            print(f"Error generating resume improvements: {e}")
            return {area:{"description":"Error generating suggestions","specific":[]} for area in improvement_areas}


    # def get_improved_resume(self,target_role="",highlight_skills=""):
    #     """Generate an improved version of the resume optimized for the job description"""
    #     if not self.resume_text:
    #         return "Please upload and analyze a resume first"
    #     try:
    #         #Parse highlight skills if provided
    #         skills_to_highlight=[]
    #         if highlight_skills:
    #             if len(highlight_skills)>100:
    #                 self.jd_text=highlight_skills
    #                 try:
    #                     parsed_skills=self.extract_skill_from_text(highlight_skills)
    #                     if parsed_skills:
    #                         skills_to_highlight=parsed_skills
    #                     else:
    #                         skills_to_highlight=[s.strip() for s in highlight_skills.split(",") if s.strip()]
    #                 except:
    #                     skills_to_highlight=[s.strip() for s in highlight_skills.split(",") if s.strip()]
    #             else:
    #                 skills_to_highlight=[s.strip() for s in highlight_skills.split(",") if s.strip()]
    #         if not skills_to_highlight and self.analysis_result:
    #             skills_to_highlight=self.analysis_result.get('missing_skills',[])
    #             skills_to_highlight.extend([
    #                 skill for skill in self.analysis_result.get('strengths',[]) if skill not in skills_to_highlight
    #             ])

    #             if self.extracted_skills:
    #                 skills_to_highlight.extend([
    #                     skill for skill in self.extracted_skills if skill not in skills_to_highlight
    #                 ])

    #         weakness_context=""
    #         improvement_examples=""

    #         if self.resume_weaknesses:
    #             weakness_context="Address these specific weaknesses:\n"

    #             for weakness in self.resume_weaknesses:
    #                 skill_name=weakness.get('skill','')
    #                 weakness_context+=f"- {skill_name}: {weakness.get('detail','')}\n"

    #                 if 'suggestions' in weakness and weakness['suggestions']:
    #                     weakness_context+=" Suggested improvements:\n"
    #                     for suggestion in weakness['suggestions']:
    #                         weakness_context+=f" * {suggestion}\n"
    #                 if 'example' in weakness and weakness['example']:
    #                     improvement_examples+=f"for {skill_name}: {weakness['example']}\n\n"
    #         # llm=ChatGroq(model='llama-3.1-8b-instant',api_key=self.api_key)

    #         jd_context=""
    #         if self.jd_text:
    #             jd_context=f"Job Description:\n{self.jd_text}\n\n"
    #         elif target_role:
    #             jd_context=f"Target Role: {target_role}\n\n"

    #         prompt=f"""
    #         You are strict prompt follower and do what only that prompt say,
    #         Rewrite and improve this resume to make it highly optimized for the target job.
    #         {jd_context}
    #         Original Resume:
    #         {self.resume_text}
    #         Skills to highlight (in order of priority): {', '.join(skills_to_highlight)}
            
    #         {weakness_context}

    #         Here are specific examples of content to add:
    #         {improvement_examples}

    #         Please improve the resume by:
    #         1. Adding strong, quantifiable achievements
    #         2. Highlighting the specified skills strategically for ATS scanning
    #         3. Addressing all the weakness areas identified with the specific suggestions provided
    #         4. Incorporating the example improvements provided above
    #         5. Structuring the example improvements provided above
    #         6. Using industry-standard terminology
    #         7. Ensuring all relevant experience is properly emphasized
    #         8. Adding measurable outcomes and achievements

    #         Return only the improved resume text without any additional explanations.
    #         Format the resume in a modern,clean style with clear section headings.
    #         """

    #         # response=llm.invoke(prompt)
    #         # improved_resume=response.content.strip()
    #         improved_resume = safe_llm_invoke(self.llm, prompt).content.strip()

    #         with tempfile.NamedTemporaryFile(delete=False,suffix='.txt',mode='w',encoding='utf-8') as tmp:
    #             tmp.write(improved_resume)
    #             self.improved_resume_path=tmp.name

    #         return improved_resume
    #     except Exception as e:
    #         print(f"Error generating improved resume: {e}")
    #         return "Error generating improved resume. Please try again."

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if hasattr(self,'resume_file_path') and os.path.exists(self.resume_file_path):
                os.unlink(self.resume_file_path)
            if hasattr(self,'improved_resume_path') and os.path.exists(self.improved_resume_path):
                os.unlink(self.improved_resume_path)
        except Exception as e:
            print("Error cleaning up temporary files: {e}")

########################################################################################################################################################################################################

    def get_improved_resume(self,analysis_result):
        """Generate an improved version of the resume optimized for the job description"""
        try:
            # # Define the LaTeX template separately
            # latex_template = r"""
            # \documentclass[a4paper,12pt]{article}
            # \usepackage[margin=1in]{geometry}
            # \usepackage{hyperref}

            # \begin{document}

            # \begin{center}
            # \Huge \textbf{Candidate's Name} \\
            # \small \href{mailto:email@example.com}{email@example.com} | 1234567890 \\
            # \href{https://www.linkedin.com/in/candidate}{LinkedIn: candidate} | 
            # \href{https://github.com/candidate}{GitHub: candidate}
            # \end{center}

            # \section*{Technical Skills}
            # \noindent \textbf{Skills:}[SKILLS_SECTION]

            # \section*{Experience}

            # \noindent \textbf{Job Title}, Company Name \hfill Employment Dates \\
            # \begin{itemize}
            #     \item [EXPERIENCE]
            # \end{itemize}


            # \section*{Projects}
            # \noindent \textbf{Project Name} \hfill \textit{Year} \\
            # \begin{itemize}
            #     \item [PROJECTS_SECTION]
            # \end{itemize}

            # \section*{Achievements}
            # \noindent \textbf{Award or Recognition} \hfill Year \\
            # [ACHIEVEMENTS_SECTION]

            # \section*{Certifications}
            # \noindent \textbf{[CERTIFICATE]} \hfill Year of Certification

            # \section*{Education}
            # \noindent \textbf{Degree Title}, University Name \hfill Graduation Year \\
            # [EDUCATION_SECTION]

            # \section*{Thesis}
            # [Thesis]


            # \end{document}
            # """

            # Now create the prompt using the template
            # prompt = f"""
            # IMPORTANT:
            # - You MUST return a COMPLETE LaTeX code
            # - Do NOT return partial edits, explanations,extra comment,or markdown

            # You are an LLM tasked with improving and structuring the resume for a candidate applying for a job. You need to follow the instructions and **strictly** use the information and references only from the provided context.
            # `resume_text`:{self.resume_text}
            # Job Role: {analysis_result["job_role"]}
            # Job Description: {analysis_result["job_description"]}
            # `analysis_result`:{analysis_result}

            # Please do the following:

            # 1. Extract the job role, skills, experience, education, contact_info and other relevant details from the provided `resume_text` .
            # 2. Use this information to fill out the LaTeX resume template below.
            # 3. Improve the resume by:
            #     - Adding strong, quantifiable achievements.
            #     - Highlighting the specified skills for ATS scanning.
            #     - Addressing all weaknesses identified in `detailed_weaknesses`and incorporating the specific suggestions provided in `improvement_area`.
            #     - Structuring the example improvements provided above in the resume.
            #     - Using industry-standard terminology.
            #     - Ensuring all relevant experience is properly emphasized and formatted from `resume_text` only .
            #     - Adding measurable outcomes and achievements wherever possible only.
            #     - Adding or modify those real requirements only that are available in `resume_text` but if not available don't forcefully change or generate

            # The output should only contain the LaTeX code in the correct format shown in latex template below, with **no extra text or comments**. 

            # Here is the LaTeX template:
            # {latex_template}

            # **Rules/Instructions**:
            # 1. **Only use the information from `resume_text` and `analysis_result`**. If a section is not present (e.g., no experience or certifications), **skip that section entirely**. 
            # 2. **Extract job role, skills, experience, education, projects, certifications, achievements**, etc., only from the provided inputs.
            # 3. **Do not include any additional explanation, comments, or text.** The output should be clean, valid LaTeX code only.
            # """


            ###########################################################################################################################################################################
            # prompt = f"""
            #     YOU ARE A STRICT RESUME FORMATTER. MUST FOLLOW THE RULES AND INSTRUCTIONS STRICTLY. YOUR ONLY JOB IS TO EXTRACT AND REPHRASE EXISTING CONTENT FROM THE RESUME — YOU MUST NEVER ADD, INVENT, OR INFER ANYTHING.

            #     Original Resume Text:
            #     \"\"\"{self.resume_text}\"\"\"

            #     Job Role (for keyword highlighting only): {analysis_result.get('job_role', '')}
            #     Missing Skills (do NOT add them in latex code): {analysis_result.get('missing_skills', [])}

            #     CRITICAL RULES — VIOLATE ANY AND YOU FAIL:
            #     - DO NOT change education degrees, majors, or universities.
            #     - DO NOT add any numbers,score,marks, percentages, metrics, accuracy, F1-score, improvements (e.g., 94%, 30%, 0.92) unless they are EXPLICITLY written in the original resume.
            #     - DO NOT mention tools or frameworks not explicitly listed (e.g., no PyTorch, TensorFlow, CNN, BERT if not in original).
            #     - DO NOT create new projects, bullets, or achievements.
            #     - You may ONLY:
            #         - Rephrase existing bullets with stronger action verbs (e.g., "Built" → "Developed and implemented").
            #         - Bold skills that appear in the original resume AND are relevant to the job role (use \\textbf{{Skill}}).
            #         - Reorder bullets slightly for better flow.
            #         - Copy education, contact, dates, titles EXACTLY.
            #     - If a section has no content → replace its placeholder with nothing (delete the section).
            #     - Use the original text almost verbatim where possible.

            #     REPLACE THE PLACEHOLDERS IN THE TEMPLATE BELOW WITH REAL EXTRACTED CONTENT ONLY:

            #     [EXTRACTED_PERSONAL_DETAIL] → Full name from resume and Email | Phone | LinkedIn | GitHub (with proper \\href for links)
            #     [SKILLS_SECTION] → \\section*{{Technical Skills}} followed by categorized skills EXACTLY as in resume, with minor rephrasing
            #     [EXPERIENCE_SECTION] → extract the experience from the resume if not present remove experience section
            #     [PROJECTS_SECTION] → Each project with name, technologies (in parentheses), year, and ORIGINAL bullets (rephrased only) and  Bold/highlight each category in [Categories:]
            #     [ACHIEVEMENTS_SECTION] → Exact achievements with dates and descriptions
            #     [EDUCATION_SECTION] → Exact degrees, universities, years — NO CHANGES
            #     [THESIS_SECTION] → Thesis title and bullets only if available in resume
            #     [CERTIFICATIONS_SECTION] → highlight the certificate only if available in resume
            #     [OPEN SOURCE CONTRIBUTION] → highlight contribution only if available in resume 

            #     *INSTRUCTION*:
            #     - dont change the format of latex template(like positions of each and every \\vspace{{-10pt}} ,\\noindent\\rule{{\\linewidth}}{{0.4pt}},\\section*{{[Experience]}}...etc),only use them as it is to fill info with given instructions and rules 
            #     - each sections have follow these 3 rules you have to consider and not to fail
            #         - [<BOLD TEXT>]: represent different section name use to identify correct sections below which its latex code is define eg. [SKILLS_SECTION],[EXPERIENCE_SECTION]... etc
            #         - [<Normal Text>]: use to put/inject the dynamic details or "Content's information" from resume/content to the latex code template eg. [Project Title],[Thesis Title]... etc
            #         - use → to specifies the following steps/instruction for every section has to follow eg. → One single line with hyperlinks,→ Format similar to projects: title + date + bullets... etc

            #     LaTeX Template:

            #     \\documentclass[a4paper,12pt]{{article}}
            #     \\usepackage[margin=1in]{{geometry}}
            #     \\usepackage{{hyperref}}
            #     \\usepackage{{enumitem}}

            #     \\begin{{document}}

            #     [EXTRACTED_PERSONAL_DETAIL]
            #     \\vspace{{-10pt}}  
            #     \\begin{{center}}
            #         \\Huge \\textbf{{[Candidate Name]}} \\\\ 
            #         \\small
            #         \\href{{[mailto:email@example.com]}}{{[email@example.com]}} \\ \\texttt{{|}}\\ [9999999999] \\ \\texttt{{|}}\\ \\ \\href{{[https://www.linkedin.com/in/candidate]}}{{[candidate_linkedin]}} \\ \\texttt{{|}}\\ \\ \\href{{[https://github.com/candidate]}}{{[candidate_github]}}
            #     \\end{{center}}
            #     → Candidate's full name from the top or header.
            #     → One single line with hyperlinks
            #     → If any missing → omit it. Use "None" only if absolutely no contact info

            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}}

            #     [SKILLS_SECTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Technical Skills]}}
            #     → Group into logical categories if present (e.g., Programming Languages, Frameworks & Tools, etc.)
            #     → Format as:
            #     \\noindent \\textbf{{[Category:]}} [Skill1, Skill2, Skill3] \\\\
            #     → If no categories → one flat list.

            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}}

            #     [EXPERIENCE_SECTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Experience]}}
            #     → For each job:
            #     \\noindent \\textbf{{[Job Title]}}, [Company Name] \\hfill {{[Start Year – End Year]}}  \\\\ 
            #     \\vspace{{-8pt}} 
            #     \\begin{{itemize}}[left=0pt, label=\\textbullet, itemsep=5pt]
            #     \\vspace{{-8pt}} 
            #         \\item [Rephrased bullet... ]
            #         \\vspace{{-8pt}} 
            #     \\end{{itemize}}

            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}} 

            #     [PROJECTS_SECTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Projects]}}
            #     → For each project:
            #     \\noindent \\textbf{{[Project Title]}} \\\\ 
            #     \\begin{{itemize}}[left=0pt, label=\\textbullet, itemsep=5pt]
            #     \\vspace{{-8pt}} 
            #         \\item [Rephrased bullet with \\textbf{{[skills]}} highlighted] 
            #         \\vspace{{-8pt}} 
            #     \\end{{itemize}}
            #     → If technologies listed under project name → put them in italics or parentheses.



            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}} 

            #     [ACHIEVEMENTS_SECTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Achievements & Hackathons]}}
            #     \\noindent \\textbf{{[Hackathon/Event Name]}}, [Location] \\\\ 
            #     → Format similar to projects: title + date + bullets.


            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}} 

            #     [EDUCATION_SECTION]:
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Education]}}
            #     → For each degree:
            #     \\noindent \\textbf{{[Degree Title]}} \\hfill {{[Start Year – End Year]}} \\\\ 
            #     [Institution Name] \\\\ 

            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}}

            #     [THESIS_SECTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Thesis]}}
            #     \\noindent \\textbf{{[Thesis Title]}} \\hfill {{[Start Year – End Year]}}\\\\ 
            #     → Title, supervisor, bullets.
                

            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}}

            #     [CERTIFICATIONS_SECTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Certifications]}}
            #     \\noindent \\textbf{{[Certification Title]}} \\hfill \\textbf{{[Certification Date]}} \\\\
                
            #     \\noindent\\rule{{\\linewidth}}{{0.4pt}}

            #     [OPEN SOURCE CONTRIBUTION]
            #     \\vspace{{-10pt}} 
            #     \\section*{{[Open Source Contributions]}}
            #     \\noindent \\textbf{{[Project Name or Repository]}} \\hfill \\textbf{{[Contribution Date]}} \\\\
            #     → Format similar to projects: title + date + bullets.

            #     \\end{{document}}
            

            #     OUTPUT ONLY THE VALID WORKING FINAL LaTeX CODE. 
            #     NO explanations, NO markdown, NO partial code, NO extra text,NO Hallucination.
            #     If you cannot fill a section with real data → remove that entire section/placeholder.
            #     """
            ###########################################################################################################################################################################

            prompt = f"""
                    YOU ARE A DETERMINISTIC RESUME FORMATTER AND COPY-EDITOR.

                    YOU ARE NOT AN IMPROVER, NOT AN OPTIMIZER, NOT A CREATOR.
                    YOU ARE ONLY ALLOWED TO COPY, LIGHTLY REPHRASE, AND REFORMAT TEXT THAT EXISTS VERBATIM IN THE RESUME.

                    IF YOU ADD EVEN ONE WORD, TOOL, METRIC, DATE, DEGREE, TITLE, SKILL, SUPERVISOR, TECHNOLOGY, OR IDEA
                    THAT DOES NOT APPEAR IN THE RESUME TEXT BELOW — THE OUTPUT IS INVALID.

                    ========================
                    SOURCE OF TRUTH — RESUME
                    ========================
                    \"\"\"{self.resume_text}\"\"\"

                    ========================
                    HARD CONSTRAINTS (ABSOLUTE)
                    ========================
                    - You MUST treat the resume text as the ONLY source of truth.
                    - You MUST NOT infer missing years, supervisors, locations, institutions, or outcomes.
                    - You MUST NOT normalize or “complete” partial information.
                    - You MUST NOT replace missing values with placeholders like [Year – Year], None, N/A, or similar.
                    - If any data is missing → DELETE THAT LINE OR ENTIRE SECTION.
                    - DO NOT mention tools, frameworks, APIs, models, metrics, cloud services, or libraries unless they are written EXACTLY in the resume.
                    - DO NOT introduce AWS, TensorFlow, supervisors, scores, rankings, accuracy, F1, percentages, or performance claims unless explicitly present.
                    - DO NOT change degree names, institute names, project titles, or event names.
                    - DO NOT summarize, extend, or generalize bullets.

                    ========================
                    CRITICAL CONTACT RULE
                    ========================
                    - CONTACT INFORMATION (email, phone, LinkedIn, GitHub) MUST APPEAR ONLY ONCE.
                    - CONTACT INFORMATION MUST APPEAR ONLY INSIDE THE CENTER BLOCK.
                    - DO NOT output contact details anywhere else.
                    - If a contact field is missing → omit ONLY that field.

                    ========================
                    SECTION CREATION GATE (CRITICAL)
                    ========================
                    A SECTION MAY BE CREATED **ONLY IF** THE RESUME TEXT CONTAINS AN EXPLICITLY LABELED SECTION
                    WITH A MATCHING OR EQUIVALENT TITLE.

                    STRICT RULES:
                    - EXPERIENCE SECTION:
                    Create ONLY if the resume explicitly contains a section labeled:
                    "Experience", "Work Experience", "Professional Experience", or "Employment".
                    PROJECT CONTENT MUST NEVER BE RECLASSIFIED AS EXPERIENCE.

                    - CERTIFICATIONS SECTION:
                    Create ONLY if the resume explicitly contains a section labeled:
                    "Certifications", "Certificates", or "Professional Certifications".
                    DO NOT treat courses, workshops, hackathons, or participation as certifications.

                    - THESIS SECTION:
                    Create ONLY if the resume explicitly contains a section labeled "Thesis" or "Dissertation".

                    - OPEN SOURCE CONTRIBUTIONS:
                    Create ONLY if explicitly labeled as "Open Source", "Open Source Contributions",
                    or similar.

                    - IF A SECTION HEADER DOES NOT EXIST IN THE RESUME → DELETE THAT ENTIRE SECTION
                    INCLUDING ITS HEADING AND RULE LINE.

                    ========================
                    ALLOWED OPERATIONS (ONLY THESE)
                    ========================
                    You may ONLY:
                    - Rephrase existing bullet points using stronger action verbs WITHOUT adding new meaning.
                    - Fix spacing, punctuation, or LaTeX escaping.
                    - Bold skills that ALREADY EXIST in the resume (\\textbf{{Skill}}).
                    - Reorder bullets within the SAME section without changing content.
                    - Convert plain text into valid LaTeX syntax.

                    ========================
                    LATEX TEMPLATE (IMMUTABLE)
                    ========================
                    You MUST use the following LaTeX structure EXACTLY.
                    DO NOT change spacing, commands, section order, or formatting.
                    ONLY replace placeholders with real extracted text OR delete the entire block.

                    \\documentclass[a4paper,12pt]{{article}}
                    \\usepackage[margin=1in]{{geometry}}
                    \\usepackage{{hyperref}}
                    \\usepackage{{enumitem}}

                    \\begin{{document}}

                    \\vspace{{-10pt}}  
                    \\begin{{center}}
                        \\Huge \\textbf{{[Candidate Name]}} \\\\ 
                        \\small
                        \\href{{mailto:[email]}}{{[email]}}
                        \\texttt{{|}} [phone]
                        \\texttt{{|}} \\href{{[linkedin_url]}}{{LinkedIn}}
                        \\texttt{{|}} \\href{{[github_url]}}{{GitHub}}
                    \\end{{center}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [SKILLS_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Technical Skills}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [EXPERIENCE_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Experience}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [PROJECTS_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Projects}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [ACHIEVEMENTS_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Achievements \\& Hackathons}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [EDUCATION_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Education}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [THESIS_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Thesis}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [CERTIFICATIONS_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Certifications}}

                    \\noindent\\rule{{\\linewidth}}{{0.4pt}}

                    [OPEN_SOURCE_SECTION]
                    \\vspace{{-10pt}}
                    \\section*{{Open Source Contributions}}

                    \\end{{document}}

                    ========================
                    FINAL OUTPUT RULE
                    ========================
                    - OUTPUT ONLY VALID, COMPILABLE LaTeX CODE.
                    - NO explanations.
                    - NO comments.
                    - NO markdown.
                    - NO placeholders.
                    - NO hallucinated content.
                    - IF A SECTION IS NOT EXPLICITLY PRESENT IN THE RESUME → DELETE IT COMPLETELY.
                    """


            try:
                # Step 1: Invoke LLM with the given prompt
                response = safe_llm_invoke(self.llm, prompt)
                
                # Step 2: Extract the LaTeX-formatted resume text
                print("✅ llm response of latex code")
                improved_resume = response.content.strip() # Remove unnecessary spaces
                # Step 3: Validate the LaTeX format
                if not improved_resume.startswith(r"\documentclass") or not improved_resume.endswith(r"\end{document}"):
                    print("❌ Generated content is not in valid LaTeX format")
                    raise ValueError("Generated content is not in valid LaTeX format.")

                # Step 5: Return the LaTeX resume content
                print("✅ generate latex code succesfully")
                print(improved_resume)
                return improved_resume

            except Exception as e:
                # Step 6: Error handling
                print(f"❌Error generating improved resume llm problem: {e}")
                return "Error generating improved resume llm problem . Please try again."
        except Exception as e:
            print(f"❌Error generating latex code: {e}")
            return "Error generating latex code. Please try again."
        

    def verify_and_correct_latex_resume(self, improved_resume, analysis_result,template):
        """Verify and correct the LaTeX resume by cross-referencing with the original resume data."""
        
        # Define the verification and correction prompt
        prompt = f"""
        IMPORTANT:
            - You MUST return a COMPLETE LaTeX document
            - Output MUST start with \\hdocumentclass
            - Output MUST end with \\end{{document}}
            - Do NOT return partial edits, explanations, or markdown
            - If no changes are required, return the original LaTeX unchanged

        You are a language model tasked with verifying and correcting a LaTeX code resume. The resume has been automatically generated by ai tool-"Improved Resume generator" based on the provided `resume_text` and `analysis_result`. Your task is to **cross-verify** the LaTeX code resume content and make any necessary corrections.

        Instructions:
        1. Review the LaTeX code resume provided below and ensure it **accurately reflects** the information in `resume_text` and `analysis_result`.
        2. Specifically, do the following:
            - **Ensure all sections are present and correctly labeled** (e.g., Experience, Skills, Education, Projects, Achievements, etc.).
            - **Ensure the content within each section** (e.g., job responsibilities, achievements, etc.) **matches the information** in `resume_text` and `analysis_result`. Cross-reference skills, job roles, responsibilities, achievements, and education.
            - **Ensure that no new content, fabricated achievements, or hallucinated details** are added to the LaTeX code resume. If any content in the LaTeX code does not exist in the `resume_text` or `analysis_result`, remove it or replace it with the correct information.
            - **Modify the LaTeX content if any discrepancies are found** (e.g., if a skill or achievement in the LaTeX code resume was not mentioned in the original data, remove or update it).
            - If any **missing sections** or incorrect details are found in the LaTeX code resume, correct them based on the original resume data.

        LaTeX code Resume:
        improved_resume={improved_resume}

        Original Resume Data:
        Resume Text: {self.resume_text}
        Comparison result with Job description
        Analysis Result: {analysis_result}

        Output:
        - **If the LaTeX code resume is correct and matches the original resume data**, simply return the original LaTeX code resume.
        - **If any corrections are needed**, update the content only in LaTeX code to ensure all content is correct. Provide the updated LaTeX code with corrections.
        - **Do not add new sections or content that doesn't exist in the original data.** Only modify or remove content that is incorrect or fabricated.

        **Return the LaTeX code with the corrected content in template skeleton-{template} and return the same output format as "improved_resume"**.
        """

        try:
            # Step 1: Invoke LLM with the verification and correction prompt
            response = safe_llm_invoke(self.llm, prompt)
            
            # Step 2: Extract the updated LaTeX content
            corrected_resume = self.clean_latex(response.content.strip())
            
            if not corrected_resume:
                raise ValueError("The LLM response did not return any LaTeX code.")
            
            # Step 4: Validate the LaTeX format
            if not corrected_resume.startswith(r"\documentclass") or not corrected_resume.endswith(r"\end{document}"):
                raise ValueError("The corrected LaTeX content is not valid LaTeX format.")
            
            # Step 5: Save the LaTeX resume to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tex', mode='w', encoding='utf-8') as tmp:
                tmp.write(corrected_resume)
                self.improved_resume_path = tmp.name  # Save the path to the file for later use
            
            # Step 3: Return the corrected LaTeX code
            print("✅ LaTeX resume has been verified and corrected.")
            return corrected_resume

        except Exception as e:
            raise ValueError(f"Error during LaTeX resume verification and correction: {e}")
            return improved_resume

    def clean_latex(self,text: str) -> str:
        start = text.find(r"\documentclass")
        end = text.rfind(r"\end{document}")
        if start != -1 and end != -1:
            return text[start:end + len(r"\end{document}")]
        return text

 
    

########################################################################################################################################################################################################

import streamlit as st
class Implement:
    def __init__(self):
        self.agent=ResumeAnalysisAgent()

    def analyze_resume(self,resume_file,role=None,custom_jd=None):
        """Analyze the resume with the agent"""
        return self.agent.analyze_system(resume_file,role,custom_jd)
    
        
    def ask_question(self,question):
        """Ask a question about the resume"""
        try:
            with st.spinner("Generating response..."):
                response=self.agent.ask_question(question)
                return response
        except Exception as e:
            return f"Error: {e}"
        
    def generate_interview_questions(self,question_types,difficulty,num_questions):
        """Generate interview question based on the resume"""
        try:
            with st.spinner("Generating personalized interview questions..."):
                questions=self.agent.generate_interview_questions(question_types,difficulty,num_questions)
                return questions
            
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return []
        
    def improve_resume(self,improvement_areas,target_role):
        """Generate resume improvement suggestions"""
        try:
            with st.spinner("Analyzing and generating improvements...."):
                return self.agent.improve_resume(improvement_areas,target_role)
        except Exception as e:
            st.error(f"Error generating improvements: {e}")
            return {}
            
    def get_improved_resume(self,target_role,highlight_skills):
        """Get an improved version of the resume"""
        try:
            with st.spinner("Creating improved resume..."):
                return self.agent.get_improved_resume(target_role,highlight_skills)
        except Exception as e:
            st.error(f"Error creating improved resume: {e}")
            return "Error generating improved resume."
