# Manual Debug Helpers

These scripts are **not** collected by pytest. Use them for manual debugging and ad-hoc API testing during development.

| Script | Purpose |
|--------|---------|
| `auth_flow_debug.py` | Debug JWT authentication flow |
| `debug_token.py` | Decode a JWT and validate user lookup |
| `server_context_debug.py` | Debug server context and configuration |

Run from repo root with `PYTHONPATH=.`:

```bash
python tests/manual/auth_flow_debug.py
```
