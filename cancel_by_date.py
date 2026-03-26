from email_calendar import EmailCalendarManager
from datetime import datetime, timedelta

manager = EmailCalendarManager()

if not manager.calendar_service:
    print("[ERROR] Calendar not authenticated")
    exit()

print("[*] Finding and cancelling 'This is amazing' meeting...\n")

try:
    # Get events for today
    now = datetime.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    end_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    
    events_result = manager.calendar_service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Find the meeting
    target_event = None
    for event in events:
        if event['summary'] == 'This is amazing':
            target_event = event
            break
    
    if target_event:
        # Delete it with notifications
        manager.calendar_service.events().delete(
            calendarId='primary',
            eventId=target_event['id'],
            sendNotifications=True
        ).execute()
        
        print("[OK] Meeting cancelled!")
        print(f"Subject: {target_event['summary']}")
        print(f"Event ID: {target_event['id']}")
    else:
        print("[INFO] Meeting not found on calendar")
        if events:
            print("\nEvents found:")
            for e in events:
                print(f"  - {e['summary']}")

except Exception as e:
    print(f"[ERROR] {e}")
