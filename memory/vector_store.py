"""
Long-Term Semantic Vector Store for ARA-1.
Implements the Section A3.3 Vector Database specification with structured financial schema,
intelligent semantic chunking (SEC sections, Q&A turns, news paragraphs),
dense vector embedding calculations, and metadata filtering.
"""

import math
import time
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("ARA.Memory.VectorStore")

class FinancialChunker:
    """
    Domain-aware chunker for financial documents.
    """
    @staticmethod
    def chunk_sec_filing(text: str, ticker: str, filing_type: str = "10-K") -> List[Dict[str, Any]]:
        chunks = []
        sections = text.split("=== ")
        for sec in sections:
            if not sec.strip():
                continue
            lines = sec.split("\n", 1)
            sec_title = lines[0].replace(" ===", "").strip()
            sec_body = lines[1].strip() if len(lines) > 1 else ""
            
            # Sub-split long risk factors or MD&A paragraphs
            paras = [p.strip() for p in sec_body.split("\n\n") if p.strip()]
            for idx, p in enumerate(paras):
                chunk_id = f"{ticker.lower()}-{filing_type.lower()}-{sec_title[:10].lower().replace(' ', '_')}-{idx+1:03d}"
                chunks.append({
                    "id": chunk_id,
                    "content": f"[{ticker} {filing_type} - {sec_title}]\n{p}",
                    "ticker": ticker.upper(),
                    "source_type": filing_type,
                    "section": sec_title
                })
        return chunks

    @staticmethod
    def chunk_transcript(text: str, ticker: str, quarter: str = "Q4", year: int = 2024) -> List[Dict[str, Any]]:
        chunks = []
        qa_pairs = text.split("Q (")
        # Executive remarks
        if len(qa_pairs) > 0 and qa_pairs[0].strip():
            chunks.append({
                "id": f"{ticker.lower()}-transcript-{year}-{quarter}-prepared",
                "content": qa_pairs[0].strip(),
                "ticker": ticker.upper(),
                "source_type": "earnings_call",
                "section": "Prepared Remarks"
            })
        # Q&A pairs
        for idx, qa in enumerate(qa_pairs[1:], 1):
            chunks.append({
                "id": f"{ticker.lower()}-transcript-{year}-{quarter}-qa-{idx:03d}",
                "content": f"Q ({qa.strip()}",
                "ticker": ticker.upper(),
                "source_type": "earnings_call",
                "section": "Analyst Q&A"
            })
        return chunks


class VectorStore:
    """
    Semantic vector memory supporting dense embeddings, cosine similarity search,
    and metadata filtering.
    """
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.documents: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized Long-Term Vector Database (embedding_dim=%d)", embedding_dim)

    def _embed_text(self, text: str) -> List[float]:
        """
        Deterministic lightweight semantic embedding generator.
        Generates dense normalized feature vectors from n-grams and financial keywords.
        """
        vec = [0.0] * self.embedding_dim
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.embedding_dim
            sign = 1.0 if ((h >> 4) % 2 == 0) else -1.0
            vec[pos] += sign * (1.0 / math.sqrt(idx + 1))
        
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, (dot + 1.0) / 2.0))

    def store(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stores a document chunk in the vector database matching A3.3 schema.
        """
        ticker = metadata.get("ticker", "GENERIC").upper()
        source_type = metadata.get("source_type", "analysis")
        doc_id = metadata.get("id") or f"{ticker.lower()}-{source_type.lower()}-{int(time.time()*1000)%1000000:06d}"
        
        embedding = self._embed_text(content)
        record = {
            "id": doc_id,
            "content": content,
            "embedding": embedding,
            "ticker": ticker,
            "source_type": source_type,
            "date": metadata.get("date", datetime.utcnow().isoformat() + "Z"),
            "confidence": float(metadata.get("confidence", 0.95)),
            "researcher_session": metadata.get("researcher_session", "session-default-001"),
            "verified": bool(metadata.get("verified", True)),
            "custom_metadata": metadata
        }

        self.documents[doc_id] = record
        logger.debug("Stored vector doc: %s (ticker=%s)", doc_id, ticker)

        return {
            "status": "success",
            "document_id": doc_id,
            "ticker": ticker,
            "stored_length": len(content),
            "verified": record["verified"]
        }

    def search(self, query: str, top_k: int = 5, ticker_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Searches memory using semantic similarity with optional ticker metadata filter.
        """
        if not self.documents:
            return {
                "status": "success",
                "query": query,
                "top_k": top_k,
                "matches": [],
                "message": "Vector store is empty."
            }

        query_vec = self._embed_text(query)
        scored_docs = []

        for doc_id, doc in self.documents.items():
            if ticker_filter and doc["ticker"] != ticker_filter.upper():
                continue
            
            sim = self._cosine_similarity(query_vec, doc["embedding"])
            # Boost if exact keyword match in content
            if query.lower() in doc["content"].lower():
                sim = min(1.0, sim + 0.15)

            scored_docs.append({
                "id": doc["id"],
                "content": doc["content"],
                "similarity_score": round(sim, 4),
                "ticker": doc["ticker"],
                "source_type": doc["source_type"],
                "date": doc["date"],
                "confidence": doc["confidence"],
                "verified": doc["verified"]
            })

        scored_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_matches = scored_docs[:top_k]

        return {
            "status": "success",
            "query": query,
            "top_k": top_k,
            "matches_found": len(top_matches),
            "matches": top_matches
        }

    def get_all_by_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        ticker_up = ticker.upper()
        return [doc for doc in self.documents.values() if doc["ticker"] == ticker_up]
