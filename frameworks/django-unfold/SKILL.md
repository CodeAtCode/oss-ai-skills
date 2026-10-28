---
name: django-unfold
description: Use when theming the Django admin with django-unfold - settings and sidebar configuration, custom admin site, components and @display decorator, filters, actions, tabs, dark mode and styling, or Django 6.x compatibility
metadata:
  author: mte90
  version: 2.0.0
  based_on: https://github.com/unfoldadmin/django-unfold
  tags:
    - python
    - django
    - admin
    - unfold
    - theme
    - dashboard
---

# Django Unfold

> **Objective:** Use this skill to reduce admin-broken-layout incidents, @display-misuse bugs, filter-registration failures, and dark-mode regressions by enforcing settings-discipline, decorator-contract rules, and component-registration patterns below.

Modern Django admin theme with Tailwind-based design.

---

## Core Rules (do X because Y)

1. **Put `unfold` before `django.contrib.admin` in INSTALLED_APPS** because the template engine loads the first admin app it finds and later apps are ignored.

2. **Extend `unfold/base.html` not `admin/base.html`** because extending the stock Django base bypasses Unfold's CSS, sidebar, and dark-mode blocks.

3. **Use UPPER_CASE keys in UNFOLD dict** because lowercase keys are silently ignored at runtime.

4. **Define UNFOLD in settings.py not admin.py** because the theme reads settings at import time; putting it in admin.py causes partial initialization.

5. **Register @display methods before list_display references them** because late decorators don't bind to the admin metaclass and the column renders empty.

6. **Use UNFOLD's COLORS palette not raw CSS overrides** because !important rules fight the Tailwind cascade and break on Unfold updates.

7. **Test dark mode with system preference toggled** because DARK_MODE_COLORS that mirror light mode create invisible text and broken contrast.

---

## Installation

```bash
pip install django-unfold
```

```python
# settings.py
INSTALLED_APPS = [
    'unfold',  # Must come BEFORE django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
]

UNFOLD = {
    'SITE_HEADER': 'My Admin',
}
```

---

## Custom Admin Site

**Do this because**: Default admin site class doesn't expose custom context or override authentication flow.

```python
# admin.py
from unfold.admin import UnfoldAdminSite

class CustomAdminSite(UnfoldAdminSite):
    site_header = 'Custom Portal'
    
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_branding'] = get_branding()
        return context

admin_site = CustomAdminSite(name='custom')
```

```python
# settings.py
UNFOLD_ADMIN_SITE_CLASS = 'myapp.admin.CustomAdminSite'
```

See `references/settings-customization.md` for full settings reference, sidebar config, and dark mode controls.

---

## @display Decorator (Django 6.0+)

**Do this because**: Without proper decorator usage, list_display columns render empty or unsortable.

```python
from unfold.decorators import display

class UserAdmin(ModelAdmin):
    @display(description="Active", boolean=True)
    def is_active(self, obj):
        return obj.is_active
    
    @display(description="Full Name", order="username")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    list_display = ['username', 'is_active', 'full_name']
```

**Failure mode**: Column shows blank because `@display` must be applied before the method is referenced in `list_display`.

See `references/components-actions.md` for @display parameters and field/widget patterns.

---

## Filters

**Do this because**: Default admin filters don't integrate with Unfold's dropdown styling and can break on large FK fields.

```python
import unfold.filters as filters

class ArticleAdmin(ModelAdmin):
    list_filter = [
        ('status', filters.DropdownFilter),  # Better than SelectFilter for long lists
        ('author', filters.AutocompleteFilter),  # Required for >100 authors
        ('created_at', filters.DateRangeFilter),
    ]
```

**Failure mode**: Filter dropdown renders as stock Django select because you used `list_filter = ['field']` without Unfold's filter class.

See `references/components-actions.md` for complete filter type listings.

---

## Actions

**Do this because**: Stock admin actions lack Unfold's button styling and confirmation UI.

