"""
Email and Calendar Integration for Henry
Handles drafting and sending emails, proposing and booking calendar meetings
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

# Configuration
CREDENTIALS_DIR = Path.home() / ".openclaw" / "credentials"
GMAIL_CREDENTIALS = CREDENTIALS_DIR / "gmail_oauth_token.json"
GMAIL_SECRETS = CREDENTIALS_DIR / "gmail_secrets.json"
HENRY_EMAIL = "henry.uriplonka@gmail.com"
URI_EMAIL = "uriplonka@gmail.com"

# OAuth scopes
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']


class EmailCalendarManager:
    """Manages email drafting and calendar meeting proposals"""
    
    def __init__(self):
        self.gmail_service = None
        self.calendar_service = None
        self.pending_emails = []  # Store drafts awaiting approval
        self.pending_meetings = []  # Store meeting proposals awaiting approval
        
        # Try to load existing credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load OAuth credentials from disk"""
        try:
            if GMAIL_CREDENTIALS.exists():
                with open(GMAIL_CREDENTIALS) as f:
                    creds_data = json.load(f)
                    creds = UserCredentials.from_authorized_user_info(creds_data, GMAIL_SCOPES)
                    if creds and creds.valid:
                        self.gmail_service = build('gmail', 'v1', credentials=creds)
                        self.calendar_service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"[WARN] Could not load existing credentials: {e}")
    
    def authenticate(self):
        """
        Set up OAuth flow for Gmail and Calendar access.
        User needs to approve access once.
        """
        if not GMAIL_SECRETS.exists():
            print(f"[ERROR] Credentials file not found: {GMAIL_SECRETS}")
            return False
        
        print("\n[AUTH] Setting up Gmail & Calendar API access...")
        print("[AUTH] A browser window will open for you to approve access.\n")
        
        try:
            # Load client secrets and start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_SECRETS,
                scopes=GMAIL_SCOPES + CALENDAR_SCOPES
            )
            
            # Run local server for OAuth callback (no_browser=False to open browser)
            # open_browser=True ensures browser opens automatically
            creds = flow.run_local_server(
                port=8080,
                open_browser=True
            )
            
            # Save credentials for future use
            CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
            with open(GMAIL_CREDENTIALS, 'w') as token:
                token.write(creds.to_json())
            
            # Build services
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            
            print("[OK] Gmail & Calendar authenticated successfully!")
            return True
        
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def draft_email(self, to: str, subject: str, body: str, approval_required: bool = True) -> dict:
        """
        Draft an email without sending.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            approval_required: If True, wait for approval before sending
        
        Returns:
            Draft object with id and preview
        """
        
        if not self.gmail_service:
            return {
                'status': 'error',
                'message': 'Gmail not authenticated. Run authenticate() first.'
            }
        
        # Add signature
        signature = "\n\n—\nHenry\nAI Chief of Staff\nAssistant to Uri Plonka"
        full_body = body + signature
        
        draft = {
            'id': f"draft_{datetime.now().timestamp()}",
            'to': to,
            'subject': subject,
            'body': full_body,
            'from': HENRY_EMAIL,
            'cc': URI_EMAIL,
            'created_at': datetime.now().isoformat(),
            'status': 'pending_approval' if approval_required else 'ready_to_send'
        }
        
        self.pending_emails.append(draft)
        
        return {
            'status': 'drafted',
            'draft_id': draft['id'],
            'preview': f"To: {to}\nCC: {URI_EMAIL}\nSubject: {subject}\n\n{body[:200]}...",
            'approval_required': approval_required
        }
    
    def list_pending_emails(self) -> list:
        """List all drafted emails awaiting approval"""
        return [
            {
                'id': d['id'],
                'to': d['to'],
                'subject': d['subject'],
                'created_at': d['created_at']
            }
            for d in self.pending_emails if d['status'] == 'pending_approval'
        ]
    
    def approve_and_send_email(self, draft_id: str) -> dict:
        """
        Approve a drafted email and send it.
        
        Args:
            draft_id: ID of the draft to send
        
        Returns:
            Result of sending
        """
        
        if not self.gmail_service:
            return {'status': 'error', 'message': 'Gmail not authenticated'}
        
        # Find the draft
        draft = None
        for d in self.pending_emails:
            if d['id'] == draft_id:
                draft = d
                break
        
        if not draft:
            return {'status': 'error', 'message': f'Draft {draft_id} not found'}
        
        try:
            # Create message
            message = self._create_message(
                from_addr=draft['from'],
                to_addr=draft['to'],
                cc_addr=draft['cc'],
                subject=draft['subject'],
                body=draft['body']
            )
            
            # Send via Gmail API
            result = self.gmail_service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            # Mark as sent
            draft['status'] = 'sent'
            draft['sent_at'] = datetime.now().isoformat()
            draft['message_id'] = result['id']
            
            return {
                'status': 'sent',
                'message_id': result['id'],
                'to': draft['to'],
                'subject': draft['subject']
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _create_message(self, from_addr: str, to_addr: str, cc_addr: str, subject: str, body: str) -> dict:
        """Create a Gmail message object"""
        import base64
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to_addr
        message['cc'] = cc_addr
        message['from'] = from_addr
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def propose_meeting(self, subject: str, attendees: list, start_time: str = None, 
                       duration_minutes: int = 30, approval_required: bool = True) -> dict:
        """
        Propose a calendar meeting without booking.
        
        Args:
            subject: Meeting title
            attendees: List of email addresses to invite
            start_time: ISO format datetime (e.g., "2026-03-26T14:00:00")
            duration_minutes: Meeting duration
            approval_required: If True, wait for approval before booking
        
        Returns:
            Proposal object
        """
        
        if not self.calendar_service:
            return {
                'status': 'error',
                'message': 'Calendar not authenticated. Run authenticate() first.'
            }
        
        # Default to next available time if not specified
        if not start_time:
            start_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        proposal = {
            'id': f"meeting_{datetime.now().timestamp()}",
            'subject': subject,
            'attendees': attendees,
            'start_time': start_time,
            'duration_minutes': duration_minutes,
            'created_at': datetime.now().isoformat(),
            'status': 'pending_approval' if approval_required else 'ready_to_book'
        }
        
        self.pending_meetings.append(proposal)
        
        return {
            'status': 'proposed',
            'proposal_id': proposal['id'],
            'preview': f"Subject: {subject}\nAttendees: {', '.join(attendees)}\nTime: {start_time}\nDuration: {duration_minutes} min",
            'approval_required': approval_required
        }
    
    def list_pending_meetings(self) -> list:
        """List all meeting proposals awaiting approval"""
        return [
            {
                'id': m['id'],
                'subject': m['subject'],
                'attendees': m['attendees'],
                'start_time': m['start_time'],
                'created_at': m['created_at']
            }
            for m in self.pending_meetings if m['status'] == 'pending_approval'
        ]
    
    def approve_and_book_meeting(self, proposal_id: str) -> dict:
        """
        Approve a meeting proposal and book it on calendar.
        
        Args:
            proposal_id: ID of the proposal to book
        
        Returns:
            Result of booking
        """
        
        if not self.calendar_service:
            return {'status': 'error', 'message': 'Calendar not authenticated'}
        
        # Find the proposal
        proposal = None
        for m in self.pending_meetings:
            if m['id'] == proposal_id:
                proposal = m
                break
        
        if not proposal:
            return {'status': 'error', 'message': f'Proposal {proposal_id} not found'}
        
        try:
            # Create calendar event
            event = {
                'summary': proposal['subject'],
                'start': {
                    'dateTime': proposal['start_time'],
                    'timeZone': 'America/Los_Angeles'
                },
                'end': {
                    'dateTime': (datetime.fromisoformat(proposal['start_time']) + 
                               timedelta(minutes=proposal['duration_minutes'])).isoformat(),
                    'timeZone': 'America/Los_Angeles'
                },
                'attendees': [{'email': email} for email in proposal['attendees']]
            }
            
            # Book via Calendar API with notifications
            result = self.calendar_service.events().insert(
                calendarId='primary',
                body=event,
                sendNotifications=True
            ).execute()
            
            # Mark as booked
            proposal['status'] = 'booked'
            proposal['booked_at'] = datetime.now().isoformat()
            proposal['event_id'] = result['id']
            
            return {
                'status': 'booked',
                'event_id': result['id'],
                'subject': proposal['subject'],
                'start_time': proposal['start_time']
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def cancel_meeting(self, proposal_id: str) -> dict:
        """
        Cancel a booked meeting.
        
        Args:
            proposal_id: ID of the meeting to cancel
        
        Returns:
            Result of cancellation
        """
        
        if not self.calendar_service:
            return {'status': 'error', 'message': 'Calendar not authenticated'}
        
        # Find the meeting
        meeting = None
        for m in self.pending_meetings:
            if m['id'] == proposal_id:
                meeting = m
                break
        
        if not meeting:
            return {'status': 'error', 'message': f'Meeting {proposal_id} not found'}
        
        if meeting['status'] != 'booked':
            return {'status': 'error', 'message': f'Meeting not booked yet'}
        
        try:
            # Delete via Calendar API with notifications
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=meeting['event_id'],
                sendNotifications=True
            ).execute()
            
            # Mark as cancelled
            meeting['status'] = 'cancelled'
            meeting['cancelled_at'] = datetime.now().isoformat()
            
            return {
                'status': 'cancelled',
                'subject': meeting['subject'],
                'event_id': meeting['event_id']
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self) -> dict:
        """Get authentication and pending items status"""
        return {
            'gmail_authenticated': self.gmail_service is not None,
            'calendar_authenticated': self.calendar_service is not None,
            'pending_emails': len(self.list_pending_emails()),
            'pending_meetings': len(self.list_pending_meetings())
        }


# Example usage
if __name__ == "__main__":
    manager = EmailCalendarManager()
    
    print(f"Status: {manager.get_status()}")
    
    if not manager.gmail_service:
        print("\n[INFO] Run setup:")
        print("manager.authenticate()")
