import os
import re
import json
import base64
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging
from collections import Counter
import math

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
    keywords: List[str] = None

class LightweightTDSVirtualTA:
    """
    Ultra-lightweight TDS Virtual TA system using keyword-based search
    Memory usage: ~50-100MB
    """
    
    def __init__(self, chunk_size: int = 300):
        self.chunk_size = chunk_size
        self.chunks: List[DocumentChunk] = []
        self.keyword_index: Dict[str, List[int]] = {}
        
        # Initialize the system
        self._load_and_process_documents()
        self._build_keyword_index()
        
        logger.info(f"Lightweight TDS Virtual TA initialized with {len(self.chunks)} chunks")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove markdown and special characters
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words and filter
        words = clean_text.split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Count frequency and return top keywords
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _chunk_text(self, text: str, source: str, url: Optional[str] = None, title: Optional[str] = None) -> List[DocumentChunk]:
        """Split text into chunks"""
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
                    keywords = self._extract_keywords(current_chunk)
                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        source=source,
                        url=url,
                        title=title,
                        keywords=keywords
                    ))
                current_chunk = sentence + ". "
        
        # Add the last chunk
        if current_chunk:
            keywords = self._extract_keywords(current_chunk)
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                source=source,
                url=url,
                title=title,
                keywords=keywords
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
        
        # Load limited discourse posts for memory efficiency
        try:
            if os.path.exists("discourse_posts.json"):
                with open("discourse_posts.json", "r", encoding="utf-8") as f:
                    posts_data = json.load(f)
                
                # Process only first 500 posts to save memory
                for post in posts_data[:500]:
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
    
    def _build_keyword_index(self):
        """Build keyword index for fast search"""
        logger.info("Building keyword index...")
        
        for i, chunk in enumerate(self.chunks):
            if chunk.keywords:
                for keyword in chunk.keywords:
                    if keyword not in self.keyword_index:
                        self.keyword_index[keyword] = []
                    self.keyword_index[keyword].append(i)
        
        logger.info(f"Keyword index built with {len(self.keyword_index)} keywords")
    
    def _calculate_similarity(self, query: str, chunk: DocumentChunk) -> float:
        """Calculate similarity between query and chunk using TF-IDF-like scoring"""
        query_words = set(re.findall(r'\w+', query.lower()))
        chunk_words = set(chunk.keywords) if chunk.keywords else set()
        
        if not query_words or not chunk_words:
            return 0.0
        
        # Calculate intersection
        intersection = query_words.intersection(chunk_words)
        
        if not intersection:
            return 0.0
        
        # Simple similarity score
        similarity = len(intersection) / max(len(query_words), len(chunk_words))
        
        # Boost score for exact matches
        for word in query_words:
            if word in chunk.content.lower():
                similarity += 0.1
        
        return min(similarity, 1.0)
    
    def _search_similar_chunks(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar chunks using keyword matching"""
        if not self.chunks:
            return []
        
        # Get query keywords
        query_keywords = self._extract_keywords(query)
        
        # Find chunks that contain query keywords
        candidate_chunks = set()
        for keyword in query_keywords:
            if keyword in self.keyword_index:
                candidate_chunks.update(self.keyword_index[keyword])
        
        # Calculate similarity scores
        chunk_scores = []
        for chunk_idx in candidate_chunks:
            if chunk_idx < len(self.chunks):
                chunk = self.chunks[chunk_idx]
                score = self._calculate_similarity(query, chunk)
                if score > 0.1:  # Only include relevant chunks
                    chunk_scores.append((chunk, score))
        
        # Sort by score and return top k
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        return chunk_scores[:top_k]
    
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
            if score > 0.2:  # Only use chunks with good relevance
                context_parts.append(chunk.content)
        
        if not context_parts:
            return "I found some related information, but it may not directly answer your question. Please try rephrasing your question."
        
        # Create a comprehensive answer
        context = "\n\n".join(context_parts)
        
        # Simple answer generation based on context
        answer = f"Based on the course content and discourse posts, here's what I found:\n\n"
        answer += context[:800]  # Limit answer length
        
        if len(context) > 800:
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

# For backward compatibility
def load_documents() -> List[Dict[str, str]]:
    """Legacy function for backward compatibility"""
    ta = LightweightTDSVirtualTA()
    return [{"source": "virtual_ta", "content": "TDS Virtual TA system"}]

def search_documents(query: str, documents: List[Dict]) -> Tuple[str, List[Dict[str, str]]]:
    """Legacy function for backward compatibility"""
    ta = LightweightTDSVirtualTA()
    return ta.answer_question(query) 