# Exposing a tenant's proxy service through Cloudflare

How to publish one store's **gateway-proxy-service** on the internet so the
hosted UI can reach it, and how to make sure that publishing it does not hand
the store's transaction data to anyone who finds the hostname.
Date created 8/6/2026
Date Modified 8/6/2026

Applies to **gateway-proxy-service v2.5.0+** and **gateway-service v1.6.0+**.

---

## 1. What is being exposed, and what is not

```
                        internet
                            │
                 ┌──────────┴───────────┐
                 │  Cloudflare edge     │   ← Access policy enforced here
                 └──────────┬───────────┘
                            │  encrypted tunnel (outbound only)
   ── store network ────────┼──────────────────────────────────────
                            │
                     ┌──────┴──────┐
                     │ cloudflared │   Windows service, on the proxy machine
                     └──────┬──────┘
                            │  http://localhost:3005   (REST API)
                            │  http://localhost:8081   (WebSocket stream)
                     ┌──────┴──────────────┐
                     │ gateway-proxy-      │
                     │ service             │
                     └──────┬──────────────┘
                            │  LAN only
                     ┌──────┴──────────────┐
                     │ gateway-service     │  ← never exposed
                     │ :3010  :5060 (POS)  │
                     └─────────────────────┘
```

**Exposed:** the proxy's REST API and WebSocket stream, and only those.

**Not exposed:** gateway-service, the POS listener ports, and the store LAN.
The tunnel config routes only to 3005 and 8081. Nothing routes to 3010.

The tunnel makes **outbound** connections to Cloudflare. No inbound firewall
rule and no port forwarding is needed, which is the main reason to use it.

### If this store has no Cloudflare account

You do not need any of this. Point the UI at the proxy's LAN address
(`http://<proxy-machine-ip>:3005`) and everything works. The auth gate in
section 5 only engages for requests that arrive through Cloudflare, so a
LAN-only install is unaffected by it.

---

## 2. Before you start

On the machine running gateway-proxy-service:

- [ ] gateway-proxy-service **v2.5.0 or later** installed and running
- [ ] `curl http://localhost:3005/health` returns `{"status":"healthy",...}`
- [ ] Administrator access (installing a Windows service)
- [ ] A Cloudflare account with the tunnel domain added as a zone

Have ready:

- [ ] The **store/tenant identifier**, e.g. `elsupermarket_store_02`
- [ ] The **hostname** it will be published on, e.g.
      `elsupermarkets-store002.store-proxycfargotunnel.win`
- [ ] The **origin of the UI** that will call it, e.g.
      `https://retail-gateway-platform.vercel.app`

### Pre-flight: fix the shipped credentials

`installers/proxy-service-installer/GatewayProxyService.xml` ships with
placeholder licence credentials:

```xml
<env name="LICENSE_USERNAME" value="test_user1"/>
<env name="LICENSE_PASSWORD" value="test1234"/>
```

Replace these with the tenant's real values **before** the service is
internet-reachable. They are visible to anyone with access to the machine.

---

## 3. Naming a new tenant

One tunnel per store. The existing scripts in this folder are written for
`elsupermarket_store_01` and are **not** parameterised, so for a new store copy
them and change four strings.

```
installers/cloudflare-tunnel/
  setup-tunnel.bat     ← copy to setup-tunnel-<store>.bat
  manage-tunnel.bat    ← copy to manage-tunnel-<store>.bat
  config.yml           ← reference only; the .bat writes the real one
```

In your copy, replace every occurrence of:

| Placeholder in the scripts | Replace with |
|---|---|
| `elsupermarket_store_01` | your tunnel name, e.g. `elsupermarket_store_02` |
| `elsupermarkets-store001.store-proxycfargotunnel.win` | your hostname |

> Tunnel names must be unique within the Cloudflare account. Hostnames must be
> unique globally. Using the store code in both keeps them aligned and makes
> logs readable.

---

## 4. Create the tunnel

### 4.1 Install cloudflared

