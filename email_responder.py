"""
Auto-email responder with cost controls
Drafts responses to emails that need them, with full cost tracking
"""

import json
import time
from datetime import datetime
from pathlib import Path
from router import TaskRouter

# Configuration
LOGS_DIR = Path.home() / ".openclaw" / "workspace" / ".learnings"
COST_LOG = LOGS_DIR / "COST_LOG.json"
EMAIL_INBOX_LOG = LOGS_DIR / "EMAIL_INBOX.json"

# Rate limits
MAX_EMAILS_PER_DAY = 50
MAX_CLAUDE_CALLS_PER_DAY = 10
MAX_DAILY_COST = 0.50  # dollars

# Filtering rules
NO_REPLY_DOMAINS = [
    "noreply@", "no-reply@", "mailer-daemon@", "postmaster@",
    "support@", "notification@", "alert@"
]

NO_RESPONSE_KEYWORDS = [
    "confirm", "receipt", "delivered", "shipped", "order #",
    "invoice", "receipt", "thank you", "thanks"
]

NEEDS_RESPONSE_KEYWORDS = [
    "?", "help", "meeting", "question", "urgent", "asap",
    "request", "action required", "review", "approve"
]

NO_RESPONSE_SUBJECTS = [
    "[newsletter]", "[notification]", "[alert]", "[automated]",
    "weekly digest", "daily summary", "automatic"
]

# Known auto-senders (blacklist)
AUTO_SENDER_DOMAINS = [
    "mailchimp.com", "stripe.com", "github.com", "amazon.com",
    "google.com", "slack.com", "zoom.com", "sendgrid.net",
    "heroku.com", "wordpress.com", "twitter.com", "facebook.com"
]


class CostLogger:
    """Log all costs to a JSON file"""
    
    @staticmethod
    def log_cost(action_type: str, cost: float, details: dict = None):
        """Log a cost entry"""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'cost': cost,
            'details': details or {}
        }
        
        # Append to log
        entries = []
        if COST_LOG.exists():
            with open(COST_LOG) as f:
                entries = json.load(f)
        
        entries.append(entry)
        
        with open(COST_LOG, 'w') as f:
            json.dump(entries, f, indent=2)
    
    @staticmethod
    def get_today_cost() -> float:
        """Get total cost today"""
        if not COST_LOG.exists():
            return 0.0
        
        with open(COST_LOG) as f:
            entries = json.load(f)
        
        today = datetime.now().date()
        return sum(
            e['cost'] for e in entries
            if datetime.fromisoformat(e['timestamp']).date() == today
        )
    
    @staticmethod
    def get_daily_stats():
        """Get cost stats by day"""
        if not COST_LOG.exists():
            return {}
        
        with open(COST_LOG) as f:
            entries = json.load(f)
        
        stats = {}
        for entry in entries:
            date = datetime.fromisoformat(entry['timestamp']).date().isoformat()
            if date not in stats:
                stats[date] = {'total': 0, 'types': {}}
            
            stats[date]['total'] += entry['cost']
            
            action_type = entry['type']
            if action_type not in stats[date]['types']:
                stats[date]['types'][action_type] = 0
            stats[date]['types'][action_type] += entry['cost']
        
        return stats


