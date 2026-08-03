#!/usr/bin/env python3
"""Batch-download product images for the report. Direct URLs first, og:image fallback for page URLs."""
import os, re, sys, urllib.request, urllib.error, html as ihtml

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "images")
os.makedirs(IMG, exist_ok=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")

def og_image(page_url):
    """Extract best image candidates from a page: og:image + large CDN imgs."""
    try:
        data, _ = fetch(page_url)
        text = data.decode("utf-8", "ignore")
    except Exception as e:
        print(f"  page fetch failed: {e}")
        return []
    cands = []
    m = re.findall(r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)', text)
    m += re.findall(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', text)
    for u in m:
        cands.append(ihtml.unescape(u))
    # large images in page (width>=800 hints or known CDN paths)
    for u in re.findall(r'(?:src|data-src|data-original)=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp))(?:\?[^"\']*)?["\']', text):
        cands.append(ihtml.unescape(u))
    return cands

def save(name, url):
    dest = os.path.join(IMG, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        print(f"[skip] {name} already ok")
        return True
    try:
        data, ctype = fetch(url)
        if len(data) < 9000:
            print(f"[small] {name}: {len(data)}B from {url[:90]}")
            return False
        if not (data[:3] == b'\xff\xd8\xff' or data[:8].startswith(b'\x89PNG') or data[:4] == b'RIFF' or data[:4] == b'GIF8'):
            print(f"[not-image] {name}: {ctype} {len(data)}B {url[:90]}")
            return False
        with open(dest, "wb") as f:
            f.write(data)
        print(f"[ok] {name}: {len(data)}B")
        return True
    except Exception as e:
        print(f"[fail] {name}: {e} ({url[:90]})")
        return False

# name -> (direct urls, page urls for og:image)
JOBS = {
    "ugreen-idx6011pro.png": (["https://storage.googleapis.com/www.taiwantradeshow.com.tw/product/202504/T-08802558.png",
        "https://pics.computerbase.de/1/2/0/6/0/8-1b6565c62200ecb0/4-1080.d3a6c727.jpg"], []),
    "ezviz-corex.jpg": (["https://www.guokewang.com.cn/static/upload/image/20260422/1776820309139090.jpg",
        "https://pic.cnmtpt.com/Uploadfiles/20260428/2026042812435485160.001.png"], []),
    "ezviz-tianji.jpg": (["https://q2.itc.cn/images01/20240726/4f9cf8ed91cf4acaa06659ecbaf9df94.jpeg",
        "https://q0.itc.cn/images01/20240726/87bf024801ea4be8a2ab6f4f4d14efd0.jpeg"], ["https://www.ithome.com/0/783/936.htm"]),
    "ugreen-syncare-d500.png": (["https://img.ithome.com/newsuploadfiles/2026/1/66edd074-7dbd-4475-abff-a6c4fe4c2a50.png?x-bce-process=image/format,f_auto"], []),
    "minisforum-n5max.png": (["https://cdn.shopify.com/s/files/1/0671/9789/4771/files/2_1de38d08-baf0-4ec3-a40a-95e8225e7f4c.png?v=1784010669&width=2048",
        "https://minisforumpc.eu/cdn/shop/files/N5MAX-1.png?v=1780907572&width=2000"], []),
    "minisforum-n5max-2.png": (["https://minisforumpc.eu/cdn/shop/files/N5MAX-8.png?v=1780907577&width=4000"], []),
    "zspace-t6.jpg": (["https://doc-fd.zol-img.com.cn/t_s2000x2000/g8/M00/08/0C/ChMkLWko-faIRjZ-AACy14zRIPgAAGj0gD7f0IAALLv530.jpg"], []),
    "zspace-z425.jpg": ([], ["https://www.ithome.com/0/889/807.htm"]),
    "zspace-z425-2.jpg": (["https://img.ithome.com/newsuploadfiles/2025/10/9ab9fb78-d065-4d43-ad0f-ac08f395ebb9.jpg?x-bce-process=image/format,f_auto"], []),
    "huawei-x2pro.jpg": (["https://img.ithome.com/newsuploadfiles/2026/3/a7f8ee81-d51b-4a44-90a9-a36290460c6e.jpg?x-bce-process=image/format,f_auto",
        "https://img.ithome.com/newsuploadfiles/2026/3/3e7442bb-4321-4fcd-8e32-ef852b2c52fe.jpg?x-bce-process=image/format,f_auto"], []),
    "aqara-s1plus.jpg": (["https://k.sinaimg.cn/n/spider20260303/199/w660h339/20260303/ecaa-5dfc295e37dccd6c9a4f3a04a1aa4e24.jpg/w700d1q75cms.jpg?by=cms_fixed_width",
        "https://static-resource.aqara.com/temp/400x400_1681178650239.png"], ["https://www.aqara.cn/magicpad-s1-plus_overview"]),
    "orvibo-mixpad7.jpg": ([], ["https://www.orvibo.com/mobile/cn/product/mixpad_7.html"]),
    "xiaomi-panel-max.jpg": ([], ["https://product.pconline.com.cn/intelligentswitch/xiaomi/2752579.html", "https://www.xiaomiyoupin.com/detail?gid=179055"]),
    "echo-show8.jpg": ([], ["https://www.ifixit.com/Device/Amazon_echo_show_8_3rd_Gen"]),
    "echo-hub.jpg": ([], ["https://me.pcmag.com/en/smart-displays/22102/amazon-echo-hub"]),
    "nest-hub-max.jpg": (["https://images.techadvisor.com/cmsdata/features/3696417/google_nest_hub_max_lifestyle_1.jpg"], []),
    "apple-homepad-render.jpg": (["https://image-cdn.hypb.st/https%3A%2F%2Fhypebeast.com%2Fimage%2F2025%2F12%2F11%2Fapple-homepad-smart-home-hub-leak-details-a18-power.jpg?q=75&w=800&cbr=1&fit=max",
        "https://www.idropnews.com/wp-content/uploads/2026/01/apple-j490-home-hub-kitchen-lifestyle-concept.jpg"], []),
    "tuya-tuyago5.jpg": ([], ["https://ah.ifeng.com/c/8XTEATY70Op"]),
    "switchbot-hub3.jpg": ([], ["https://us.switch-bot.com/products/switchbot-hub-3"]),
    "aqara-hub-m3.webp": (["https://eu.aqara.com/cdn/shop/files/M3_1.webp?v=1729064019&width=1200"], []),
    "homey-pro.jpg": ([], ["https://www.trustedreviews.com/reviews/homey-pro-2026", "https://homey.app/en-us/products/homey-pro/"]),
    "ha-voice-pe.jpg": ([], ["https://www.home-assistant.io/voice-pe/"]),
    "ha-green.jpg": ([], ["https://www.home-assistant.io/green/"]),
    "ugreen-dxp4800.png": (["https://storage.googleapis.com/www.taiwantradeshow.com.tw/product/202504/T-18189900.png"], []),
}

for name, (directs, pages) in JOBS.items():
    if os.path.exists(os.path.join(IMG, name)) and os.path.getsize(os.path.join(IMG, name)) > 10000:
        print(f"[skip] {name} already ok"); continue
    done = any(save(name, u) for u in directs)
    if not done:
        for p in pages:
            cands = og_image(p)
            print(f"  {p[:70]} -> {len(cands)} candidates")
            if any(save(name, u) for u in cands[:8]):
                done = True; break
    if not done:
        print(f"[MISSING] {name}")
