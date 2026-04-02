# 🔒 Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x | ✅ Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in **Stickman Runner**, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Contact the maintainer directly via [LinkedIn](https://www.linkedin.com/in/utkarsh-mani-tripathi/)
3. Provide a detailed description of the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Security Considerations

Stickman Runner is a single-player offline game with a minimal attack surface:

- **No network access** — The game makes zero network requests
- **No file I/O** — No data is read from or written to disk during gameplay
- **No external assets** — All sprites and sounds are generated at runtime
- **No user input storage** — No personal data is collected or stored
- **Sandboxed execution** — Runs within the Pygame window context only

## Dependencies

| Dependency | Purpose | Risk Level |
|---|---|---|
| `pygame` | Game engine, rendering, audio | Low — well-maintained, widely used |

---

Thank you for helping keep **Stickman Runner** safe! 🛡️
