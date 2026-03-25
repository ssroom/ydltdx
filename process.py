import json, csv, datetime, os, shutil, sys

with open('data/latest.json') as f:
    raw = f.read()

print("Raw response (first 500 chars):", raw[:500])

try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    sys.exit(1)

print("Top-level keys:", list(data.keys()) if isinstance(data, dict) else type(data))

info = data.get('info', [])
print(f"info length: {len(info)}")
if info:
    print("First item type:", type(info[0]))
    print("First item:", info[0])

if not info:
    print("No IP data found, skipping.")
    sys.exit(0)

if isinstance(info[0], str):
    print("ERROR: info items are strings. Full structure:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    sys.exit(1)

now = datetime.datetime.now(datetime.timezone.utc)
timestamp = now.strftime('%Y%m%d_%H%M%S')

os.makedirs('data/history', exist_ok=True)
shutil.copy('data/latest.json', f'data/history/{timestamp}.json')

ips = [item['ip'] for item in info if item.get('ip')]
with open('data/ip_list.txt', 'w') as f:
    f.write('\n'.join(ips))

with open('data/latest.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['ip','delay','speed','loss','type','colo'])
    writer.writeheader()
    for item in info:
        writer.writerow({
            'ip':    item.get('ip',''),
            'delay': item.get('delay',''),
            'speed': item.get('speed',''),
            'loss':  item.get('loss',''),
            'type':  item.get('type',''),
            'colo':  item.get('colo', item.get('region','')),
        })

delays = [float(i['delay']) for i in info if i.get('delay')]
speeds = [float(i['speed']) for i in info if i.get('speed') and float(i.get('speed',0)) > 0]
avg_delay = round(sum(delays)/len(delays), 1) if delays else 0
avg_speed = round(sum(speeds)/len(speeds), 2) if speeds else 0
now_str = now.strftime('%Y-%m-%d %H:%M:%S UTC')
repo = os.environ.get('GITHUB_REPOSITORY', '')

readme = f"""# Cloudflare IP 自動抓取

數據來源：[wetest.vip](https://www.wetest.vip/page/cloudflare/address_v4.html)
每 15 分鐘自動更新（GitHub Actions）

## 最新數據

| 項目 | 數值 |
|------|------|
| 更新時間 | {now_str} |
| IP 總數 | {len(info)} |
| 平均延遲 | {avg_delay} ms |
| 平均速度 | {avg_speed} MB/s |

## 文件說明

| 文件 | 說明 |
|------|------|
| `data/latest.json` | 完整 JSON |
| `data/latest.csv` | CSV，可用 Excel 打開篩選 |
| `data/ip_list.txt` | 純 IP 列表，每行一個 |
| `data/history/` | 歷史快照（保留最近 200 次）|

## 直接獲取

\`\`\`
https://raw.githubusercontent.com/{repo}/main/data/ip_list.txt
https://raw.githubusercontent.com/{repo}/main/data/latest.json
https://raw.githubusercontent.com/{repo}/main/data/latest.csv
\`\`\`
"""

with open('README.md', 'w') as f:
    f.write(readme)

print(f"Done: {len(info)} IPs, avg {avg_delay}ms, {avg_speed}MB/s")
