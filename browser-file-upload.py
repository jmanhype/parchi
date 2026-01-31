#!/usr/bin/env python3
"""
Browser automation examples for file uploads and social media posting.

This demonstrates:
1. Using your Chrome profile (stays logged in)
2. File uploads (images, videos, documents)
3. Form filling and posting

Usage:
    python3 browser-file-upload.py
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Chrome user data directory
CHROME_USER_DATA = Path.home() / "Library" / "Application Support" / "Google" / Chrome"


async def upload_file_to_twitter(page, file_path: str, caption: str = ""):
    """
    Upload a file to Twitter/X using your logged-in session.

    Args:
        page: Playwright page object
        file_path: Path to image/video file
        caption: Optional caption text
    """
    try:
        # Navigate to Twitter
        await page.goto("https://twitter.com", wait_until="domcontentloaded")

        # Wait for page to load
        await asyncio.sleep(2)

        # Look for the "Post" button to open composer
        # Twitter's DOM changes frequently, so these selectors might need updates
        post_button = page.locator('a[aria-label="Post"], [data-testid="SideNav_NewTweet_Button"]').first
        await post_button.click()

        await asyncio.sleep(1)

        # Upload file
        file_input = page.locator('input[type="file"]').first
        await file_input.set_input_files(file_path)

        await asyncio.sleep(2)

        # Add caption if provided
        if caption:
            text_area = page.locator('div[contenteditable="true"][role="textbox"]').first
            await text_area.fill(caption)

        # Post button (disabled when empty, enabled after file upload)
        post_button = page.locator('button[data-testid="tweetButton"], button[role="button"]:has-text("Post")').first
        # await post_button.click()  # Uncomment to actually post

        print("✅ File loaded in Twitter composer")
        print(f"📁 File: {file_path}")
        print(f"💬 Caption: {caption}")
        print("⚠️  Post button NOT clicked (comment out to enable)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def upload_file_to_facebook(page, file_path: str, caption: str = ""):
    """
    Upload a file to Facebook using your logged-in session.
    """
    try:
        await page.goto("https://facebook.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # Click "What's on your mind?" or similar
        composer = page.locator('[aria-label*="What\'s on your"], [role="complementary"]').first
        await composer.click()

        await asyncio.sleep(1)

        # Upload photo/video
        file_input = page.locator('input[type="file"]').first
        await file_input.set_input_files(file_path)

        await asyncio.sleep(2)

        # Add caption
        if caption:
            text_area = page.locator('[role="textbox"], div[contenteditable="true"]').first
            await text_area.fill(caption)

        print("✅ File loaded in Facebook composer")
        print(f"📁 File: {file_path}")
        print(f"💬 Caption: {caption}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def generic_file_upload_example(page, url: str, file_path: str, selector: str = 'input[type="file"]'):
    """
    Generic file upload example for any site.

    Args:
        page: Playwright page object
        url: URL of the page with file upload
        file_path: Path to file to upload
        selector: CSS selector for file input (default: input[type="file"])
    """
    await page.goto(url, wait_until="domcontentloaded")

    # Wait for page load
    await asyncio.sleep(2)

    # Find and upload to file input
    file_input = page.locator(selector).first
    await file_input.set_input_files(file_path)

    print(f"✅ Uploaded {file_path} to {url}")
    await asyncio.sleep(2)

    # Take screenshot
    await page.screenshot(path="upload_result.png")
    print("📸 Screenshot saved: upload_result.png")


async def main():
    """Main function demonstrating file uploads."""

    async with async_playwright() as p:
        print("🚀 Starting Chrome with your profile...")

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_USER_DATA),
            headless=False,
            channel="chrome",
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()

        print("=" * 60)
        print("File Upload Examples")
        print("=" * 60)
        print()
        print("Select an example:")
        print("1. Twitter/X upload")
        print("2. Facebook upload")
        print("3. Generic upload (custom URL)")
        print()

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            file_path = input("Enter file path: ").strip()
            caption = input("Enter caption (optional): ").strip()
            await upload_file_to_twitter(page, file_path, caption)

        elif choice == "2":
            file_path = input("Enter file path: ").strip()
            caption = input("Enter caption (optional): ").strip()
            await upload_file_to_facebook(page, file_path, caption)

        elif choice == "3":
            url = input("Enter URL: ").strip()
            file_path = input("Enter file path: ").strip()
            await generic_file_upload_example(page, url, file_path)

        else:
            print("Invalid choice")
            await browser.close()
            return

        print()
        print("Press Enter to close browser...")
        input()

        await browser.close()


if __name__ == "__main__":
    import subprocess

    # Check if Chrome is running
    try:
        result = subprocess.run(
            ["pgrep", "-x", "Chrome"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("=" * 60)
            print("⚠️  WARNING: Chrome is currently running!")
            print("=" * 60)
            print()
            print("Please close Chrome before running this script.")
            print("Your Chrome profile can only be used by one process at a time.")
            print()
            exit(1)
    except FileNotFoundError:
        pass

    asyncio.run(main())