class EmailResponder:
    """Auto-respond to emails with cost controls"""
    
    def __init__(self):
        self.router = TaskRouter()
        self.today_cost = 0.0
        self.emails_processed_today = 0
        self.claude_calls_today = 0
    
    def should_skip_auto_response(self, from_email: str, subject: str, body: str) -> tuple:
        """
        Determine if email should skip auto-response.
        Returns: (should_skip, reason)
        """
        
        # Check no-reply domains
        from_lower = from_email.lower()
        for domain in NO_REPLY_DOMAINS:
            if domain in from_lower:
                return (True, "no_reply_domain")
        
        # Check auto-sender domains
        for domain in AUTO_SENDER_DOMAINS:
            if domain in from_lower:
                return (True, "auto_sender_domain")
        
        # Check subject
        subject_lower = subject.lower()
        for keyword in NO_RESPONSE_SUBJECTS:
            if keyword in subject_lower:
                return (True, "no_response_subject")
        
        return (False, None)
    
    def needs_response_heuristic(self, subject: str, body: str) -> bool:
        """
        Use keywords to guess if email needs response.
        Returns: True if likely needs response
        """
        text = (subject + " " + body).lower()
        
        # Check for obvious "no response needed"
        for keyword in NO_RESPONSE_KEYWORDS:
            if keyword in text:
                return False
        
        # Check for obvious "needs response"
        for keyword in NEEDS_RESPONSE_KEYWORDS:
            if keyword in text:
                return True
        
        # Default: uncertain (needs Claude)
        return None
    
    def check_rate_limits(self) -> tuple:
        """
        Check if we're within rate limits.
        Returns: (allowed, reason)
        """
        if self.emails_processed_today >= MAX_EMAILS_PER_DAY:
            return (False, f"Reached max {MAX_EMAILS_PER_DAY} emails/day")
        
        if self.claude_calls_today >= MAX_CLAUDE_CALLS_PER_DAY:
            return (False, f"Reached max {MAX_CLAUDE_CALLS_PER_DAY} Claude calls/day")
        
        today_cost = CostLogger.get_today_cost()
        if today_cost >= MAX_DAILY_COST:
            return (False, f"Reached max ${MAX_DAILY_COST}/day")
        
        return (True, None)
    
    def should_use_claude_for_response_check(self) -> bool:
        """Should we use Claude to check if response needed?"""
        # Only use Claude if we have budget
        return self.claude_calls_today < MAX_CLAUDE_CALLS_PER_DAY
    
    def process_email(self, from_email: str, subject: str, body: str) -> dict:
        """
        Process an incoming email.
        Returns: action and cost
        """
        
        # Check rate limits
        allowed, reason = self.check_rate_limits()
        if not allowed:
            return {'status': 'rate_limited', 'reason': reason, 'cost': 0}
        
        # Check if should skip
        skip, skip_reason = self.should_skip_auto_response(from_email, subject, body)
        if skip:
            CostLogger.log_cost('email_skipped', 0, {
                'from': from_email,
                'subject': subject,
                'reason': skip_reason
            })
            return {'status': 'skipped', 'reason': skip_reason, 'cost': 0}
        
        # Heuristic check
        heuristic_result = self.needs_response_heuristic(subject, body)
        
        if heuristic_result is False:
            # Clearly no response needed
            CostLogger.log_cost('email_no_response_needed', 0, {
                'from': from_email,
                'subject': subject,
                'method': 'heuristic'
            })
            return {'status': 'no_response_needed', 'method': 'heuristic', 'cost': 0}
        
        if heuristic_result is True:
            # Clearly needs response
            return self.draft_response(from_email, subject, body, method='heuristic')
        
        # Uncertain: use Claude (if within budget)
        if not self.should_use_claude_for_response_check():
            CostLogger.log_cost('email_uncertain_skipped', 0, {
                'from': from_email,
                'subject': subject,
                'reason': 'claude_budget_exhausted'
            })
            return {'status': 'skipped', 'reason': 'claude_budget_exhausted', 'cost': 0}
        
        # Ask Claude
        try:
            prompt = f"Subject: {subject}\n\nBody: {body}\n\nDoes this email need a response? Answer only 'yes' or 'no'."
            response = self.router.call_claude(prompt)
            
            self.claude_calls_today += 1
            cost = 0.0001  # Rough estimate for classification
            CostLogger.log_cost('email_classification', cost, {
                'from': from_email,
                'subject': subject
            })
            
            needs_response = 'yes' in response.lower()
            
            if not needs_response:
                return {'status': 'no_response_needed', 'method': 'claude', 'cost': cost}
            
            return self.draft_response(from_email, subject, body, method='claude', classification_cost=cost)
        
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'cost': 0}
    
    def draft_response(self, from_email: str, subject: str, body: str, 
                      method: str = 'unknown', classification_cost: float = 0) -> dict:
        """
        Draft a response to the email.
        """
        
        try:
            # Route through hybrid router
            response_body = self.router.execute(
                f"Draft a professional email response to:\n\nFrom: {from_email}\nSubject: {subject}\n\nBody: {body}",
                log=True
            )
            
            draft_cost = response_body['cost']
            total_cost = classification_cost + draft_cost
            
            CostLogger.log_cost('email_response_drafted', total_cost, {
                'from': from_email,
                'subject': subject,
                'method': method,
                'routing_model': response_body['model']
            })
            
            self.today_cost += total_cost
            self.emails_processed_today += 1
            
            return {
                'status': 'response_drafted',
                'from': from_email,
                'subject': subject,
                'response': response_body['output'][:300],  # First 300 chars
                'method': method,
                'cost': total_cost,
                'model': response_body['model']
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'cost': classification_cost}


if __name__ == "__main__":
    responder = EmailResponder()
    
    # Test
    print("[*] Email Responder Test\n")
    
    result = responder.process_email(
        from_email="test@example.com",
        subject="Question about project",
        body="Hi, do you have time to discuss the project tomorrow?"
    )
    
    print(f"Result: {result}")
    print(f"\nCost today: ${responder.today_cost:.4f}")
