import os
import glob
from llm import get_llm_response  # 使用 LLM 來分析
from collections import defaultdict

# 系統提示詞
SYSTEM_PROMPT = """你是一位專業的區塊鏈分析師，負責分析不同交易群組的特徵。
你將會獲得 **同一個區塊深度 (Depth) 和時期 (Epoch)** 內的 **所有交易群組 (Clusters)** 摘要，請根據這些資訊進行比較分析：

**你的任務**：
1. 分析 **這些群組為什麼會被區分為不同的 Clusters**。
2. **比較這些 Clusters**，找出它們的共通點與差異。
3. 判斷是否有 **主要參與者 (From/To)** 在多個群組內頻繁出現。
4. 檢查交易額 (`Value`) 是否存在某種模式，例如：
   - 一群交易額較大，一群較小
   - 一群主要使用特定的 `TokenName`
   - 交易時間 (`TimeStamp`) 是否有特定模式
5. 提出可能的推測，例如：
   - 是否有某種套利行為？
   - 是否可能是同一組交易者拆分交易？
   - 是否是來自不同來源的交易流動？

請確保你的分析完整，並能提供有價值的見解。"""

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
