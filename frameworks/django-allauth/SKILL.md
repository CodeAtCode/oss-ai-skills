---
name: django-allauth
description: Use when implementing Django authentication - local accounts, OAuth, email verification, MFA, OIDC, django-organizations
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - django
    - authentication
    - oauth
    - social-login
    - mfa
    - django-allauth
---

# django-allauth

> **Objective:** Use this skill to reduce account-takeover incidents, OAuth-misconfig rejections, email-verification bypass, and MFA-enrollment failures by enforcing provider-config discipline, verification-flow checks, and MFA-setup patterns.

## Installation

```bash
pip install django-allauth
pip install django-allauth[socialaccount]  # OAuth providers
pip install django-allauth[mfa]  # MFA support
```

## Core Configuration

**Do configure SITE_ID correctly because** allauth ties accounts and social logins to a specific Django site; wrong ID breaks provider callbacks.

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.sites',  # Required
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1  # Must match your Site object
```

**Do set ACCOUNT_EMAIL_VERIFICATION=mandatory because** optional/none lets unverified emails bypass security flows, enabling account takeover via email-spoofed signups.

```python
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Block login until verified
ACCOUNT_EMAIL_REQUIRED = True  # Enforce email presence
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Email-only login
```

See `references/settings-reference.md` for complete settings catalog.

## Email Verification Flow

**Do test SMTP configuration before production because** misconfigured EMAIL_BACKEND causes verification emails to vanish, locking users out.

```python
# Production: configure real SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Dev: console backend shows emails in terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Do customize email templates because** default branding confuses users and reduces trust in verification links.

Override in `templates/account/email/` — see `references/templates-list.md` for template names.

## OAuth Provider Setup

**Do configure SOCIALACCOUNT_ADAPTER because** missing adapters leave providers at unsafe defaults, enabling unauthorized domain signups.

```python
# settings.py
INSTALLED_APPS += ['allauth.socialaccount.providers.google']

SOCIALACCOUNT_ADAPTER = 'myapp.adapter.CustomSocialAccountAdapter'
```

**Do enforce domain allowlists in pre_social_login because** open OAuth providers let attackers claim accounts via compromised provider tokens.

```python
# myapp/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    ALLOWED_DOMAINS = {'company.com', 'partner.org'}
    
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email
        if not email:
            return
        
        domain = email.split('@')[-1].lower()
        if domain not in self.ALLOWED_DOMAINS:
            raise PermissionDenied(f'@{domain} not authorized')
```

**Do merge duplicate accounts in pre_social_login because** same user signing up via email then OAuth creates orphaned identities.

Check `EmailAddress` table for matching email before creating new user.

See `references/provider-adapters.md` for provider class list.

## Multi-Factor Authentication

**Do enable MFA in all environments because** dev-only MFA creates false confidence; users won't re-enroll in production.

```python
INSTALLED_APPS += ['allauth.mfa']

MFA_ENABLED = True
MFA_SUPPORTED_AUTHENTICATORS = [
    'allauth.mfa.authenticators.Totp',
    'allauth.mfa.authenticators.WebAuthn',
    'allauth.mfa.authenticators.RecoveryCodes',
]
```

**Do generate recovery codes on MFA activation because** users locked out of TOTP/WebAuthn need fallback; without codes, account recovery requires admin intervention.

```python
# GET /mfa/recovery_codes/generate/ — show codes once on activation
```

**Do enforce MFA per-role via middleware because** global MFA_REQUIRED blocks legacy clients; high-privilege users need stricter protection.

```python
# Middleware: check groups, redirect to /mfa/ if not enrolled
```

See `references/urls-endpoints.md` for MFA endpoint paths.

## Session Management

**Do set short ACCOUNT_SESSION_COOKIE_AGE because** long-lived sessions survive password resets, enabling attackers to maintain access after compromise.

```python
ACCOUNT_SESSION_COOKIE_AGE = 86400  # 24 hours
```

**Do invalidate sessions on password change via signals because** password reset alone doesn't kill active sessions elsewhere.

```python
from allauth.account import signals
from django.dispatch import receiver

@receiver(signals.password_changed)
def on_password_change(sender, user, **kwargs):
    # Revoke other sessions
    pass
```

