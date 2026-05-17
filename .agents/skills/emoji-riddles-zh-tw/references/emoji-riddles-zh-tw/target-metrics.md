# 中文 Emoji 表意設計 Target Metrics

這份文件定義 `emoji-riddles-zh-tw` 的目標指標，讓 benchmark 結果有明確標準可比。

## Primary goal

希望達成：

1. **generators** 產出的 emoji 設計自然、好懂、有畫面
2. **full-tier solvers** 大多能解出
3. **mini-tier solvers** 也大多能解出，或至少猜得非常接近

## Generator quality targets

對 generators：

- 平均格式正確率：**100%**
- 平均 4 emoji 遵守率：**100%**
- 平均 generator quality score：**>= 8/10**

如果 generator 產出的設計中有 2 題以上低於 7/10，表示 skill 本身還不夠穩。

## Solver targets

### Full-tier solver targets

- 正確答案率：**>= 85%**
- 平均總分：**>= 7/10**
- 理由對齊度平均：**>= 2/3**

### Mini-tier solver targets

- 正確答案率：**>= 70%**
- 平均總分：**>= 6/10**
- 理由對齊度平均：**>= 1.5/3**

## Tier-fit targets

plain 版不是要拉大差距，而是要避免：

- full-tier 能解，但 mini-tier 卻常常完全看不懂
- 設計為了「聰明」而犧牲可讀性

### Score gap

- full-tier 平均總分 - mini-tier 平均總分：**<= 2 分**

### Answer-rate gap

- full-tier 正確答案率 - mini-tier 正確答案率：**<= 20 個百分點**

如果 gap 過大，通常表示設計開始偏向 clever / witty，而不是 plain。

## Interpretation

### Strong result

符合以下大多數條件：

- generators 把 target 轉成 emoji 的品質穩
- full-tier solvers 高分
- mini-tier solvers 也有不錯的成功率
- 公布答案後，多數人會覺得自然而不是硬湊

### Weak result

常見情況：

- full-tier 也常猜錯
- mini-tier 猜中率太低
- generator 產出的設計像百科關鍵詞列點
- 公布答案後仍覺得牽強

## Benchmark maturity levels

### Level 1

- 單一情境測試可行
- 流程跑得通

### Level 2

- 三種情境都能穩定跑
- 有穩定可讀性

### Level 3

- 多輪 benchmark 都維持高可讀性
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
- 提高解析與可讀性評語對 generator 的要求

### If mini-tier is too weak

- 減少過度私人的聯想
- 多補 1 個核心或場景線索
- 避免把 plain 版硬做成機智版
