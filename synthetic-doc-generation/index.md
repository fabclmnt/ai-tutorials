# Build and Test Document-Based AI Agents with Synthetic Data

Welcome to this hands-on workshop on building and testing document-based AI agents using synthetic data! This workshop will guide you through creating a complete RAG (Retrieval-Augmented Generation) system with multiple specialized AI agents.

## 🎯 Workshop Overview

In this workshop, you'll learn to:

1. **Generate Synthetic Documents** - Create realistic invoices and bank statements using GenAI
2. **Split, Embed & Store in Vector Database** - Process documents and build a searchable knowledge base
3. **Build a Retrieval-Augmented Agent** - Create an AI agent that can answer questions about your documents
4. **Extend to Multi-Agent Systems** - Build specialized agents that work together

## 🛠️ Prerequisites

- Python 3.12+
- Basic understanding of Python
- Familiarity with AI/ML concepts (helpful but not required)

## 📋 Setup Instructions

### 1. Environment Setup

```bash
# Clone or navigate to the workshop directory
cd synthetic-doc-generation

# Option A: Using conda (recommended)
conda env create -f environment.yml
conda activate synthetic-doc-generation

# Option B: Using pip
pip install -r requirements.txt
```

### 2. API Keys Setup

You'll need to set up API keys for the AI services:

```bash
# Required: YData SDK License Key
export YDATA_LICENSE_KEY='your-ydata-license-key'

# Optional: OpenAI API Key (for enhanced AI responses)
export OPENAI_API_KEY='your-openai-api-key'
```

