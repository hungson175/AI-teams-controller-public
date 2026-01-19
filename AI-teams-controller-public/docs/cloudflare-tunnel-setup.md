# Cloudflare Tunnel Setup for AI Teams Controller (MacBook)

**Date:** 2024-12-10
**Status:** ACTIVE

---

## Summary

Permanent Cloudflare Tunnel on MacBook với 2 custom subdomains:

| Service | Hostname | Port |
|---------|----------|------|
| Frontend (Next.js) | `voice-ui.hungson175.com` | localhost:3334 |
| Backend (FastAPI) | `voice-backend.hungson175.com` | localhost:17061 |

---

## Tunnel Information

- **Tunnel Name:** `ai-teams-mac`
- **Tunnel ID:** `4f9b3451-37c6-44fc-b269-8056b3458e52`
- **Status:** Active (installed as macOS system service)
- **Logs:**
  - `/Library/Logs/com.cloudflare.cloudflared.out.log`
  - `/Library/Logs/com.cloudflare.cloudflared.err.log`

---

## Service Management

### Check Status
```bash
pgrep -la cloudflared
# Or check logs
tail -f /Library/Logs/com.cloudflare.cloudflared.out.log
```

### Restart Service
```bash
sudo launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

### Stop Service
```bash
sudo launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

### Start Service
```bash
sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

### Uninstall Service
```bash
sudo cloudflared service uninstall
```

---

## Auto-Restart & Health Check

The cloudflared macOS service (`com.cloudflare.cloudflared.plist`) is configured to:

1. **Auto-start on boot** - Service runs when MacBook starts
2. **Auto-reconnect** - cloudflared automatically reconnects if connection drops
3. **Keep-alive** - System restarts the service if it crashes

No additional health check script needed - cloudflared handles reconnection automatically.

---

## URLs

| Service | URL |
|---------|-----|
| Frontend | https://voice-ui.hungson175.com |
| Backend | https://voice-backend.hungson175.com |
| Health Check | https://voice-backend.hungson175.com/health |

---

## Verify Setup

```bash
# Test backend health
curl https://voice-backend.hungson175.com/health
# Expected: {"status":"healthy","version":"0.1.0"}

# Test frontend
curl -I https://voice-ui.hungson175.com
# Expected: HTTP/2 200
```

---

## Troubleshooting

### Tunnel not connecting

1. Check if services are running locally:
```bash
curl http://localhost:17061/health  # Backend
curl http://localhost:3334          # Frontend
```

2. Check cloudflared logs:
```bash
tail -50 /Library/Logs/com.cloudflare.cloudflared.err.log
```

3. Restart cloudflared service:
```bash
sudo launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

### DNS not resolving

Wait 1-5 minutes for DNS propagation:
```bash
dig voice-ui.hungson175.com
dig voice-backend.hungson175.com
```

---

## Token (for reinstallation)

If you need to reinstall:
```bash
sudo cloudflared service install eyJhIjoiMWFiZjRiY2U1ZGI3NTgwMWZiZjEyMmI4YzhmOWU2Y2YiLCJ0IjoiNGY5YjM0NTEtMzdjNi00NGZjLWIyNjktODA1NmIzNDU4ZTUyIiwicyI6IlpXWTBaRGM1WmpndE9HRTFZaTAwWXpjMkxXRTFNVFl0TjJNd09HTmtPRFF6TmpRMSJ9
```

---

## Cloudflare Dashboard

To manage this tunnel:
1. Go to https://one.dash.cloudflare.com
2. Navigate to: Networks > Connectors
3. Find tunnel: `ai-teams-mac`
