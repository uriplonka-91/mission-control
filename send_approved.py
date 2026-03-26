from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

pending = manager.list_pending_emails()
if pending:
    result = manager.approve_and_send_email(pending[0]['id'])
    print(f"[OK] Email sent!")
    print(f"To: {result['to']}")
    print(f"Subject: {result['subject']}")
    print(f"From: henry.uriplonka@gmail.com")
else:
    print("[ERROR] No pending emails found")
