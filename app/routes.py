import asyncio
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import HelpRequest, KnowledgeItem
from app.agent import agent
from app.knowledge_base import KnowledgeBase
from pyngrok import ngrok

main = Blueprint('main', __name__)

# Create knowledge base - this will be initialized lazily
knowledge_base = KnowledgeBase()

@main.route('/')
def index():
    """Render the main supervisor dashboard"""
    return render_template('index.html')

@main.route('/knowledge')
def knowledge():
    """Render the knowledge base view"""
    return render_template('knowledge.html')

@main.route('/api/help-requests', methods=['GET'])
def get_help_requests():
    """Get all help requests"""
    status = request.args.get('status', None)
    
    query = HelpRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(HelpRequest.created_at.desc()).all()
    return jsonify([req.to_dict() for req in requests])

@main.route('/api/help-requests/<int:request_id>', methods=['GET'])
def get_help_request(request_id):
    """Get a specific help request"""
    help_request = HelpRequest.query.get_or_404(request_id)
    return jsonify(help_request.to_dict())

@main.route('/api/help-requests/<int:request_id>/resolve', methods=['POST'])
def resolve_help_request(request_id):
    """Resolve a help request with supervisor's answer"""
    data = request.get_json()
    
    if not data or 'answer' not in data:
        return jsonify({'error': 'Answer is required'}), 400
        
    help_request = HelpRequest.query.get_or_404(request_id)
    
    if help_request.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
        
    # Update the help request
    help_request.answer = data['answer']
    help_request.status = 'resolved'
    help_request.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    # Follow up with customer
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(agent.follow_up_with_customer(request_id))
    
    # Update knowledge base
    agent.update_knowledge_base(request_id)
    
    return jsonify({'success': True})

@main.route('/api/help-requests/<int:request_id>/unresolve', methods=['POST'])
def unresolve_help_request(request_id):
    """Mark a help request as unresolved"""
    help_request = HelpRequest.query.get_or_404(request_id)
    
    if help_request.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
        
    help_request.status = 'unresolved'
    db.session.commit()
    
    return jsonify({'success': True})

@main.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """Get all knowledge items"""
    items = knowledge_base.get_all_knowledge()
    return jsonify([item.to_dict() for item in items])

@main.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    """Add a new knowledge item"""
    data = request.get_json()
    
    if not data or 'question' not in data or 'answer' not in data:
        return jsonify({'error': 'Question and answer are required'}), 400
        
    item = knowledge_base.add_knowledge(
        question=data['question'],
        answer=data['answer']
    )
    
    return jsonify(item.to_dict())

@main.route('/api/simulate-call', methods=['POST'])
def simulate_call():
    """Simulate an incoming call for testing"""
    data = request.get_json()
    
    question = data.get('question', 'Do you offer hair coloring services?')
    phone = data.get('phone', '1234567890')
    
    # Try to answer directly
    answer, confidence = knowledge_base.get_answer(question)
    
    if answer and confidence > 0.6:
        # Known answer
        return jsonify({
            'status': 'answered',
            'question': question,
            'answer': answer,
            'confidence': confidence
        })
    else:
        # Create help request
        help_request = HelpRequest(
            customer_phone=phone,
            question=question,
            status="pending",
            call_session_id="simulated-call"
        )
        db.session.add(help_request)
        db.session.commit()
        
        # Simulate notification
        print(f"[SUPERVISOR NOTIFICATION] Hey, I need help answering: {question}")
        
        return jsonify({
            'status': 'escalated',
            'request_id': help_request.id,
            'question': question
        })

@main.route('/setup-ngrok', methods=['GET'])
def setup_ngrok():
    """Setup ngrok tunnel for local development"""
    # Get the ngrok tunnel
    port = current_app.config.get('PORT', 5000)
    public_url = ngrok.connect(port).public_url
    
    return jsonify({
        'ngrok_url': public_url
    })

@main.route('/webhook/livekit', methods=['POST'])
def livekit_webhook():
    """Handle LiveKit webhooks"""
    data = request.get_json()
    
    # In a real implementation, we would verify the signature
    
    # Process asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(agent.handle_call(
        data.get('room_name', 'demo-room'),
        data.get('participant_identity', 'customer')
    ))
    
    return jsonify({'received': True})