# Gmail & Calendar Setup for Henry

This guide sets up Henry to draft and send emails, and propose/book calendar meetings.

---

## Step 1: Create Google Cloud Project

1. Go to **https://console.cloud.google.com/**
2. Click **"Create Project"**
   - Name: `Henry-Email-Calendar`
   - Organization: (leave default)
   - Click **Create**

3. Wait for project to be created (~1 min)

---

## Step 2: Enable Required APIs

1. In the left sidebar, go to **APIs & Services → Library**

2. Search for and enable these APIs:
   - **Gmail API**
     - Click it → **Enable**
   
   - **Google Calendar API**
     - Click it → **Enable**

---

## Step 3: Create OAuth Credentials

1. Go to **APIs & Services → Credentials**

2. Click **+ Create Credentials → OAuth 2.0 Client IDs**

3. If prompted, configure OAuth consent screen first:
   - **User Type:** External
   - **Display name:** Henry
   - **Email:** uriplonka@gmail.com
   - **Developer contact:** uriplonka@gmail.com
   - Save and continue

4. Back to credentials, click **+ Create Credentials → OAuth 2.0 Client IDs** again

5. Configure:
   - **Application type:** Desktop application
   - **Name:** Henry-Email-Calendar
   - Click **Create**

6. **Download JSON file**
   - Click the download icon next to your credentials
   - Save as: `gmail_secrets.json`
   - Place in: `C:\Users\URI-AI\.openclaw\credentials\`

---

## Step 4: Authenticate Henry

Once you have the `gmail_secrets.json` file, run:

```python
from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()
manager.authenticate()
```

This will:
1. Open a browser window
2. Ask you to sign in to your Google account
3. Ask you to approve access for "Henry-Email-Calendar"
4. Save credentials locally (encrypted)

---

## Step 5: Test It

```python
from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

# Draft an email
result = manager.draft_email(
    to="someone@example.com",
    subject="Test from Henry",
    body="This is a test email from Henry."
)

print(f"Draft created: {result}")

# List pending emails
pending = manager.list_pending_emails()
print(f"Pending: {pending}")

# Approve and send
if pending:
    manager.approve_and_send_email(pending[0]['id'])
```

---

## Troubleshooting

### "Could not find gmail_secrets.json"
- Make sure file is at: `C:\Users\URI-AI\.openclaw\credentials\gmail_secrets.json`
- Verify filename matches exactly

### "Authentication failed"
- Make sure Gmail API and Calendar API are both **enabled** in Google Cloud
- Try re-downloading the credentials file

### "Calendar not authenticated"
- Both Gmail and Calendar APIs must be enabled
- Credentials file has scopes for both

---

## Security Notes

- Credentials are stored locally in `.openclaw/credentials/`
- They're encrypted and never transmitted
- You can revoke access anytime via Google account settings
- Only Henry can access these files in your workspace

---

## Once Set Up

You can then use in your router or directly:

```python
from email_calendar import EmailCalendarManager

manager = EmailCalendarManager()

# Draft email
manager.draft_email(
    to="client@company.com",
    subject="Meeting proposal",
    body="Would you like to meet next Tuesday?"
)

# Propose meeting
manager.propose_meeting(
    subject="Q1 Planning",
    attendees=["director@company.com"],
    start_time="2026-04-01T14:00:00"
)

# You approve via Telegram/chat
# I send/book on your approval
```

---

## Next: Integration into Router

Once authenticated, we can add `send_email()` and `book_meeting()` functions to your main router, triggered by tasks like:

- "Draft an email to sales team about new pricing"
- "Schedule a meeting with the board next Friday at 2pm"

---

**Ready to set up? Follow the steps above, then let me know when you have the credentials file.** ⚡
