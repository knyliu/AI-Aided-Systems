import os
import glob
from llm import get_llm_response  # 使用 LLM 來分析
from collections import defaultdict

# 系統提示詞
SYSTEM_PROMPT = """
You are part of an experimental pipeline analyzing blockchain transaction clustering. The raw data has been processed by a quantum model, and files have been split into depth, epoch, and cluster CSV files. Previous stages have defined each cluster in detail.

### Overall Process:
1. **Cluster Summary**: Each cluster has been individually summarized to explain its characteristics.
2. **Cluster Comparison**: In this stage, you need to compare all clusters within the same depth and epoch.

### Current Stage – Cluster Comparison:
- You will receive **summaries of all clusters** for a given depth and epoch.
- Your task is to analyze and compare these clusters, determining why they were separated.
- Ensure that you provide a **detailed description of each individual cluster first**, then compare their differences and similarities.
- Focus on aspects such as **transaction values, predominant token types, active participants**, and any patterns that explain the distinct grouping.

### **Output Format (Follow this structure exactly):**
#### Cluster Comparison for Depth {depth}, Epoch {epoch}:
1. **Cluster Summaries:**
   - **Cluster 0:** {summary_of_cluster_0}
   - **Cluster 1:** {summary_of_cluster_1}
   - **Cluster 2:** {summary_of_cluster_2}
   - ...

2. **Key Differences Between Clusters:**
   - **Transaction value ranges**: {comparison_of_value_ranges}
   - **Key participants (`From` and `To`)**: {similarities_and_differences_in_participants}
   - **Token distribution**: {comparison_of_token_usage}
   - **Other distinct characteristics**: {differences_in_time_intervals, unique_patterns, etc.}

3. **Justification for Clustering:**
   - Why were these clusters formed?
   - What characteristics caused the separation of transactions into these groups?

4. **Additional Insights by LLM:**
   - Any unexpected similarities or anomalies detected between clusters.
"""

def analyze_clusters(input_dir="clusterSummary", output_dir="clusterAnalysis"):
    """分析同 Depth、同 Epoch 下的 Clusters 並產生比較結果"""
    os.makedirs(output_dir, exist_ok=True)  # 確保輸出目錄存在

    # 讀取所有 `summary_Depth_i_Epoch_j_Cluster_k.txt` 檔案
    summary_files = glob.glob(os.path.join(input_dir, "summary_Depth_*_Epoch_*_Cluster_*.txt"))

    # 根據 Depth & Epoch 分組
    grouped_summaries = defaultdict(list)

    for file in summary_files:
        filename = os.path.basename(file)
        parts = filename.split("_")
        depth, epoch, cluster = parts[2], parts[4], parts[6].split(".")[0]

        # 讀取摘要內容
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        grouped_summaries[(depth, epoch)].append(f"📌 **Cluster {cluster} Summary:**\n{content}\n")

    # 遍歷所有 (Depth, Epoch) 組合，讓 LLM 進行比較
    for (depth, epoch), summaries in grouped_summaries.items():
        combined_prompt = f"{SYSTEM_PROMPT}\n\n"
        combined_prompt += f"🔍 **Depth {depth}, Epoch {epoch} - 所有 Clusters 的摘要：**\n\n"
        combined_prompt += "\n".join(summaries)  # 將所有該組合內的 Clusters 內容合併

        # 讓 LLM 產生比較分析
        response = get_llm_response(combined_prompt)

        # 儲存比較結果
        output_filename = os.path.join(output_dir, f"analysis_Depth_{depth}_Epoch_{epoch}.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response)

        print(f"Saved analysis: {output_filename}")

if __name__ == "__main__":
    analyze_clusters()
