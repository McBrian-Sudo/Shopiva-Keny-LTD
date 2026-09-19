# Shopiva Security Policy

Shopiva follows a defense-in-depth security model informed by Django production security guidance and OWASP ASVS.

Current controls include:
- HTTPS-only production traffic and HSTS.
- Secure, HttpOnly, SameSite session cookies.
- CSRF and clickjacking protection.
- Explicit ALLOWED_HOSTS and trusted origins.
- Browser isolation and CSP reporting.
- Database-backed login brute-force protection.
- Separate customer, seller, delivery and admin authorization boundaries.
- Server-side authorization checks for protected resources.
- Transactional order and inventory operations.
- Secrets supplied through deployment environment variables.
- Automated Django deployment, migration, regression, compile, mobile-release and production-health checks.
- Dependency monitoring through Dependabot.

## Vulnerability reporting

Do not publicly disclose an unpatched vulnerability. Report the affected component, reproduction steps, impact and relevant evidence through the private Shopiva security contact channel.

Do not include passwords, payment credentials, API secrets or unnecessary personal data.

## Important limitation

No Internet-connected application can honestly be guaranteed impossible to compromise. Shopiva is being hardened using layered prevention, detection, containment, recovery and continuous verification.
