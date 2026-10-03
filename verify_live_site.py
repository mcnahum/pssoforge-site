"""Verify deployed public pages and HTTP-to-HTTPS redirects without disabling TLS."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
DOMAIN = "pssoforge.e-nahum.net"


def request(url):
    response = subprocess.check_output([
        "curl", "--silent", "--show-error", "--connect-timeout", "10",
        "--max-time", "30", "--write-out", "\n%{http_code}\n%{redirect_url}", url,
    ])
    body, status, redirect = response.rsplit(b"\n", 2)
    return body, int(status), redirect.decode()


def main():
    routes = {
        "/": "index.html",
        "/en/": "en/index.html",
        "/fr/": "fr/index.html",
        "/en/support/": "en/support/index.html",
        "/fr/support/": "fr/support/index.html",
        "/en/privacy/": "en/privacy/index.html",
        "/fr/privacy/": "fr/privacy/index.html",
    }
    for route, file in routes.items():
        body, status, redirect = request(f"https://{DOMAIN}{route}")
        if status != 200 or redirect:
            raise RuntimeError(f"Unexpected HTTPS result for {route}: {status}, {redirect}")
        if body != (ROOT / file).read_bytes():
            raise RuntimeError(f"Deployed content does not match local approved page: {route}")
        _, status, redirect = request(f"http://{DOMAIN}{route}")
        if status not in (301, 308) or redirect != f"https://{DOMAIN}{route}":
            raise RuntimeError(f"HTTPS is not enforced for {route}: {status}, {redirect}")
        print(f"Verified HTTPS content and HTTP redirect: {route}")
    body, status, _ = request(f"https://{DOMAIN}/missing-page-check/")
    if status != 404 or body != (ROOT / "404.html").read_bytes():
        raise RuntimeError("The deployed custom 404 page is missing or incorrect.")
    print("Verified custom 404 page.")


if __name__ == "__main__":
    main()
