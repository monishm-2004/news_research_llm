"""
News Research Tool Backend
Handles document loading, embedding, and RAG chain operations
"""

import os
import pickle
from typing import List, Dict, Tuple
from langchain_community.document_loaders import TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQAWithSourcesChain
import google.genai as genai


class NewsResearchTool:
    """Main class for news research using LangChain and Google Generative AI"""

    def __init__(self, google_api_key: str):
        """Initialize the news research tool with API key"""
        self.google_api_key = google_api_key
        os.environ["GOOGLE_API_KEY"] = google_api_key
        genai.configure(api_key=google_api_key)

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview"
        )
        self.vector_store = None
        self.chain = None
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", google_api_key=google_api_key
        )

    def load_text_file(self, file_path: str) -> List:
        """Load text file using TextLoader"""
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Error loading text file: {str(e)}")

    def load_web_urls(self, urls: List[str]) -> List:
        """Load documents from web URLs"""
        try:
            loader = WebBaseLoader(urls)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Error loading web URLs: {str(e)}")

    def split_documents(self, documents: List, chunk_size: int = 1000, chunk_overlap: int = 100) -> List:
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        docs = text_splitter.split_documents(documents)
        return docs

    def create_vector_store(self, documents: List, index_name: str = "vector_index") -> None:
        """Create FAISS vector store from documents"""
        try:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            self.save_vector_store(index_name)
            self.initialize_chain()
        except Exception as e:
            raise Exception(f"Error creating vector store: {str(e)}")

    def save_vector_store(self, index_name: str = "vector_index", folder_path: str = ".") -> None:
        """Save FAISS vector store locally"""
        try:
            if self.vector_store:
                self.vector_store.save_local(
                    folder_path=folder_path, index_name=index_name
                )
        except Exception as e:
            raise Exception(f"Error saving vector store: {str(e)}")

    def load_vector_store(self, index_name: str = "vector_index", folder_path: str = ".") -> None:
        """Load FAISS vector store from local storage"""
        try:
            self.vector_store = FAISS.load_local(
                folder_path=folder_path,
                embeddings=self.embeddings,
                index_name=index_name,
                allow_dangerous_deserialization=True,
            )
            self.initialize_chain()
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")

    def initialize_chain(self) -> None:
        """Initialize the retrieval QA chain"""
        if self.vector_store and self.llm:
            self.chain = RetrievalQAWithSourcesChain.from_llm(
                llm=self.llm, retriever=self.vector_store.as_retriever()
            )

    def query(self, question: str) -> Dict:
        """Ask a question and get an answer with sources"""
        if not self.chain:
            raise Exception("Chain not initialized. Please load documents first.")

        try:
            result = self.chain.invoke({"question": question})
            return {
                "answer": result.get("answer"),
                "sources": result.get("sources"),
                "success": True,
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": "",
                "success": False,
            }

    def process_news_sources(self, file_paths: List[str] = None, urls: List[str] = None) -> None:
        """
        Process news from files and/or URLs
        
        Args:
            file_paths: List of text file paths
            urls: List of web URLs to scrape
        """
        all_documents = []

        # Load from text files
        if file_paths:
            for file_path in file_paths:
                try:
                    docs = self.load_text_file(file_path)
                    all_documents.extend(docs)
                except Exception as e:
                    print(f"Error loading file {file_path}: {str(e)}")

        # Load from URLs
        if urls:
            try:
                docs = self.load_web_urls(urls)
                all_documents.extend(docs)
            except Exception as e:
                print(f"Error loading URLs: {str(e)}")

        if all_documents:
            # Split documents into chunks
            split_docs = self.split_documents(all_documents)
            # Create vector store
            self.create_vector_store(split_docs)
        else:
            raise Exception("No documents were loaded")
