# Router + Email/Calendar Integration Examples

## Overview

The router now supports email and calendar operations alongside task execution.

---

## Email Operations

### Draft an Email

```python
from router import TaskRouter

router = TaskRouter()

# Draft an email
result = router.draft_email(
    to="client@company.com",
    subject="Project Update",
    body="Here's the Q1 status update..."
)

print(result['preview'])
# Shows: Draft preview with subject, body, and signature
```

### List Pending Emails

```python
# Get all emails awaiting approval
pending = router.list_pending_emails()

for email in pending:
    print(f"To: {email['to']}")
    print(f"Subject: {email['subject']}")
    print(f"Draft ID: {email['id']}")
```

### Send an Approved Email

```python
# Get pending emails
pending = router.list_pending_emails()

if pending:
    # Send the first one
    result = router.send_email(pending[0]['id'])
    
    print(f"[OK] Email sent to {result['to']}")
    print(f"Subject: {result['subject']}")
```

---

## Calendar Operations

### Propose a Meeting

```python
# Propose a meeting
result = router.propose_meeting(
    subject="Q1 Planning",
    attendees=["director@company.com", "finance@company.com"],
    start_time="2026-04-01T14:00:00",
    duration_minutes=60
)

print(result['preview'])
# Shows: Meeting details (subject, attendees, time, duration)
```

### List Pending Meetings

```python
# Get all meetings awaiting approval
pending = router.list_pending_meetings()

for meeting in pending:
    print(f"Subject: {meeting['subject']}")
    print(f"Attendees: {meeting['attendees']}")
    print(f"Time: {meeting['start_time']}")
    print(f"Proposal ID: {meeting['id']}")
```

### Book an Approved Meeting

```python
# Get pending meetings
pending = router.list_pending_meetings()

if pending:
    # Book the first one
    result = router.book_meeting(pending[0]['id'])
    
    print(f"[OK] Meeting booked!")
    print(f"Subject: {result['subject']}")
    print(f"Time: {result['start_time']}")
```

### Cancel a Meeting

```python
# Cancel a meeting by proposal ID
result = router.cancel_meeting("meeting_1774536160.491841")

if result['status'] == 'cancelled':
    print(f"[OK] Meeting cancelled: {result['subject']}")
    # Attendees automatically receive cancellation email
```

---

## Combined Workflow Example

Draft an email AND propose a meeting:

```python
from router import TaskRouter

router = TaskRouter()

# Draft email
email_result = router.draft_email(
    to="client@company.com",
    subject="Meeting Confirmation",
    body="Let's confirm our meeting for next week."
)

print("Email draft:")
print(email_result['preview'])

# Propose meeting
meeting_result = router.propose_meeting(
    subject="Client Discussion",
    attendees=["client@company.com"],
    start_time="2026-04-08T15:00:00",
    duration_minutes=30
)

print("\nMeeting proposal:")
print(meeting_result['preview'])

# User reviews both and approves

# Send email
pending_emails = router.list_pending_emails()
if pending_emails:
    router.send_email(pending_emails[0]['id'])

# Book meeting
pending_meetings = router.list_pending_meetings()
if pending_meetings:
    router.book_meeting(pending_meetings[0]['id'])
```

---

## Email Signature

All emails automatically include:

```
—
Henry
AI Chief of Staff
Assistant to Uri Plonka
```

No need to add manually.

---

## Status Check

```python
# Check authentication status
status = router.email_manager.get_status()

print(f"Gmail: {status['gmail_authenticated']}")
print(f"Calendar: {status['calendar_authenticated']}")
print(f"Pending emails: {status['pending_emails']}")
print(f"Pending meetings: {status['pending_meetings']}")
```

---

## Error Handling

```python
result = router.draft_email(
    to="invalid@example.com",
    subject="Test",
    body="Test"
)

if result['status'] == 'error':
    print(f"Error: {result['message']}")
else:
    print("Draft created successfully")
```

---

## Workflow with Task Execution

Combine task execution with email/calendar:

```python
from router import TaskRouter

router = TaskRouter()

# 1. Execute a task (analysis)
task_result = router.execute(
    "Analyze Q1 sales data and summarize key findings"
)

print(f"Analysis: {task_result['output']}")

# 2. Draft email with results
email_result = router.draft_email(
    to="leadership@company.com",
    subject="Q1 Sales Summary",
    body=f"Here are the Q1 findings:\n\n{task_result['output']}"
)

print(f"\nEmail drafted: {email_result['preview']}")

# 3. Propose follow-up meeting
meeting_result = router.propose_meeting(
    subject="Q1 Sales Review",
    attendees=["leadership@company.com"],
    start_time="2026-03-30T10:00:00",
    duration_minutes=60
)

print(f"\nMeeting proposed: {meeting_result['preview']}")

# 4. User approves all three items in order

# 5. Execute sends
pending_emails = router.list_pending_emails()
if pending_emails:
    router.send_email(pending_emails[0]['id'])

pending_meetings = router.list_pending_meetings()
if pending_meetings:
    router.book_meeting(pending_meetings[0]['id'])
```

---

## Usage in Mission Control

You can integrate email/calendar into Mission Control dashboard:

```javascript
// In React component
async function sendEmail(to, subject, body) {
  const response = await fetch('/api/email/draft', {
    method: 'POST',
    body: JSON.stringify({ to, subject, body })
  });
  return response.json();
}

async function approveEmail(draftId) {
  const response = await fetch('/api/email/send', {
    method: 'POST',
    body: JSON.stringify({ draftId })
  });
  return response.json();
}
```

Backend (Python):

```python
@app.route('/api/email/draft', methods=['POST'])
def draft_email():
    data = request.json
    result = router.draft_email(data['to'], data['subject'], data['body'])
    return jsonify(result)

@app.route('/api/email/send', methods=['POST'])
def send_email():
    data = request.json
    result = router.send_email(data['draftId'])
    return jsonify(result)
```

---

## Key Points

- ✅ All emails include signature automatically
- ✅ All emails CC you (uriplonka@gmail.com)
- ✅ All calendar invites send notifications
- ✅ All operations require approval before execution
- ✅ Full logging of all actions
- ✅ Works alongside task execution (Phi/Claude routing)
