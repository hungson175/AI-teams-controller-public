# Cloudflare Tunnel Alternatives for WebSocket Connections

**Research Date:** 2026-01-06
**Requested by:** Boss (via SM)
**Context:** Backend pushes to frontend every 0.5s via WebSocket, need stable solution for low-spec VPS (1-2 CPU, 1GB RAM)

---

## Executive Summary

| Solution | Cost/Month | RAM Usage | WebSocket Support | Setup Complexity | Recommendation |
|----------|------------|-----------|-------------------|------------------|----------------|
| **Direct VPS + Caddy** | $5.59 | ~50MB | Excellent | Medium | **Best Overall** |
| **Direct VPS + Nginx** | $5.59 | ~20MB | Excellent | Medium-High | Best Performance |
| **rathole (self-hosted tunnel)** | $5.59 | ~5MB | Explicit | Medium | Best Lightweight |
| **Chisel (self-hosted tunnel)** | $5.59 | ~30MB | Native | Low | Best Security |
| **frp (self-hosted tunnel)** | $5.59 | ~50MB | Via HTTP | High | Most Features |
| **Cloudflare Tunnel** | $0 | N/A | Undocumented | Very Low | Current (issues?) |
| **ngrok (paid)** | $20 | N/A | Yes | Very Low | Managed Alternative |

**TL Recommendation:** Direct VPS hosting with Caddy ($5.59/month on Hetzner) provides the best balance of cost, stability, and simplicity for WebSocket applications.

---

## Option 1: Direct VPS Hosting (Recommended)

### Why Direct Hosting?

- **Lower latency**: No tunnel overhead (10-50ms saved)
- **Full control**: Configure timeouts, keep-alive, buffers
- **Cost-effective**: $5.59/month for 2 vCPU, 2GB RAM
- **Simpler debugging**: Direct access to logs

### VPS Provider Comparison

| Provider | Specs | Price/Month | Notes |
|----------|-------|-------------|-------|
| **Hetzner CPX11** | 2 vCPU, 2GB RAM, 40GB NVMe | **$5.59** | Best value |
| Vultr Regular | 1 vCPU, 1GB RAM, 25GB SSD | $5.00 | Good alternative |
| DigitalOcean Basic | 1 vCPU, 1GB RAM, 25GB SSD | $6.00 | More documentation |
| Vultr High Performance | 1 vCPU, 2GB RAM, 50GB NVMe | $12.00 | Better I/O |

**Winner:** Hetzner CPX11 at $5.59/month (2x RAM of competitors at same price)

### Reverse Proxy Options

#### Caddy (Recommended for Simplicity)

```caddyfile
voice-backend.yourdomain.com {
    reverse_proxy localhost:17061
}
```

- **Auto-HTTPS**: Zero-config Let's Encrypt
- **WebSocket**: Automatic, no configuration needed
- **RAM**: ~40-50 MB baseline
- **Pros**: Simplest setup, auto-renewal, modern
- **Cons**: Higher memory than Nginx

#### Nginx (Best Performance)

```nginx
server {
    listen 443 ssl http2;
    server_name voice-backend.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain/privkey.pem;

    location / {
        proxy_pass http://localhost:17061;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;  # 24h for WebSocket
    }
}
```

- **RAM**: ~10-20 MB baseline (lowest)
- **WebSocket**: Requires explicit configuration
- **SSL**: Manual Certbot setup + cron renewal
- **Pros**: Battle-tested, lowest memory, best scale
- **Cons**: More configuration required

#### HAProxy (Load Balancing)

- **RAM**: ~10-30 MB
- **WebSocket**: Automatic tunnel mode on HTTP 101
- **Use when**: Multiple backend instances needed
- **Skip if**: Single backend (overkill)

#### Traefik (Skip for Low-Spec VPS)

- **RAM**: 50-100+ MB (too heavy for 1GB VPS)
- **Use when**: Kubernetes/Docker orchestration
- **Skip if**: Simple reverse proxy needs

### Security Hardening

```bash
# UFW Firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirect)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### Total Cost: Direct VPS

| Component | Cost |
|-----------|------|
| Hetzner CPX11 | $5.59/month |
| Let's Encrypt SSL | $0 |
| Domain (yearly) | ~$1/month |
| **Total** | **~$6.59/month** |

---

## Option 2: Self-Hosted Tunneling

If you prefer keeping the backend on your local MacBook (current setup) but want alternatives to Cloudflare:

### rathole (Best for Low-Spec VPS)

**GitHub:** 12.6k stars | **Language:** Rust | **License:** Apache-2.0

```toml
# Server config (on VPS)
[server]
bind_addr = "0.0.0.0:2333"

[server.transport.websocket]
tls = true

[server.services.voice-backend]
token = "your-secret-token"
bind_addr = "0.0.0.0:443"
```

- **WebSocket**: Explicit first-class support
- **RAM**: ~500KB binary, extremely lightweight
- **Performance**: Claims better than frp under load
- **Security**: TLS + Noise Protocol encryption
- **Best for**: Resource-constrained VPS, WebSocket-heavy apps

### Chisel (Best Security)

**GitHub:** 15.4k stars | **Language:** Go | **License:** MIT

```bash
# Server (on VPS)
chisel server --port 443 --reverse