```powershell
# Download and run the MSI
https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi

# Verify
cloudflared --version
```

### 4.2 Run the setup script

From an **Administrator** command prompt:

```bat
cd installers\cloudflare-tunnel
setup-tunnel-<store>.bat
```

It performs five steps:

1. **Login** — opens a browser; authorise the zone for your hostname.
2. **Create tunnel** — prints a UUID. Copy it; the script prompts for it.
3. **Write config** — `C:\ProgramData\cloudflared\config.yml` plus the
   credentials JSON.
4. **DNS route** — creates the CNAME to `<uuid>.cfargotunnel.com`.
5. **Install service** — registers and starts `cloudflared` as a Windows
   service so it survives reboots.

### 4.3 What the generated config means

```yaml
ingress:
  # WebSocket first — path matches are evaluated in order, and the catch-all
  # below would otherwise swallow /ws/... and send it to the REST port.
  - hostname: <your-hostname>
    path: /ws/retail-gateway
    service: http://localhost:8081

  # Everything else → REST API
  - hostname: <your-hostname>
    service: http://localhost:3005
    originRequest:
      httpHostHeader: localhost

  # Required by cloudflared, must be last
  - service: http_status:404
```

**Order matters.** If the WebSocket rule is moved below the REST rule, the live
transaction feed silently stops working while the REST API keeps responding —
the hardest kind of failure to diagnose, because the UI looks half-alive.

### 4.4 Confirm the tunnel is up

```powershell
sc query cloudflared
curl https://<your-hostname>/health
```

You want `{"status":"healthy","service":"gateway-proxy-service"}`.

**Stop here and read section 5 before telling anyone the URL.** At this point
the API is on the internet with no authentication.

---

## 5. Secure it — do not skip this

Section 4 published every REST route, including configuration writes. Verified
against a running proxy with no token, no cookie and no header:

```
GET  /api/config/lanes              200   returns lane configuration
GET  /api/monitoring/parsing/stats  200   returns transaction counters
POST /api/config/lanes              201   creates a lane
```

Hostnames are not secret. They appear in **Certificate Transparency logs**
within minutes of the certificate being issued, and those logs are public and
searchable. "Nobody knows the URL" is not a control.

CORS does not help either — it is a browser control and does nothing against
`curl` or a script.

Apply **both** of the following.

### 5.1 Allow the UI's origin (CORS)

The hosted UI is a different origin from the tunnel, so the proxy must allow it
explicitly. `production.json` already lists the standard UI origin. For a
different origin — a preview deploy, a customer-branded domain — add it at
install time without editing shipped config:

```xml
<!-- GatewayProxyService.xml -->
<env name="CORS_ORIGINS" value="https://retail-gateway-platform.vercel.app,https://ui.customer.example"/>
```

Comma-separated. Never use `*`: these endpoints serve transaction data, and
allowing every origin *with credentials* is what makes a browser attack work.

### 5.2 Require a token on the proxy (v2.5.0+)

```xml
<!-- GatewayProxyService.xml -->
<env name="PROXY_REQUIRE_AUTH" value="true"/>
```

Restart the service. On startup the log should read:

```
[AUTH] Proxy API requires a token for requests arriving through Cloudflare
[AUTH] WebSocket requires a token for connections through Cloudflare
```

If instead you see `[AUTH] Proxy API is UNAUTHENTICATED`, the variable did not
take effect.

**How it decides.** `cloudflared` runs on the same machine and connects to
`localhost:3005`, so an internet request arrives with the same source address as
one from the gateway service next door. Address proves nothing. Cloudflare adds
its own headers to everything it forwards (`cf-ray`, `cf-connecting-ip`), and
their presence is what marks a request as external.

Consequences, all intended:

| Caller | Token required |
|---|---|
| gateway-service on the LAN | no |
| an engineer on the machine | no |
| health probes | no |
| **anything through the tunnel** | **yes** |

`/health` and `/api/auth/*` stay open so the system can bootstrap.

