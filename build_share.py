"""Build a self-contained share.html for WorkBuddy sharing."""
import os

BASE = r"F:\Work\2026-05-24-10-39-23\dashboard"

# Read dashboard.html
with open(os.path.join(BASE, "dashboard.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Read data.js
with open(os.path.join(BASE, "data.js"), "r", encoding="utf-8") as f:
    data_js = f.read()

# 1. Replace echarts local + fallback with single CDN (bootcdn = China-friendly)
old_echarts = '''<script src="lib/echarts.min.js"></script>
<script>if(typeof echarts==='undefined'){document.write('<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"><\\/script>');}</script>'''
new_echarts = '''<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
<script>if(typeof echarts==='undefined'){document.write('<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"><\\/script>');}</script>'''
html = html.replace(old_echarts, new_echarts)

# 2. Replace external data.js with inline script
old_data = '<script src="data.js"></script>'
new_data = f'<script>\n{data_js}\n</script>'
html = html.replace(old_data, new_data)

# Write share.html
share_path = os.path.join(BASE, "share.html")
with open(share_path, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = round(os.path.getsize(share_path) / 1024, 1)
print(f"Done: {share_path} ({size_kb} KB)")
