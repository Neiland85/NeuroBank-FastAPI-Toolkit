# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please send an email to security@neurobank.com. 
Do not report security vulnerabilities through public GitHub issues.

## Security Measures Implemented

### Authentication
- API Key authentication required for all endpoints
- No default/weak keys in production
- Bearer token and X-API-Key header support

### CORS
- Strict CORS policy (no wildcards in production)
- Domain-specific origins only
- Credentials support controlled

### Environment Variables
- All sensitive configuration via environment variables
- No hardcoded secrets in code
- Validation of required security variables

### Logging
- Structured logging without sensitive data exposure
- Production log level controls
- Security event logging

### Dependencies
- Regular dependency updates
- Security scanning with bandit and safety
- Minimal attack surface

## Railway Deployment Security

### Required Environment Variables
- `API_KEY`: Strong API key (minimum 32 characters)
- `SECRET_KEY`: Cryptographic secret (minimum 32 characters)
- `CORS_ORIGINS`: Specific allowed origins (no wildcards)

### Automatic Security Features
- HTTPS enforced by Railway
- Environment isolation
- Secure variable storage
- Network-level protection

## Security Checklist for Deployment

- [ ] API_KEY configured and strong
- [ ] SECRET_KEY configured and strong  
- [ ] CORS_ORIGINS properly configured
- [ ] No wildcard CORS origins
- [ ] No hardcoded secrets in code
- [ ] Environment variables validated
- [ ] HTTPS enabled
- [ ] Logging configured for production
- [ ] Dependencies updated and scanned
