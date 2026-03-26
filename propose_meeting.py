from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

print("[*] Proposing calendar meeting...\n")

# Propose meeting for today at 3:00 PM for 30 minutes
result = manager.propose_meeting(
    subject="This is amazing",
    attendees=["uriplonka@gmail.com"],
    start_time="2026-03-26T15:00:00",
    duration_minutes=30
)

print("[PROPOSAL] Meeting proposed:")
print("=" * 60)
print(result['preview'])
print("=" * 60)
print(f"\nProposal ID: {result['proposal_id']}")
print("\nShould I book this? (yes/no): ", end="")

# Auto-approve for testing
pending = manager.list_pending_meetings()
if pending:
    book_result = manager.approve_and_book_meeting(pending[0]['id'])
    print("\n[OK] Meeting booked!")
    print(f"Subject: {book_result['subject']}")
    print(f"Time: {book_result['start_time']}")
    print(f"Attendees: uriplonka@gmail.com")
