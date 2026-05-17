# 中文 Emoji 表意設計測資

這份測資用來驗證 `emoji-riddles-zh-tw` 是否真的影響 agent 行為，而不是只被看見。

這裡的測試流程分成三個角色：

1. **generator agent**：根據 skill 產出 emoji 設計
2. **solver agent**：看到 emoji 後還原 target 並說明理由
3. **judge agent**：根據 `references/shared/scoring-rubric.md` 打分

## 共用輸出規格

所有測試都要求：

1. 使用 **繁體中文**
2. 每題 **剛好 4 個 emoji**
3. 輸出格式固定為：
   - `target`
   - `emoji`
   - `解析`
   - `可讀性評語`
4. 不要直接拆 target 字面
5. 不要用國旗、地圖輪廓、或一眼秒懂的直給提示

rubric 請看 `references/shared/scoring-rubric.md`。

## Generator output contract

generator agent 應產出：

1. `target`
2. `emoji`
3. `解析`
4. `可讀性評語`

其中：

- `emoji` 必須是 4 個 emoji
- `解析` 要說明每個 emoji 為什麼能連到 target
- `可讀性評語` 要交代這組為什麼自然、好懂、但又不至於太乾

## Solver output contract

solver agent 應產出：

1. `猜測答案`
2. `信心`
3. `解題理由`
4. `可能的備選答案`

其中：

- `解題理由` 不能只說直覺，要對到每個 emoji 的推理
- 如果有不確定，也要指出卡點

## 測資 1：旅遊類 target

### 目標

確認 skill 在旅遊類 target 上能成立，而且整體讀感自然，不會只剩 landmark 列點。

### Generator prompt

```text
請使用目前啟用的 emoji-riddles-zh-tw skill，將「大阪旅遊」轉成 1 組繁體中文 4-emoji 表意設計。只輸出這四個段落：target、emoji、解析、可讀性評語。設計要自然、好懂、有畫面，不要只是 landmark 關鍵詞列點。
```

### Solver prompt

```text
請根據這組 4 個 emoji 還原 target，target 類型是台灣使用者熟悉的旅遊城市、景點或旅程印象。請用繁體中文，且只輸出這四個段落：猜測答案、信心、解題理由、可能的備選答案。
```

### 預期特徵

- 旅行主題明確
- 不用國旗或地圖
- 至少有 1 個氣氛或生活印象，不是全靠 landmark

## 測資 2：食物或飲料類 target

### 目標

確認 skill 能處理台灣日常感強的 target，不只城市地點。

### Generator prompt

```text
請使用目前啟用的 emoji-riddles-zh-tw skill，將「珍珠奶茶」轉成 1 組繁體中文 4-emoji 表意設計。只輸出這四個段落：target、emoji、解析、可讀性評語。設計要自然、有台灣生活感，而且不要只是把外觀拆成 4 個圖示。
```

### Solver prompt

```text
請根據這組 4 個 emoji 還原 target，target 類型是台灣使用者熟悉的食物或飲料。請用繁體中文，且只輸出這四個段落：猜測答案、信心、解題理由、可能的備選答案。
```

### 預期特徵

- 題材不是旅遊
- 有台灣生活感
- 不是把食物外觀直接拆成 4 個圖示

## 測資 3：影視、角色或流行文化類 target

### 目標

確認 skill 能跨到文化題材，維持繁中語感與 target-driven 設計感。

### Generator prompt

```text
請使用目前啟用的 emoji-riddles-zh-tw skill，將「宮崎駿」轉成 1 組繁體中文 4-emoji 表意設計。只輸出這四個段落：target、emoji、解析、可讀性評語。設計要公平、有畫面，不能只是直接摘要 target。
```

### Solver prompt

```text
請根據這組 4 個 emoji 還原 target，target 類型是台灣使用者熟悉的電影、角色或流行文化題材。請用繁體中文，且只輸出這四個段落：猜測答案、信心、解題理由、可能的備選答案。
```

### 預期特徵

- 題材不是旅遊、不是食物
- 有文化或角色聯想
- 解析後會覺得連法合理

## Plain 版通過訊號

如果這個 skill 表現正常，常見訊號應該是：

1. full-tier 很容易猜中
2. mini-tier 也常能猜中或猜得很接近
3. judge 雖然不一定把「難點辨識」打很高，但整體分數仍高
4. 讀者會覺得這是好懂的表意設計，不是故意藏梗

## 建議驗證流程

1. 先用 generator agent 產出 emoji 設計
2. 再用不同 solver agent 解同一組 emoji
3. judge agent 依 `references/shared/scoring-rubric.md` 打分
4. 至少覆蓋旅遊、食物、文化三種情境
5. 若同一 agent 在 3 題中有 2 題以上總分偏低，回頭修 skill description、output contract 或題材選擇方式
