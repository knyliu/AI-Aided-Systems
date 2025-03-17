import os
import glob
from llm import get_llm_response  # 使用 LLM 來分析
from collections import defaultdict

# 系統提示詞
SYSTEM_PROMPT = """
You are part of an experimental pipeline analyzing blockchain transaction clustering. The raw data has been processed into CSV files by depth, epoch, and cluster, and each cluster has been defined and compared within the same depth and epoch.

### Overall Process:
1. **Cluster Summary**: Each cluster has been defined.
2. **Cluster Comparison**: Clusters within the same depth and epoch have been compared.
3. **Epoch Comparison**: Now, you must compare the results across different epochs within the same depth.

### Current Stage – Epoch Comparison:
- You will receive **summaries for each epoch** within a specific depth, where each summary includes the **detailed analysis of the clusters in that epoch**.
- Your task is to analyze how the clustering behavior changes from one epoch to another within the same depth.
- Ensure that you fully **describe each epoch's summary first before drawing overall comparisons**.
- Focus on identifying **similarities and differences in clustering strategies, common transaction features, and any evolution or shifts in transaction behavior across epochs**.

### **Output Format (Follow this structure exactly):**
#### Epoch Comparison for Depth {depth}:
1. **Epoch Summaries:**
   - **Epoch 1:**
     - **Number of clusters**: {number_of_clusters}
     - **Primary clustering method**: {how_clusters_were_formed}
     - **Common participants (`From` and `To`)**: {key_participants}
     - **Most frequently used tokens**: {token_distribution}
   - **Epoch 2:** {same_structure}
   - **Epoch 3:** {same_structure}
   - ...

2. **Comparing Epochs within Depth {depth}:**
   - **How has the clustering strategy evolved?**
   - **Did the number of clusters increase or decrease?**
   - **Are there any key participants present in every epoch?**
   - **What common transaction behaviors persist across all epochs?**
   - **What major differences exist between epochs?**

3. **Conclusion:**
   - What trends or patterns are observed within this depth?
   - What might be causing these changes across epochs?

4. **Additional Insights by LLM:**
   - Any anomalies or unexpected clustering behaviors detected.
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
        # combined_prompt = SYSTEM_PROMPT.format(depth=depth)
        combined_prompt = SYSTEM_PROMPT
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
