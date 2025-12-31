"""
RAG Assistant with OpenAI GPT-4
Uses your OpenAI API key for better summarization
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os

from sqlalchemy.orm import Session
from sqlalchemy import desc
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from .database import Article

class OpenAIRAGAssistant:
    """RAG Assistant using OpenAI GPT-4"""
    
    def __init__(self, db: Session, openai_api_key: str):
        self.db = db
        self.openai_api_key = openai_api_key
        
        # Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # GPT-4 for summarization
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        self.vectorstore: Optional[FAISS] = None
        self.last_update: Optional[datetime] = None
    
    def build_vectorstore(self, days: int = 30, filters: Optional[Dict] = None, force_rebuild: bool = False):
        """Build vector store from articles"""
        query = self.db.query(Article)
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Article.published_at >= cutoff)
        
        if filters:
            if filters.get("is_goi"):
                query = query.filter(Article.is_goi == True)
        
        articles = query.order_by(desc(Article.published_at)).limit(5000).all()
        
        if not articles:
            raise ValueError("No articles found")
        
        documents = []
        for article in articles:
            title = article.translated_title or article.title
            summary = article.translated_summary or article.summary
            
            if not title and not summary:
                continue
            
            content = f"Title: {title}\n\nSummary: {summary}"
            
            metadata = {
                "article_id": article.id,
                "url": article.url,
                "source": article.source or "Unknown",
                "language": article.detected_language or "unknown",
                "published_at": str(article.published_at) if article.published_at else None,
                "sentiment": article.sentiment_label or "neutral",
                "is_goi": article.is_goi or False,
                "ministries": article.goi_ministries or [],
                "schemes": article.goi_schemes or [],
            }
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        split_docs = self.text_splitter.split_documents(documents)
        self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        self.last_update = datetime.utcnow()
        
        return self.vectorstore
    
    def _rerank_docs(self, docs: List[Document]) -> List[Document]:
        """Re-rank documents by recency and GOI relevance"""
        scored = []
        for doc in docs:
            score = 1.0
            if doc.metadata.get('is_goi'):
                score += 0.5
            if doc.metadata.get('ministries'):
                score += 0.3
            if doc.metadata.get('published_at'):
                try:
                    pub_date = datetime.fromisoformat(doc.metadata['published_at'].replace('Z', '+00:00'))
                    days_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).days
                    if days_old < 7:
                        score += 0.4
                    elif days_old < 30:
                        score += 0.2
                except:
                    pass
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored]
    
    def query(self, question: str, k: int = 5, filters: Optional[Dict] = None, language: str = "en") -> Dict[str, Any]:
        """Query with GPT-4 and improved retrieval"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        
        # Retrieve more documents for re-ranking
        docs = self.vectorstore.similarity_search(question, k=k*2)
        
        # Re-rank for relevance
        docs = self._rerank_docs(docs)
        
        # Take top k
        docs = docs[:k]
        
        if not docs:
            return {
                "answer": "No relevant information found.",
                "sources": [],
                "confidence": 0.0,
                "retrieved_docs": 0
            }
        
        # Prepare context with metadata
        context_parts = []
        for i, doc in enumerate(docs[:3]):  # Use top 3 docs
            metadata_info = []
            if doc.metadata.get('source'):
                metadata_info.append(f"Source: {doc.metadata['source']}")
            if doc.metadata.get('published_at'):
                metadata_info.append(f"Date: {doc.metadata['published_at'][:10]}")
            if doc.metadata.get('sentiment'):
                metadata_info.append(f"Sentiment: {doc.metadata['sentiment']}")
            if doc.metadata.get('ministries'):
                metadata_info.append(f"Ministries: {', '.join(doc.metadata['ministries'][:3])}")
            
            meta_str = " | ".join(metadata_info)
            context_parts.append(f"[Article {i+1}] {meta_str}\n{doc.page_content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate answer with GPT-4 - Enhanced prompt
        prompt = f"""You are an expert AI assistant for PIB (Press Information Bureau) officers monitoring Government of India news.

Your task: Provide accurate, comprehensive answers based on the context below. Focus on:
- Government schemes and policies
- Ministry announcements
- Sentiment and public perception
- Regional impacts

Context from recent news articles:
{context}

---

Question: {question}

Instructions:
1. Answer directly and factually based on the context
2. Cite specific ministries, schemes, or regions when relevant
3. Mention sentiment if it's significant (positive/negative)
4. If information is incomplete, clearly state that
5. Use bullet points for clarity when listing multiple items

Answer:"""

        try:
            response = self.llm.invoke(prompt)
            answer = response.content
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
        
        # Extract sources
        sources = []
        for doc in docs:
            sources.append({
                "article_id": doc.metadata.get("article_id"),
                "url": doc.metadata.get("url"),
                "source": doc.metadata.get("source"),
                "published_at": doc.metadata.get("published_at"),
                "sentiment": doc.metadata.get("sentiment"),
                "ministries": doc.metadata.get("ministries", []),
            })
        
        return {
            "answer": answer,
            "sources": sources[:10],
            "confidence": min(len(docs) / k, 1.0),
            "retrieved_docs": len(docs)
        }
    
    def get_summary(self, filters: Dict[str, Any], summary_type: str = "topics") -> Dict[str, Any]:
        """Get aggregated summary"""
        query = self.db.query(Article)
        
        if filters.get("date_from"):
            query = query.filter(Article.published_at >= filters["date_from"])
        if filters.get("is_goi"):
            query = query.filter(Article.is_goi == True)
        
        articles = query.all()
        
        if summary_type == "topics":
            topic_counts = {}
            for article in articles:
                for topic in (article.topic_labels or []):
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            return {"topics": sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]}
        
        elif summary_type == "sentiment":
            sentiment_counts = {}
            for article in articles:
                sent = article.sentiment_label or "neutral"
                sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
            return {"sentiment_distribution": sentiment_counts}
        
        elif summary_type == "ministries":
            ministry_counts = {}
            for article in articles:
                for ministry in (article.goi_ministries or []):
                    ministry_counts[ministry] = ministry_counts.get(ministry, 0) + 1
            return {"ministries": sorted(ministry_counts.items(), key=lambda x: x[1], reverse=True)[:15]}
        
        return {"total_articles": len(articles)}


_rag_instance: Optional[OpenAIRAGAssistant] = None

def get_openai_rag(db: Session, api_key: str) -> OpenAIRAGAssistant:
    """Get OpenAI RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = OpenAIRAGAssistant(db, api_key)
    return _rag_instance
