# Cloudflare IP 自動抓取

數據來源：[wetest.vip](https://www.wetest.vip/page/cloudflare/address_v4.html)  
每 15 分鐘自動更新，**累積去重存儲**，越跑越多

## 最新統計

**更新時間**：2026-04-17 23:44:52 UTC  
**本次獲取**：20 個  
**累積總計**：6086 個（去重）  
**平均延遲**：103.4 ms  
**平均速度**：638.5 KB/s  

## 各線路統計

| 線路 | IP 數 | 平均延遲 |
|------|-------|----------|
| 三网 | 1446 | 89.1 ms |
| 电信 | 1540 | 83.1 ms |
| 移动 | 1607 | 77.2 ms |
| 联通 | 1493 | 166.4 ms |

## 文件說明

| 文件 | 說明 |
|------|------|
| `data/latest.csv` | **所有累積 IP**，按延遲排序，Excel 打開直接篩選 |
| `data/current.csv` | 本次獲取的 20 個 IP |
| `data/ip_list.txt` | 純 IP 列表，每行一個 |
| `data/all_ips.json` | 累積 IP 完整數據（JSON）|
| `data/history/` | 每次原始 JSON 快照 |

## 直接獲取

- 累積 IP 列表：`https://raw.githubusercontent.com/ssroom/ydltdx/main/data/ip_list.txt`
- 累積 CSV：`https://raw.githubusercontent.com/ssroom/ydltdx/main/data/latest.csv`
- 本次 CSV：`https://raw.githubusercontent.com/ssroom/ydltdx/main/data/current.csv`
