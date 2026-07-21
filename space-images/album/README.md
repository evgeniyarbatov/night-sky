# Album

Local collection of inspiration images (not committed).

| Path | Role |
| --- | --- |
| `daily/YYYY-MM-DD/` | Output of `make inspire` — image, story, `post.txt` social draft |
| `daily/LATEST.md` | Pointer to the most recent daily pull |
| `selected/` | Hand-picked favorites via `make select IMAGE=…` |

Cron example (daily at 08:00):

```bash
cd /path/to/space-images && make inspire
```
