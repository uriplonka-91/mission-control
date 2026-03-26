from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

# Draft
manager.draft_email(
    to="uriplonka@gmail.com",
    subject="hello",
    body="holdy smoeks"
)

# Get pending
pending = manager.list_pending_emails()

# Send
if pending:
    result = manager.approve_and_send_email(pending[0]['id'])
    print(f"[OK] Email sent!")
    print(f"From: henry.uriplonka@gmail.com")
    print(f"To: {result['to']}")
    print(f"Subject: {result['subject']}")
