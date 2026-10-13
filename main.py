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

    write_status("🟡", "Script started. Testing Cloudflare bypass with Advanced Headers...")

    # ক্লাউডস্ক্র্যাপার দিয়ে ব্রাউজার সেশন তৈরি
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    target_url = "https://playerdee.top/alpha/manchester-united-vs-atletico-madrid/2777"
    
    # আসল ব্রাউজারের মতো হেডার্স সেট করা
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    write_status("🟡", f"Connecting to: {target_url}")

    try:
        response = scraper.get(target_url, headers=headers, timeout=30)
        
        write_status("🟡", f"HTTP Response Code: {response.status_code}")

        if response.status_code == 200:
            html_content = response.text
            if "Just a moment" in html_content or "Checking your browser" in html_content:
                write_status("🔴", "Failed: Still trapped in Cloudflare challenge page.")
            else:
                write_status("🟢", "Success! Cloudflare protection bypassed completely.")
                write_status("🟢", f"Page Snippet: {html_content[:150].strip()}")
        else:
            write_status("🔴", f"Failed with HTTP Status: {response.status_code}")

    except Exception as e:
        write_status("🔴", f"Critical Error occurred: {str(e)}")

if __name__ == "__main__":
    test_cloudflare_bypass()
