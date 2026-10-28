> Loaded on demand from SKILL.md when the agent needs settings-key catalogs.

# Settings Reference

## Core Settings

```python
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # or 'username' or 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # or 'optional', 'none'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'
ACCOUNT_EMAIL_NOTIFICATIONS = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SESSION_COOKIE_AGE = 86400  # seconds
ACCOUNT_PASSWORD_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
```

## Headless/REST Settings

```python
ALLAUTH_HEADLESS_ENABLED = True
ALLAUTH_HEADLESS_TOKEN_STRATEGY = 'allauth.headless.token.StrategyJWT'
ALLAUTH_HEADLESS_TOKEN_JWT_SECRET_KEY = 'your-secret'
ALLAUTH_HEADLESS_TOKEN_JWT_ALGORITHM = 'HS256'
```

## MFA Settings

```python
MFA_ENABLED = True
MFA_SUPPORTED_AUTHENTICATORS = [
    'allauth.mfa.authenticators.Totp',
    'allauth.mfa.authenticators.WebAuthn',
    'allauth.mfa.authenticators.RecoveryCodes',
]
MFA_REQUIRED = False  # Force MFA at login
```

## Adapter Configuration

```python
ACCOUNT_ADAPTER = 'myapp.adapter.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'myapp.adapter.CustomSocialAccountAdapter'
```
