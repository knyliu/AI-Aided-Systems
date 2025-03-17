import os
import gradio as gr

import agents.reEncode as re_encode
import agents.dataTransferringAgent as data_transfer
import agents.toClustered as to_cluster
import agents.clusterSummary as cluster_summary
import agents.clusterChecker as cluster_checker
import agents.epochComparison as epoch_comparison
import agents.depthComparison as depth_comparison

# 預設旗標值
USE_ENCODED_DATA = True
REFRESH_DATA_TRANSFER = True
REGENERATE_SUMMARY = True
REGENERATE_CLUSTER_COMPARISON = True
REGENERATE_EPOCH_COMPARISON = True
REGENERATE_DEPTH_SUMMARY = True
REGENERATE_DEPTH_COMPARISON = True

def main(data_file):
    # 若 data_file 為 None，則使用預設的 data.csv
    if not data_file:
        data_file = "data.csv"
    
    if USE_ENCODED_DATA:
        print("🔄 Re-encoding data...")
        re_encode.re_encode_data()
        # 使用重新編碼後的檔案
        data_file = "data_encoded.csv"
    else:
        print("⚡ Skipping data re-encoding.")

    if REFRESH_DATA_TRANSFER:
        print("🔄 Starting data transfer...")
        data_transfer.transfer_data(input_file=data_file)

        print("🔄 Splitting data into clusters...")
        to_cluster.split_into_clusters()
    else:
        print("⚡ Skipping data transfer and clustering.")

    if REGENERATE_SUMMARY:
        print("🔄 Generating summaries for clusters...")
        cluster_summary.summarize_clustered_data()
    else:
        print("⚡ Skipping cluster summary generation.")

    if REGENERATE_CLUSTER_COMPARISON:
        print("🔍 Comparing clusters within each Depth and Epoch...")
        cluster_checker.analyze_clusters()
    else:
        print("⚡ Skipping cluster comparison.")

    if REGENERATE_EPOCH_COMPARISON:
        print("🔍 Comparing Epochs within each Depth...")
        epoch_comparison.summarize_depths()
    else:
        print("⚡ Skipping epoch comparison.")

    if REGENERATE_DEPTH_SUMMARY:
        print("🔍 Generating depth-wide summary...")
        epoch_comparison.summarize_depths()
    else:
        print("⚡ Skipping depth-wide summary.")

    if REGENERATE_DEPTH_COMPARISON:
        print("🔍 Comparing all Depths...")
        depth_comparison.compare_depths()
    else:
        print("⚡ Skipping depth comparison.")

    print("✅ Processing complete!")
    return "Processing complete!"

def process_data(uploaded_file, use_encoded_data, refresh_data_transfer, regenerate_summary,
                 regenerate_cluster_comparison, regenerate_epoch_comparison,
                 regenerate_depth_summary, regenerate_depth_comparison):
    global USE_ENCODED_DATA, REFRESH_DATA_TRANSFER, REGENERATE_SUMMARY
    global REGENERATE_CLUSTER_COMPARISON, REGENERATE_EPOCH_COMPARISON
    global REGENERATE_DEPTH_SUMMARY, REGENERATE_DEPTH_COMPARISON

    USE_ENCODED_DATA = use_encoded_data
    REFRESH_DATA_TRANSFER = refresh_data_transfer
    REGENERATE_SUMMARY = regenerate_summary
    REGENERATE_CLUSTER_COMPARISON = regenerate_cluster_comparison
    REGENERATE_EPOCH_COMPARISON = regenerate_epoch_comparison
    REGENERATE_DEPTH_SUMMARY = regenerate_depth_summary
    REGENERATE_DEPTH_COMPARISON = regenerate_depth_comparison

    # 檢查是否有上傳檔案
    data_file_path = None
    if uploaded_file is not None:
        # 使用 binary 模式，上傳的檔案內容會是 bytes 物件
        data_file_path = "uploaded_data.csv"
        with open(data_file_path, "wb") as f:
            f.write(uploaded_file)
        print(f"Uploaded file saved as {data_file_path}")
    else:
        print("No file uploaded, using default 'data.csv'.")

    return main(data_file_path)

iface = gr.Interface(
    fn=process_data,
    inputs=[
        gr.File(label="上傳 CSV 檔案 (非必要)", type="binary"),
        gr.Checkbox(label="使用重新編碼", value=True),
        gr.Checkbox(label="重新處理 Data Transfer (檢查是否有新 data.csv)", value=True),
        gr.Checkbox(label="重新產生 Cluster Summary", value=True),
        gr.Checkbox(label="重新產生 Cluster Comparison", value=True),
        gr.Checkbox(label="重新產生 Epoch Comparison", value=True),
        gr.Checkbox(label="重新產生 Depth Summary", value=True),
        gr.Checkbox(label="重新產生 Depth Comparison", value=True),
    ],
    outputs="text",
    title="資料處理流程",
    description="請上傳 CSV 檔案（選擇性），並調整旗標設定以啟動資料處理流程。"
)

if __name__ == "__main__":
    iface.launch()
