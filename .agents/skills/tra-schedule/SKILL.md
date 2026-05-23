---
name: tra-schedule
description: Use when the user asks about Taiwan Railway (台鐵) train schedules, departure times, or arrival times between two stations. Handles Chinese station names, date parsing, and time-range filtering. Uses official TRA website via Playwright for accurate results.
---

# TRA Schedule Query Skill

## Purpose

Query Taiwan Railway (台鐵) official schedules between two stations using a headless browser. Returns accurate results including all train types (自強/莒光/區間快/區間), remarks (週末停駛, 親子車廂), and route (山線/海線).

## When to use

Activate when the user asks:
- 幾點的車 / 班次 / 幾點到
- Train times between any two 台鐵 stations
- Departure or arrival schedule queries
- Comparing train options for a specific day/time

## Workflow

### ⚠️ IMPORTANT: Always execute the script first

Before doing anything else, run the query script to get live data from the official TRA website.
Do NOT answer from training knowledge — train schedules change frequently and training data will be wrong.

### 1. Parse the request

Extract from user's message:
| Field | Example | Default |
|---|---|---|
| `from` | 員林、台中、高雄 | required |
| `to` | 台北、板橋 | required |
| `date` | 下週三、2026/05/27 | today |
| `startTime` | 15:00 | 00:00 |
| `endTime` | 20:00 | 23:30 |
| `trainType` | 自強 (optional) | ALL |

Convert natural date expressions to `YYYY/MM/DD`:
- 下週三 → compute from current datetime
- 明天 → tomorrow's date
- 週六 → next Saturday

### 2. Run the query script

```bash
node /home/node/.copilot/skills/tra-schedule/scripts/query_tra.js \
  --from "員林" \
  --to "台北" \
  --date "2026/05/27" \
  --startTime "15:00" \
  --endTime "20:00"
```

The script outputs JSON to stdout.

### 3. Format and present results

Present as a markdown table with columns:
- 車種、車次、出發、抵達、行駛時間、經由、備註

Always include:
- Ticket price (全票 $NNN)
- Any special remarks (週末停駛、親子車廂 etc.)
- Data source note: 「資料來源：台鐵官網」

### 4. Handle errors

| Error | Action |
|---|---|
| Playwright not installed | Run `cd /tmp && npm install playwright && npx playwright install chromium` |
| No trains found | Tell user and suggest widening time range |
| Station name not found | Suggest correct station name |

## Constraints

- Always use official TRA website (`tip.railway.gov.tw`) — not timetables.tw (incomplete)
- Playwright headless Chrome is required; curl/fetch won't work (JS-rendered site)
- Script caches nothing; always fetches live data
- TRA autocomplete requires typing + ArrowDown + Enter (not direct value injection)
- **MUST execute the script to get live data — do NOT use training knowledge or cached data for schedules**

## Expected output

```
## 員林 → 台北（2026/05/27，15:00–20:00）

| 車種 | 車次 | 出發 | 抵達 | 行駛時間 | 經由 | 備註 |
|------|------|------|------|---------|------|------|
| 自強 | 128 | 15:36 | 18:25 | 2h49m | 山線 | — |
| 自強 | 134 | 16:46 | 19:41 | 2h55m | 山線 | — |
| 自強 | 138 | 17:41 | 20:30 | 2h49m | 山線 | 第12車親子車廂 |
| 自強 | 142 | 18:24 | 21:10 | 2h46m | 山線 | — |

全票 $591 ｜ 資料來源：台鐵官網
```
