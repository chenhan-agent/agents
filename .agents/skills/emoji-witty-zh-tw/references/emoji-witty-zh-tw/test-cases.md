# 中文 Emoji 表意設計（機智版）測資

這份測資用來驗證 `emoji-witty-zh-tw` 是否真的能把 plain 版拉成更有層次的 clever / witty 輸出。

這份測資的重點不是單純看誰猜中答案，而是看：

1. full-tier 是否更能講對設計理由
2. mini-tier 就算猜中，是否仍停在表面理由
3. judge 是否能看出明顯的 reasoning gap

這裡的測試流程分成三個角色：

1. **generator agent**：根據 skill 產出 emoji 設計
2. **solver agent**：看到 emoji 後還原 target 並說明理由
3. **judge agent**：依共用 scoring rubric 打分

## 共用輸出規格

所有測試都要求：

1. 使用 **繁體中文**
2. 每題 **剛好 4 個 emoji**
3. 輸出格式固定為：
   - `target`
   - `emoji`
   - `解析`
   - `難度評語`
4. 不要直接拆 target 字面
5. 不要用國旗、地圖輪廓、或一眼秒懂的直給提示

## Generator output contract

generator agent 應產出：

1. `target`
2. `emoji`
3. `解析`
4. `難度評語`

其中：

- `emoji` 必須是 4 個 emoji
- `解析` 要說明每個 emoji 為什麼能連到 target
- `難度評語` 要交代為何 strong model 比較容易、mini model 比較容易卡住

## Solver output contract

solver agent 應產出：

1. `猜測答案`
2. `信心`
3. `解題理由`
4. `可能的備選答案`

其中：

- `解題理由` 不能只說表面聯想，要盡量對到每個 emoji 的功能
- 如果有覺得哪一個 emoji 是轉折、誤導或側面文化線索，應明說

## 測資 1：旅遊類 target

### Generator prompt

```text
請使用目前啟用的 emoji-witty-zh-tw skill，將「大阪旅遊」轉成 1 組繁體中文 4-emoji 表意設計。只輸出這四個段落：target、emoji、解析、難度評語。設計要有層次、有巧思，不要太直白。
```

### 預期特徵

- 不用國旗或地圖
- 不直接丟最唯一地標 + 經典食物 + 國家
- 至少 1 個線索是城市氣質或旅人記憶
- 至少 1 個線索是城市的社會氣質、在地行為或旅人情緒記憶
- 至少 1 個線索可以合理誤導到另一個觀光城市
- 不把「經典食物 + 主題樂園 / 唯一 landmark」同時放進同一組
- 任兩個 emoji 不應足以讓 mini model 直接鎖定答案

## 測資 2：食物或飲料類 target

### Generator prompt

```text
請使用目前啟用的 emoji-witty-zh-tw skill，將「珍珠奶茶」轉成 1 組繁體中文 4-emoji 表意設計。只輸出這四個段落：target、emoji、解析、難度評語。設計要有趣、有機智感，而且不要太簡單。
```

### 預期特徵

- 不只是外觀拆解
- 至少 1 個線索帶有台灣生活感或文化轉譯
- mini model 不應該只靠表面關鍵詞秒答

## 測資 3：影視、角色或流行文化類 target

### Generator prompt

```text
請使用目前啟用的 emoji-witty-zh-tw skill，將「宮崎駿」轉成 1 組繁體中文 4-emoji 表意設計。只輸出這四個段落：target、emoji、解析、難度評語。設計要公平、有巧思，不能只是直接摘要 target。
```

### 預期特徵

- 題材不是旅遊、不是食物
- 有文化或角色聯想
- 如果 target 是創作者，應該偏作者指紋，不是作品元素清單
- 至少留 1 個「懂的人會會心一笑」的層次

## 建議 benchmark pool

不要只固定測 1 題旅遊、1 題食物、1 題文化，否則很容易 overfit。

建議至少維持一個小型 pool，輪流抽題：

### 旅遊類

- 大阪旅遊
- 香港旅遊
- 九份
- 沖繩自由行

### 食物 / 飲料類

- 珍珠奶茶
- 刈包
- 大腸包小腸
- 鹽酥雞

### 文化 / 創作者 / 作品類

- 宮崎駿
- 吉卜力
- 神隱少女
- 周星馳

## 最低取樣建議

為了避免 overfit，單輪 benchmark 至少應該：

1. **每大類至少抽 2 題**
2. **總題數至少 6 題**
3. **同一題不要連續超過 2 輪都用**
4. **每 2 到 3 輪就替換一部分 target**

如果只是 smoke test，可以先跑 3 題；但只跑 3 題的結果不能拿來宣稱 skill 已經穩定。

## 輪替原則

建議交錯使用：

- 1 題相對好做 reasoning gap 的題
- 1 題中等難度題
- 1 題容易讓 generator 掉回直球模板的題

這樣比較容易看出 skill 是真的進步，還是只是剛好對某幾題有效。

## 機智版通過訊號

如果這個 skill 表現正常，常見訊號應該是：

1. full-tier 常能猜中，或至少猜得接近
2. mini-tier 就算猜中，也更常停在表面理由
3. judge 在理由對齊度、理由品質與難點辨識上能看出層次差距
4. 公布答案後，讀者會覺得這組「有梗，而且合理」
5. generator 不會反覆掉回「經典食物 + 觀光 magnet」的直球模板
