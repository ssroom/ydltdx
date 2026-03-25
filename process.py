import json, csv, datetime, os, shutil, sys

with open('data/latest.json') as f:
    data = json.load(f)

info = data.get('info', {})
now = datetime.datetime.now(datetime.timezone.utc)
timestamp = now.strftime('%Y%m%d_%H%M%S')
now_str = now.strftime('%Y-%m-%d %H:%M:%S UTC')
repo = os.environ.get('GITHUB_REPOSITORY', '')

os.makedirs('data/history', exist_ok=True)
shutil.copy('data/latest.json', f'data/history/{timestamp}.json')

# 解析本次數據
current = []
for line_key, items in info.items():
    for item in items:
        current.append({
            'ip':       item.get('ip', ''),
            'delay':    item.get('rtt_avg', ''),
            'speed':    item.get('speed', ''),
            'loss':     item.get('loss_rate', ''),
            'type':     item.get('line_name', line_key),
            'colo':     item.get('colo', ''),
            'bandwidth':item.get('bandwidth', ''),
            'updated':  timestamp,
        })

# 讀取已累積的 IP 庫（去重合併）
all_file = 'data/all_ips.json'
if os.path.exists(all_file):
    with open(all_file) as f:
        accumulated = json.load(f)
else:
    accumulated = {}

# 以 IP 為 key，更新或新增
for item in current:
    ip = item['ip']
    if ip:
        accumulated[ip] = item  # 有新數據就覆蓋（保持最新測速結果）

# 保存累積庫
with open(all_file, 'w') as f:
    json.dump(accumulated, f, ensure_ascii=False)

all_ips = list(accumulated.values())
all_ips.sort(key=lambda x: float(x['delay']) if x['delay'] != '' else 9999)

print(f"本次新增/更新: {len(current)} 個，累積總計: {len(all_ips)} 個")

# 純 IP 列表
with open('data/ip_list.txt', 'w') as f:
    f.write('\n'.join(d['ip'] for d in all_ips if d['ip']))

# CSV（按延遲排序，加上表頭說明）
fields = ['ip', 'delay', 'speed', 'loss', 'type', 'colo', 'bandwidth', 'updated']
headers = {'ip':'IP地址', 'delay':'延遲(ms)', 'speed':'速度(KB/s)', 'loss':'丟包率', 'type':'線路', 'colo':'節點', 'bandwidth':'帶寬(Mbps)', 'updated':'更新時間'}

with open('data/latest.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writerow(headers)
    writer.writerows(all_ips)

# 本次快照 CSV
with open('data/current.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writerow(headers)
    writer.writerows(sorted(current, key=lambda x: float(x['delay']) if x['delay'] != '' else 9999))

# 統計
delays = [float(d['delay']) for d in all_ips if d['delay'] != '']
speeds = [float(d['speed']) for d in all_ips if d['speed'] != '' and float(d['speed']) > 0]
avg_delay = round(sum(delays)/len(delays), 1) if delays else 0
avg_speed = round(sum(speeds)/len(speeds), 2) if speeds else 0

# 各線路統計
by_type = {}
for d in all_ips:
    t = d['type']
    by_type.setdefault(t, []).append(d)

type_table = "\n".join(
    f"| {t} | {len(ips)} | {round(sum(float(i['delay']) for i in ips if i['delay'] != '')/len(ips),1)} ms |"
    for t, ips in sorted(by_type.items())
)

readme = (
    "# Cloudflare IP 自動抓取\n\n"
    "數據來源：[wetest.vip](https://www.wetest.vip/page/cloudflare/address_v4.html)  \n"
    "每 15 分鐘自動更新，**累積去重存儲**，越跑越多\n\n"
    "## 最新統計\n\n"
    f"**更新時間**：{now_str}  \n"
    f"**本次獲取**：{len(current)} 個  \n"
    f"**累積總計**：{len(all_ips)} 個（去重）  \n"
    f"**平均延遲**：{avg_delay} ms  \n"
    f"**平均速度**：{avg_speed} KB/s  \n\n"
    "## 各線路統計\n\n"
    "| 線路 | IP 數 | 平均延遲 |\n"
    "|------|-------|----------|\n"
    f"{type_table}\n\n"
    "## 文件說明\n\n"
    "| 文件 | 說明 |\n"
    "|------|------|\n"
    "| `data/latest.csv` | **所有累積 IP**，按延遲排序，Excel 打開直接篩選 |\n"
    "| `data/current.csv` | 本次獲取的 20 個 IP |\n"
    "| `data/ip_list.txt` | 純 IP 列表，每行一個 |\n"
    "| `data/all_ips.json` | 累積 IP 完整數據（JSON）|\n"
    "| `data/history/` | 每次原始 JSON 快照 |\n\n"
    "## 直接獲取\n\n"
    f"- 累積 IP 列表：`https://raw.githubusercontent.com/{repo}/main/data/ip_list.txt`\n"
    f"- 累積 CSV：`https://raw.githubusercontent.com/{repo}/main/data/latest.csv`\n"
    f"- 本次 CSV：`https://raw.githubusercontent.com/{repo}/main/data/current.csv`\n"
)

with open('README.md', 'w') as f:
    f.write(readme)

print(f"Done: 累積 {len(all_ips)} 個 IP，avg {avg_delay}ms，{avg_speed}KB/s")
