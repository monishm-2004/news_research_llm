# 📰 News Research Tool with Streamlit

A modern web application for researching and querying news articles using LangChain, FAISS, and Google Generative AI. Ask questions about news content and get answers with source citations.

## Features

 **Key Features:**
-  Upload text files with news articles
-  Scrape and process web URLs
-  Semantic search using FAISS vector database
-  AI-powered question answering with Google Generative AI
-  Source citation and tracking
-  Persistent vector store for future queries
-  Clean, intuitive Streamlit UI



## Prerequisites

- Python 3.9+
- Google API Key (with Generative AI access)
- pip package manager

## Installation

### 1. Clone/Copy the Project

```bash
cd news_research_app
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup API Key

**Option A: Using `.env` file**
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

**Option B: Using Streamlit Secrets**
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your Google API key
```

### 5. Get Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy the generated API key
4. Add it to `.env` or `.streamlit/secrets.toml`

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### How to Use

1. **Load Documents:**
   - Use the sidebar to upload `.txt` files OR
   - Paste URLs of news articles (one per line)
   - Click "Process Documents"

2. **Ask Questions:**
   - Type your question in the main area
   - Click "Search"
   - View the AI-generated answer with sources

3. **Load Existing Index:**
   - If you've previously processed documents, use "Load Existing Index" button
   - This loads the saved FAISS vector store for faster querying

4. **View Query History:**
   - Your questions and answers are automatically saved
   - Expand any entry to see full details including sources

## Example Queries

- "What is the price of the new car model?"
- "Who was appointed as the CEO?"
- "What are the main economic impacts mentioned?"
- "Summarize the key points about the stock market"

## Architecture

### Data Flow

```
News Sources (Files/URLs)
        ↓
   TextLoader / WebBaseLoader
        ↓
   RecursiveCharacterTextSplitter
        ↓
   Google Generative AI Embeddings
        ↓
   FAISS Vector Store
        ↓
   RetrievalQAWithSourcesChain
        ↓
   Google Generative AI (gemini-2.5-flash)
        ↓
   Streamlit UI Display
```

### Key Components

- **NewsResearchTool** (`news_research.py`): Core backend class handling document processing and RAG
- **Streamlit App** (`app.py`): User interface with sidebar for configuration
- **FAISS**: Vector database for efficient semantic search
- **LangChain**: Framework for building RAG chains
- **Google Generative AI**: LLM for answer generation

## Configuration

### Streamlit Config (`config.toml`)

Customize theme colors and other settings:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## Troubleshooting

**Issue: "Google API key not found"**
- Ensure `.env` or `.streamlit/secrets.toml` is properly configured
- Verify the API key is valid

**Issue: "Error loading vector store"**
- Delete old vector store files: `vector_index.faiss` and `vector_index.pkl`
- Re-process your documents

**Issue: "WebBaseLoader errors"**
- Some websites may block automated scraping
- Try using text files instead
- Add proper User-Agent headers if needed

## Performance Tips

1. **Chunk Size**: Adjust `chunk_size` in `split_documents()` for different document types
2. **Embeddings**: Google Generative AI embeddings are faster than some alternatives
3. **Vector Store**: FAISS is optimized for semantic search on local machines
4. **Caching**: Streamlit automatically caches function results

## Future Enhancements

- 🔐 User authentication
- 📈 Multiple vector store management
- 🌍 Multi-language support
- 📊 Analytics dashboard
- 🔄 Real-time news updates
- 💬 Chat interface for multi-turn conversations

## Dependencies Overview

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` | LLM orchestration framework |
| `langchain-community` | Community document loaders |
| `langchain-google-genai` | Google AI integration |
| `google-generativeai` | Generative AI API |
| `faiss-cpu` | Vector similarity search |
| `beautifulsoup4` | HTML parsing |
| `python-dotenv` | Environment variable management |

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review [LangChain Documentation](https://python.langchain.com/)
3. Check [Google AI Studio](https://aistudio.google.com/)

## Author Notes

This project demonstrates:
- Modern RAG (Retrieval-Augmented Generation) architecture
- Integration of multiple AI services
- Production-ready Streamlit applications
- Document processing and embedding workflows

---

**Happy researching! 🚀**
