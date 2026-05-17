# 中文 Emoji 表意設計 Target Metrics

這份文件定義 `emoji-riddles-zh-tw` 的目標指標，讓 benchmark 結果有明確標準可比。

## Primary goal

希望達成：

1. **general / full-tier generators** 產出的 emoji 設計夠好
2. **general / full-tier solvers** 大多能解出
3. **mini-tier solvers** 解出率與理由品質顯著較低

## Generator quality targets

對 full-tier generators：

- 平均格式正確率：**100%**
- 平均 4 emoji 遵守率：**100%**
- 平均 generator quality score：**>= 8/10**

如果 generator 產出的設計中有 2 題以上低於 7/10，表示 skill 本身還不夠穩。

## Solver targets

### Full-tier solver targets

- 正確答案率：**>= 80%**
- 平均總分：**>= 7/10**
- 理由對齊度平均：**>= 2/3**

### Mini-tier solver targets

- 正確答案率：**<= 35%**
- 平均總分：**<= 4/10**
- 理由對齊度平均：**<= 1/3**

## Separation targets

這是最重要的指標。

### Score gap

- full-tier 平均總分 - mini-tier 平均總分：**>= 3 分**

### Answer-rate gap

- full-tier 正確答案率 - mini-tier 正確答案率：**>= 40 個百分點**

如果 gap 不夠，表示設計還不夠有層次，或是太直白。

## Interpretation

### Strong result

符合以下大多數條件：

- full-tier generators 把 target 轉成 emoji 的品質穩
- full-tier solvers 高分
- mini-tier solvers 明顯低分
- 理由品質也能拉開差距

### Weak result

常見情況：

- full-tier 也常猜錯
- mini-tier 猜中率太高
- mini-tier 猜錯但理由仍然拿高分

## Benchmark maturity levels

### Level 1

- 單一情境測試可行
- 流程跑得通

### Level 2

- 三種情境都能穩定跑
- 有初步 separation

### Level 3

- 多輪 benchmark 都維持 separation
- skill 規則能穩定產出高品質 emoji 設計

## Recommended first benchmark

第一輪 benchmark 建議：

1. 每個 full-tier generator 至少出 1 題
2. target 類型至少含：
   - 旅遊
   - 食物 / 飲料
   - 流行文化
3. 每題至少讓 6 個 solvers 作答：
   - 3 個 full-tier
   - 3 個 mini-tier

## What to tune when metrics miss

### If full-tier is too weak

- 增加收斂線索
- 減少過度飄忽的聯想
- 提高解析與難度評語對 generator 的要求

### If mini-tier is too strong

- 減少直接 landmark / 直接俗稱
- 增加側面線索
- 增加文化轉譯與雙關
- 避免 4 個 emoji 都在講同一件事
