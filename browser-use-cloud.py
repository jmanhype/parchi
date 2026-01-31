#!/usr/bin/env python3
"""
Browser Use Cloud - Python automation script
Uses your cloud profile with persisted logins for file uploads and automation.

Usage:
    python3 browser-use-cloud.py start
    python3 browser-use-cloud.py upload <file_path> <caption>
"""

import asyncio
import sys
import os
from pathlib import Path
import requests
from playwright.async_api import async_playwright

API_KEY = "bu_-RidfzaFluhAZyFRpW7WGMPawCt283uC5ckFNRaMux4"
PROFILE_ID = "e20b0219-f8b5-4fce-95ad-f9fc447d3716"
BASE_URL = "https://api.browser-use.com/api/v2"


def create_session():
    """Create a new browser session with your profile."""
    response = requests.post(
        f"{BASE_URL}/browsers",
        headers={"X-Browser-Use-API-Key": API_KEY},
        json={"profileId": PROFILE_ID, "timeout": 60}
    )
    data = response.json()
    return data["id"], data["cdpUrl"], data.get("liveUrl", "")


async def upload_to_twitter(cdp_url: str, file_path: str, caption: str = ""):
    """Upload a file to Twitter using your cloud profile."""
    async with async_playwright() as p:
        # Connect to cloud browser via CDP
        browser = await p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]

        # Get or create page
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = await context.new_page()

        # Navigate to Twitter
        await page.goto("https://twitter.com", wait_until="domcontentloaded")
        print("📍 Navigated to Twitter")

        # You should already be logged in via your profile!
        # Look for logged-in state indicators

        # Find and click the post button
        await asyncio.sleep(2)

        # Upload file
        file_input = page.locator('input[type="file"]').first
        if await file_input.count() > 0:
            await file_input.set_input_files(file_path)
            print(f"✅ File uploaded: {file_path}")
        else:
            print("⚠️  No file input found - Twitter might need manual navigation")

        # Add caption if provided
        if caption:
            text_area = page.locator('div[contenteditable="true"][role="textbox"]').first
            if await text_area.count() > 0:
                await text_area.fill(caption)
                print(f"💬 Caption added")

        print("\n📸 Screenshot saved: twitter_upload.png")
        await page.screenshot(path="twitter_upload.png")

        # Keep browser open for review
        print("\nPress Enter to close session...")
        input()

        await browser.close()

        # Stop the cloud session to save money
        session_id, _, _ = create_session()
        stop_session(session_id)


def list_sessions():
    """List active browser sessions."""
    response = requests.get(
        f"{BASE_URL}/browsers",
        headers={"X-Browser-Use-API-Key": API_KEY}
    )
    sessions = response.json()

    print("📋 Active Sessions:")
    if not sessions:
        print("   No active sessions")
        return

    for s in sessions:
        print(f"   {s['id']} - {s['status']} (cost: ${s.get('browserCost', 0)})")


def stop_session(session_id: str):
    """Stop a session and refund unused time."""
    response = requests.patch(
        f"{BASE_URL}/browsers/{session_id}",
        headers={"X-Browser-Use-API-Key": API_KEY},
        json={"status": "stopped"}
    )
    print(f"✅ Session stopped: {session_id}")
    print(f"   Unused time refunded")


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  start              - Start new session and get live URL")
        print("  upload <file>      - Upload file to Twitter")
        print("  list               - List active sessions")
        print("  stop <session_id>  - Stop a session")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        session_id, cdp_url, live_url = create_session()
        print("✅ Browser session started!")
        print(f"   Session ID: {session_id}")
        print(f"\n🌐 Open this URL to see the browser:")
        print(f"   {live_url}")
        print(f"\n💡 To connect programmatically:")
        print(f"   CDP URL: {cdp_url}")

    elif command == "list":
        list_sessions()

    elif command == "stop":
        if len(sys.argv) < 3:
            print("Usage: python3 browser-use-cloud.py stop <session_id>")
            sys.exit(1)
        stop_session(sys.argv[2])

    elif command == "upload":
        if len(sys.argv) < 3:
            print("Usage: python3 browser-use-cloud.py upload <file_path> [caption]")
            sys.exit(1)

        file_path = sys.argv[2]
        caption = sys.argv[3] if len(sys.argv) > 3 else ""

        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)

        # Start new session
        session_id, cdp_url, live_url = create_session()
        print(f"✅ Session started: {session_id}")

        # Do the upload
        await upload_to_twitter(cdp_url, file_path, caption)

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
