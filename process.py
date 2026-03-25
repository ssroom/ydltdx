import json, csv, datetime, os, shutil

with open('data/latest.json') as f:
    data = json.load(f)

info = data.get('info', [])
now = datetime.datetime.utcnow()
timestamp = now.strftime('%Y%m%d_%H%M%S')

shutil.copy('data/latest.json', f'data/history/{timestamp}.json')

ips = [item['ip'] for item in info if item.get('ip')]
with open('data/ip_list.txt', 'w') as f:
    f.write('\n'.join(ips))

with open('data/latest.csv', 'w', newline='') as f:
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
| `data/latest.csv` | CSV，可用 Excel 篩選 |
| `data/ip_list.txt` | 純 IP 列表，每行一個 |
| `data/history/` | 歷史快照（保留最近 200 次）|

## 直接獲取

```
https://raw.githubusercontent.com/{repo}/main/data/ip_list.txt
https://raw.githubusercontent.com/{repo}/main/data/latest.json
https://raw.githubusercontent.com/{repo}/main/data/latest.csv
```
"""

with open('README.md', 'w') as f:
    f.write(readme)

print(f"OK: {len(info)} IPs, avg {avg_delay}ms, {avg_speed}MB/s")
