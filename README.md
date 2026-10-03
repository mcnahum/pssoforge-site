# PSSO Forge website

Public English/French support and privacy pages for PSSO Forge, published by
Marc Nahum under the e-nahum.net brand.

This repository contains website content only, not application source, tenant
profiles, credentials or purchase records.

## Publishing

GitHub Pages publishes the `main` branch at repository root, with the custom
domain `pssoforge.e-nahum.net`. HTTPS must be verified and enforced before these
URLs are used in the application or App Store Connect.

## Editing

Edit the approved text in `content/en/` and `content/fr/`, then run:

```sh
python3 build_site.py
```

The builder uses only Python's standard library and generates self-contained
HTML with no external scripts, fonts, analytics, cookies or embedded widgets.
It supports the headings, paragraphs, lists, bold text, inline code and links
used by these content files; it is not a general-purpose Markdown renderer.
Review content and links before committing regenerated pages.

To import newly owner-approved policy/support drafts:

```sh
python3 build_site.py --import-approved-drafts /path/to/AppStore \
  --effective-date YYYY-MM-DD
```

The importer extracts only the public English/French sections, removes editorial
instructions, sets the effective date and prepares hosting wording for the
published site. Never import unapproved drafts.

Website publication is independent of an App Store app submission or release.
