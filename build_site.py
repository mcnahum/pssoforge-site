#!/usr/bin/env python3
"""Build the owner-approved bilingual, dependency-free PSSO Forge website."""

import argparse
from datetime import date
import html
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
CONTACT = "pssoforge@e-nahum.net"
DOMAIN = "https://pssoforge.e-nahum.net"

THEME_SCRIPT = """(() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();"""

THEME_CSS = """
:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}
"""

LAYOUT_CSS = """
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--cp-bg); color: var(--cp-text);
  font-family: "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.65; font-size: 1rem;
}
a { color: var(--cp-link); text-underline-offset: .2em; overflow-wrap: anywhere; }
a:hover { color: var(--cp-accent-hover); }
a:focus-visible { outline: 3px solid var(--cp-accent); outline-offset: 4px; }
.skip { position: absolute; left: 16px; top: -120px; padding: 12px;
  background: var(--cp-surface); border: 1px solid var(--cp-border); z-index: 1; }
.skip:focus { top: 12px; }
header { background: var(--cp-bg-elevated); border-bottom: 1px solid var(--cp-border); }
.bar { max-width: 1040px; margin: auto; padding: 24px; display: flex;
  flex-wrap: wrap; align-items: center; gap: 20px; justify-content: space-between; }
.brand { font-size: 1.25rem; font-weight: 700; color: var(--cp-text); text-decoration: none; }
nav { display: flex; flex-wrap: wrap; gap: 16px; }
nav a { padding: 4px 0; }
main { max-width: 880px; margin: 40px auto; padding: 32px;
  background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 16px; }
h1 { line-height: 1.2; font-size: clamp(2rem, 6vw, 2.75rem); margin: 0 0 28px; }
h2 { line-height: 1.3; font-size: 1.4rem; margin: 36px 0 12px;
  padding-bottom: 8px; border-bottom: 1px solid var(--cp-border); }
p, ul { margin: 16px 0; }
li { margin: 8px 0; }
code { font-family: Consolas, "Courier New", Courier, monospace;
  background: var(--cp-surface-soft); padding: 2px 4px; border-radius: 4px; }
.actions { display: flex; gap: 16px; flex-wrap: wrap; margin: 24px 0; }
.button { display: inline-block; padding: 12px 20px; border-radius: .625rem;
  background: var(--cp-accent); color: var(--cp-accent-fg); text-decoration: none; font-weight: 600; }
.button:hover { background: var(--cp-accent-hover); color: var(--cp-accent-fg); }
footer { max-width: 880px; margin: 24px auto 40px; padding: 0 24px;
  color: var(--cp-text-muted); font-size: .9rem; }
@media (max-width: 600px) {
  .bar { padding: 20px; } main { margin: 20px 12px; padding: 24px 20px; }
  nav { gap: 12px; } h2 { margin-top: 28px; }
}
"""

LABELS = {
    "en": {
        "home": "Home", "support": "Support", "privacy": "Privacy policy",
        "skip": "Skip to content", "navigation": "Main navigation",
        "footer": "Published by Marc Nahum, under the e-nahum.net brand.",
        "summary": "Local Platform SSO profile tools for Microsoft Intune.",
    },
    "fr": {
        "home": "Accueil", "support": "Assistance", "privacy": "Confidentialité",
        "skip": "Aller au contenu", "navigation": "Navigation principale",
        "footer": "Édité par Marc Nahum, sous la marque e-nahum.net.",
        "summary": "Outils locaux de profils Platform SSO pour Microsoft Intune.",
    },
}


def plain(text):
    return html.escape(text).replace(
        CONTACT, f'<a href="mailto:{CONTACT}">{CONTACT}</a>'
    )


