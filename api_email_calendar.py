"""
Flask API for email, calendar, and cost operations
"""

from flask import Flask, request, jsonify
from router import TaskRouter
from cost_anomaly_detector import AnomalyDetector
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

## COST ENDPOINTS

@app.route('/api/costs', methods=['GET'])
@require_password
def get_costs():
    """Get cost data"""
    try:
        detector = AnomalyDetector()
        breakdown = detector.get_cost_breakdown_today()
    except:
        breakdown = {}
    
    # Format for frontend
    cost_data = {
        'today': {
            'total': sum(d.get('total_cost', 0) for d in breakdown.values()) if breakdown else 0,
            'email': breakdown.get('email_response_drafted', {}).get('total_cost', 0) if breakdown else 0,
            'calendar': breakdown.get('calendar_event_booked', {}).get('total_cost', 0) if breakdown else 0,
            'other': sum(d.get('total_cost', 0) for k, d in breakdown.items() if k not in ['email_response_drafted', 'calendar_event_booked']) if breakdown else 0,
            'email_count': breakdown.get('email_response_drafted', {}).get('count', 0) if breakdown else 0,
            'calendar_count': breakdown.get('calendar_event_booked', {}).get('count', 0) if breakdown else 0,
            'other_count': sum(d.get('count', 0) for k, d in breakdown.items() if k not in ['email_response_drafted', 'calendar_event_booked']) if breakdown else 0,
            'recent_transactions': []
        },
        'limits': {
            'daily_budget': 0.50,
            'max_emails': 50,
            'max_claude': 10,
            'auto_filter_blocks': 80
        },
        'daily_stats': {}
    }
    
    return jsonify(cost_data)

@app.route('/api/cost-anomalies', methods=['GET'])
@require_password
def get_cost_anomalies():
    """Get cost anomalies and leaks"""
    try:
        detector = AnomalyDetector()
        report = detector.generate_report()
    except:
        report = {
            'anomalies': [],
            'cost_by_area': [],
            'alerts': [],
            'total_today': 0
        }
    
    return jsonify({
        'anomalies': report.get('anomalies', []),
        'cost_by_area': report.get('cost_by_area', []),
        'alerts': report.get('alerts', []),
        'total_today': report.get('total_today', 0)
    })

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
