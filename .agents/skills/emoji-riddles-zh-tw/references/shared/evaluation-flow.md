# 中文 Emoji 表意設計 Benchmark Flow

這份文件定義 emoji 類 skill 的 benchmark 流程，目標是量測：

1. **generators** 用了 skill 之後，能不能穩定把指定 target 轉成夠好的 emoji 設計
2. **solvers** 能不能從 emoji 還原 target，而且理由對得上
3. 不同 model tiers 的表現是否符合該 skill 自己的目標

## 核心概念

這個 benchmark 不是單看「有沒有讀到 skill」，而是看三件事：

1. **設計品質**
2. **可解性**
3. **tier fit**

其中第 3 點不是固定要求 separation，而是看：

- 如果 skill 是 plain 版，mini-tier 也應該常能理解
- 如果 skill 是 witty 版，則應允許 full-tier 與 mini-tier 拉開差距

換句話說，請以各 skill 自己的 `target-metrics.md` 為最終標準。

## Roles

### generator agent

負責依照目標 skill，將指定 target 轉成 4 個 emoji。

### solver agent

負責根據 emoji 反推 target，並提供理由。

### judge agent

負責依照 scoring rubric 對 solver 結果打分。

## Model tiers

### Full / general tier

- Copilot: `gpt-5.4` + `--effort high`
- Codex: `gpt-5.4`
- Gemini: `gemini-3.1-pro-preview`

### Mini tier

- Copilot: `gpt-5.4-mini`
- Codex: `gpt-5.4-mini`
- Gemini: `gemini-3-flash-preview`

## Suggested benchmark matrix

### Stage 1: generator quality

每個 full-tier generator agent 各針對同一個 target 產出 1 組 emoji：

- Copilot full
- Codex full
- Gemini full

先檢查：

- 格式是否正確
- 是否真的是 4 個 emoji
- 設計是否有層次
- target 揭曉後是否合理

### Stage 2: solver performance

對每一組生成結果，交給以下 solver 嘗試還原 target：

- Copilot full
- Codex full
- Gemini full
- Copilot mini
- Codex mini
- Gemini mini

### Stage 3: judge scoring

每個 solver 結果都交給 judge agent 依 rubric 打分。

至少記錄：

- 答案正確度
- 理由對齊度
- 理由品質
- 難點辨識
- 總分

## Recommended scenarios

至少跑三種 target 類型：

1. 旅遊
2. 食物 / 飲料
3. 影視 / 角色 / 流行文化

## Output format for automation

如果要做 benchmark 自動化，建議 generator 與 solver 改用 **JSON only** 輸出，方便後處理。

### Generator JSON example

```json
{
  "target": "大阪旅遊",
  "emoji": "😆 🏃 🐙 🌉",
  "rationale": {
    "😆": "大阪的綜藝感與城市氣質",
    "🏃": "道頓堀跑跑人印象",
    "🐙": "章魚燒",
    "🌉": "橋邊夜逛畫面"
  }
}
```

### Solver JSON example

```json
{
  "guess": "大阪旅遊",
  "confidence": 88,
  "reasoning": {
    "😆": "聯想到大阪的搞笑文化",
    "🏃": "想到道頓堀跑跑人",
    "🐙": "章魚燒",
    "🌉": "橋邊和河岸夜景"
  },
  "alternatives": ["大阪", "道頓堀"]
}
```

## What counts as success

一組 emoji 設計要算成功，不只要 full-tier 猜得出來，還要符合：

1. 至少多數 solver 結果能維持高可解性
2. generator 的設計理由與 solver 的理解大致對得上
3. full-tier / mini-tier 的表現差距要符合該 skill 的 target metrics

## Failure diagnosis

如果 full-tier 也解不出：

- 設計太飄
- skill 規則太抽象
- 線索不夠收斂

如果 mini-tier 也輕鬆解出：

- 對 witty skill：可能代表設計太直白、線索太 obvious
- 對 plain skill：這不一定是問題，先回頭看該 skill 的 target metrics

## Iteration loop

1. 跑 benchmark
2. 找出不符合 target metrics 的題目
3. 回頭修：
   - skill description
   - emoji 設計原則
   - 線索分配
   - 評語要求
4. 再跑一次