def inline(text):
    pattern = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)|\*\*(.+?)\*\*|`([^`]+)`")
    result = []
    end = 0
    for match in pattern.finditer(text):
        result.append(plain(text[end:match.start()]))
        if match.group(1) is not None:
            target = match.group(2)
            if not target.startswith(("https://", "/", "mailto:")) or target.startswith("//"):
                raise ValueError(f"Unsupported link destination: {target}")
            result.append(f'<a href="{html.escape(target, quote=True)}">{inline(match.group(1))}</a>')
        elif match.group(3) is not None:
            result.append(f"<strong>{inline(match.group(3))}</strong>")
        else:
            result.append(f"<code>{html.escape(match.group(4))}</code>")
        end = match.end()
    result.append(plain(text[end:]))
    return "".join(result)


def markdown(text):
    output, paragraph, items = [], [], []

    def flush():
        if paragraph:
            output.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()
        if items:
            output.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            items.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("### "):
            flush()
            output.append(f"<h2>{inline(line[4:])}</h2>")
        elif line.startswith("- "):
            if paragraph:
                flush()
            items.append(line[2:])
        elif line.startswith(("#", ">", "```", "|", "![")):
            raise ValueError(f"Unsupported Markdown structure: {line}")
        else:
            if items:
                flush()
            paragraph.append(line)
    flush()
    return "\n".join(output)


def public_sections(path):
    source = path.read_text(encoding="utf-8")
    english, french = source.split("## English\n", 1)[1].split("\n## Français\n", 1)
    french = french.split("\n## Editorial references", 1)[0]
    return {"en": english.strip(), "fr": french.strip()}


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one approved-draft phrase: {old}")
    return text.replace(old, new, 1)


def import_drafts(folder, effective_date):
    published = date.fromisoformat(effective_date)
    dates = {
        "en": f"{published.strftime('%B')} {published.day}, {published.year}",
        "fr": f"{published.day} " + ["janvier", "février", "mars", "avril", "mai", "juin",
                                     "juillet", "août", "septembre", "octobre", "novembre",
                                     "décembre"][published.month - 1] + f" {published.year}",
    }
    privacy = public_sections(folder / "PRIVACY-DRAFT.md")
    support = public_sections(folder / "SUPPORT-DRAFT.md")
    privacy["en"] = replace_once(
        privacy["en"], "TO BE SET WHEN THE APPROVED POLICY IS PUBLISHED", dates["en"])
    privacy["fr"] = replace_once(
        privacy["fr"], "À FIXER LORS DE LA PUBLICATION DE LA POLITIQUE APPROUVÉE", dates["fr"])
    privacy["en"] = replace_once(
        privacy["en"], "The support/privacy website is planned to use GitHub Pages.",
        "The support/privacy website is hosted using GitHub Pages.")
    privacy["fr"] = replace_once(
        privacy["fr"], "Le site d'assistance et de confidentialité est prévu sur GitHub Pages.",
        "Le site d'assistance et de confidentialité est hébergé sur GitHub Pages.")
    privacy["en"] = replace_once(
        privacy["en"], "No developer-added advertising, analytics scripts, tracking pixels or embedded\n"
        "third-party widgets are planned for this website.",
        "This website does not include developer-added advertising, analytics scripts,\n"
        "tracking pixels or embedded third-party widgets.")
    privacy["fr"] = replace_once(
        privacy["fr"], "Aucune publicité, aucun script d'analyse, pixel de suivi ou composant tiers\n"
        "intégré ajouté par le développeur n'est prévu sur ce site.",
        "Ce site ne contient aucune publicité, aucun script d'analyse, pixel de suivi ou\n"
        "composant tiers intégré ajouté par le développeur.")
    support["en"] = replace_once(
        support["en"], "Privacy information will be available on the English privacy page of this site.",
        "Read the [privacy policy](/en/privacy/) for information about data handling.")
    support["fr"] = replace_once(
        support["fr"], "Les informations de confidentialité seront accessibles sur la page française\n"
        "de ce site.",
        "Consultez la [politique de confidentialité](/fr/privacy/) pour le traitement des données.")
    providers = (
        ("Apple Privacy Policy", "Confidentialité Apple", "https://www.apple.com/legal/privacy/"),
        ("GitHub Privacy Statement", "Confidentialité GitHub",
         "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"),
        ("Google Privacy Policy", "Confidentialité Google", "https://policies.google.com/privacy"),
        ("GitHub Pages visitor logging", "Journaux des visites GitHub Pages",
         "https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages"),
    )
    for language in LABELS:
        heading = "Provider privacy information" if language == "en" else "Confidentialité des prestataires"
        provider_links = "".join(
            f"- [{english if language == 'en' else french}]({url})\n"
            for english, french, url in providers)
        privacy[language] += f"\n\n### {heading}\n\n{provider_links}"
        content = ROOT / "content" / language
        content.mkdir(parents=True, exist_ok=True)
        for section, text in (("privacy", privacy[language]), ("support", support[language])):
            (content / f"{section}.md").write_text(text + "\n", encoding="utf-8")


def page(language, title, body, route="", root=False):
    labels = LABELS[language]
    other = "fr" if language == "en" else "en"
    counterpart = f"/{other}/{route}" if route and route != "404.html" else f"/{other}/"
    path = "/404.html" if route == "404.html" else ("/" if root else f"/{language}/{route}")
    navigation = "".join(
        f'<a href="/{language}/{suffix}">{html.escape(labels[key])}</a>'
        for key, suffix in (("home", ""), ("support", "support/"), ("privacy", "privacy/"))
    )
    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | PSSO Forge</title>
<meta name="description" content="{html.escape(labels['summary'], quote=True)}">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<link rel="canonical" href="{DOMAIN}{path}">
<script>{THEME_SCRIPT}</script>
<style>{THEME_CSS}{LAYOUT_CSS}</style>
</head>
<body>
<a class="skip" href="#content">{labels['skip']}</a>
<header><div class="bar"><a class="brand" href="/{language}/">PSSO Forge</a>
<nav aria-label="{labels['navigation']}">{navigation}
<a href="{counterpart}" lang="{other}" hreflang="{other}">{'Français' if other == 'fr' else 'English'}</a>
</nav></div></header>
<main id="content"><h1>{html.escape(title)}</h1>{body}</main>
<footer><p>© 2026 Marc Nahum. {labels['footer']}
<a href="mailto:{CONTACT}">{CONTACT}</a></p></footer>
</body></html>
"""


def write_page(relative, content):
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build():
    forbidden = ("TO BE SET", "À FIXER", "OWNER TO CONFIRM", "OWNER APPROVAL",
                 "À CONFIRMER", "PUBLIC SUPPORT ADDRESS", "NOT PUBLISHED")
    for language, labels in LABELS.items():
        for section in ("privacy", "support"):
            text = (ROOT / "content" / language / f"{section}.md").read_text(encoding="utf-8")
            if any(marker in text.upper() for marker in forbidden):
                raise ValueError(f"Unresolved editorial marker in {language}/{section}")
            write_page(f"{language}/{section}/index.html",
                       page(language, labels[section], markdown(text), f"{section}/"))
        if language == "en":
            intro = (
                "<p>Create, inspect and correct local macOS Platform SSO Settings Catalog "
                "profiles for Microsoft Intune.</p>"
                "<p>Requires macOS 26 or later. The application interface is English. "
                "The application is free; optional tips do not unlock features.</p>"
                "<p>The application does not deploy profiles or execute exported PowerShell. "
                "Review and test any profile before deploying it separately.</p>"
            )
        else:
            intro = (
                "<p>Créez, examinez et corrigez des profils locaux Platform SSO macOS au "
                "format Settings Catalog pour Microsoft Intune.</p>"
                "<p>Prérequis : macOS 26 ou ultérieur. L’interface de l’application est en anglais. "
                "L’application est gratuite ; les pourboires facultatifs ne débloquent aucune fonction.</p>"
                "<p>L’application ne déploie pas les profils et n’exécute pas le PowerShell exporté. "
                "Vérifiez et testez tout profil avant un déploiement séparé.</p>"
            )
        actions = f"""<div class="actions">
<a class="button" href="/{language}/support/">{labels['support']}</a>
<a class="button" href="/{language}/privacy/">{labels['privacy']}</a></div>"""
        write_page(f"{language}/index.html", page(language, "PSSO Forge", intro + actions))
    write_page("index.html", page(
        "en", "PSSO Forge",
        '<p>Support and privacy information. Choose your language.</p>'
        '<p lang="fr">Assistance et confidentialité. Choisissez votre langue.</p>'
        '<div class="actions"><a class="button" href="/en/" lang="en">English</a>'
        '<a class="button" href="/fr/" lang="fr">Français</a></div>', root=True))
    write_page("404.html", page(
        "en", "Page not found",
        '<p>This page is unavailable. / Cette page est introuvable.</p>'
        '<p><a href="/en/">English home</a> · <a href="/fr/" lang="fr">Accueil français</a></p>',
        route="404.html"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-approved-drafts", type=Path)
    parser.add_argument("--effective-date")
    args = parser.parse_args()
    if bool(args.import_approved_drafts) != bool(args.effective_date):
        parser.error("Draft import and its effective date must be supplied together.")
    if args.import_approved_drafts:
        import_drafts(args.import_approved_drafts, args.effective_date)
    build()
    print("Built eight self-contained bilingual website pages.")


if __name__ == "__main__":
    main()
