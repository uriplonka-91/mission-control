"""Test email/calendar setup"""
from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()
print("[*] Testing Gmail & Calendar setup...\n")

# Try to authenticate
print("[AUTH] Starting authentication...")
result = manager.authenticate()

if result:
    print("\n[OK] Authentication successful!")
    status = manager.get_status()
    print(f"Status: {status}\n")
    
    # Test drafting an email
    print("[TEST] Drafting test email...")
    draft_result = manager.draft_email(
        to="uriplonka@gmail.com",
        subject="Test from Henry",
        body="If you see this, Gmail is working!"
    )
    print(f"Draft result: {draft_result}\n")
    
    # Test proposing a meeting
    print("[TEST] Proposing test meeting...")
    meeting_result = manager.propose_meeting(
        subject="Test Meeting",
        attendees=["uriplonka@gmail.com"],
        start_time="2026-03-26T14:00:00"
    )
    print(f"Meeting result: {meeting_result}\n")
    
    print("[OK] All tests passed!")
else:
    print("\n[ERROR] Authentication failed")
