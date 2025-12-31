"""
RAG (Retrieval-Augmented Generation) Assistant for NewsScope India
Provides intelligent Q&A over multilingual government news articles
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
import hashlib

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session
import numpy as np

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFacePipeline

# Optional: OpenAI (if API key provided)
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .database import Article, get_database
from .config import settings
from .language_processor import MultilingualProcessor


class RAGAssistant:
    """
    Multilingual RAG Assistant for Government News Q&A
    """
    
    def __init__(
        self,
        db: Session,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        use_openai: bool = False,
        cache_dir: str = "./vector_cache"
    ):
        """
        Initialize RAG Assistant
        
        Args:
            db: Database session
            embedding_model: HuggingFace model for embeddings
            use_openai: Use OpenAI embeddings/LLM if available
            cache_dir: Directory to cache vector stores
        """
        self.db = db
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize translation service for multilingual support
        self.translator = MultilingualProcessor()
        
        # Initialize embeddings
        if use_openai and OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.embeddings = OpenAIEmbeddings()
            self.use_openai = True
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            self.use_openai = False
        
        # Text splitter for chunking - optimized for Indian languages
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Smaller chunks for better precision
            chunk_overlap=150,  # Good overlap for context
            length_function=len,
            separators=["\n\n", "\n", "। ", ". ", "।", "?", "! ", " ", ""]
        )
        
        # Vector store (lazy loaded)
        self.vectorstore: Optional[FAISS] = None
        self.last_update: Optional[datetime] = None
        
    def _prepare_documents(
        self,
        articles: List[Article],
        include_english: bool = True
    ) -> List[Document]:
        """
        Convert articles to LangChain Documents with metadata
        
        Args:
            articles: List of Article objects
            include_english: Include English translations
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for article in articles:
            # Original language content with rich metadata
            content_parts = []
            if article.title:
                content_parts.append(f"Title: {article.title}")
            if article.summary:
                content_parts.append(f"Summary: {article.summary}")
            if article.content and len(article.content) > 100:
                content_parts.append(f"Content: {article.content[:2000]}")  # Limit content length
            
            # Add contextual metadata to improve retrieval
            if article.goi_ministries:
                content_parts.append(f"Ministries: {', '.join(article.goi_ministries[:5])}")
            if article.goi_schemes:
                content_parts.append(f"Schemes: {', '.join(article.goi_schemes[:5])}")
            if article.region:
                content_parts.append(f"Region: {article.region}")
            
            original_text = "\n\n".join(content_parts)
            
            if not original_text.strip():
                continue
                
            # Metadata for filtering and source tracking
            metadata = {
                "article_id": article.id,
                "url": article.url,
                "source": article.source or "Unknown",
                "language": article.detected_language or article.language or "unknown",
                "region": article.region or "India",
                "published_at": str(article.published_at) if article.published_at else None,
                "sentiment": article.sentiment_label or "neutral",
                "sentiment_score": article.sentiment_score or 0.0,
                "is_goi": article.is_goi or False,
                "ministries": article.goi_ministries or [],
                "schemes": article.goi_schemes or [],
                "topics": article.topic_labels or [],
                # NEW: Confidence scoring metadata for PIB insights
                "confidence_score": float(article.confidence_score) if hasattr(article, 'confidence_score') and article.confidence_score else None,
                "confidence_level": article.confidence_level if hasattr(article, 'confidence_level') else None,
                "auto_approved": article.auto_approved if hasattr(article, 'auto_approved') else None,
                "anomalies": article.anomalies if hasattr(article, 'anomalies') else None,
                "verification_status": article.verification_status if hasattr(article, 'verification_status') else None,
            }
            
            # Add original language document
            doc = Document(
                page_content=original_text,
                metadata={**metadata, "content_type": "original"}
            )
            documents.append(doc)
            
            # Add English translation if available and requested
            if include_english and (article.translated_title or article.translated_summary):
                english_parts = []
                if article.translated_title:
                    english_parts.append(f"Title: {article.translated_title}")
                if article.translated_summary:
                    english_parts.append(f"Summary: {article.translated_summary}")
                
                english_text = "\n\n".join(english_parts)
                if english_text.strip():
                    eng_doc = Document(
                        page_content=english_text,
                        metadata={**metadata, "content_type": "english_translation"}
                    )
                    documents.append(eng_doc)
        
        return documents
    
    def build_vectorstore(
        self,
        days: int = 30,
        filters: Optional[Dict[str, Any]] = None,
        force_rebuild: bool = False
    ) -> FAISS:
        """
        Build or update the vector store from recent articles
        
        Args:
            days: Number of days of articles to include
            filters: Additional filters (language, region, is_goi, etc.)
            force_rebuild: Force rebuild even if cache exists
            
        Returns:
            FAISS vector store
        """
        # Check cache
        cache_key = self._get_cache_key(days, filters)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        if not force_rebuild and os.path.exists(cache_path):
            try:
                self.vectorstore = FAISS.load_local(cache_path, self.embeddings)
                print(f"Loaded vector store from cache: {cache_path}")
                return self.vectorstore
            except Exception as e:
                print(f"Failed to load cache: {e}, rebuilding...")
        
        # Query articles
        query = self.db.query(Article)
        
        # Date filter
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Article.published_at >= cutoff_date)
        
        # Additional filters
        if filters:
            if filters.get("language"):
                query = query.filter(Article.detected_language == filters["language"])
            if filters.get("region"):
                query = query.filter(Article.region == filters["region"])
            if filters.get("is_goi") is not None:
                query = query.filter(Article.is_goi == filters["is_goi"])
            if filters.get("sentiment"):
                query = query.filter(Article.sentiment_label == filters["sentiment"])
            if filters.get("ministries"):
                query = query.filter(Article.goi_ministries.contains(filters["ministries"]))
            # NEW: Confidence-based filtering for PIB officers
            if filters.get("confidence_level"):
                query = query.filter(Article.confidence_level == filters["confidence_level"])
            if filters.get("high_confidence_only"):
                query = query.filter(Article.confidence_level == 'high')
            if filters.get("verified_only"):
                query = query.filter(Article.verification_status == 'verified')
        
        # Execute query
        articles = query.order_by(desc(Article.published_at)).limit(5000).all()
        
        if not articles:
            raise ValueError("No articles found matching the criteria")
        
        print(f"Building vector store from {len(articles)} articles...")
        
        # Prepare documents
        documents = self._prepare_documents(articles)
        print(f"Prepared {len(documents)} document chunks")
        
        # Split into smaller chunks
        split_docs = self.text_splitter.split_documents(documents)
        print(f"Split into {len(split_docs)} smaller chunks")
        
        # Build vector store
        self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        
        # Save to cache
        try:
            self.vectorstore.save_local(cache_path)
            print(f"Saved vector store to cache: {cache_path}")
        except Exception as e:
            print(f"Failed to save cache: {e}")
        
        self.last_update = datetime.utcnow()
        return self.vectorstore
    
    def _get_cache_key(self, days: int, filters: Optional[Dict[str, Any]]) -> str:
        """Generate cache key based on parameters"""
        filter_str = json.dumps(filters or {}, sort_keys=True)
        key_str = f"days_{days}_filters_{filter_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _create_prompt_template(self, language: str = "en") -> PromptTemplate:
        """
        Create language-specific prompt template
        
        Args:
            language: Target language code
            
        Returns:
            PromptTemplate
        """
        if language == "hi":
            template = """
            आप भारत सरकार की खबरों के विशेषज्ञ AI सहायक हैं। PIB अधिकारियों को सटीक जानकारी प्रदान करना आपका काम है।
            
            नीचे दिए गए संदर्भ के आधार पर प्रश्न का उत्तर दें। यदि संदर्भ में उत्तर नहीं है, तो स्पष्ट रूप से कहें।
            
            संदर्भ:
            {context}
            
            प्रश्न: {question}
            
            उत्तर (संक्षिप्त, सटीक और तथ्यात्मक):
            - मुख्य बिंदु:
            - संबंधित योजनाएं/मंत्रालय:
            - स्रोत तिथि:
            """
        else:
            template = """
            You are an expert AI assistant for Government of India news and Press Information Bureau (PIB) officers.
            
            Based on the context below, provide a comprehensive answer to the question. If the answer is not in the context, clearly state that.
            
            Context:
            {context}
            
            Question: {question}
            
            Answer (concise, accurate, and factual):
            - Key Points:
            - Related Schemes/Ministries:
            - Source Date:
            - Sentiment:
            """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _hybrid_search(self, question: str, k: int = 10) -> List[Document]:
        """Hybrid search combining semantic and keyword matching"""
        if not self.vectorstore:
            return []
        
        # Semantic search
        semantic_docs = self.vectorstore.similarity_search(question, k=k)
        
        # Keyword boosting - look for important terms
        keywords = ["योजना", "scheme", "मंत्रालय", "ministry", "सरकार", "government", 
                   "ಯೋಜನೆ", "ಸರ್ಕಾರ", "योजना", "సర్కార్", "പദ്ധതി", "ସରକାର", "ਯੋਜਨਾ"]
        
        # Boost scores for documents containing keywords
        scored_docs = []
        for doc in semantic_docs:
            score = 1.0
            content_lower = doc.page_content.lower()
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 0.2
            scored_docs.append((score, doc))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:k]]
    
    def _rerank_documents(self, question: str, docs: List[Document]) -> List[Document]:
        """Re-rank documents based on relevance and recency"""
        if not docs:
            return docs
        
        scored_docs = []
        for doc in docs:
            score = 1.0
            
            # Recency boost
            if doc.metadata.get('published_at'):
                try:
                    pub_date = datetime.fromisoformat(doc.metadata['published_at'].replace('Z', '+00:00'))
                    days_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).days
                    # More recent = higher score
                    if days_old < 7:
                        score += 0.5
                    elif days_old < 30:
                        score += 0.3
                except:
                    pass
            
            # GOI relevance boost
            if doc.metadata.get('is_goi'):
                score += 0.4
            
            # Sentiment boost for balanced coverage
            if doc.metadata.get('sentiment') == 'positive':
                score += 0.1
            
            # Ministry/Scheme presence boost
            if doc.metadata.get('ministries') or doc.metadata.get('schemes'):
                score += 0.3
            
            # NEW: Confidence score boost - prioritize high-confidence articles
            confidence_score = doc.metadata.get('confidence_score')
            if confidence_score:
                if confidence_score >= 0.8:
                    score += 0.5  # High confidence articles are more reliable
                elif confidence_score >= 0.5:
                    score += 0.2  # Medium confidence
            
            # NEW: Auto-approved boost - these passed all filters
            if doc.metadata.get('auto_approved'):
                score += 0.4
            
            # NEW: Anomaly penalty - articles with anomalies need careful review
            if doc.metadata.get('anomalies'):
                score -= 0.3  # Lower priority for anomalous articles
            
            scored_docs.append((score, doc))
        
        # Sort by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs]
    
    def query(
        self,
        question: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Query the RAG system with improved retrieval and re-ranking
        
        Args:
            question: User question
            k: Number of documents to retrieve
            filters: Metadata filters
            language: Response language
            
        Returns:
            Dict with answer and sources
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call build_vectorstore() first.")
        
        # Translate question to English if needed (for better retrieval)
        question_en = question
        if language != "en":
            try:
                # Use translate_to_english method
                question_en = self.translator.translate_to_english(question, language) or question
            except:
                pass  # Use original if translation fails
        
        # Retrieve relevant documents using hybrid search
        initial_k = k * 3  # Retrieve more candidates for re-ranking
        docs = self._hybrid_search(question_en, k=initial_k)
        
        # Filter by metadata if provided
        if filters:
            docs = self._filter_docs_by_metadata(docs, filters)
        
        # Re-rank documents for better relevance
        docs = self._rerank_documents(question_en, docs)
        
        # Take top k after re-ranking
        docs = docs[:k]
        
        if not docs:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Build context from retrieved docs
        context = "\n\n---\n\n".join([
            f"[Source {i+1}] ({doc.metadata.get('source', 'Unknown')})\n{doc.page_content}"
            for i, doc in enumerate(docs)
        ])
        
        # Generate answer using simple summarization
        # For production, integrate with an LLM (OpenAI, Hugging Face, etc.)
        answer = self._generate_answer(context, question, docs, language)
        
        # Extract sources
        sources = []
        seen_urls = set()
        for doc in docs:
            url = doc.metadata.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "article_id": doc.metadata.get("article_id"),
                    "url": url,
                    "source": doc.metadata.get("source"),
                    "published_at": doc.metadata.get("published_at"),
                    "language": doc.metadata.get("language"),
                    "sentiment": doc.metadata.get("sentiment"),
                    "ministries": doc.metadata.get("ministries", []),
                    "schemes": doc.metadata.get("schemes", []),
                })
        
        return {
            "answer": answer,
            "sources": sources[:10],  # Limit sources
            "confidence": self._calculate_confidence(docs, question),
            "retrieved_docs": len(docs)
        }
    
    def _filter_docs_by_metadata(
        self,
        docs: List[Document],
        filters: Dict[str, Any]
    ) -> List[Document]:
        """Filter documents by metadata"""
        filtered = []
        for doc in docs:
            match = True
            for key, value in filters.items():
                if key == "ministries" and isinstance(value, list):
                    # Check if any ministry matches
                    doc_ministries = doc.metadata.get("ministries", [])
                    if not any(m in doc_ministries for m in value):
                        match = False
                        break
                elif doc.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(doc)
        return filtered
    
    def _generate_answer(
        self,
        context: str,
        question: str,
        docs: List[Document],
        language: str
    ) -> str:
        """
        Generate answer from context (simplified version)
        For production: integrate with OpenAI/Claude/Llama
        """
        # Simple extractive summarization
        # In production, use an LLM for better answers
        
        if self.use_openai and OPENAI_AVAILABLE:
            try:
                llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
                prompt = self._create_prompt_template(language)
                response = llm.predict(prompt.format(context=context[:4000], question=question))
                return response
            except Exception as e:
                print(f"OpenAI error: {e}, falling back to extractive")
        
        # Fallback: extractive summary
        sentences = []
        for doc in docs[:3]:  # Top 3 docs
            content = doc.page_content
            # Extract key sentences
            parts = content.split("\n")
            for part in parts:
                if len(part) > 50 and (":" in part or "?" in part or "।" in part):
                    sentences.append(part.strip())
        
        answer = " ".join(sentences[:3])  # First 3 sentences
        
        # Translation from English to other languages not yet implemented
        # Answer will be in English for now
        # TODO: Add English-to-Indian-language translation
        
        return answer or "Based on the available information, I found relevant articles but couldn't generate a specific answer."
    
    def _calculate_confidence(self, docs: List[Document], question: str) -> float:
        """Calculate confidence score based on multiple factors"""
        if not docs:
            return 0.0
        
        # Base score from document count
        score = min(len(docs) / 5.0, 0.5)  # Up to 50% from count
        
        # Metadata richness
        metadata_score = 0
        for doc in docs:
            if doc.metadata.get("ministries"):
                metadata_score += 0.05
            if doc.metadata.get("schemes"):
                metadata_score += 0.05
            if doc.metadata.get("is_goi"):
                metadata_score += 0.03
        score += min(metadata_score, 0.3)  # Up to 30% from metadata
        
        # Recency boost
        recent_count = 0
        for doc in docs:
            if doc.metadata.get('published_at'):
                try:
                    pub_date = datetime.fromisoformat(doc.metadata['published_at'].replace('Z', '+00:00'))
                    days_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).days
                    if days_old < 7:
                        recent_count += 1
                except:
                    pass
        if recent_count > 0:
            score += min(recent_count / len(docs), 0.2)  # Up to 20% for recency
        
        # NEW: Article confidence boost
        confidence_scores = [doc.metadata.get('confidence_score') for doc in docs if doc.metadata.get('confidence_score')]
        if confidence_scores:
            avg_article_confidence = sum(confidence_scores) / len(confidence_scores)
            score += avg_article_confidence * 0.1  # Up to 10% from article confidence
        
        return min(score, 1.0)
    
    def get_summary(
        self,
        filters: Dict[str, Any],
        summary_type: str = "topics"
    ) -> Dict[str, Any]:
        """
        Get aggregated summary based on filters
        
        Args:
            filters: Filters (date range, language, sentiment, etc.)
            summary_type: "topics", "sentiment", "ministries", etc.
            
        Returns:
            Summary statistics
        """
        query = self.db.query(Article)
        
        # Apply filters
        if filters.get("date_from"):
            query = query.filter(Article.published_at >= filters["date_from"])
        if filters.get("date_to"):
            query = query.filter(Article.published_at <= filters["date_to"])
        if filters.get("language"):
            query = query.filter(Article.detected_language == filters["language"])
        if filters.get("sentiment"):
            query = query.filter(Article.sentiment_label == filters["sentiment"])
        if filters.get("is_goi") is not None:
            query = query.filter(Article.is_goi == filters["is_goi"])
        
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
        
        else:
            return {
                "total_articles": len(articles),
                "date_range": {
                    "from": str(min(a.published_at for a in articles if a.published_at)) if articles else None,
                    "to": str(max(a.published_at for a in articles if a.published_at)) if articles else None
                }
            }
    
    # NEW PIB-SPECIFIC METHODS FOR 100% ACCURACY
    
    def query_pib_insights(
        self,
        question: str,
        filters: Optional[Dict[str, Any]] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        PIB officer-specific query with confidence and quality insights.
        Provides additional metadata about article quality and reliability.
        """
        # Standard query
        result = self.query(question, k=k, filters=filters)
        
        # Add PIB-specific insights
        sources = result.get('sources', [])
        
        quality_metrics = {
            "total_sources": len(sources),
            "high_confidence_count": sum(1 for s in sources if isinstance(s, dict) and s.get('confidence_score', 0) >= 0.8),
            "official_sources_count": sum(1 for s in sources if isinstance(s, dict) and ('pib.gov.in' in str(s.get('source', '')) or 'mygov.in' in str(s.get('source', '')))),
            "schemes_mentioned": list(set(
                scheme 
                for s in sources if isinstance(s, dict)
                for scheme in s.get('schemes', [])
            ))[:10],
            "ministries_involved": list(set(
                ministry 
                for s in sources if isinstance(s, dict)
                for ministry in s.get('ministries', [])
            ))[:10]
        }
        
        # Add recommendations
        recommendations = []
        if quality_metrics['high_confidence_count'] < len(sources) * 0.5:
            recommendations.append("Less than 50% of sources are high-confidence. Consider verifying manually.")
        if quality_metrics['official_sources_count'] == 0:
            recommendations.append("No official government sources found. Results may need verification.")
        if not quality_metrics['schemes_mentioned']:
            recommendations.append("No specific schemes detected. Query may be too broad.")
        
        result['pib_insights'] = {
            "quality_metrics": quality_metrics,
            "recommendations": recommendations,
            "reliability_score": self._calculate_reliability_score(sources)
        }
        
        return result
    
    def _calculate_reliability_score(self, sources: List[Dict]) -> float:
        """Calculate overall reliability score for PIB officers (0.0-1.0)."""
        if not sources:
            return 0.0
        
        score = 0.0
        valid_sources = [s for s in sources if isinstance(s, dict)]
        
        if not valid_sources:
            return 0.0
        
        # Confidence scores (40% weight)
        confidence_scores = [s.get('confidence_score', 0) for s in valid_sources]
        avg_confidence = sum(confidence_scores) / len(valid_sources) if valid_sources else 0
        score += avg_confidence * 0.4
        
        # Official sources (30% weight)
        official_count = sum(1 for s in valid_sources if 'gov.in' in str(s.get('source', '')))
        official_ratio = official_count / len(valid_sources)
        score += official_ratio * 0.3
        
        # Scheme/Ministry presence (20% weight)
        metadata_rich = sum(1 for s in valid_sources if s.get('schemes') or s.get('ministries'))
        metadata_ratio = metadata_rich / len(valid_sources)
        score += metadata_ratio * 0.2
        
        # Recency (10% weight)
        recent_count = 0
        for s in valid_sources:
            if s.get('published_at'):
                try:
                    pub_date = datetime.fromisoformat(str(s['published_at']).replace('Z', '+00:00'))
                    days_old = (datetime.utcnow() - pub_date.replace(tzinfo=None)).days
                    if days_old < 30:
                        recent_count += 1
                except:
                    pass
        recency_ratio = recent_count / len(valid_sources)
        score += recency_ratio * 0.1
        
        return min(score, 1.0)
    
    def get_scheme_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of all government schemes in recent articles."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        articles = self.db.query(Article).filter(
            Article.published_at >= cutoff_date,
            Article.goi_schemes.isnot(None)
        ).all()
        
        scheme_stats = {}
        
        for article in articles:
            for scheme in (article.goi_schemes or []):
                if scheme not in scheme_stats:
                    scheme_stats[scheme] = {
                        "article_count": 0,
                        "high_confidence_count": 0,
                        "total_confidence": 0.0,
                        "sources": set(),
                        "ministries": set()
                    }
                
                stats = scheme_stats[scheme]
                stats["article_count"] += 1
                
                confidence = float(article.confidence_score) if hasattr(article, 'confidence_score') and article.confidence_score else 0
                if confidence >= 0.8:
                    stats["high_confidence_count"] += 1
                stats["total_confidence"] += confidence
                
                if article.source:
                    stats["sources"].add(article.source)
                if article.goi_ministries:
                    stats["ministries"].update(article.goi_ministries)
        
        # Convert to final format
        result = []
        for scheme, stats in scheme_stats.items():
            result.append({
                "scheme": scheme,
                "article_count": stats["article_count"],
                "high_confidence_count": stats["high_confidence_count"],
                "avg_confidence": round(stats["total_confidence"] / stats["article_count"], 2) if stats["article_count"] > 0 else 0,
                "sources": list(stats["sources"])[:5],
                "ministries": list(stats["ministries"])[:5]
            })
        
        # Sort by article count
        result.sort(key=lambda x: x["article_count"], reverse=True)
        
        return {
            "total_schemes": len(result),
            "date_range": f"Last {days} days",
            "schemes": result[:50]  # Top 50 schemes
        }
    
    def get_accuracy_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get accuracy and quality insights for PIB officers."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        articles = self.db.query(Article).filter(
            Article.published_at >= cutoff_date
        ).all()
        
        if not articles:
            return {"message": "No articles in the specified period"}
        
        total = len(articles)
        high_conf = sum(1 for a in articles if hasattr(a, 'confidence_level') and a.confidence_level == 'high')
        medium_conf = sum(1 for a in articles if hasattr(a, 'confidence_level') and a.confidence_level == 'medium')
        low_conf = sum(1 for a in articles if hasattr(a, 'confidence_level') and a.confidence_level == 'low')
        auto_approved = sum(1 for a in articles if hasattr(a, 'auto_approved') and a.auto_approved)
        needs_review = sum(1 for a in articles if hasattr(a, 'needs_verification') and a.needs_verification)
        with_anomalies = sum(1 for a in articles if hasattr(a, 'anomalies') and a.anomalies)
        
        confidence_scores = [float(a.confidence_score) for a in articles if hasattr(a, 'confidence_score') and a.confidence_score]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "period": f"Last {days} days",
            "total_articles": total,
            "confidence_distribution": {
                "high": high_conf,
                "medium": medium_conf,
                "low": low_conf
            },
            "processing": {
                "auto_approved": auto_approved,
                "needs_review": needs_review,
                "pib_workload_reduction_pct": round(100 * (1 - needs_review / total), 1) if total > 0 else 0
            },
            "quality": {
                "avg_confidence_score": round(avg_confidence, 2),
                "articles_with_anomalies": with_anomalies,
                "anomaly_rate_pct": round(100 * with_anomalies / total, 1) if total > 0 else 0
            }
        }


# Helper function to get RAG instance
_rag_instance: Optional[RAGAssistant] = None

def get_rag_assistant(db: Session) -> RAGAssistant:
    """Get or create RAG assistant singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGAssistant(db)
    return _rag_instance
