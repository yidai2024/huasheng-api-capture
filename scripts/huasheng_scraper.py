#!/usr/bin/env python3
"""huasheng.cn API 抓取脚本"""

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
                'timestamp': datetime.now().isoformat(),
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

        # 首页
        print("=== 首页 ===")
        page.goto('https://www.huasheng.cn/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)
        page.screenshot(path='/root/huasheng_home.png', full_page=False)
        print(f"  请求数: {len(all_apis)}")
        
        # 提取链接
        links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                href: a.href, text: a.textContent.trim().substring(0,60)
            })).filter(l => l.href.includes('huasheng.cn')).filter((v,i,a) => a.findIndex(x=>x.href===v.href)===i);
        }''')
        print(f"  链接数: {len(links)}")
        for l in links[:30]:
            print(f"    {l['href'][:80]}  |  {l['text'][:30]}")
        
        # 滚动
        for i in range(8):
            page.evaluate('window.scrollBy(0, 800)')
            time.sleep(1)
        page.screenshot(path='/root/huasheng_scrolled.png', full_page=True)
        print(f"  滚动后请求数: {len(all_apis)}")
        
        # 点击所有导航/按钮
        print("\n=== 按钮/导航 ===")
        btns = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button, [role="button"], nav a, .nav a, header a'))
                .map(b => ({tag: b.tagName, text: b.textContent.trim().substring(0,60), href: b.href||''}))
                .filter(b => b.text.length > 0);
        }''')
        print(f"  按钮数: {len(btns)}")
        for b in btns[:20]:
            print(f"    [{b['tag']}] {b['text'][:40]}  →  {b['href'][:50]}")
        
        # 依次访问发现的链接
        print("\n=== 访问子页面 ===")
        visited = {'https://www.huasheng.cn/'}
        for l in links[:25]:
            href = l['href']
            if href not in visited and 'huasheng.cn' in href and '#' not in href.split('/')[-1]:
                visited.add(href)
                try:
                    page.goto(href, wait_until='domcontentloaded', timeout=15000)
                    time.sleep(3)
                    for _ in range(3):
                        page.evaluate('window.scrollBy(0, 600)')
                        time.sleep(0.8)
                    name = urlparse(href).path.replace('/','_') or 'root'
                    page.screenshot(path=f'/root/huasheng_{name[:20]}.png')
                    print(f"  ✓ {href[:60]} ({len(all_apis)} requests)")
                except Exception as e:
                    print(f"  ✗ {href[:60]} - {str(e)[:40]}")
        
        # 从JS中提取API端点
        print("\n=== JS中的API端点 ===")
        js_endpoints = page.evaluate('''() => {
            const found = [];
            document.querySelectorAll('script:not([src])').forEach(s => {
                const t = s.textContent;
                // /api/ 路径
                (t.match(/["'](\\/api\\/[^"']{2,100})["']/g) || []).forEach(m => found.push('api: ' + m));
                // fetch/axios
                (t.match(/fetch\s*\(\s*["']([^"']+)["']/g) || []).forEach(m => found.push('fetch: ' + m));
                (t.match(/\.get\s*\(\s*["']([^"']+)["']/g) || []).forEach(m => found.push('get: ' + m));
                (t.match(/\.post\s*\(\s*["']([^"']+)["']/g) || []).forEach(m => found.push('post: ' + m));
                // 域名API
                (t.match(/["'](https?:\/\/[^"']*(?:api|service|gateway|backend)[^"']*)["']/gi) || []).forEach(m => found.push('url: ' + m));
            });
            // script src
            document.querySelectorAll('script[src]').forEach(s => {
                if (s.src.includes('chunk') || s.src.includes('app') || s.src.includes('main') || s.src.includes('bundle'))
                    found.push('script: ' + s.src);
            });
            // global vars
            if (window.__INITIAL_STATE__) found.push('global: __INITIAL_STATE__');
            if (window.__NEXT_DATA__) found.push('global: __NEXT_DATA__');
            if (window.__NUXT__) found.push('global: __NUXT__');
            if (window.pageData) found.push('global: pageData');
            return found;
        }''')
        for j in js_endpoints:
            print(f"  {j}")
        
        # 保存HTML
        html = page.content()
        with open('/root/huasheng_home.html', 'w') as f:
            f.write(html)
        print(f"\n  HTML已保存: {len(html)} bytes")
        
        browser.close()
    return all_apis

if __name__ == '__main__':
    print(f"开始抓取 huasheng.cn ... {datetime.now()}")
    apis = capture()
    
    with open('/root/huasheng_raw_apis.json', 'w', encoding='utf-8') as f:
        json.dump(apis, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n抓取完成! 共 {len(apis)} 个请求")
    by_domain = {}
    for a in apis:
        d = a['domain']
        by_domain[d] = by_domain.get(d, 0) + 1
    for d, c in sorted(by_domain.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
