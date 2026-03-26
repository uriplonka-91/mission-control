# Mission Control API Documentation

## Endpoints

### Dashboard
- `GET /` - Main dashboard UI
- `GET /login` - Login page
- `POST /api/login` - Authenticate (password: mission2024)

### Router API
- `POST /api/route` - Route a task to appropriate model

```json
REQUEST:
{
  "task": "Your task description here"
}

RESPONSE:
{
  "model": "phi" | "claude",
  "reasoning": "Why this model was chosen",
  "confidence": 0.85,
  "complexity": 5,
  "risk": "low" | "medium" | "high",
  "uncertainty": 30
}
```

### Cost Tracking
- `GET /api/costs` - Get cost data
- `GET /api/costs/anomalies` - Get detected anomalies

### Email (DISABLED)
- `POST /api/email/draft` - Draft an email
- `POST /api/email/send` - Send approved email
- `GET /api/email/pending` - List pending emails

### Calendar (DISABLED)
- `POST /api/calendar/propose` - Propose a meeting
- `POST /api/calendar/book` - Book a meeting
- `DELETE /api/calendar/meeting/:id` - Cancel meeting

## Request/Response Format

All endpoints return JSON with standard format:

### Success Response (200)
```json
{
  "success": true,
  "data": {...},
  "timestamp": "2026-03-26T14:00:00Z"
}
```

### Error Response (400+)
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-03-26T14:00:00Z"
}
```

## Error Codes

- `400_BAD_REQUEST` - Invalid input
- `401_UNAUTHORIZED` - Not authenticated
- `403_FORBIDDEN` - No permission
- `429_RATE_LIMITED` - Too many requests
- `500_INTERNAL_ERROR` - Server error

## Rate Limiting

Current limits (per account, per day):
- Email: 50 messages
- Calendar: 10 meetings
- API calls: Unlimited (but monitored for cost)

## Authentication

Include password in request headers:
```
Authorization: Bearer mission2024
```

Or authenticate via login page first (session cookie).

## Examples

### Route a Task

```bash
curl -X POST http://localhost:3000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Format this list: apple, orange, banana"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "model": "phi",
    "reasoning": "Simple, routine task",
    "confidence": 0.9,
    "complexity": 2,
    "risk": "low",
    "uncertainty": 5
  }
}
```

### Get Costs

```bash
curl http://localhost:3000/api/costs \
  -H "Authorization: Bearer mission2024"
```

Response:
```json
{
  "success": true,
  "data": {
    "today": 0.42,
    "thisWeek": 2.15,
    "thisMonth": 5.67,
    "total": 12.20,
    "phi_calls": 1245,
    "claude_calls": 23
  }
}
```

## Webhook Events (Future)

Planned webhook support for:
- Cost anomalies detected
- Budget thresholds exceeded
- New model versions available
- Deployment events

---

**API Version:** 1.0
**Last Updated:** 2026-03-26
