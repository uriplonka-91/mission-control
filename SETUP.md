# Mission Control Setup Guide

## Prerequisites

### System Requirements
- Windows 10/11 (or Linux/macOS with similar tools)
- 8GB+ RAM
- 2GB+ free disk space (for Phi model)

### Required Software
- **Node.js** 20+ (for Next.js)
- **Python** 3.9+ (for router logic)
- **Ollama** (for local Phi-3.5-mini model)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/uriplonka-91/mission-control.git
cd mission-control
```

### 2. Install Dependencies

**Node.js dependencies:**
```bash
npm install
```

**Python dependencies:**
```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
ANTHROPIC_API_KEY=your_key_here
OLLAMA_HOST=http://localhost:11434
```

### 4. Start Ollama Service

Ollama must be running for the router to access Phi model:
```bash
ollama serve
```

Or if Ollama is installed as a service, verify it's running:
```bash
ollama list
```

### 5. Download Phi Model

If not already downloaded:
```bash
ollama pull phi
```

This downloads 1.6GB and may take 15-30 minutes on first run.

### 6. Run Locally

**Development mode:**
```bash
npm run dev
```

Visit: http://localhost:3000 (or http://localhost:3001 if 3000 is in use)

Password: `mission2024`

**Production build:**
```bash
npm run build
npm start
```

## Architecture

### Components

- **router.py** - Intelligent task routing (Phi for simple, Claude for complex)
- **email_calendar.py** - Email/Calendar management (DISABLED by default)
- **cost_anomaly_detector.py** - Cost tracking and anomaly detection
- **pages/index.js** - Next.js dashboard UI
- **components/*.js** - React components for different views

### Task Routing Logic

1. **Simple tasks** (complexity 0-3, low risk, high certainty)
   - Route to Phi (local, FREE)
   - Examples: formatting, copying, basic summarization

2. **Complex tasks** (complexity 7+, high risk, strategic)
   - Route to Claude (API, PAID)
   - Examples: strategy, analysis, decision-making

3. **Medium tasks** (complexity 4-6)
   - Decision based on risk, uncertainty, and complexity thresholds

### Cost Optimization

- **Phi model** runs locally on localhost:11434 (zero API cost)
- **Claude** used only for complex tasks requiring AI judgment
- **Classification caching** prevents repeated analysis of similar tasks
- **Budget alerts** trigger when spending exceeds thresholds

## Deployment

### Vercel

Project is pre-configured for Vercel deployment:

```bash
vercel deploy --prod
```

### Environment Variables (Vercel)

Add these to your Vercel project settings:
- `ANTHROPIC_API_KEY` - Your Claude API key
- `OLLAMA_HOST` - Ollama endpoint (if using remote Ollama)

**Note:** Local Phi inference won't work on Vercel Functions (serverless/stateless). For production, consider:
1. Using remote Ollama server
2. Running Phi locally and using Vercel only for UI
3. Disabling Phi and using Claude for all tasks

## Monitoring & Costs

### Daily Cost Tracking

Check `/pages/index.js` Cost tab to see:
- Daily spending
- Anomalies detected
- Model usage breakdown

### Log Files

Logs are stored in:
- `.learnings/ROUTING.md` - Task routing decisions
- `.learnings/CLASSIFICATION_CACHE.json` - Task classification cache
- `.learnings/COST_LOG.json` - Cost tracking

## Troubleshooting

### Phi not responding
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Claude API errors
```bash
# Verify API key is set
echo $env:ANTHROPIC_API_KEY  # Windows PowerShell
echo $ANTHROPIC_API_KEY      # Linux/macOS
```

### Port already in use
```bash
# If 3000 is in use, Next.js will try 3001
npm run dev
# Check http://localhost:3001
```

## Performance Tips

1. **Batch similar tasks** - Router learns classifications and caches them
2. **Use Phi for routine work** - Saves 80%+ on API costs
3. **Monitor costs daily** - Alert threshold: $5.00/day
4. **Cache aggressively** - Classification cache grows over time (~50MB per 100k tasks)

## Security

- All credentials stored in `.env` (not committed to git)
- Phi runs locally - no data sent to external services
- Claude API calls sent only for complex tasks requiring AI judgment
- `.gitignore` prevents secrets from leaking

## Support

For issues or questions:
1. Check logs in `.learnings/`
2. Review this SETUP.md
3. Check OpenClaw documentation: https://docs.openclaw.ai

---

**Last updated:** 2026-03-26
**Status:** Production-ready
