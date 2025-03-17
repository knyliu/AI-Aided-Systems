import pandas as pd
import os
import glob
from llm import get_llm_response  # 引入 llm.py 的函數

# 系統提示詞
# 系統提示詞
SYSTEM_PROMPT = """
You are part of an experimental pipeline analyzing blockchain transaction clustering. The original raw data has been processed by a quantum model and split into CSV files based on depth, epoch, and cluster.

### Overall Process:
1. **Data Processing**: The raw data is split into files organized by depth, epoch, and cluster.
2. **Cluster Definition**: Your task is to provide a detailed description of each individual cluster to help later stages (cluster comparison, epoch comparison, and depth comparison) understand the cluster structure.

### Current Stage – Cluster Summary:
- You will receive data from a **single cluster** (for a specific depth and epoch).
- Your task is to analyze and describe in detail the defining characteristics of this cluster.
- Ensure that you clearly explain the transaction patterns, key participants, transaction amounts, token types, and any other features that justify why these transactions were grouped together.

### **Output Format (Follow this structure exactly):**
#### Cluster Summary for Depth {depth}, Epoch {epoch}, Cluster {cluster_id}:
1. **Cluster Characteristics:**
   - **Number of transactions**: {number_of_transactions}
   - **Key participants (`From` and `To`)**: {summary_of_key_participants}
   - **Common token types**: {list_of_tokens_used}
   - **Transaction value range**: {min_value} - {max_value}
   - **Notable patterns**: {any_unique_trends_or_repetitions}

2. **Justification for Clustering:**
   - Why were these transactions grouped into this cluster?
   - What differentiates this cluster from others?

3. **Additional Observations by LLM:**
   - Any other patterns or anomalies detected in this cluster.
"""



def summarize_clustered_data(input_dir="clustered_csv", output_dir="clusterSummary"):
    """處理所有 cluster CSV，並產生對應的 LLM 摘要"""
    os.makedirs(output_dir, exist_ok=True)  # 確保輸出目錄存在

    csv_files = glob.glob(os.path.join(input_dir, "Depth_*_Epoch_*_Cluster_*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        # 取得檔名資訊
        filename = os.path.basename(file)
        depth, epoch, cluster = filename.split("_")[1], filename.split("_")[3], filename.split("_")[5].split(".")[0]

        # 轉換 CSV 內容為文字摘要格式
        csv_content = df.head(10).to_string(index=False)  # 取前 10 筆資料
        prompt = f"{SYSTEM_PROMPT}\n\n以下是數據樣本：\n{csv_content}\n\n請產生摘要："

        # 調用 LLM
        response = get_llm_response(prompt)

        # 儲存摘要
        output_filename = os.path.join(output_dir, f"summary_Depth_{depth}_Epoch_{epoch}_Cluster_{cluster}.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response)

        print(f"Saved summary: {output_filename}")

if __name__ == "__main__":
    summarize_clustered_data()
