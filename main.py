import time
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

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
    if os.path.exists("status.txt"):
        os.remove("status.txt")
    if os.path.exists("playlist.m3u"):
        os.remove("playlist.m3u")

    write_status("🟡", "Script started. Initializing Stealth Browser...")

    with sync_playwright() as p:
        try:
            # হেডার বা অটোমেশন ফ্ল্যাগ হাইড করার জন্য অতিরিক্ত আর্গুমেন্ট
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            
            # স্টিলথ মোড এপ্লাই করা যাতে বট ডিটেক্ট না হয়
            stealth_sync(page)
            write_status("🟢", "Stealth mode applied to browser successfully.")

            master_link = None

            def handle_request(request):
                nonlocal master_link
                if ".m3u8" in request.url or "playlist" in request.url or "manifest" in request.url:
                    if not master_link:
                        master_link = request.url
                        write_status("🟢", f"Stream link captured via network: {master_link}")

            page.on("request", handle_request)

            write_status("🟡", "Navigating to target URL: https://playsza.st/player.php?id=willow")
            page.goto("https://playsza.st/player.php?id=willow", timeout=60000)
            
            # ক্লাউডফ্লেয়ার পাস হওয়ার জন্য ডাইনামিক চেক (সর্বোচ্চ ৪০ সেকেন্ড)
            write_status("🟡", "Waiting for Cloudflare protection to clear with stealth...")
            bypassed = False
            for i in range(40):
                time.sleep(1)
                title = page.title()
                content = page.content()
                
                # যদি ক্লাউডফ্লেয়ার পেজ টাইটেল বা টেক্সট রিমুভ হয়ে যায়
                if "Just a moment" not in title and "Checking your browser" not in content and "ddg" not in content:
                    write_status("🟢", f"Cloudflare bypassed successfully after {i+1} seconds!")
                    bypassed = True
                    break
            
            if not bypassed:
                write_status("🔴", "Failed: Cloudflare challenge could not be bypassed within time limit.")

            # প্লেয়ার ও আইফ্রেম লোড হওয়ার জন্য আরও কিছুক্ষণ অপেক্ষা করে লিংক খোঁজা
            if bypassed:
                write_status("🟡", "Waiting for video player frames to load...")
                time.sleep(8)

                if not master_link:
                    write_status("🟡", "Scanning frames and page DOM for .m3u8 links...")
                    for frame in page.frames:
                        try:
                            f_content = frame.content()
                            if ".m3u8" in f_content:
                                write_status("🟢", "Found .m3u8 reference inside frame content!")
                                import re
                                urls = re.findall(r'https?://[^\s<>"]+?\.m3u8[^\s<>"]*', f_content)
                                if urls:
                                    master_link = urls[0]
                                    break
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
