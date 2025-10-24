# Document-Based AI Agents Workshop

This workshop demonstrates how to build and test document-based AI agents using synthetic data.

## Quick Start

1. **Setup Environment**
   ```bash
   conda env create -f environment.yml
   conda activate synthetic-doc-generation
   ```

2. **Set API Keys**
   ```bash
   export YDATA_LICENSE_KEY='your-ydata-license-key'
   export OPENAI_API_KEY='your-openai-api-key'  # Optional
   ```

## Workshop Files

- `generate_documents.py` - Creates synthetic invoices and bank statements using ydata-sdk
- `ai_agent.py` - Single-agent RAG system with FAISS vector database
- `multi_agent_system.py` - Multi-agent system with specialized agents
- `index.md` - Comprehensive workshop documentation
- `requirements.txt` - Python dependencies
- `environment.yml` - Conda environment specification

## Workshop Steps

1. **Generate Synthetic Documents** - Create realistic test data
2. **Build Vector Database** - Process documents with FAISS
3. **Single Agent Q&A** - Basic RAG system
4. **Multi-Agent System** - Specialized agents working together

See `index.md` for detailed instructions and explanations.