# Client (on MacBook)
chisel client wss://your-vps:443 R:443:localhost:17061
```

- **WebSocket**: Uses WebSocket as transport layer (native support)
- **Encryption**: Always-on SSH encryption
- **RAM**: Single binary, low overhead
- **Auto-SSL**: Built-in Let's Encrypt support
- **Best for**: Security-conscious deployments

### frp (Most Features)

**GitHub:** 103k stars | **Language:** Go | **License:** Apache-2.0

- **WebSocket**: Via HTTP/HTTPS support
- **Features**: Connection pooling, load balancing, Prometheus metrics, dashboard
- **RAM**: Higher than rathole (~50MB+)
- **Best for**: Production environments needing monitoring/advanced features
- **Trade-off**: Most complex setup

### Comparison Matrix

| Feature | rathole | Chisel | frp | bore |
|---------|---------|--------|-----|------|
| WebSocket | **Explicit** | **Native** | Via HTTP | **No** |
| Encryption | TLS + Noise | SSH (always) | TLS (optional) | Auth only |
| RAM Usage | **~500KB** | Low | ~50MB | Low |
| GitHub Stars | 12.6k | 15.4k | 103k | 10.6k |
| Setup | Medium | **Easy** | Complex | Easiest |
| Best For | Resources | Security | Features | TCP only |

**Avoid bore:** TCP-only, no WebSocket support

### Total Cost: Self-Hosted Tunnel

| Component | Cost |
|-----------|------|
| Cheap VPS (tunnel server) | $5.59/month |
| Let's Encrypt SSL | $0 |
| Domain | ~$1/month |
| **Total** | **~$6.59/month** |

---

## Option 3: Managed Cloud Services

### ngrok (Paid Tier)

| Tier | Price | Bandwidth | Rate Limit | WebSocket |
|------|-------|-----------|------------|-----------|
| Free | $0 | 1GB | 100/min | Yes (limited) |
| Hobbyist | $8-10/mo | 5GB | 150/min | Yes |
| Pay-as-you-go | $20/mo | Unlimited | 600/min | **Yes** |

- **Pros**: Zero setup, managed service, good documentation
- **Cons**: $20/month for production use (vs $5.59 self-hosted)
- **Use when**: Team doesn't want to manage infrastructure

### Tailscale Funnel

- **Pricing**: Requires Premium plan (contact sales)
- **Free/Personal Plus**: Funnel NOT included
- **Verdict**: Not cost-effective for this use case

### Cloudflare Tunnel (Current)

**Known Configuration for WebSocket:**

```yaml
# ~/.cloudflared/config.yml
ingress:
  - service: http://localhost:17061
    originRequest:
      keepAliveTimeout: 5m    # Increase from 90s default
      tcpKeepAlive: 10s       # More frequent keepalives
```

- **Cost**: Free
- **Issue**: Poor WebSocket documentation, 90s default keepalive may cause disconnects
- **Stability**: Undocumented for high-frequency WebSocket (0.5s pushes)

---

## Recommendations

### For Boss's Use Case (0.5s WebSocket pushes, cheap VPS available)

**Primary Recommendation: Direct VPS + Caddy**

1. Deploy backend directly on Hetzner CPX11 ($5.59/month)
2. Use Caddy for auto-HTTPS and WebSocket proxy
3. Configure UFW + fail2ban for security
4. **Result**: Lower latency, full control, ~$6.59/month total

**Alternative: rathole tunnel**

If keeping backend on MacBook is preferred:
1. Deploy rathole server on cheap VPS ($5.59/month)
2. Run rathole client on MacBook
3. Explicit WebSocket support with minimal resources
4. **Result**: Tunnel approach with better WebSocket handling than Cloudflare

### Decision Matrix

| Priority | Best Choice |
|----------|-------------|
| **Lowest latency** | Direct VPS + Nginx |
| **Simplest setup** | Direct VPS + Caddy |
| **Keep local backend** | rathole or Chisel tunnel |
| **Zero management** | ngrok Pay-as-you-go ($20/mo) |
| **Free** | Stay with Cloudflare (tune keepalive) |

---

## Quick Start: Direct VPS + Caddy

```bash
# 1. Create Hetzner CPX11 ($5.59/month)
# 2. SSH into VPS
ssh root@your-vps-ip

# 3. Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy

# 4. Configure Caddy
sudo nano /etc/caddy/Caddyfile
# Add:
# voice-backend.yourdomain.com {
#     reverse_proxy localhost:17061
# }

# 5. Deploy your backend
cd /opt/ai-teams-controller/backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 17061 &

# 6. Start Caddy
sudo systemctl restart caddy

# 7. Update DNS: A record → VPS IP
```

---

## Sources

- [Hetzner Cloud Pricing](https://www.hetzner.com/cloud)
- [Vultr Pricing](https://www.vultr.com/pricing)
- [DigitalOcean Droplet Pricing](https://www.digitalocean.com/pricing/droplets)
- [Nginx WebSocket Proxy Documentation](https://nginx.org/en/docs/http/websocket.html)
- [Caddy Reverse Proxy Documentation](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [HAProxy 3.0 Configuration Manual](https://docs.haproxy.org/3.0/configuration.html)
- [rathole GitHub Repository](https://github.com/rapiz1/rathole)
- [Chisel GitHub Repository](https://github.com/jpillora/chisel)
- [frp GitHub Repository](https://github.com/fatedier/frp)
- [ngrok Pricing](https://ngrok.com/pricing)
- [Tailscale Funnel Use Cases](https://tailscale.com/kb/1247/funnel-serve-use-cases)
- [Cloudflare Origin Configuration](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/configure-tunnels/origin-configuration/)
