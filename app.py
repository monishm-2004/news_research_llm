"""
Streamlit Web UI for News Research Tool
"""
import os

# Set User-Agent BEFORE importing anything else
os.environ["USER_AGENT"] = "MyNewsResearchApp/1.0"

import streamlit as st
from dotenv import load_dotenv
from news_research import NewsResearchTool
from pathlib import Path

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="News Research Tool",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > label, .stTextArea > label {
        font-weight: 600;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "research_tool" not in st.session_state:
        st.session_state.research_tool = None
    if "vector_store_loaded" not in st.session_state:
        st.session_state.vector_store_loaded = False
    if "query_history" not in st.session_state:
        st.session_state.query_history = []


def setup_api_key():
    """Setup and validate Google API key"""
    # Try to get from .env file first (more reliable)
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Fallback to secrets if available
    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            pass
    
    if not api_key:
        st.error("❌ Google API key not found. Please set GOOGLE_API_KEY in .env file")
        st.stop()
    
    return api_key


def load_documents_section():
    """Section for loading documents"""
    st.header("📚 Load News Documents")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("From Local Files")
        uploaded_file = st.file_uploader(
            "Upload .txt files",
            type="txt",
            accept_multiple_files=True,
            help="Upload text files containing news articles"
        )
    
    with col2:
        st.subheader("From Web URLs")
        urls_text = st.text_area(
            "Enter URLs (one per line)",
            height=150,
            placeholder="https://example.com/news1\nhttps://example.com/news2",
            help="Paste URLs of news articles to scrape"
        )
    
    return uploaded_file, urls_text


def process_documents(api_key, uploaded_files, urls_text):
    """Process uploaded documents and URLs"""
    file_paths = []
    urls = []
    
    # Save uploaded files temporarily
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
    
    # Parse URLs
    if urls_text:
        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]
    
    if not file_paths and not urls:
        st.warning("⚠️ Please provide either files or URLs")
        return False
    
    try:
        with st.spinner("🔄 Processing documents..."):
            tool = NewsResearchTool(api_key)
            tool.process_news_sources(file_paths=file_paths, urls=urls)
            st.session_state.research_tool = tool
            st.session_state.vector_store_loaded = True
            
            st.success("✅ Documents processed successfully!")
            
            # Save vector store info
            st.info("📊 Vector store created and saved locally for future use")
        
        # Cleanup temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return True
    except Exception as e:
        st.error(f"❌ Error processing documents: {str(e)}")
        return False


def query_section():
    """Section for querying the news database"""
    st.header("❓ Ask Questions About News")
    
    if not st.session_state.vector_store_loaded:
        st.info("📌 Please load documents first from the sidebar")
        return
    
    # Query input
    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What is the price of Tesla stock?",
        help="Ask any question about the loaded news articles"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_button = st.button("🔍 Search", use_container_width=True)
    with col2:
        load_existing_button = st.button("📂 Load Existing Index", use_container_width=True)
    with col3:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    if search_button and question:
        with st.spinner("🔄 Searching..."):
            result = st.session_state.research_tool.query(question)
            
            if result["success"]:
                st.session_state.query_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "sources": result["sources"]
                })
                
                # Display results
                st.subheader("📖 Answer")
                st.write(result["answer"])
                
                if result["sources"]:
                    st.subheader("🔗 Sources")
                    st.write(result["sources"])
            else:
                st.error(f"❌ {result['answer']}")
    
    if load_existing_button:
        api_key = setup_api_key()
        try:
            with st.spinner("📂 Loading existing vector store..."):
                tool = NewsResearchTool(api_key)
                tool.load_vector_store()
                st.session_state.research_tool = tool
                st.session_state.vector_store_loaded = True
                st.success("✅ Vector store loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading vector store: {str(e)}")
    
    if clear_button:
        st.session_state.query_history = []
        st.success("✅ History cleared")
    
    # Display query history
    if st.session_state.query_history:
        st.subheader("📋 Query History")
        for i, item in enumerate(st.session_state.query_history, 1):
            with st.expander(f"Query {i}: {item['question'][:50]}..."):
                st.write(f"**Q:** {item['question']}")
                st.write(f"**A:** {item['answer']}")
                if item['sources']:
                    st.write(f"**Sources:** {item['sources']}")


def sidebar():
    """Sidebar configuration"""
    st.sidebar.title("⚙️ Configuration")
    
    # API Key status - safely check both sources
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            pass
    
    if api_key:
        st.sidebar.success("✅ Google API Key Configured")
    else:
        st.sidebar.error("❌ Google API Key Missing")
    
    st.sidebar.divider()
    
    # Document loading section
    st.sidebar.header("📚 Load Documents")
    
    uploaded_files, urls_text = load_documents_section()
    
    if st.sidebar.button("📤 Process Documents", use_container_width=True):
        api_key = setup_api_key()
        process_documents(api_key, uploaded_files, urls_text)
    
    st.sidebar.divider()
    
    # Status
    st.sidebar.header("📊 Status")
    if st.session_state.vector_store_loaded:
        st.sidebar.success("✅ Vector Store Loaded")
    else:
        st.sidebar.info("⏳ Waiting for documents...")
    
    st.sidebar.divider()
    
    # Help
    st.sidebar.header("ℹ️ Help")
    st.sidebar.markdown("""
    **How to use:**
    1. Upload text files or paste URLs in the sidebar
    2. Click "Process Documents"
    3. Ask questions in the main area
    
    **Supported formats:**
    - Text files (.txt)
    - Web URLs
    
    **Tips:**
    - Be specific with your questions
    - Sources will be provided with answers
    - Your query history is saved during the session
    """)


def main():
    """Main application"""
    st.title("📰 News Research Tool")
    st.markdown("*Powered by LangChain & Google Generative AI*")
    
    initialize_session_state()
    
    # Setup API key
    try:
        api_key = setup_api_key()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()
    
    # Sidebar
    sidebar()
    
    st.divider()
    
    # Main content
    query_section()
    
    # Footer
    st.divider()
    st.markdown("""
    ---
    **Built with** Streamlit, LangChain, and Google Generative AI  
    *For more information, visit [LangChain Documentation](https://python.langchain.com/)*)
    """)


if __name__ == "__main__":
    main()
