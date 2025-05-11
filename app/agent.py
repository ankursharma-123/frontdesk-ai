import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
import requests
from config import Config
from app.knowledge_base import KnowledgeBase
from app import db
from app.models import HelpRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        # Create knowledge base but don't initialize it yet
        self.knowledge_base = KnowledgeBase()
        self.config = Config()
        
    async def handle_call(self, room_name, participant_identity):
        """Handle an incoming call from LiveKit"""
        logger.info(f"Handling call in room {room_name} from {participant_identity}")
        
        # This would be replaced with actual LiveKit connection code
        # For demo purposes, we'll just simulate the call flow
        
        # Simulate customer asking a question
        customer_phone = "1234567890"  # In a real system, we'd get this from participant metadata
        question = "Do you offer hair coloring services?"
        
        # Try to answer the question
        answer, confidence = self.knowledge_base.get_answer(question)
        
        if answer and confidence > 0.6:
            # We know the answer, respond directly
            await self._respond_to_caller(room_name, participant_identity, answer)
            logger.info(f"Responded to question: {question} with answer: {answer}")
            return True
        else:
            # We don't know the answer, create help request
            await self._escalate_to_supervisor(room_name, participant_identity, customer_phone, question)
            return False
            
    async def _respond_to_caller(self, room_name, participant_identity, message):
        """Send a response to the caller via LiveKit"""
        # In a real implementation, this would use LiveKit's SDK to speak the message
        logger.info(f"AI to caller: {message}")
        
        # Simulate LiveKit response
        print(f"[LIVEKIT SIMULATION] AI to {participant_identity} in room {room_name}: {message}")
        
    async def _escalate_to_supervisor(self, room_name, participant_identity, customer_phone, question):
        """Create a help request and notify the supervisor"""
        logger.info(f"Escalating question to supervisor: {question}")
        
        # Tell the caller we're escalating
        await self._respond_to_caller(
            room_name, 
            participant_identity, 
            "Let me check with my supervisor and get back to you."
        )
        
        # Create help request in database
        help_request = HelpRequest(
            customer_phone=customer_phone,
            question=question,
            status="pending",
            call_session_id=room_name
        )
        db.session.add(help_request)
        db.session.commit()
        
        # Simulate sending text to supervisor
        self._notify_supervisor(help_request)
        
        # Start timeout checker for this request
        asyncio.create_task(self._check_request_timeout(help_request.id))
        
    def _notify_supervisor(self, help_request):
        """Send notification to supervisor about the pending request"""
        # In a real system, this would send an SMS or notification
        # For demo, we'll just log it
        print(f"[SUPERVISOR NOTIFICATION] Hey, I need help answering: {help_request.question}")
        logger.info(f"Notified supervisor about help request #{help_request.id}")
        
    async def _check_request_timeout(self, request_id):
        """Check if a request has timed out after the configured timeout period"""
        timeout_minutes = self.config.REQUEST_TIMEOUT
        await asyncio.sleep(timeout_minutes * 60)  # Convert to seconds
        
        # Check if request is still pending
        help_request = HelpRequest.query.get(request_id)
        if help_request and help_request.status == "pending":
            # Mark as unresolved due to timeout
            help_request.status = "unresolved"
            db.session.commit()
            
            logger.info(f"Help request #{request_id} marked as unresolved due to timeout")
            
            # Could notify customer here about the timeout
            
    async def follow_up_with_customer(self, request_id):
        """Follow up with customer once supervisor provides an answer"""
        help_request = HelpRequest.query.get(request_id)
        if not help_request or help_request.status != "resolved":
            logger.error(f"Cannot follow up on request #{request_id}: Not resolved or not found")
            return False
            
        # In a real system, we would initiate a call or send SMS
        # For demo, we'll simulate it
        print(f"[CUSTOMER FOLLOW-UP] To {help_request.customer_phone}: {help_request.answer}")
        logger.info(f"Followed up with customer about help request #{request_id}")
        
        return True
        
    def update_knowledge_base(self, request_id):
        """Update knowledge base with the resolved request"""
        help_request = HelpRequest.query.get(request_id)
        if not help_request or help_request.status != "resolved":
            logger.error(f"Cannot update knowledge base from request #{request_id}")
            return False
            
        # Add to knowledge base
        self.knowledge_base.add_knowledge(
            question=help_request.question,
            answer=help_request.answer,
            help_request_id=help_request.id
        )
        
        logger.info(f"Knowledge base updated from help request #{request_id}")
        return True

# Create a singleton instance
agent = AIAgent()

# Example LiveKit room handler (simplified for demo)
async def livekit_room_handler(request):
    """Handle LiveKit webhook events"""
    # In a real implementation, this would properly parse and verify LiveKit webhooks
    
    # Extract room and participant info (simplified)
    room_name = request.get("room_name", "demo-room")
    participant_identity = request.get("participant_identity", "customer")
    
    # Handle the call
    await agent.handle_call(room_name, participant_identity)