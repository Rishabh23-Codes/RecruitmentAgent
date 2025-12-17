import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from config import LLM_MODEL,GROQ_API_KEY
from langchain_ollama.chat_models import ChatOllama


class ResumeContextExtractor:
    """
    RAG-based resume context extractor.
    Uses embeddings + LLM instead of regex & hardcoded rules.
    """

    def __init__(self):
        # self.llm = ChatGroq(model=LLM_MODEL,api_key=GROQ_API_KEY)
        self.llm=ChatOllama(model=LLM_MODEL,temperature=0)
        self.embeddings =HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

        self.prompt = ChatPromptTemplate.from_template(
                    """You are an expert resume parser.
        Use ONLY the provided resume context.
        Be concise and factual.

        Context:
        {context}

        Task:
        {question}

        Answer:"""
                )

        self.output_parser = StrOutputParser()

    def _build_rag_chain(self, resume_text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_text(resume_text)

        vectorstore = FAISS.from_texts(
            texts=chunks,
            embedding=self.embeddings
        )

        retriever = vectorstore.as_retriever()

        rag_chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | self.output_parser
        )

        return rag_chain


    def extract_keywords(self, resume_text, max_keywords=10):
        rag_chain = self._build_rag_chain(resume_text)

        response = rag_chain.invoke(
            f"Extract the {max_keywords} most important keywords for job search. "
            "Include technical skills, tools, roles, and domains. "
            "Return a comma-separated list of main keywords terms only."
        )

        keywords = [
            k.strip()
            for k in re.split(r"[,\n•\-]", response)
            if 1 < len(k.strip()) < 50
        ]

        return keywords[:max_keywords]


    def extract_job_title(self, resume_text):
        rag_chain = self._build_rag_chain(resume_text)

        response = rag_chain.invoke(
            "What is the most likely primary job title of this candidate? "
            "Return a single job title only."
        )

        return response.strip().lower()

    def extract_full_context(self, resume_text):
        rag_chain = self._build_rag_chain(resume_text)

        response = rag_chain.invoke(
            """Extract the resume into the following structure:

            - Skills (comma-separated)
            - Education (one entry per line)
            - Experience (one role per line)
            - Most likely job title

            Be concise."""
                    )

        return response