**Fail-closed:** tokens are validated against the backend. If the backend is
unreachable, tunnel-side requests are **refused** — unverifiable is not the same
as valid. Local access is unaffected, so an on-site engineer can still work, but
remote support cannot while the backend is down.

### 5.3 Put Cloudflare Access in front (recommended)

Section 5.2 protects the origin. Access protects the edge, so unauthenticated
traffic never reaches the store at all, and it keeps working even if the proxy's
config is wrong.

In the Cloudflare dashboard: **Zero Trust → Access → Applications → Add**

- Type: **Self-hosted**
- Application domain: `<your-hostname>`
- Session duration: to taste (8–24 h is typical)
- Policy: allow your operators' email domain, or specific addresses
- For machine-to-machine callers, issue a **service token** and add a policy
  with `Service Auth` accepting it

> Access adds an interstitial login. If you use it for the hosted UI, the UI
> must be able to complete Cloudflare's cookie flow. Test this with one store
> before rolling it out.

---

## 6. Known limitation: the UI's WebSocket has no token

**Read this before enabling `PROXY_REQUIRE_AUTH` on a store whose users need
the live transaction feed.**

The UI attaches `Authorization: Bearer <token>` to its REST calls, so those work
with the gate on. But it opens the WebSocket as:

```ts
new WebSocket(wsUrl)          // src/services/websocket.ts
```

with no token, because browsers cannot set an `Authorization` header on a
WebSocket. With `PROXY_REQUIRE_AUTH=true` and a tunnel, that connection is
**refused with 401** and the live feed stays empty. The rest of the UI works, so
this presents as "the dashboard loads but transactions never appear".

The proxy already accepts the token via the standard browser mechanism. The UI
change is one line:

```ts
const token = localStorage.getItem('gulfcoast_token');
this.ws = token
  ? new WebSocket(wsUrl, ['bearer', token])
  : new WebSocket(wsUrl);
```

A `?token=` query parameter also works and needs no UI change, but is
**discouraged**: query strings are recorded in Cloudflare and CDN access logs,
and a bearer token should not be written to a log.

Until the UI ships that change, choose one:

| Option | Live feed | API protected |
|---|---|---|
| Access only, `PROXY_REQUIRE_AUTH=false` | works | at the edge only |
| `PROXY_REQUIRE_AUTH=true` | **broken** | origin + edge |
| Ship the UI fix, then enable both | works | origin + edge |

---

## 7. Verify

Run these from a machine **outside** the store network.

```bash
HOST=https://<your-hostname>

# 1. Tunnel is up and reaching the proxy
curl -s $HOST/health
# → {"status":"healthy","service":"gateway-proxy-service"}

# 2. With PROXY_REQUIRE_AUTH=true, an unauthenticated read is refused
curl -s -o /dev/null -w '%{http_code}\n' $HOST/api/config/lanes
# → 401     (200 means the gate is NOT on — go back to 5.2)

# 3. An unauthenticated write is refused
curl -s -o /dev/null -w '%{http_code}\n' -X POST $HOST/api/config/lanes \
     -H 'Content-Type: application/json' -d '{"lane_id":"probe"}'
# → 401     (201 means anyone on the internet can reconfigure this store)

# 4. A valid token is accepted
curl -s -o /dev/null -w '%{http_code}\n' $HOST/api/config/lanes \
     -H "Authorization: Bearer <token>"
# → 200
```

On the store machine, confirm the gate did **not** break local traffic:

```powershell
curl http://localhost:3005/api/config/lanes          # → 200
curl http://localhost:3005/api/monitoring/parsing/stats
```

Then confirm data still flows end to end — the check that matters most, because
it proves the gateway's own WebSocket to the proxy is unaffected:

```powershell
# parsing stats before and after a real transaction
curl http://localhost:3005/api/monitoring/parsing/stats
```

