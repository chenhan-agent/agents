# 中文 Emoji 表意設計 Benchmark Flow

這份文件定義 `emoji-riddles-zh-tw` 的 benchmark 流程，目標是量測：

1. **general / full-tier generators** 用了 skill 之後，能不能穩定把指定 target 轉成夠好的 emoji 設計
2. **general / full-tier solvers** 能不能從 emoji 還原 target，而且理由對得上
3. **mini-tier solvers** 是否明顯比較難解出

## 核心概念

這個 benchmark 不是單看「有沒有讀到 skill」，而是看三件事：

1. **設計品質**
2. **可解性**
3. **tier separation**

其中最重要的是 **tier separation**：

- full-tier 要有高成功率
- mini-tier 要有明顯較低成功率

## Roles

### generator agent

負責依照 `emoji-riddles-zh-tw` skill，將指定 target 轉成 4 個 emoji。

### solver agent

負責根據 emoji 反推 target，並提供理由。

### judge agent

負責依照 `references/shared/scoring-rubric.md` 對 solver 結果打分。

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
- 是否不直白

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
  "target": "刈包（虎咬豬）",
  "emoji": "🐯 🐷 🥜 🌿",
  "rationale": {
    "🐯": "虎咬豬俗稱",
    "🐷": "豬五花內餡",
    "🥜": "花生粉",
    "🌿": "香菜"
  },
  "difficulty_note": "full-tier 較容易透過俗稱與配料聯想解出，mini-tier 較容易停在食材層次。"
}
```

### Solver JSON example

```json
{
  "guess": "刈包（虎咬豬）",
  "confidence": 95,
  "reasoning": {
    "🐯": "虎咬豬俗稱",
    "🐷": "豬五花",
    "🥜": "花生粉",
    "🌿": "香菜"
  },
  "alternatives": []
}
```

## What counts as success

一組 emoji 設計要算成功，不只要 full-tier 猜得出來，還要符合：

1. 至少多數 full-tier solvers 得分高
2. mini-tier 平均分明顯較低
3. mini-tier 就算偶爾猜中，也不能在理由對齊度上拿高分

## Failure diagnosis

如果 full-tier 也解不出：

- 設計太飄
- skill 規則太抽象
- 線索不夠收斂

如果 mini-tier 也輕鬆解出：

- 設計太直白
- 線索太 obvious
- skill 沒有成功要求側面聯想或轉折

## Iteration loop

1. 跑 benchmark
2. 找出 low separation 題目
3. 回頭修：
   - skill description
   - emoji 設計原則
   - 禁用過直白線索
   - 難度評語要求
4. 再跑一次