```python
from unfold.decorators import action

class ArticleAdmin(ModelAdmin):
    @action(description='Publish selected articles')
    def publish_selected(self, request, queryset):
        queryset.update(status='published')
    
    actions = ['publish_selected']
```

**Failure mode**: Action runs but shows no success message because `message_level` wasn't set or the method wasn't registered in `actions`.

See `references/components-actions.md` for row actions and CSV export patterns.

---

## Common Pitfalls

### INSTALLED_APPS Ordering

**Failure**: Unfold silently ignored, admin renders with default Django theme.

```python
# WRONG
INSTALLED_APPS = [
    'django.contrib.admin',  # ❌ Already loaded templates
    'unfold',
]

# CORRECT
INSTALLED_APPS = [
    'unfold',  # ✅ Template override works
    'django.contrib.admin',
]
```

### Template Extension Mistake

**Failure**: Custom template loses Unfold styling.

```python
# WRONG
{% extends "admin/base.html" %}  # ❌ No Unfold blocks

# CORRECT
{% extends "unfold/base.html" %}  # ✅ Gets CSS, layout, sidebar
```

### Styling Without Theme Pipeline

**Failure**: Custom CSS conflicts with Unfold's Tailwind classes.

```python
# WRONG
UNFOLD = {
    'STYLES': ['css/custom.css'],
}
/* custom.css */
.sidebar { background: blue !important; }  # ❌ Brittle
```

**Correct**:

```python
UNFOLD = {
    'COLORS': {
        'primary': {
            '500': '59 130 246',
        },
    },
}
```

---

## Integrations

### django-guardian

**Do this because**: You need per-object permissions beyond Django's model-level permissions.

```python
INSTALLED_APPS = ['guardian', 'unfold', 'django.contrib.admin']

from unfold.contrib.guardian.admin import GuardedModelAdmin

class ArticleAdmin(GuardedModelAdmin):
    pass
```

**URL**: https://github.com/django-guardian/django-guardian

### django-import-export

**Do this because**: Non-technical users need bulk import/export via admin.

```python
from import_export import resources
from unfold.admin import ImportExportMixin

class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article
        fields = ('id', 'title', 'status')

class ArticleAdmin(ImportExportMixin, ModelAdmin):
    resource_classes = [ArticleResource]
```

**URL**: https://github.com/django-import-export/django-import-export

### django-celery-beat

**Do this because**: You need cron-like scheduling with admin UI.

```python
# Automatic integration - no config needed
pip install django-celery-beat
```

**URL**: https://github.com/celery/django-celery-beat

### django-constance

**Do this because**: You need runtime site-wide settings without redeploy.

```python
INSTALLED_APPS = ['constance', 'unfold']
# Automatic integration
```

**URL**: https://github.com/jazzband/django-constance

See `references/ecosystem-compat.md` for django-unfold-modal, django-unfold-markdown, and Django 6.x compatibility patches.

---

## When Not to Use Unfold

Stock Django admin is sufficient when:

- **Small internal projects** — Admin used by <5 power users, no branding requirements
- **Heavy customization needed** — Unfold's template override layer becomes maintenance cost when rewriting 50% of templates
- **No Tailwind expertise** — Adding Tailwind build pipeline just for admin theming is overkill

**Check before adopting**:
1. Does your team have Tailwind CSS experience?
2. Will admin branding be reviewed by stakeholders?
3. Is the admin used frequently enough to justify the UX investment?

---

## Deep Dives

For detailed reference, load these on-demand:

- **Settings & Customization** — `references/settings-customization.md` - Full settings reference, custom admin site, dark mode, sidebar config
- **Components & Actions** — `references/components-actions.md` - @display decorator, filters, actions, tabs, fields/widgets
- **Ecosystem & Compatibility** — `references/ecosystem-compat.md` - django-unfold-modal, django-unfold-markdown, Django 6.x patches

---

## References

- **GitHub**: https://github.com/unfoldadmin/django-unfold
- **Documentation**: https://unfoldadmin.com/docs
- **Demo**: https://unfoldadmin.com/