`transactions` must increase. If it does not, see section 8.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `curl $HOST/health` times out | tunnel service not running | `sc query cloudflared`, then `sc start cloudflared` |
| `502 Bad Gateway` from Cloudflare | tunnel is up, proxy is not | `curl http://localhost:3005/health` on the machine |
| `404` on every path | hostname not matched in `config.yml` | check the `hostname:` lines match your DNS record exactly |
| UI loads, live feed empty | WebSocket not routed, or refused | check the `/ws/retail-gateway` ingress rule is **first**; see section 6 |
| UI shows CORS errors in console | origin not allowlisted | add it to `CORS_ORIGINS` (5.1) and restart |
| Everything 401, including local | `allowLocalWithoutAuth` set to false | remove it, or set `true` |
| 401 through tunnel with a valid token | backend unreachable → fail-closed | check `externalApi.baseUrl` is reachable from the machine |
| Transactions stop after enabling auth | gateway's WS refused | gateway connects locally and should be exempt — check it is not routed through the tunnel |

Useful commands:

```powershell
sc query cloudflared                                   # service state
cloudflared tunnel info <tunnel-name>                  # tunnel + connector health
cloudflared tunnel list                                # all tunnels on the account
type C:\ProgramData\cloudflared\config.yml             # effective config
manage-tunnel-<store>.bat                              # start/stop/logs menu
```

Proxy log lines worth grepping:

```
[AUTH]            gate state at startup, and every refusal
[CORS]            which origins are allowed
[WEBSOCKET]       gateway client connect/disconnect
```

---

## 9. Removing a tunnel

```powershell
sc stop cloudflared
cloudflared service uninstall
cloudflared tunnel delete <tunnel-name>
```

Then delete the CNAME record in the Cloudflare dashboard. The proxy keeps
running and stays reachable on the LAN — removing the tunnel only removes
internet access.

---

## 10. Per-store checklist

Copy this per install.

```
Store / tenant : ______________________
Hostname       : ______________________
Tunnel UUID    : ______________________
Date           : ______________________

[ ] proxy v2.5.0+ installed, /health OK on localhost
[ ] LICENSE_USERNAME / LICENSE_PASSWORD replaced with real values
[ ] scripts copied and the four strings replaced
[ ] cloudflared installed, tunnel created, DNS CNAME created
[ ] cloudflared installed as a Windows service and started
[ ] CORS_ORIGINS set to the UI origin(s)
[ ] decision recorded on section 6 (live feed vs auth gate)
[ ] PROXY_REQUIRE_AUTH set as decided
[ ] Cloudflare Access application + policy created
[ ] verified from OUTSIDE: /health 200, unauthenticated read 401,
    unauthenticated write 401, valid token 200
[ ] verified ON the machine: local API 200, transactions still parsing
[ ] hostname recorded in the tenant record on the backend
```

---

## Appendix — configuration reference

Proxy settings that matter for a tunnelled install. Environment variables are
set in `GatewayProxyService.xml`; they override `config/production.json`.

| Setting | Env var | Default | Purpose |
|---|---|---|---|
| `security.requireAuth` | `PROXY_REQUIRE_AUTH` | `false` | Require a bearer token for requests arriving through Cloudflare |
| `security.allowLocalWithoutAuth` | — | `true` | Let LAN callers (gateway service, health probes) skip the check |
| `security.publicPaths` | — | `[]` | Extra paths reachable without a token |
| `server.cors.origins` | `CORS_ORIGINS` | localhost + hosted UI | Browser origins allowed to call this proxy |
| `server.port` | `PORT` | `3005` | REST API port the tunnel targets |
| `websocket.port` | `WS_PORT` | `8081` | WebSocket port the tunnel targets |
| `externalApi.baseUrl` | `EXTERNAL_API_BASE_URL` | backend URL | Where tokens are validated |

> `WS_PORT` silently outranks `websocket.port` in config. When the two disagree
> the service reports one port and binds another — one site ran with
> `production.json` on 8091 and `WS_PORT` on 8081 for weeks, and the gateway
> never connected. Set it in one place.
