import json, csv, datetime, os, shutil, sys

with open('data/latest.json') as f:
    data = json.load(f)

info = data.get('info', {})
print("Lines found:", list(info.keys()))

all_ips = []
for line_key, items in info.items():
    for item in items:
        all_ips.append({
            'ip':    item.get('ip', ''),
            'delay': item.get('rtt_avg', ''),
            'speed': item.get('speed', ''),
            'loss':  item.get('loss_rate', ''),
            'type':  item.get('line_name', line_key),
            'colo':  item.get('colo', ''),
        })

print(f"Total IPs: {len(all_ips)}")
if all_ips:
    print("Sample:", all_ips[0])

if not all_ips:
    print("No IPs found, skipping.")
    sys.exit(0)

now = datetime.datetime.now(datetime.timezone.utc)
timestamp = now.strftime('%Y%m%d_%H%M%S')

os.makedirs('data/history', exist_ok=True)
shutil.copy('data/latest.json', f'data/history/{timestamp}.json')

with open('data/ip_list.txt', 'w') as f:
    f.write('\n'.join(d['ip'] for d in all_ips if d['ip']))

with open('data/latest.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['ip','delay','speed','loss','type','colo'])
    writer.writeheader()
    writer.writerows(all_ips)

delays = [float(d['delay']) for d in all_ips if d['delay'] != '']
speeds = [float(d['speed']) for d in all_ips if d['speed'] != '' and float(d['speed']) > 0]
avg_delay = round(sum(delays)/len(delays), 1) if delays else 0
avg_speed = round(sum(speeds)/len(speeds), 2) if speeds else 0
now_str = now.strftime('%Y-%m-%d %H:%M:%S UTC')
repo = os.environ.get('GITHUB_REPOSITORY', '')

readme = (
    "# Cloudflare IP 自動抓取\n\n"
    "數據來源：[wetest.vip](https://www.wetest.vip/page/cloudflare/address_v4.html)\n"
    "每 15 分鐘自動更新（GitHub Actions）\n\n"
    "## 最新數據\n\n"
    "| 項目 | 數值 |\n"
    "|------|------|\n"
    f"| 更新時間 | {now_str} |\n"
    f"| IP 總數 | {len(all_ips)} |\n"
    f"| 線路 | {', '.join(info.keys())} |\n"
    f"| 平均延遲 | {avg_delay} ms |\n"
    f"| 平均速度 | {avg_speed} MB/s |\n\n"
    "## 文件說明\n\n"
    "| 文件 | 說明 |\n"
    "|------|------|\n"
    "| `data/latest.json` | 完整 JSON |\n"
    "| `data/latest.csv` | CSV，可用 Excel 打開篩選 |\n"
    "| `data/ip_list.txt` | 純 IP 列表，每行一個 |\n"
    "| `data/history/` | 歷史快照（保留最近 200 次）|\n\n"
    "## 直接獲取\n\n"
    f"- IP 列表：`https://raw.githubusercontent.com/{repo}/main/data/ip_list.txt`\n"
    f"- 完整 JSON：`https://raw.githubusercontent.com/{repo}/main/data/latest.json`\n"
    f"- CSV：`https://raw.githubusercontent.com/{repo}/main/data/latest.csv`\n"
)

with open('README.md', 'w') as f:
    f.write(readme)

print(f"Done: {len(all_ips)} IPs, avg {avg_delay}ms, {avg_speed}MB/s")
