import time
from playwright.sync_api import sync_playwright

def get_video_stream():
    with sync_playwright() as p:
        # GitHub Actions-এর জন্য headless মোড চালু রাখা আবশ্যক
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        master_link = None

        # নেটওয়ার্ক রিকোয়েস্ট ট্র্যাক করে .m3u8 বা স্ট্রিম লিংক খুঁজে বের করা
        def handle_request(request):
            nonlocal master_link
            if ".m3u8" in request.url or "playlist" in request.url:
                master_link = request.url

        page.on("request", handle_request)

        try:
            print("Opening target URL...")
            page.goto("https://playsza.st/player.php?id=willog", timeout=60000)
            
            # ক্লাউডফ্লেয়ার ভেরিফিকেশন এবং প্লেয়ার লোড হওয়ার জন্য পর্যাপ্ত সময় দেওয়া (১০-১৫ সেকেন্ড)
            print("Waiting for Cloudflare and player to load...")
            time.sleep(15)

            # যদি সরাসরি রিকোয়েস্টে না পাওয়া যায়, তবে আইফ্রেমের ভেতর থেকে সোর্স খোঁজা
            frames = page.frames
            for frame in frames:
                try:
                    content = frame.content()
                    if ".m3u8" in content:
                        print("Found m3u8 in frame content!")
                except:
                    pass

            if master_link:
                print(f"Captured Master Link: {master_link}")
            else:
                print("Master link not captured directly, checking page state...")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_video_stream()
