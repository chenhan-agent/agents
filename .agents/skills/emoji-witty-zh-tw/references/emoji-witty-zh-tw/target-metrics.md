# 中文 Emoji 表意設計（機智版）Target Metrics

這份文件定義 `emoji-witty-zh-tw` 的目標指標，讓 benchmark 結果有明確標準可比。

## Sample-size baseline

為了避免 overfit，解讀這份 metrics 時：

- **至少 6 題** 才能當成一輪有代表性的 benchmark
- 而且應覆蓋 **旅遊、食物 / 飲料、文化 / 創作者** 三大類
- 如果只跑 3 題，最多只能視為 smoke test，不應直接拿來宣稱 skill 已穩定

## Primary goal

希望達成：

1. **generators** 產出的 emoji 設計夠好
2. **full-tier solvers** 大多能掌握設計理由
3. **mini-tier solvers** 就算猜中，也較常停在表面理由

## Generator quality targets

對 generators：

- 平均格式正確率：**100%**
- 平均 4 emoji 遵守率：**100%**
- 平均 generator quality score：**>= 8/10**

如果 generator 產出的設計中有 2 題以上低於 7/10，表示 skill 本身還不夠穩。

## Solver targets

### Full-tier solver targets

- 正確答案率：**>= 70%**
- 平均總分：**>= 7/10**
- 理由對齊度平均：**>= 3/4**
- 理由品質平均：**>= 2/3**
- 難點辨識率：**>= 60%**

### Mini-tier solver targets

- 正確答案率：**不設硬上限**
- 平均總分：**<= 6/10**
- 理由對齊度平均：**<= 2/4**
- 理由品質平均：**<= 1.5/3**
- 難點辨識率：**<= 30%**

## Reasoning-gap targets

這是最重要的指標。

### Score gap

- full-tier 平均總分 - mini-tier 平均總分：**>= 1.5 分**

### Reason-alignment gap

- full-tier 理由對齊度平均 - mini-tier 理由對齊度平均：**>= 1 分**

### Difficulty-awareness gap

- full-tier 難點辨識率 - mini-tier 難點辨識率：**>= 25 個百分點**

如果 gap 不夠，表示設計還不夠有層次，或是理由設計得不夠可被 strong model 正確讀出。

如果只有少數固定 target 表現好，也不能算 strong result；必須在多題輪替下仍大致維持這些 gap。

## Interpretation

### Strong result

符合以下大多數條件：

- generators 把 target 轉成 emoji 的品質穩
- full-tier solvers 高分
- full-tier 比 mini-tier 更能講對設計理由
- mini-tier 就算猜中，也常漏掉轉折或文化層次

### Weak result

常見情況：

- full-tier 也常猜錯
- full-tier 跟 mini-tier 的理由看起來差不多
- mini-tier 雖然理由短，但其實抓到的線索也差不多完整
- generator 放進去的轉折沒有真的被 full-tier讀出

## What to tune when metrics miss

### If full-tier is too weak

- 增加收斂線索
- 減少過度飄忽的聯想
- 提高解析與難度評語對 generator 的要求
- 讓真正關鍵的文化 clue 更可被 strong model 說清楚，而不是只有作者自己知道

### If mini-tier is too strong

- 減少直接 landmark / 直接俗稱
- 增加側面線索
- 增加文化轉譯與雙關
- 避免 4 個 emoji 都在講同一件事
- 避免把經典食物和主題樂園 / 唯一 landmark 同時放進同一組
- 檢查任兩個 emoji 是否已經足夠鎖定答案
- 就算答案不容易再降，也要優先增加「理由層次差距」而不是只追求答錯率
