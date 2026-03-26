from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

print("[*] Cancelling calendar meeting...\n")

# The meeting ID from the previous booking
meeting_id = "meeting_1774536160.491841"

result = manager.cancel_meeting(meeting_id)

if result['status'] == 'cancelled':
    print("[OK] Meeting cancelled!")
    print(f"Subject: {result['subject']}")
    print(f"Event ID: {result['event_id']}")
else:
    print(f"[ERROR] {result['message']}")
