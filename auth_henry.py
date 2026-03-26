"""Authenticate as Henry"""
from email_calendar import EmailCalendarManager

print("[*] Starting OAuth flow for henry.uriplonka@gmail.com\n")
print("[AUTH] A browser window will open.")
print("[AUTH] Sign in as: henry.uriplonka@gmail.com")
print("[AUTH] Approve the access request\n")

manager = EmailCalendarManager()
result = manager.authenticate()

if result:
    print("\n[OK] Authentication successful!")
    print(f"Status: {manager.get_status()}")
else:
    print("\n[ERROR] Authentication failed")
