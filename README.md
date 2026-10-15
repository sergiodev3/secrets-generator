# secrets-generator

CLI to generate cryptographically secure secrets (JWT keys, session secrets, API keys) for production apps.

Uses Python's `secrets` module (OS CSPRNG). Never `random`.

## Install

```bash
uv tool install .
```

## Usage

```bash
# Raw secret (32 bytes = 256 bits, base64url)
secrets-gen

# .env lines
secrets-gen JWT_SECRET SESSION_SECRET
# JWT_SECRET=Q3x...
# SESSION_SECRET=9fA...

# Append to an .env file
secrets-gen JWT_SECRET >> .env

# More entropy and a different encoding
secrets-gen JWT_SECRET --bytes 64 --format hex
```

### Options

| Option | Default | Description |
|---|---|---|
| `--bytes`, `-b` | `32` | Entropy in bytes (minimum 16). 32 bytes = 256 bits, enough for HS256. Use 64 for HS512. |
| `--format`, `-f` | `base64url` | `base64url`, `base64`, `hex`, or `alnum` |

Length is driven by entropy, not by character count: 32 bytes give 64 chars in `hex`, 43 in `base64url`, 43 in `alnum`.

## Development

```bash
uv sync
uv run pytest
```
