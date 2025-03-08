import os
import glob
from llm import get_llm_response  # 使用 LLM 來分析
from collections import defaultdict

# 系統提示詞
SYSTEM_PROMPT = """你是一位專業的區塊鏈分析師，負責研究區塊鏈交易的分群趨勢。
你將會獲得 **同一個區塊深度 (Depth)** 內的 **不同 Epochs 的交易群組分析結果**，請根據這些資訊進行綜合分析：

⚡ **你的任務**：
1. **比較不同 Epochs 的群組結構是否相似？**
   - 這些 Epoch 之間的交易行為是否趨於一致？
   - 是否有某些 Epoch 有特別多或少的 Clusters？
   - 是否有某些 Epoch 出現了全新的交易類型？

2. **找出該 Depth 下所有 Epoch 都有的共通性**
   - 哪些 `From` 或 `To` 是該 Depth 的核心交易者？
   - 哪些 `TokenName` 或 `TokenSymbol` 在所有 Epoch 都活躍？
   - 交易額 (`Value`) 是否呈現某種固定範圍？
   - 是否存在某些 Clusters 模式，在不同 Epochs 下重複出現？

3. **推測分群變化的可能原因**
   - 是否可能是市場行情變動導致的？
   - 是否某些時間點發生了事件導致交易模式改變？
   - 是否某些交易策略（如套利）在某些 Epochs 下特別明顯？

🔍 **請確保你的分析完整，並且能夠提供關於該 Depth 的關鍵見解，找出此深度內 Epochs 之間的異同點與共通特徵。**

---

### **Depth {depth} - 不同 Epochs 的分析結果：**
"""

def summarize_depths(input_dir="clusterAnalysis", output_dir="epochSummary"):
    """分析同 Depth 下的不同 Epochs，並產生比較與共通點的總結"""
    os.makedirs(output_dir, exist_ok=True)  # 確保輸出目錄存在

    # 讀取所有 `analysis_Depth_i_Epoch_j.txt` 檔案
    analysis_files = glob.glob(os.path.join(input_dir, "analysis_Depth_*_Epoch_*.txt"))

    # 根據 Depth 分組
    grouped_analyses = defaultdict(list)

    for file in analysis_files:
        filename = os.path.basename(file)
        parts = filename.split("_")
        depth, epoch = parts[2], parts[4].split(".")[0]

        # 讀取分析內容
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        grouped_analyses[depth].append(f"📌 **Epoch {epoch} Analysis:**\n{content}\n")

    # 遍歷所有 Depth，讓 LLM 進行 Epochs 間的比較與共通性分析
    for depth, analyses in grouped_analyses.items():
        combined_prompt = SYSTEM_PROMPT.format(depth=depth)
        combined_prompt += "\n".join(analyses)  # 將所有該 Depth 內的 Epochs 內容合併

        # 讓 LLM 產生比較分析
        response = get_llm_response(combined_prompt)

        # 儲存比較結果
        output_filename = os.path.join(output_dir, f"summary_Depth_{depth}.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response)

        print(f"Saved depth summary: {output_filename}")

if __name__ == "__main__":
    summarize_depths()