## Signals (Operational Subset)

Use signals at trust boundaries — never in business logic.

| Signal | When it fires | Use case |
|--------|---------------|----------|
| `user_signed_up` | After user created, before email sent | Create profile, send welcome |
| `user_logged_in` | After authentication | Log activity, sync external |
| `email_confirmed` | After verification completes | Grant features, update CRM |
| `password_changed` | After password update | Invalidate sessions, audit |
| `social_account_added` | After OAuth link | Sync profile, merge duplicates |

```python
from allauth.account import signals

@receiver(signals.user_signed_up)
def on_signup(request, user, **kwargs):
    # Send welcome, create profile
    pass
```

## Headless REST API

**Do configure ALLAUTH_HEADLESS_TOKEN_JWT_SECRET_KEY explicitly because** default/missing secret breaks token validation across restarts.

```python
INSTALLED_APPS += ['allauth.headless']
ALLAUTH_HEADLESS_ENABLED = True
ALLAUTH_HEADLESS_TOKEN_STRATEGY = 'allauth.headless.token.StrategyJWT'
ALLAUTH_HEADLESS_TOKEN_JWT_SECRET_KEY = 'your-secret-key'
```

See `references/urls-endpoints.md` for headless endpoint paths.

## Anti-Patterns

| Failure | Cause | Fix |
|---------|-------|-----|
| `user.email` raises `DoesNotExist` | Accessing email before checking `EmailAddress` | Use `EmailAddress.objects.get_primary(user)` |
| Stale sessions after password reset | Not invalidating other sessions | Use `signals.password_changed` to revoke |
| Verification emails not sending | Console backend in production | Configure real SMTP; test with console in dev |
| Social login creates duplicates | Not checking existing emails | In `pre_social_login`: check `EmailAddress`, merge |
| MFA bypass in dev | `MFA_ENABLED = False` in dev | Keep MFA on in all envs; disable per-user for testing |

## When Not to Use allauth

**API-only / headless projects** — If building SPA/mobile backend with no server-rendered pages, allauth's templates are dead weight. Consider:
- Simple JWT with `djangorestframework-simplejwt`
- Custom views using Django's `User` model directly
- Adopt allauth only if you need social providers or complex email flows

**Existing user model conflicts** — If your project already has:
- Custom `AbstractUser` with unexpected fields
- Existing auth logic requiring unwinding
- Incompatible third-party auth packages

Check before adopting:
1. `python manage.py shell` → `from django.contrib.auth import get_user_model; print(get_user_model()._meta.fields)`
2. Search for `AUTH_USER_MODEL` — is it already custom?
3. Review existing login/signup views — can they be replaced?

## Flow Decisions

### Email Verification Mode

| Requirement | Setting | Common failure |
|-------------|---------|----------------|
| Must verify before login | `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` | Users can't login; forgot SMTP config |
| Optional, prefer verified | `ACCOUNT_EMAIL_VERIFICATION = 'optional'` + middleware | Feature access not gated; check `EmailAddress.verified` |
| No verification needed | `ACCOUNT_EMAIL_VERIFICATION = 'none'` | Only for internal tools |

### MFA Enablement Strategy

| Timing | Approach |
|--------|----------|
| Force at next login | `MFA_REQUIRED = True`; redirect to `/mfa/` on auth |
| Optional, encourage | Show MFA status in profile; no enforcement |
| Per-role enforcement | Middleware: check groups, redirect high-priv users if not enrolled |

### Redirect Configuration

| Setting | Purpose | Common failure |
|---------|--------|----------------|
| `LOGIN_REDIRECT_URL` | Post-login destination | Set inconsistently with `ACCOUNT_LOGIN_REDIRECT_URL` |
| `ACCOUNT_LOGIN_REDIRECT_URL` | allauth-specific override | Pick one and stick with it |
| `ACCOUNT_LOGOUT_REDIRECT_URL` | Post-logout destination | — |

## Deep Dives

- `references/examples.md` — custom signup form, verified email middleware
- `references/settings-reference.md` — complete settings catalog
- `references/urls-endpoints.md` — URL and endpoint reference
- `references/templates-list.md` — overridable template names
- `references/provider-adapters.md` — provider class list
