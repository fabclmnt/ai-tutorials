"""
Multi-Agent Document Analysis System

This script extends the single-agent system to demonstrate multi-agent coordination
for document-based AI systems. It includes specialized agents for different tasks:

1. Invoice Analyzer Agent - Specializes in invoice-related queries
2. Payment Verifier Agent - Focuses on payment and transaction analysis
3. Summary Agent - Provides high-level summaries and insights
4. Coordinator Agent - Routes queries to appropriate specialists

The system demonstrates:
- Agent specialization and expertise
- Query routing and delegation
- Multi-agent coordination
- Fallback mechanisms
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from enum import Enum

# Import existing components
from ai_agent import (
    VectorIndex, RAGContext, RetrievedChunk, 
    ensure_pdfs_present, load_corpus_from_pdfs, 
    chunk_documents, extract_text_from_pdf,
    INDEX_PATH, DOCS_JSONL, EMBED_MODEL, MODEL_NAME, OPENAI_API_KEY
)

# Multi-agent imports
try:
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic import BaseModel, Field
    PAI_OK = True
except Exception:
    PAI_OK = False

# ---------------------------
# Multi-Agent System Configuration
# ---------------------------

class AgentType(Enum):
    INVOICE_ANALYZER = "invoice_analyzer"
    PAYMENT_VERIFIER = "payment_verifier"
    SUMMARY_AGENT = "summary_agent"
    COORDINATOR = "coordinator"

class QueryIntent(BaseModel):
    """Classify the intent of a user query"""
    intent: str = Field(description="The classified intent: invoice_analysis, payment_verification, summary, or general")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Explanation of the classification")

class AgentResponse(BaseModel):
    """Response from a specialized agent"""
    agent_type: str
    response: str
    confidence: float
    sources_used: List[str]
    reasoning: str

class MultiAgentDeps(BaseModel):
    """Dependencies for multi-agent system - holds vector index and documents"""
    vector_index: VectorIndex
    docs: List[Dict]
    
    class Config:
        arbitrary_types_allowed = True

# ---------------------------
# Specialized Agent Definitions
# ---------------------------

if PAI_OK:
    # Initialize models
    model = OpenAIModel(MODEL_NAME, api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    # Invoice Analyzer Agent
    invoice_agent = Agent(
        model=model,
        deps_type=MultiAgentDeps,
        system_prompt=(
            "You are an Invoice Analysis Specialist. You excel at analyzing invoices, "
            "extracting financial data, identifying vendors, calculating totals, and "
            "understanding invoice structures. Focus on invoice-specific queries and "
            "provide detailed financial analysis. Always cite specific invoice details "
            "and line items when available."
        )
    )
    
    @invoice_agent.tool
    def retrieve_invoice_data(ctx: RunContext[MultiAgentDeps], query: str, k: int = 5) -> List[RetrievedChunk]:
        """Retrieve invoice-specific information"""
        results = ctx.deps.vector_index.search(query, ctx.deps.docs, k=k)
        # Filter for invoice-related content
        invoice_results = [r for r in results if 'invoice' in r['source'].lower() or 'inv-' in r['text'].lower()]
        return [RetrievedChunk(source=r["source"], score=r["score"], text=r["text"]) for r in invoice_results]
    
    # Payment Verifier Agent
    payment_agent = Agent(
        model=model,
        deps_type=MultiAgentDeps,
        system_prompt=(
            "You are a Payment Verification Specialist. You focus on payment methods, "
            "transaction verification, payment terms, due dates, and financial compliance. "
            "You excel at identifying payment patterns, verifying transaction details, "
            "and ensuring payment accuracy. Always provide specific payment information "
            "and highlight any discrepancies or issues."
        )
    )
    
    @payment_agent.tool
    def retrieve_payment_data(ctx: RunContext[MultiAgentDeps], query: str, k: int = 5) -> List[RetrievedChunk]:
        """Retrieve payment and transaction information"""
        results = ctx.deps.vector_index.search(query, ctx.deps.docs, k=k)
        # Filter for payment-related content
        payment_keywords = ['payment', 'transaction', 'due', 'paid', 'amount', 'balance', 'deposit', 'withdrawal']
        payment_results = [r for r in results if any(keyword in r['text'].lower() for keyword in payment_keywords)]
        return [RetrievedChunk(source=r["source"], score=r["score"], text=r["text"]) for r in payment_results]
    
    # Summary Agent
    summary_agent = Agent(
        model=model,
        deps_type=MultiAgentDeps,
        system_prompt=(
            "You are a Document Summary Specialist. You excel at providing high-level "
            "summaries, identifying key trends, patterns, and insights across multiple "
            "documents. You focus on big-picture analysis, trend identification, and "
            "comprehensive overviews. Always synthesize information from multiple sources "
            "and provide actionable insights."
        )
    )
    
    @summary_agent.tool
    def retrieve_summary_data(ctx: RunContext[MultiAgentDeps], query: str, k: int = 8) -> List[RetrievedChunk]:
        """Retrieve comprehensive data for summary analysis"""
        results = ctx.deps.vector_index.search(query, ctx.deps.docs, k=k)
        return [RetrievedChunk(source=r["source"], score=r["score"], text=r["text"]) for r in results]
    
    # Coordinator Agent
    coordinator_agent = Agent(
        model=model,
        deps_type=MultiAgentDeps,
        system_prompt=(
            "You are a Query Coordinator. Your job is to classify user queries and "
            "determine which specialized agent should handle them. Classify queries as: "
            "invoice_analysis (for invoice-specific questions), payment_verification "
            "(for payment/transaction questions), summary (for overview/trend questions), "
            "or general (for other queries). Provide clear reasoning for your classification."
        )
    )
    
    @coordinator_agent.tool
    def classify_query(ctx: RunContext[MultiAgentDeps], query: str) -> QueryIntent:
        """Classify the intent of a user query"""
        # Simple keyword-based classification (in production, use more sophisticated NLP)
        query_lower = query.lower()
        
        invoice_keywords = ['invoice', 'vendor', 'line item', 'total', 'subtotal', 'tax', 'billing']
        payment_keywords = ['payment', 'transaction', 'due date', 'paid', 'balance', 'deposit', 'withdrawal']
        summary_keywords = ['summary', 'overview', 'trend', 'pattern', 'all', 'across', 'compare']
        
        invoice_score = sum(1 for keyword in invoice_keywords if keyword in query_lower)
        payment_score = sum(1 for keyword in payment_keywords if keyword in query_lower)
        summary_score = sum(1 for keyword in summary_keywords if keyword in query_lower)
        
        max_score = max(invoice_score, payment_score, summary_score)
        
        if max_score == 0:
            intent = "general"
            confidence = 0.5
            reasoning = "No specific keywords detected, treating as general query"
        elif invoice_score == max_score:
            intent = "invoice_analysis"
            confidence = min(0.9, 0.5 + invoice_score * 0.1)
            reasoning = f"Detected {invoice_score} invoice-related keywords"
        elif payment_score == max_score:
            intent = "payment_verification"
            confidence = min(0.9, 0.5 + payment_score * 0.1)
            reasoning = f"Detected {payment_score} payment-related keywords"
        else:
            intent = "summary"
            confidence = min(0.9, 0.5 + summary_score * 0.1)
            reasoning = f"Detected {summary_score} summary-related keywords"
        
        return QueryIntent(intent=intent, confidence=confidence, reasoning=reasoning)

# ---------------------------
# Multi-Agent Orchestration
# ---------------------------

class MultiAgentSystem:
    """Orchestrates multiple specialized agents"""
    
    def __init__(self, vector_index: VectorIndex, docs: List[Dict]):
        self.deps = MultiAgentDeps(vector_index=vector_index, docs=docs)
    
    def route_query(self, query: str) -> AgentResponse:
        """Route query to appropriate specialized agent"""
        if not PAI_OK:
            return self._fallback_response(query)
        
        try:
            # Step 1: Classify the query
            classification = coordinator_agent.run(
                f"Classify this query: {query}",
                deps=self.deps
            ).data
            
            print(f"🔍 Query Classification: {classification.intent} (confidence: {classification.confidence:.2f})")
            print(f"   Reasoning: {classification.reasoning}")
            
            # Step 2: Route to appropriate agent
            if classification.intent == "invoice_analysis":
                return self._handle_invoice_query(query)
            elif classification.intent == "payment_verification":
                return self._handle_payment_query(query)
            elif classification.intent == "summary":
                return self._handle_summary_query(query)
            else:
                return self._handle_general_query(query)
                
        except Exception as e:
            print(f"⚠️ Error in multi-agent routing: {e}")
            return self._fallback_response(query)
    
    def _handle_invoice_query(self, query: str) -> AgentResponse:
        """Handle invoice-specific queries"""
        print("📄 Routing to Invoice Analyzer Agent...")
        
        prompt = (
            f"As an Invoice Analysis Specialist, answer this query: {query}\n"
            "Use the retrieve_invoice_data tool to find relevant invoice information. "
            "Focus on invoice details, line items, totals, and vendor information."
        )
        
        result = invoice_agent.run(prompt, deps=self.deps)
        
        return AgentResponse(
            agent_type="Invoice Analyzer",
            response=result.data,
            confidence=0.9,
            sources_used=[f"Invoice documents"],
            reasoning="Specialized invoice analysis with focused retrieval"
        )
    
    def _handle_payment_query(self, query: str) -> AgentResponse:
        """Handle payment-specific queries"""
        print("💳 Routing to Payment Verifier Agent...")
        
        prompt = (
            f"As a Payment Verification Specialist, answer this query: {query}\n"
            "Use the retrieve_payment_data tool to find relevant payment information. "
            "Focus on payment methods, transactions, due dates, and financial compliance."
        )
        
        result = payment_agent.run(prompt, deps=self.deps)
        
        return AgentResponse(
            agent_type="Payment Verifier",
            response=result.data,
            confidence=0.9,
            sources_used=[f"Payment and transaction data"],
            reasoning="Specialized payment analysis with focused retrieval"
        )
    
    def _handle_summary_query(self, query: str) -> AgentResponse:
        """Handle summary queries"""
        print("📊 Routing to Summary Agent...")
        
        prompt = (
            f"As a Document Summary Specialist, answer this query: {query}\n"
            "Use the retrieve_summary_data tool to gather comprehensive information. "
            "Provide high-level insights, trends, and patterns across all documents."
        )
        
        result = summary_agent.run(prompt, deps=self.deps)
        
        return AgentResponse(
            agent_type="Summary Agent",
            response=result.data,
            confidence=0.85,
            sources_used=[f"All document types"],
            reasoning="Comprehensive analysis across all document types"
        )
    
    def _handle_general_query(self, query: str) -> AgentResponse:
        """Handle general queries using basic retrieval"""
        print("🔍 Handling as general query...")
        
        results = self.deps.vector_index.search(query, self.deps.docs, k=5)
        if not results:
            response = "I don't have enough information to answer this query."
        else:
            response = f"Based on the available documents:\n\n"
            for i, result in enumerate(results[:3], 1):
                response += f"{i}. From {Path(result['source']).name}:\n{result['text'][:300]}...\n\n"
        
        return AgentResponse(
            agent_type="General",
            response=response,
            confidence=0.7,
            sources_used=[result['source'] for result in results[:3]],
            reasoning="General retrieval without specialization"
        )
    
    def _fallback_response(self, query: str) -> AgentResponse:
        """Fallback when Pydantic AI is not available"""
        print("⚠️ Using fallback mode (Pydantic AI not available)")
        
        results = self.deps.vector_index.search(query, self.deps.docs, k=5)
        if not results:
            response = "I don't have enough information to answer this query."
        else:
            response = f"[Fallback Mode] Based on available documents:\n\n"
            for i, result in enumerate(results[:3], 1):
                response += f"{i}. From {Path(result['source']).name}:\n{result['text'][:300]}...\n\n"
        
        return AgentResponse(
            agent_type="Fallback",
            response=response,
            confidence=0.6,
            sources_used=[result['source'] for result in results[:3]],
            reasoning="Fallback mode without specialized agents"
        )

# ---------------------------
# Main Multi-Agent Demo
# ---------------------------

def main():
    """Demonstrate the multi-agent system"""
    print("🤖 Multi-Agent Document Analysis System")
    print("=" * 60)
    
    # Ensure PDFs exist
    pdfs = ensure_pdfs_present(Path("synthetic_pdfs"))
    print(f"📄 Found {len(pdfs)} PDFs")
    
    # Load and process documents
    corpus = load_corpus_from_pdfs(pdfs)
    chunks = chunk_documents(corpus)
    print(f"📝 Processed {len(chunks)} text chunks")
    
    # Build vector index
    vindex = VectorIndex(EMBED_MODEL)
    if INDEX_PATH.exists():
        print("📚 Loading existing vector index...")
        docs_loaded = vindex.load(INDEX_PATH, DOCS_JSONL)
    else:
        print("🔨 Building new vector index...")
        vindex.build(chunks, INDEX_PATH, DOCS_JSONL)
        docs_loaded = vindex.load(INDEX_PATH, DOCS_JSONL)
    
    print(f"✅ Vector index ready with {len(docs_loaded)} chunks")
    
    # Initialize multi-agent system
    multi_agent = MultiAgentSystem(vindex, docs_loaded)
    
    # Test queries for different agent types
    test_queries = [
        # Invoice Analysis Queries
        "What is the total amount for invoice INV-1003?",
        "Which vendor has the highest invoice total?",
        "List all line items from the most recent invoice",
        
        # Payment Verification Queries
        "What payment methods are used across all documents?",
        "Are there any overdue payments or past due amounts?",
        "What is the average transaction amount?",
        
        # Summary Queries
        "Provide a summary of all financial activity",
        "What are the key trends across all documents?",
        "Compare invoice totals vs bank statement deposits",
        
        # General Queries
        "What documents do we have?",
        "Find any mentions of tax calculations",
    ]
    
    print("\n🧪 Testing Multi-Agent System")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"❓ {query}")
        
        response = multi_agent.route_query(query)
        
        print(f"🤖 Agent: {response.agent_type}")
        print(f"📊 Confidence: {response.confidence:.2f}")
        print(f"💭 Reasoning: {response.reasoning}")
        print(f"📄 Sources: {len(response.sources_used)} documents")
        print(f"✅ Answer:\n{response.response}")
        print("-" * 80)
    
    print("\n🎯 Multi-Agent System Demo Complete!")
    print("\nKey Benefits Demonstrated:")
    print("✅ Specialized agent expertise")
    print("✅ Intelligent query routing")
    print("✅ Confidence scoring")
    print("✅ Fallback mechanisms")
    print("✅ Source attribution")

if __name__ == "__main__":
    main()
