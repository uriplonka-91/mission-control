"""
Flask API for email and calendar operations
"""

from flask import Flask, request, jsonify
from router import TaskRouter
from functools import wraps

app = Flask(__name__)
router = TaskRouter()

# Simple auth decorator
def require_password(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = request.headers.get('X-Password')
        if password != 'mission2024':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

---

## EMAIL ENDPOINTS

@app.route('/api/email/draft', methods=['POST'])
@require_password
def draft_email():
    """Draft an email"""
    data = request.json
    
    result = router.draft_email(
        to=data.get('to'),
        subject=data.get('subject'),
        body=data.get('body')
    )
    
    return jsonify(result)

@app.route('/api/email/pending', methods=['GET'])
@require_password
def get_pending_emails():
    """List pending emails"""
    pending = router.list_pending_emails()
    return jsonify({'pending': pending})

@app.route('/api/email/send', methods=['POST'])
@require_password
def send_email():
    """Send an approved email"""
    data = request.json
    draft_id = data.get('draft_id')
    
    result = router.send_email(draft_id)
    return jsonify(result)

@app.route('/api/email/preview/<draft_id>', methods=['GET'])
@require_password
def preview_email(draft_id):
    """Get email preview for approval"""
    pending = router.list_pending_emails()
    
    for email in pending:
        if email['id'] == draft_id:
            return jsonify({
                'id': email['id'],
                'to': email['to'],
                'subject': email['subject'],
                'created_at': email['created_at']
            })
    
    return jsonify({'error': 'Email not found'}), 404

---

## CALENDAR ENDPOINTS

@app.route('/api/calendar/propose', methods=['POST'])
@require_password
def propose_meeting():
    """Propose a calendar meeting"""
    data = request.json
    
    result = router.propose_meeting(
        subject=data.get('subject'),
        attendees=data.get('attendees', []),
        start_time=data.get('start_time'),
        duration_minutes=data.get('duration_minutes', 30)
    )
    
    return jsonify(result)

@app.route('/api/calendar/pending', methods=['GET'])
@require_password
def get_pending_meetings():
    """List pending meetings"""
    pending = router.list_pending_meetings()
    return jsonify({'pending': pending})

@app.route('/api/calendar/book', methods=['POST'])
@require_password
def book_meeting():
    """Book an approved meeting"""
    data = request.json
    proposal_id = data.get('proposal_id')
    
    result = router.book_meeting(proposal_id)
    return jsonify(result)

@app.route('/api/calendar/cancel', methods=['POST'])
@require_password
def cancel_meeting():
    """Cancel a booked meeting"""
    data = request.json
    proposal_id = data.get('proposal_id')
    
    result = router.cancel_meeting(proposal_id)
    return jsonify(result)

@app.route('/api/calendar/preview/<proposal_id>', methods=['GET'])
@require_password
def preview_meeting(proposal_id):
    """Get meeting preview for approval"""
    pending = router.list_pending_meetings()
    
    for meeting in pending:
        if meeting['id'] == proposal_id:
            return jsonify({
                'id': meeting['id'],
                'subject': meeting['subject'],
                'attendees': meeting['attendees'],
                'start_time': meeting['start_time'],
                'created_at': meeting['created_at']
            })
    
    return jsonify({'error': 'Meeting not found'}), 404

---

## STATUS ENDPOINT

@app.route('/api/status', methods=['GET'])
@require_password
def get_status():
    """Get system status"""
    status = router.email_manager.get_status()
    return jsonify(status)

---

## ERROR HANDLER

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
