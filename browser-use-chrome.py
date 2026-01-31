#!/usr/bin/env python3
"""
Browser automation with Chrome profile integration.
Uses Playwright to connect to your existing Chrome profile.

Usage:
    python3 browser-use-chrome.py

Profiles available:
    - Default (main profile)
    - Profile 1, 2, 3 (additional profiles)
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Chrome user data directory
CHROME_USER_DATA = Path.home() / "Library" / "Application Support" / "Google" / Chrome"

# Available profiles
PROFILES = ["Default", "Profile 1", "Profile 2", "Profile 3"]


async def main():
    """Main automation function with Chrome profile."""

    async with async_playwright() as p:
        # Launch Chrome with persistent context (your profile)
        # Note: Only ONE Chrome instance can use a profile at a time
        # Close regular Chrome before running this, or use a different profile

        profile = PROFILES[0]  # Use "Default" profile, change as needed

        print(f"🚀 Starting Chrome with profile: {profile}")
        print(f"📁 Profile path: {CHROME_USER_DATA / profile}")
        print()
        print("⚠️  IMPORTANT: Close all Chrome windows before running this!")
        print("   Only one Chrome instance can use a profile at a time.")
        print()

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_USER_DATA),
            headless=False,  # Show the browser
            channel="chrome",  # Use actual Chrome instead of bundled Chromium
            args=[
                "--disable-extensions-except=/Users/speed/Downloads/parchi",
                "--load-extension=/Users/speed/Downloads/parchi",
            ],
            # Don't specify profile here - use the default profile
        )

        # Get existing pages or create new one
        if len(browser.contexts) > 0:
            context = browser.contexts[0]
        else:
            context = browser

        pages = context.pages
        if len(pages) > 0:
            page = pages[0]
        else:
            page = await context.new_page()

        print(f"✅ Browser started with {len(context.pages)} pages")

        # Example: Navigate to a page
        await page.goto("https://twitter.com", wait_until="domcontentloaded")
        print(f"📍 Navigated to: {page.url}")

        # Example: Take a screenshot
        await page.screenshot(path="screenshot.png")
        print("📸 Screenshot saved to: screenshot.png")

        # Example: Check if logged in (you should be if you use your profile)
        title = await page.title()
        print(f"📄 Page title: {title}")

        # Keep browser open for interaction
        print()
        print("Press Enter to close browser...")
        input()

        await browser.close()
        print("✅ Browser closed")


async def simple_example():
    """Simple example without profile - good for testing."""
    async with async_playwright() as p:
        # Launch without persistent context (fresh session)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://example.com")
        print("Opened example.com")

        # Wait for user to see it
        await asyncio.sleep(3)

        await browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Browser Automation with Chrome Profile")
    print("=" * 60)
    print()

    # Check if Chrome is running
    import subprocess
    try:
        result = subprocess.run(
            ["pgrep", "-x", "Chrome"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("⚠️  WARNING: Chrome is currently running!")
            print("   Please close Chrome before using your profile.")
            print("   Or use 'simple_example()' for a fresh session.")
            print()
            choice = input("Continue anyway? (y/N): ")
            if choice.lower() != "y":
                print("Running simple example instead...")
                asyncio.run(simple_example())
                exit(0)
    except FileNotFoundError:
        pass

    asyncio.run(main())
