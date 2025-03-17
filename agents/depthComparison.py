import os
import glob
from llm import get_llm_response  # 使用 LLM 來分析

# 系統提示詞
SYSTEM_PROMPT = """
You are part of an experimental pipeline analyzing blockchain transaction clustering. The raw data has been processed into CSV files by depth, epoch, and cluster, and previous stages have produced detailed summaries at the cluster level, compared clusters within the same epoch, and compared epochs within the same depth.

### Overall Process:
1. **Cluster Summary**: Define each cluster.
2. **Cluster Comparison**: Compare clusters within the same depth and epoch.
3. **Epoch Comparison**: Compare different epochs within the same depth.
4. **Depth Comparison**: Now, you must compare the clustering strategies across different depths.

### Current Stage – Depth Comparison:
- You will receive **summaries for all depths**.
- Your task is to analyze how clustering behavior varies as depth changes.
- Ensure that you **provide a comprehensive description of each depth individually** before making any comparisons.
- Focus on identifying trends in transaction patterns, **variations in cluster structure, differences in key participants, and any changes in transaction values or token types that vary with blockchain depth**.

### **Output Format (Follow this structure exactly):**
#### Depth Comparison Summary:
1. **Depth Summaries:**
   - **Depth 1:**
     - **Number of epochs**: {number_of_epochs}
     - **General clustering approach**: {how_clusters_were_formed}
     - **Common transaction behaviors**: {key_patterns}
     - **Most frequent tokens used**: {token_distribution}
   - **Depth 2:** {same_structure}
   - **Depth 3:** {same_structure}
   - ...

2. **Comparing Depths:**
   - **How do clustering strategies evolve as depth increases?**
   - **Does transaction behavior become more complex or simplified?**
   - **What similarities exist across different depths?**
   - **Are certain participants or tokens more dominant in deeper or shallower depths?**
   - **Are transaction values significantly different between depths?**

3. **Conclusion:**
   - What are the overarching trends across all depths?
   - What could explain the shifts in clustering behavior as depth changes?

4. **Additional Insights by LLM:**
   - Any unexpected relationships or irregularities across depths.
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
