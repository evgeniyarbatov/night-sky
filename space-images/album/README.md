# Album

Local collection of inspiration images (not committed).

| Path | Role |
| --- | --- |
| `daily/YYYY-MM-DD/` | Pulls for that calendar day — each `make inspire` adds another image + sidecars |
| `daily/LATEST.md` | Pointer to the most recent pull |

Cron example (daily at 08:00):

```bash
cd /path/to/space-images && make inspire
```
