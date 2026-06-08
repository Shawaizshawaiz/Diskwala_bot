import httpx
import time

# API endpoint that extracts direct links from Terabox share URLs
SAVETUBE_API = "https://ytshorts.savetube.me/api/v1/terabox-downloader"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://ytshorts.savetube.me/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def get_direct_link(url: str) -> dict | None:
    """
    Extract direct playable/downloadable links from a Terabox share URL.

    Args:
        url: Terabox share link (terabox.com or teraboxapp.com)

    Returns:
        dict with keys: title, thumbnail, resolutions (dict of quality->link)
        Returns None if extraction fails.
    """
    payload = {"url": url}

    # Try up to 2 times (1 retry on failure)
    for attempt in range(2):
        try:
            with httpx.Client(timeout=20) as client:
                response = client.post(
                    SAVETUBE_API,
                    json=payload,
                    headers=HEADERS
                )

            # Check HTTP status
            if response.status_code != 200:
                print(f"[terabox] API returned status {response.status_code}")
                if attempt == 0:
                    time.sleep(2)
                    continue
                return None

            data = response.json()

            # Parse the API response
            return parse_response(data)

        except httpx.TimeoutException:
            print(f"[terabox] Timeout on attempt {attempt + 1}")
            if attempt == 0:
                time.sleep(2)
                continue
            return None

        except Exception as e:
            print(f"[terabox] Error: {e}")
            return None

    return None


def parse_response(data: dict) -> dict | None:
    """
    Parse the raw API response into a clean dict.

    Args:
        data: Raw JSON response from savetube API

    Returns:
        Cleaned dict with title, thumbnail, resolutions, or None
    """
    try:
        # API returns a list of results
        if not data or "response" not in data:
            print("[terabox] Unexpected API response structure")
            return None

        results = data["response"]
        if not results or not isinstance(results, list):
            return None

        item = results[0]  # Take the first result

        title = item.get("title", "Terabox Video")
        thumbnail = item.get("thumbnail", "")

        # Extract available resolution links
        resolutions = {}
        resolutions_raw = item.get("resolutions", {})

        # Map known quality keys
        quality_map = {
            "HD Video": "HD",
            "SD Video": "SD",
            "1080p": "1080p",
            "720p": "720p",
            "480p": "480p",
            "360p": "360p",
            "Fast Download": "Fast",
        }

        for key, label in quality_map.items():
            if key in resolutions_raw and resolutions_raw[key]:
                resolutions[label] = resolutions_raw[key]

        # Fallback: grab whatever links exist
        if not resolutions:
            for k, v in resolutions_raw.items():
                if v and isinstance(v, str) and v.startswith("http"):
                    resolutions[k] = v

        if not resolutions:
            print("[terabox] No downloadable links found in response")
            return None

        return {
            "title": title,
            "thumbnail": thumbnail,
            "resolutions": resolutions,
        }

    except Exception as e:
        print(f"[terabox] Parse error: {e}")
        return None


def is_terabox_url(url: str) -> bool:
    """Check if a given URL is a valid Terabox share link."""
    terabox_domains = [
        "terabox.com",
        "teraboxapp.com",
        "1024tera.com",
        "4funbox.com",
        "mirrobox.com",
        "nephobox.com",
        "freeterabox.com",
    ]
    return any(domain in url.lower() for domain in terabox_domains)
