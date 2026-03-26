"""Draft and send email with approval"""
from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

print("[*] Drafting email...\n")

# Draft the email
result = manager.draft_email(
    to="uriplonka@gmail.com",
    subject="hello",
    body="holdy smoeks"
)

print("[DRAFT] Email drafted:")
print("=" * 60)
print(result['preview'])
print("=" * 60)
print(f"\nDraft ID: {result['draft_id']}")
print("\nWaiting for approval...")
print("Type 'approve' to send, or 'cancel' to discard: ", end="")

response = input().strip().lower()

if response == "approve":
    pending = manager.list_pending_emails()
    if pending:
        send_result = manager.approve_and_send_email(pending[0]['id'])
        print(f"\n[OK] Email sent!")
        print(f"To: {send_result['to']}")
        print(f"Subject: {send_result['subject']}")
        print(f"Message ID: {send_result['message_id']}")
else:
    print("\n[CANCEL] Email discarded")
