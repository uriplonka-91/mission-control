"""Send test email"""
from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

print("[*] Drafting test email...\n")

# Draft the email
result = manager.draft_email(
    to="uriplonka@gmail.com",
    subject="test",
    body="hello"
)

print("[DRAFT] Email drafted:")
print(result['preview'])
print(f"\nDraft ID: {result['draft_id']}")

# List pending
pending = manager.list_pending_emails()
print(f"\nPending emails: {pending}")

# Approve and send
if pending:
    print("\n[SEND] Approving and sending...")
    send_result = manager.approve_and_send_email(pending[0]['id'])
    print(f"\n[OK] Email sent!")
    print(send_result)
