import os
import re
import json
import base64
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss
import gc
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of document with metadata"""
    content: str
    source: str
    url: Optional[str] = None
    title: Optional[str] = None

class TDSVirtualTA:
    """
    Memory-efficient TDS Virtual TA system using semantic search
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[DocumentChunk] = []
        self.embeddings = None
        self.index = None
        self.model = None
        
        # Initialize the system
        self._load_model()
        self._load_and_process_documents()
        self._build_search_index()
        
        # Clear memory after initialization
        gc.collect()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        logger.info("Loading sentence transformer model...")
        # Use a lightweight model to save memory
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    
    def _chunk_text(self, text: str, source: str, url: Optional[str] = None, title: Optional[str] = None) -> List[DocumentChunk]:
        """Split text into overlapping chunks"""
        chunks = []
        sentences = re.split(r'[.!?]+', text)
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        source=source,
                        url=url,
                        title=title
                    ))
                current_chunk = sentence + ". "
        
        # Add the last chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                source=source,
                url=url,
                title=title
            ))
        
        return chunks
    
    def _extract_links_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract markdown links from text"""
        pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
        matches = re.findall(pattern, text)
        return [{"text": text, "url": url} for text, url in matches]
    
    def _load_markdown_file(self, filepath: str) -> str:
        """Load markdown file with error handling"""
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return ""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return ""
    
    def _load_and_process_documents(self):
        """Load and chunk all documents"""
        logger.info("Loading and processing documents...")
        
        # Load course content
        course_content = self._load_markdown_file("course.md")
        if course_content:
            course_chunks = self._chunk_text(course_content, "course")
            self.chunks.extend(course_chunks)
            logger.info(f"Added {len(course_chunks)} course chunks")
        
        # Load discourse content
        discourse_content = self._load_markdown_file("discourse.md")
        if discourse_content:
            discourse_chunks = self._chunk_text(discourse_content, "discourse")
            self.chunks.extend(discourse_chunks)
            logger.info(f"Added {len(discourse_chunks)} discourse chunks")
        
        # Load discourse posts JSON for better link extraction
        try:
            if os.path.exists("discourse_posts.json"):
                with open("discourse_posts.json", "r", encoding="utf-8") as f:
                    posts_data = json.load(f)
                
                # Process posts and add to chunks
                for post in posts_data[:1000]:  # Limit to first 1000 posts to save memory
                    if isinstance(post, dict) and 'content' in post:
                        post_chunks = self._chunk_text(
                            post['content'], 
                            "discourse_post",
                            url=post.get('url'),
                            title=post.get('title')
                        )
                        self.chunks.extend(post_chunks)
        except Exception as e:
            logger.error(f"Error loading discourse posts: {e}")
        
        logger.info(f"Total chunks created: {len(self.chunks)}")
    
    def _build_search_index(self):
        """Build FAISS index for semantic search"""
        if not self.chunks:
            logger.warning("No chunks available for indexing")
            return
        
        logger.info("Building search index...")
        
        # Create embeddings
        texts = [chunk.content for chunk in self.chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.index.add(self.embeddings.astype('float32'))
        
        logger.info(f"Search index built with {len(self.chunks)} documents")
    
    def _search_similar_chunks(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar chunks using semantic search"""
        if not self.index or not self.chunks:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def _extract_relevant_links(self, chunks: List[Tuple[DocumentChunk, float]]) -> List[Dict[str, str]]:
        """Extract relevant links from chunks"""
        links = []
        seen_urls = set()
        
        for chunk, score in chunks:
            # Extract links from chunk content
            chunk_links = self._extract_links_from_text(chunk.content)
            
            # Add chunk URL if available
            if chunk.url and chunk.url not in seen_urls:
                links.append({
                    "url": chunk.url,
                    "text": chunk.title or f"Relevant content from {chunk.source}"
                })
                seen_urls.add(chunk.url)
            
            # Add extracted links
            for link in chunk_links:
                if link["url"] not in seen_urls:
                    links.append(link)
                    seen_urls.add(link["url"])
        
        return links[:5]  # Limit to top 5 links
    
    def _generate_answer(self, query: str, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> str:
        """Generate answer based on relevant chunks"""
        if not relevant_chunks:
            return "I couldn't find specific information to answer your question. Please try rephrasing or ask about a different topic related to the TDS course."
        
        # Combine top chunks for context
        context_parts = []
        for chunk, score in relevant_chunks[:3]:  # Use top 3 chunks
            if score > 0.3:  # Only use chunks with good relevance
                context_parts.append(chunk.content)
        
        if not context_parts:
            return "I found some related information, but it may not directly answer your question. Please try rephrasing your question."
        
        # Create a comprehensive answer
        context = "\n\n".join(context_parts)
        
        # Simple answer generation based on context
        answer = f"Based on the course content and discourse posts, here's what I found:\n\n"
        answer += context[:1000]  # Limit answer length
        
        if len(context) > 1000:
            answer += "\n\n[Content truncated for brevity]"
        
        return answer
    
    def answer_question(self, question: str, image_base64: Optional[str] = None) -> Tuple[str, List[Dict[str, str]]]:
        """
        Answer a student question with optional image
        
        Args:
            question: The student's question
            image_base64: Optional base64 encoded image
            
        Returns:
            Tuple of (answer, links)
        """
        try:
            # For now, we'll ignore images to keep it simple and memory-efficient
            # In a full implementation, you'd use OCR or image analysis here
            if image_base64:
                logger.info("Image provided but not processed in this version")
            
            # Search for relevant chunks
            relevant_chunks = self._search_similar_chunks(question)
            
            # Generate answer
            answer = self._generate_answer(question, relevant_chunks)
            
            # Extract relevant links
            links = self._extract_relevant_links(relevant_chunks)
            
            return answer, links
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I encountered an error while processing your question. Please try again.", []

def load_documents() -> List[Dict[str, str]]:
    """Legacy function for backward compatibility"""
    ta = TDSVirtualTA()
    return [{"source": "virtual_ta", "content": "TDS Virtual TA system"}]

def search_documents(query: str, documents: List[Dict]) -> Tuple[str, List[Dict[str, str]]]:
    """Legacy function for backward compatibility"""
    ta = TDSVirtualTA()
    return ta.answer_question(query)
