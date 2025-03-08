import os
import glob
from llm import get_llm_response  # 使用 LLM 來分析

# 系統提示詞
SYSTEM_PROMPT = """你是一位專業的區塊鏈分析師，負責研究不同區塊深度 (Depth) 下的分群策略。
你將會獲得 **所有不同 Depths 的總結報告**，請根據這些資訊進行整體比較分析：

⚡ **你的任務**：
1. **比較不同 Depths 的分群策略是否一致？**
   - 深度較大的區塊是否與較淺的區塊有不同的交易行為？
   - 是否有某些 `Depth` 的交易更集中，而某些 `Depth` 的交易較為分散？
   - `Clusters` 的數量是否隨 `Depth` 改變？
   
2. **發現隨 Depth 變化的關鍵因素**
   - `TokenName` 是否在不同 `Depth` 下有不同的分佈？
   - 交易額 (`Value`) 是否隨 `Depth` 變化？
   - 是否有某些 `From` 或 `To` 參與者僅在特定 `Depth` 出現？

3. **推測不同 Depths 為何產生這些差異**
   - 是否可能與區塊鏈共識機制、手續費、或者區塊大小有關？
   - 是否某些 Depth 反映了歷史時間內交易行為的變遷？
   - 是否某些交易策略（如套利）在某些 `Depth` 內特別明顯？

🔍 **請確保你的分析完整，並提供對整體交易模式的深入見解。**

---

### **所有不同 Depths 的比較分析**
"""

def compare_depths(input_dir="epochSummary", output_dir="depthComparison"):
    """分析不同 Depths 之間的分群策略差異，並產生總結報告"""
    os.makedirs(output_dir, exist_ok=True)  # 確保輸出目錄存在

    # 讀取所有 `summary_Depth_i.txt` 檔案
    summary_files = glob.glob(os.path.join(input_dir, "summary_Depth_*.txt"))

    depth_summaries = []

    for file in sorted(summary_files):  # 確保 Depth 順序排列
        depth = os.path.basename(file).split("_")[2].split(".")[0]

        # 讀取分析內容
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        depth_summaries.append(f"📌 **Depth {depth} Summary:**\n{content}\n")

    if not depth_summaries:
        print("⚠ No depth summaries found. Skipping depth comparison.")
        return

    # 準備 LLM 輸入
    combined_prompt = SYSTEM_PROMPT + "\n".join(depth_summaries)

    # 讓 LLM 產生最終比較
    response = get_llm_response(combined_prompt)

    # 儲存最終比較結果
    output_filename = os.path.join(output_dir, "final_summary.txt")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"✅ Saved final depth comparison summary: {output_filename}")

if __name__ == "__main__":
    compare_depths()
