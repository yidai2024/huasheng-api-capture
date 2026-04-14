#!/usr/bin/env python3
"""huasheng.cn 深度抓取 - 登录/创作页面"""

from playwright.sync_api import sync_playwright
import json, time
from datetime import datetime
from urllib.parse import urlparse

def capture():
    all_apis = []
    seen = set()
    skip_ext = ['.js','.css','.png','.jpg','.jpeg','.gif','.svg','.woff','.woff2','.ttf','.ico','.webp','.mp4','.m3u8','.map','.xml','.txt','.eot']

    def on_req(req):
        url = req.url
        if any(url.lower().endswith(e) for e in skip_ext): return
        if url.startswith(('data:','blob:')): return
        if url not in seen:
            seen.add(url)
            parsed = urlparse(url)
            info = {
                'url': url, 'method': req.method,
                'domain': parsed.netloc, 'path': parsed.path,
                'query': parsed.query,
                'headers': dict(req.headers),
                'post_data': None
            }
            if req.method in ('POST','PUT','PATCH','DELETE'):
                try: info['post_data'] = req.post_data[:5000]
                except: pass
            all_apis.append(info)

    def on_resp(resp):
        for api in all_apis:
            if api['url'] == resp.url:
                api['status'] = resp.status
                api['content_type'] = resp.headers.get('content-type','')
                try:
                    if 'json' in api.get('content_type',''):
                        api['resp_body'] = resp.text()[:3000]
                except: pass
                break

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(
            viewport={'width':1920,'height':1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN'
        )
        page = ctx.new_page()
        page.on('request', on_req)
        page.on('response', on_resp)

        # 多个页面
        pages_to_visit = [
            ('https://www.huasheng.cn/', '首页'),
            ('https://www.huasheng.cn/create', '创作页'),
            ('https://www.huasheng.cn/ai', 'AI功能'),
            ('https://www.huasheng.cn/video', '视频'),
            ('https://www.huasheng.cn/workspace', '工作台'),
            ('https://www.huasheng.cn/draft', '草稿'),
            ('https://www.huasheng.cn/template', '模板'),
            ('https://www.huasheng.cn/voice', '配音'),
            ('https://www.huasheng.cn/sound', '声音'),
            ('https://www.huasheng.cn/material', '素材'),
            ('https://www.huasheng.cn/help', '帮助'),
            ('https://www.huasheng.cn/user', '用户'),
            ('https://www.huasheng.cn/account', '账户'),
            ('https://www.huasheng.cn/vip', 'VIP'),
            ('https://www.huasheng.cn/pricing', '价格'),
        ]
        
        for url, name in pages_to_visit:
            print(f"--- {name} ({url}) ---")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=15000)
                time.sleep(3)
                for _ in range(3):
                    page.evaluate('window.scrollBy(0, 600)')
                    time.sleep(0.8)
                page.screenshot(path=f'/root/huasheng_{name}.png')
                print(f"  ✓ {len(all_apis)} requests")
                
                # 提取新链接
                new_links = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                        .filter(h => h.includes('huasheng.cn'))
                        .filter((v,i,a) => a.indexOf(v) === i);
                }''')
                if new_links:
                    print(f"  链接: {len(new_links)}")
                    for l in new_links[:5]:
                        print(f"    {l[:70]}")
            except Exception as e:
                print(f"  ✗ {str(e)[:50]}")
        
        # 点击"创建"按钮看看
        print("\n=== 尝试点击创建按钮 ===")
        try:
            page.goto('https://www.huasheng.cn/', wait_until='domcontentloaded', timeout=15000)
            time.sleep(2)
            create_btn = page.locator('button:has-text("创建")').first
            if create_btn.is_visible():
                create_btn.click(timeout=5000)
                time.sleep(3)
                page.screenshot(path='/root/huasheng_after_create.png')
                print(f"  点击创建后请求数: {len(all_apis)}")
                # 获取当前URL
                print(f"  当前URL: {page.url}")
        except Exception as e:
            print(f"  点击失败: {e}")
        
        # 从HTML中提取所有API
        print("\n=== HTML中的API端点 ===")
        html = page.content()
        with open('/root/huasheng_deep.html', 'w') as f:
            f.write(html)
        
        js_apis = page.evaluate('''() => {
            const found = [];
            document.querySelectorAll('script:not([src])').forEach(s => {
                const t = s.textContent;
                // huasheng.cn API
                (t.match(/["'](https?:\/\/[^"']*(?:huasheng|hdslb|bilibili)[^"']*(?:api|service|interface)[^"']*)["']/gi) || []).forEach(m => found.push(m));
                (t.match(/["'](\/api\/[^"']{2,100})["']/g) || []).forEach(m => found.push(m));
                (t.match(/["'](\/x\/[^"']{2,100})["']/g) || []).forEach(m => found.push(m));
            });
            return [...new Set(found)];
        }''')
        for j in js_apis:
            print(f"  {j}")
        
        browser.close()
    return all_apis

if __name__ == '__main__':
    print(f"开始深度抓取 huasheng.cn ... {datetime.now()}")
    apis = capture()
    
    with open('/root/huasheng_deep_apis.json', 'w', encoding='utf-8') as f:
        json.dump(apis, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n抓取完成! 共 {len(apis)} 个请求")
    by_domain = {}
    for a in apis:
        d = a['domain']
        by_domain[d] = by_domain.get(d, 0) + 1
    for d, c in sorted(by_domain.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
