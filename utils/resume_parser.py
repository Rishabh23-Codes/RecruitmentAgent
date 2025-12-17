import tempfile
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from config import GROQ_API_KEY,LLM_MODEL
from langchain_ollama.chat_models import ChatOllama

class ResumeParser:
    """Enhanced tool for parsing resume files and extracting structured information."""

    def __init__(self):
        """Initialize the parser with huggingface components for RAG"""
        self.use_rag=False
        try:
            self.embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
            # self.llm=ChatGroq(model=LLM_MODEL,api_key=GROQ_API_KEY)
            self.llm=ChatOllama(model=LLM_MODEL,temperature=0)
            self.use_rag=True
        except Exception as e:
            print(f"Error: {e}")
            self.use_rag=False

    def save_uploaded_file(self,uploaded_file):
        """Save an uploaded file to a temporary location"""
        with tempfile.NamedTemporaryFile(delete=False,suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getbuffer())
            return tmp.name
        
    def parse_resume(self,text):
        """Parse a resume text and extract structured information.
        
        Args:
            text (str): The raw text content of the resume 
            
        Returns:
            dict: Structured information from the resume"""
        
        if not text:
            return None
        
        structured_data=self.extract_information(text)

        return structured_data
    
    def extract_information(self,text):
        """Extract structured information from resume text."""

        # Initialize categories
        skills=[]
        education=[]
        experience=[]
        contact_info={"email":"","phone":""}

        # Extract email and phone using regex
        email_pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails=re.findall(email_pattern,text)
        if emails:
            contact_info["email"]=emails[0]

        phone_pattern=r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phones=re.findall(phone_pattern,text)
        if phones:
            contact_info["phone"]=phones[0]

        if self.use_rag:
            try:
                # Create embeddings from the resume text
                text_splitter=RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )

                texts=text_splitter.split_text(text=text)

                # Create the vectorstore
                vectorstore=FAISS.from_texts(texts=texts,embedding=self.embeddings)

                # Create the retrieval chain
                retriever=vectorstore.as_retriever()

                prompt=ChatPromptTemplate.from_template("""
                    You are a resume extraction expert. 
                    Use ONLY the resume context below to extract information. 
                    If information is not found in the context, say "Not found".
                    Be precise and structured in your responses.

                    Context:
                    {context}

                    Question:
                    {question}
                """)

                rag_chain=(
                    {
                        "context": retriever,
                        "question": RunnablePassthrough()
                    } | prompt | self.llm | StrOutputParser()

                )

                 # Extract skills using RAG
                rag_skills_response=rag_chain.invoke("List all technical skills, programming languages, frameworks, "
                                                     "databases, and tools mentioned in this resume. "
                                                     "Return only a comma-separated list.")
                if rag_skills_response:
                    # Process the response, assuming it's a list or comma-separated skills
                    rag_skills=[s.strip() for s in re.split(r'[,\n•-]',rag_skills_response) if s.strip()]
                    for skill in rag_skills:
                        if skill and len(skill)<50: # Avoid adding long text chunks as skills
                            skills.append(skill)
                

                # Extract education using RAG
                rag_education_response=rag_chain.invoke("Extract all education details including institution, degree, "
                                                        "field of study, and graduation dates from the resume. "
                                                        )
                if rag_education_response:
                    # Process the education information
                    rag_education=[e.strip() for e in rag_education_response.split('\n') if e.strip()]
                    for edu in rag_education:
                        if edu and not any(edu in existing_edu for existing_edu in education):
                            education.append(edu)


                # Extract work experience using RAG
                rag_experience_reponse=rag_chain.invoke("Extract all work experience including company name, job title, "
                                                        "employment dates, and key responsibilities from the resume. ")
                if rag_experience_reponse:
                    # Process the experience information
                    rag_experience=[e.strip() for e in rag_experience_reponse.split('\n') if e.strip()]
                    for exp in rag_experience:
                        if exp and len(exp)>20 and not any(exp in existing_exp for existing_exp in experience):
                            experience.append(exp)


            except Exception as e:
                print(f"RAG extraction error: {e}")
        return {
            "raw_text": text,
            "skills": list(set(skills)),
            "education": list(set(education)),
            "experience": list(set(experience)),
            "contact_info": contact_info

        }
                            


                