**Getting API Keys:**
- **YData SDK**: Sign up at [ydata.ai](https://ydata.ai) for a free license
- **OpenAI**: Get an API key from [platform.openai.com](https://platform.openai.com)

## 🚀 Workshop Steps

### Step 1: Generate Synthetic Documents

Let's start by creating realistic synthetic documents using the YData SDK.

```bash
python generate_documents.py
```

**What this does:**
- Generates 5 corporate invoices with detailed line items
- Creates 3 retail/supermarket invoices 
- Produces 4 bank statements with transaction history
- Saves all documents as PDFs in the `synthetic_pdfs/` directory

**Expected Output:**
```
🚀 Synthetic Document Generation for AI Agent Workshop
============================================================
✅ License key found: abc12345...
📄 Initializing Document Generator...

=== Generating 5 Corporate Invoices ===
=== Generating 3 Retail Invoices ===
=== Generating 4 Bank Statements ===

✅ Successfully generated 12 documents:
   📁 Output directory: /path/to/synthetic_pdfs
   📄 Corporate invoices: 5
   🛒 Retail invoices: 3
   🏦 Bank statements: 4
```

### Step 2: Process Documents and Build Vector Database

Now let's process these documents and build a searchable vector database using FAISS.

```bash
python ai_agent.py
```

**What this does:**
- Extracts text from all PDF documents
- Splits text into manageable chunks (900 characters with 120 overlap)
- Creates embeddings using sentence-transformers
- Builds a FAISS vector index for fast similarity search
- Saves the index and document metadata for reuse

**Key Components:**
- **Text Extraction**: Uses `pypdf` to extract text from PDFs
- **Chunking**: Uses LangChain's `RecursiveCharacterTextSplitter`
- **Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` model
- **Vector DB**: FAISS for fast similarity search with cosine similarity

### Step 3: Test Single Agent Q&A

The script will automatically test the AI agent with sample questions:

```
Q: Which vendors appear on the invoices?
A: [Agent retrieves relevant chunks and provides answer]

Q: What invoice has the highest total?
A: [Agent analyzes invoice totals and identifies the highest]

Q: List any transactions with negative amounts.
A: [Agent finds negative transactions across documents]
```

### Step 4: Multi-Agent System

Let's extend our system to use multiple specialized agents:

```bash
python multi_agent_system.py
```

**Specialized Agents:**
- **Invoice Analyzer**: Specializes in invoice-related queries
- **Payment Verifier**: Focuses on payment and transaction analysis  
- **Summary Agent**: Provides high-level summaries and insights

## 🔧 Technical Deep Dive

### Vector Database Architecture

We use **FAISS** (Facebook AI Similarity Search) as our open-source vector database:

```python
# FAISS Index Configuration
- Index Type: IndexFlatIP (Inner Product for cosine similarity)
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
- Dimensions: 384 (from the embedding model)
- Normalization: L2 normalization for cosine similarity
```

### Document Processing Pipeline

```
PDF Documents → Text Extraction → Text Chunking → Embeddings → FAISS Index
     ↓              ↓              ↓            ↓           ↓
  Raw PDFs    →  Plain Text  →  Chunks    →  Vectors  →  Searchable DB
```

### Agent Architecture

Our agents use **Pydantic AI** framework:

```python
@agent.tool
def retrieve(ctx: RAGContext, query: str, k: int = 5) -> List[RetrievedChunk]:
    """Retrieve top-k document chunks relevant to query"""
    results = ctx.vector_index.search(query, ctx.docs, k=k)
    return [RetrievedChunk(...) for r in results]
```

## 🧪 Testing Your System

### Sample Queries to Try

**Invoice Analysis:**
- "What is the total amount for invoice INV-1003?"
- "Which vendor has the highest invoice total?"
- "List all invoices from last month"

**Payment Analysis:**
- "What payment methods are used across all documents?"
- "Are there any overdue payments?"
- "What is the average transaction amount?"

**Cross-Document Queries:**
- "Find all transactions over $1000"
- "Which documents mention tax calculations?"
- "Summarize all payment terms across invoices"

### Performance Testing

```python
# Test retrieval speed
import time
start = time.time()
results = vector_index.search("test query", docs, k=5)
print(f"Retrieval time: {time.time() - start:.3f}s")
```

## 🎨 Customization Options

### Modify Document Types

Edit `generate_documents.py` to create different document types:

```python
# Add new document types
generator.generate(
    document_type="Contract",
    audience="Legal team",
    tone="formal",
    purpose="Generate legal contracts with terms and conditions",
    # ... other parameters
)
```

### Adjust Chunking Strategy

Modify chunking parameters in `ai_agent.py`:

```python
CHUNK_SIZE = 1200      # Larger chunks for more context
CHUNK_OVERLAP = 200    # More overlap for better continuity
```

### Change Embedding Model

Switch to different embedding models:

```python
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Better quality
# or
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual
```

## 🚨 Troubleshooting

### Common Issues

**1. YData License Key Error**
```
Error: YDATA_LICENSE_KEY environment variable not set
```
**Solution**: Set your license key: `export YDATA_LICENSE_KEY='your-key'`

**2. OpenAI API Error**
```
Error: OpenAI API key not configured
```
**Solution**: Set your OpenAI key or the system will use fallback mode

**3. PDF Processing Error**
```
Error: No PDFs found in synthetic_pdfs/
```
**Solution**: Run `python generate_documents.py` first

**4. Memory Issues with Large Documents**
```
Error: Out of memory during embedding
```
**Solution**: Reduce `CHUNK_SIZE` or process documents in batches

### Performance Optimization

**For Large Document Collections:**
- Use `faiss-gpu` instead of `faiss-cpu` if you have a GPU
- Implement batch processing for embeddings
- Use more efficient chunking strategies

**For Better Accuracy:**
- Increase `CHUNK_OVERLAP` for better context continuity
- Use larger embedding models (trade-off: slower processing)
- Implement re-ranking for retrieved results

## 📚 Next Steps

### Extensions to Try

1. **Add More Document Types**: Contracts, reports, emails
2. **Implement Hybrid Search**: Combine vector search with keyword search
3. **Add Document Metadata**: Store creation dates, document types, etc.
4. **Build a Web Interface**: Create a simple web app for querying
5. **Add Evaluation Metrics**: Measure retrieval accuracy and response quality

### Production Considerations

1. **Scalability**: Use distributed vector databases (Pinecone, Weaviate)
2. **Security**: Implement access controls and data encryption
3. **Monitoring**: Add logging and performance metrics
4. **Caching**: Cache frequent queries and embeddings
5. **Error Handling**: Robust error handling and fallback mechanisms

## 🤝 Contributing

Found a bug or have an improvement idea? Feel free to:
- Open an issue
- Submit a pull request
- Share your custom document types or agent configurations

## 📖 Additional Resources

- [YData SDK Documentation](https://docs.sdk.ydata.ai/)
- [FAISS Documentation](https://faiss.ai/)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [Sentence Transformers Documentation](https://www.sbert.net/)

---

**Happy Building! 🚀**

This workshop provides a solid foundation for building production-ready document-based AI agents. The techniques you learn here can be applied to various domains including legal document analysis, financial report processing, and customer support automation.
