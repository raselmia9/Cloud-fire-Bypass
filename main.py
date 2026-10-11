import os
import cloudscraper

def write_status(status_dot, message):
    log_line = f"{status_dot} {message}\n"
    print(log_line.strip())
    with open("status.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

def test_cloudflare_bypass():
    if os.path.exists("status.txt"):
        os.remove("status.txt")

    write_status("🟡", "Script started. Testing Cloudflare bypass...")

    # ক্লাউডস্ক্র্যাপার দিয়ে ব্রাউজার সেশন তৈরি
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    target_url = "https://playsza.st/player.php?id=willow"
    write_status("🟡", f"Connecting to: {target_url}")

    try:
        response = scraper.get(target_url, timeout=30)
        
        # স্ট্যাটাস কোড ও রেসপন্স চেক
        write_status("🟡", f"HTTP Response Code: {response.status_code}")

        if response.status_code == 200:
            html_content = response.text
            # যদি ক্লাউডফ্লেয়ারের চ্যালেঞ্জ পেজ বা 'Just a moment' লেখা না থাকে, তবে বাইপাস সফল
            if "Just a moment" in html_content or "Checking your browser" in html_content:
                write_status("🔴", "Failed: Still trapped in Cloudflare challenge page.")
            else:
                write_status("🟢", "Success! Cloudflare protection bypassed completely.")
                write_status("🟢", f"Page Title/Snippet: {html_content[:150].strip()}")
        else:
            write_status("🔴", f"Failed with HTTP Status: {response.status_code}")

    except Exception as e:
        write_status("🔴", f"Critical Error occurred: {str(e)}")

if __name__ == "__main__":
    test_cloudflare_bypass()
