"""
藏剑阁·网络工具 V1.0
网页抓取·连接检查·纯标准库 urllib
"""
import urllib.request
import urllib.error
import re
import socket
import ssl
import webbrowser

def zhuawang_ye(canshu):
    """抓取网页内容·智能解析·参数:URL字符串"""
    url = str(canshu).strip().strip('"').strip("'")
    if not url.startswith("http"):
        url = "https://" + url
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            
            # 1. 提取标题
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE|re.DOTALL)
            title = title_match.group(1).strip() if title_match else "(无标题)"
            
            # 2. 提取meta描述
            desc = ""
            dm = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if not dm:
                dm = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html, re.IGNORECASE)
            if dm: desc = dm.group(1)[:300]
            
            # 3. 提取正文 (优先 main/article, 否则最大文本块)
            body = html
            for tag in ['script','style','nav','footer','header','noscript','iframe','svg']:
                body = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', body, flags=re.DOTALL|re.IGNORECASE)
            
            # 尝试找 main/article
            main = ""
            for tag in ['main','article','div[class*="content"]','div[id*="content"]',
                       'div[class*="main"]','div[id*="main"]','div[class*="post"]']:
                tag_end = tag.split("[")[0]
                m = re.search(r'<' + tag + r'[^>]*>(.*?)</' + tag_end + r'>', body, re.DOTALL|re.IGNORECASE)
                if m:
                    candidate = m.group(1)
                    if len(candidate) > len(main): main = candidate
            
            if not main:
                main = body  # fallback to whole body
            
            # 去标签
            text = re.sub(r'<[^>]+>', '\n', main)
            # 合并空白
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            # 过滤页脚垃圾
            filtered = []
            boilerplate = ['cookie','copyright','©','ICP','公网安备','版权所有','隐私政策','用户协议',
                          'English','加入我们','岗位详情','获取 App','服务状态','法务']
            for l in lines:
                if any(b in l for b in boilerplate): continue
                if len(l) < 2: continue
                if l in filtered[-2:]: continue  # 去相邻重复
                filtered.append(l)
            text = '\n'.join(filtered[:40])  # 最多40行
            
            # 4. 提取关键链接
            links = []
            for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', html, re.IGNORECASE):
                href, label = m.group(1), m.group(2).strip()
                if label and not any(b in label for b in boilerplate):
                    if href.startswith('/'): href = url.rstrip('/') + href
                    if len(links) < 8 and len(label) < 80:
                        links.append(f"  [{label}]({href})")
            
            # 5. 组装输出
            parts = [f"【{title}】"]
            if desc: parts.append(f"\n简介: {desc}")
            if links: parts.append(f"\n链接:\n" + "\n".join(links))
            parts.append(f"\n内容:\n{text}")
            
            return {
                "success": True,
                "output": "\n".join(parts)[:2000],
                "data": {"title": title, "url": url, "desc": desc, "links": links}
            }
    except urllib.error.URLError as e:
        return {"success": False, "error": f"网络错误: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

def jiancha_lianjie(canshu=""):
    """检查网络连通性·参数:域名(默认baidu.com)"""
    host = str(canshu).strip().strip('"').strip("'") if canshu else "baidu.com"
    host = host.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        socket.create_connection((host, 443), timeout=5)
        return {"success": True, "output": f"已连通 {host}:443"}
    except Exception as e:
        return {"success": False, "error": f"无法连接 {host}: {e}"}

def tiqiu_wenben(canshu):
    """提取网页纯文本·参数:URL"""
    r = zhuawang_ye(canshu)
    if r.get("success"):
        return r
    return r

def diaoyong_api(canshu):
    """调用API·参数:JSON{url,method,headers,body}"""
    import json
    s = str(canshu).strip()
    try:
        d = json.loads(s) if s.startswith("{") else {"url": s, "method": "GET"}
    except:
        return {"success": False, "error": "参数格式错误"}
    url = d.get("url", "")
    method = d.get("method", "GET").upper()
    headers = d.get("headers", {})
    body = d.get("body", "").encode() if d.get("body") else None
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = resp.read().decode('utf-8', errors='replace')
            return {"success": True, "output": data[:2000], "data": {"status": resp.status}}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

def dakai_liulanqi(canshu):
    """在默认浏览器中打开URL·参数:URL字符串"""
    url = str(canshu).strip().strip('"').strip("'")
    if not url.startswith("http"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return {"success": True, "output": f"已在浏览器中打开 {url}"}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}

def neihua_gongju(canshu):
    """内化外部Python工具·抓取→LLM改写→铸剑炉部署·参数:URL"""
    url = str(canshu).strip().strip('"').strip("'")
    if not url.startswith("http"):
        url = "https://" + url
    
    # 阶段1: 抓取外部代码
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            waibu_daima = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return {"success": False, "error": f"抓取失败: {e}"}
    
    if len(waibu_daima) < 50:
        return {"success": False, "error": f"代码太短({len(waibu_daima)}字),疑似非源码"}
    
    # 阶段2: 构造铸剑炉改写需求
    from pathlib import Path
    import re
    # 提取文件名
    name_match = re.search(r'/([^/]+\.py)', url)
    wenjianming = name_match.group(1) if name_match else "neihua_gongju.py"
    mubiao_lujing = str(Path(__file__).parent / wenjianming)
    
    xuqiu = f"""将以下外部Python代码改写为星巢藏剑阁兵器。铁律：
1. 所有函数名/变量名用拼音,禁止英文命名
2. 零外部依赖,只用Python标准库
3. 每个函数返回标准字典: {{"success": bool, "output": str, "error": str}}
4. 文件头加文档字符串描述功能
5. 保持原有功能逻辑不变

外部代码:
{waibu_daima[:3000]}"""
    
    # 阶段3: 调用铸剑炉全流水线
    try:
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        jieguo = s.zhujianlu.quanliushuixian(xuqiu, mubiao_lujing)
        if jieguo.get("success"):
            return {"success": True, "output": f"已内化 → {mubiao_lujing}", "data": {"lujing": mubiao_lujing}}
        else:
            return {"success": False, "error": f"铸剑炉内化失败: {jieguo.get('error','')[:200]}"}
    except Exception as e:
        return {"success": False, "error": f"铸剑炉调用失败: {e}"}
