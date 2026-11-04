"""Save a PNG screenshot of the Dallas case map for the README (Week 10 stretch).

What it does:
    Opens reports/dallas_map.html in headless Google Chrome (no window
    appears) and saves reports/dallas_map.png. Chrome is used because it's
    already installed on most machines, so nothing extra has to be pip
    installed. The map's background tiles load from the internet, so this
    needs a network connection.

If Chrome can't be found, it prints how to take the screenshot by hand
and exits without failing.

How to run (from the repo root, after src.casemap):
    .venv/bin/python -m src.map_screenshot
"""

import shutil
import subprocess
from pathlib import Path

MAP_PATH = Path("reports/dallas_map.html")
PNG_PATH = Path("reports/dallas_map.png")

# Common Chrome/Chromium locations: macOS app bundle first, then names
# found on PATH (Linux / Windows).
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
    "chrome",
]

MANUAL_STEPS = (
    "To take the screenshot yourself: open reports/dallas_map.html in a browser, "
    "wait for the map to load, then press Cmd+Shift+4 (Mac) or Win+Shift+S "
    "(Windows), drag over the map and legend, and save it as reports/dallas_map.png."
)


def find_chrome():
    """Return the path to a Chrome/Chromium executable, or None if there isn't one."""
    for candidate in CHROME_CANDIDATES:
        # Full paths are checked directly; bare names are looked up on PATH.
        if Path(candidate).is_file():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def screenshot(chrome):
    """Run headless Chrome once to render the map and write the PNG.

    --virtual-time-budget gives the page 10 seconds of "page time" to fetch
    map tiles and draw the markers before the picture is taken. Without it,
    the screenshot can catch the map half loaded.
    """
    cmd = [
        chrome,
        "--headless=new",            # no visible window
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1200,900",    # size of the picture in pixels
        "--virtual-time-budget=10000",
        f"--screenshot={PNG_PATH.resolve()}",
        MAP_PATH.resolve().as_uri(),  # file:///... URL of the saved map
    ]
    # check=True raises if Chrome exits with an error; output is captured so
    # Chrome's own log lines don't clutter the terminal.
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)


def main():
    """Find Chrome and take the screenshot, or print manual steps."""
    if not MAP_PATH.exists():
        print(f"{MAP_PATH} not found; run `python -m src.casemap` first.")
        return

    chrome = find_chrome()
    if chrome is None:
        print("Chrome/Chromium not found, so no screenshot was taken.")
        print(MANUAL_STEPS)
        return

    screenshot(chrome)
    print(f"wrote {PNG_PATH} ({PNG_PATH.stat().st_size / 1000:.0f} KB)")


# Only run when executed directly (python -m src.map_screenshot), not on import.
if __name__ == "__main__":
    main()
