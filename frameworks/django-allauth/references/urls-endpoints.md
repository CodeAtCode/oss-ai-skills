> Loaded on demand from SKILL.md when the agent needs URL/endpoints reference.

# URLs and Endpoints

## Standard URLs (allauth.urls)

```python
# Local auth
GET/POST /accounts/signup/
GET/POST /accounts/login/
POST /accounts/logout/
GET/POST /accounts/password/change/
GET/POST /accounts/password/set/
GET/POST /accounts/password/reset/
GET/POST /accounts/password/reset/confirm/
```

## MFA Endpoints

```python
# TOTP
GET /mfa/totp/create/
POST /mfa/totp/activate/

# WebAuthn
GET /mfa/webauthn/create/
POST /mfa/webauthn/activate/

# Recovery codes
GET /mfa/recovery_codes/generate/
```

## Headless API Endpoints

```python
POST /headless/signup/
POST /headless/authentication/login/
POST /headless/authentication/logout/
GET /headless/users/me/
GET/POST/DELETE /headless/emails/
POST /headless/password/set/
POST /headless/password/change/
POST /headless/password/reset/
```
