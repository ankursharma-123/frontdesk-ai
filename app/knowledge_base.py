from app import db
from app.models import KnowledgeItem
import re

class KnowledgeBase:
    def __init__(self):
        # Load initial salon knowledge
        self.initial_knowledge = {
            "What are your business hours?": "Our salon is open Monday through Friday from 9 AM to 7 PM, Saturday from 10 AM to 6 PM, and Sunday from 12 PM to 5 PM.",
            "Do you offer haircuts?": "Yes, we offer haircuts for all hair types. Our stylists are experienced in various styles and techniques.",
            "How much does a haircut cost?": "Our haircuts start at $45 for short hair and $60 for long hair. Prices may vary depending on the stylist's experience level.",
            "Do I need an appointment?": "Yes, we recommend booking an appointment in advance. Walk-ins are accepted based on availability.",
            "Where are you located?": "We are located at 123 Beauty Lane, San Francisco, CA 94110."
        }
        # Don't initialize during construction - will be done lazily
        self._is_initialized = False
    
    def _initialize_knowledge(self):
        """Initialize the knowledge base with default information if empty"""
        # Check if knowledge base is empty
        if KnowledgeItem.query.count() == 0:
            # Add initial knowledge
            for question, answer in self.initial_knowledge.items():
                item = KnowledgeItem(question=question, answer=answer)
                db.session.add(item)
            db.session.commit()
        self._is_initialized = True
    
    def _ensure_initialized(self):
        """Make sure knowledge base is initialized before operations"""
        if not self._is_initialized:
            self._initialize_knowledge()
    
    def get_answer(self, question):
        """
        Try to find an answer for the given question
        Returns (answer, confidence) tuple
        """
        self._ensure_initialized()
        
        # Simple keyword matching for now
        question_lower = question.lower()
        
        # Get all knowledge items
        items = KnowledgeItem.query.all()
        
        best_match = None
        highest_score = 0
        
        for item in items:
            # Split into keywords and check for overlap
            keywords = set(re.findall(r'\w+', item.question.lower()))
            user_words = set(re.findall(r'\w+', question_lower))
            
            # Calculate overlap score
            overlap = len(keywords.intersection(user_words))
            total = len(keywords)
            
            if total > 0:
                score = overlap / total
                
                if score > highest_score:
                    highest_score = score
                    best_match = item
        
        # If confidence is above threshold, return the answer
        if highest_score > 0.6 and best_match:
            return best_match.answer, highest_score
        
        return None, 0
    
    def add_knowledge(self, question, answer, help_request_id=None):
        """Add a new item to the knowledge base"""
        self._ensure_initialized()
        
        item = KnowledgeItem(
            question=question,
            answer=answer,
            help_request_id=help_request_id
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    def get_all_knowledge(self):
        """Get all knowledge items"""
        self._ensure_initialized()
        
        return KnowledgeItem.query.order_by(KnowledgeItem.last_updated.desc()).all()