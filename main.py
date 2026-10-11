import time
import os
from playwright.sync_api import sync_playwright

def write_status(status_dot, message):
    log_line = f"{status_dot} {message}\n"
    print(log_line.strip())
    with open("status.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

def save_m3u(stream_url, title="Willow TV"):
    m3u_content = f"#EXTM3U\n#EXTINF:-1,{title}\n{stream_url}\n"
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print("🟢 playlist.m3u file successfully generated!")

def get_video_stream():
    # আগের স্ট্যাটাস ফাইল রিসেট করা
    if os.path.exists("status.txt"):
        os.remove("status.txt")

    write_status("🟡", "Script started. Initializing Playwright browser...")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            write_status("🟢", "Browser launched successfully.")

            master_link = None

            def handle_request(request):
                nonlocal master_link
                if ".m3u8" in request.url or "playlist" in request.url:
                    master_link = request.url
                    write_status("🟢", f"Stream link captured: {master_link}")

            page.on("request", handle_request)

            write_status("🟡", "Navigating to target URL: https://playsza.st/player.php?id=willow")
            page.goto("https://playsza.st/player.php?id=willow", timeout=60000)
            
            write_status("🟡", "Waiting for Cloudflare verification and player load (15 seconds)...")
            time.sleep(15)

            # আইফ্রেম বা পেজ কন্টেন্ট চেক করা
            frames = page.frames
            write_status("🟡", f"Total frames found: {len(frames)}")
            for idx, frame in enumerate(frames):
                try:
                    content = frame.content()
                    if ".m3u8" in content:
                        write_status("🟢", f"Found m3u8 reference inside frame {idx}")
                except Exception as e:
                    pass

            browser.close()

            if master_link:
                write_status("🟢", "Process successful! Saving M3U playlist...")
                save_m3u(master_link, "Willow Live TV")
            else:
                write_status("🔴", "Failed: Master link (.m3u8) could not be captured.")

        except Exception as e:
            write_status("🔴", f"Critical Error occurred: {str(e)}")

if __name__ == "__main__":
    get_video_stream()
