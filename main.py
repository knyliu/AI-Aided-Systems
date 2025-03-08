import os
import agents.reEncode as re_encode
import agents.dataTransferringAgent as data_transfer
import agents.toClustered as to_cluster
import agents.clusterSummary as cluster_summary
import agents.clusterChecker as cluster_checker
import agents.epochComparison as epoch_comparison
import agents.depthComparison as depth_comparison  # 新增

# 設定是否使用重新編碼
USE_ENCODED_DATA = True

# 設定是否重新處理 Data Transfer（檢查是否有新 data.csv）
REFRESH_DATA_TRANSFER = True

# 設定是否重新產生 Cluster Summary
REGENERATE_SUMMARY = True

# 設定是否重新產生 Cluster Comparison
REGENERATE_CLUSTER_COMPARISON = True

# 設定是否重新產生 Epoch Comparison
REGENERATE_EPOCH_COMPARISON = True

# 設定是否重新產生 Depth Summary
REGENERATE_DEPTH_SUMMARY = True

# 設定是否重新產生 Depth Comparison
REGENERATE_DEPTH_COMPARISON = True

def main():
    data_file = "data.csv"

    if USE_ENCODED_DATA:
        print("🔄 Re-encoding data...")
        re_encode.re_encode_data()
        data_file = "data_encoded.csv"  # 使用重新編碼後的資料
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

if __name__ == "__main__":
    main()
