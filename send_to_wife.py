from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

print("[*] Drafting email to Hadassah...\n")

# Draft the email
result = manager.draft_email(
    to="hadassahplonka@gmail.com",
    subject="I love you",
    body="this is so cool!"
)

print("[DRAFT] Email drafted:")
print("=" * 60)
print(result['preview'])
print("=" * 60)

# Send immediately
pending = manager.list_pending_emails()
if pending:
    send_result = manager.approve_and_send_email(pending[0]['id'])
    print(f"\n[OK] Email sent!")
    print(f"To: {send_result['to']}")
    print(f"Subject: {send_result['subject']}")
