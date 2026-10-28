> Loaded on demand from SKILL.md when the agent needs provider class references.

# Provider Adapters Reference

## Common OAuth2 Providers

```python
# Google
'allauth.socialaccount.providers.google'

# GitHub
'allauth.socialaccount.providers.github'

# Facebook
'allauth.socialaccount.providers.facebook'

# Microsoft
'allauth.socialaccount.providers.microsoft'

# Slack
'allauth.socialaccount.providers.slack'
```

## Custom Provider Structure

```python
from allauth.socialaccount.providers.base import Provider
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

class MyCustomProvider(OAuth2Provider):
    id = 'myprovider'
    name = 'My Provider'
    # Implement get_authorization_url(), get_access_token(), etc.
```
