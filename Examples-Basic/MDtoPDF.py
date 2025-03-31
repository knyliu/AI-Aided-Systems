import os
from google import genai
import markdown
import pdfkit
from llm import get_llm_response


def markdown_to_pdf(markdown_text: str, output_pdf_path: str):
    # 將 Markdown 轉換成 HTML 內容
    html_body = markdown.markdown(markdown_text)
    
    # 取得當前資料夾中 NotoSansTC-Regular.ttf 的絕對路徑，並轉換成 file:// URL
    current_dir = os.path.abspath(os.path.dirname(__file__))
    font_path = os.path.join(current_dir, "NotoSansTC-Regular.ttf")
    font_path = font_path.replace("\\", "/")  # 處理 Windows 路徑的反斜線
    font_url = f"file:///{font_path}"
    
    # 嵌入 CSS，指定字型及 local file access 支援
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'Noto Sans TC';
                src: url('{font_url}');
            }}
            body {{
                font-family: 'Noto Sans TC', sans-serif;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # 指定 wkhtmltopdf 的路徑（請根據實際安裝路徑調整）
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    # 加入啟用 local file access 的選項，避免載入本地資源時產生錯誤
    options = {
        'enable-local-file-access': ''
    }
    
    # 使用 pdfkit 將 HTML 轉換成 PDF
    pdfkit.from_string(html_content, output_pdf_path, configuration=config, options=options)

if __name__ == "__main__":
    # 讓使用者選擇輸入方式：1-從 txt 檔案讀取，2-手動輸入 prompt
    mode = input("請選擇輸入方式 (1: txt 檔案, 2: 手動輸入): ").strip()
    if mode == "1":
        file_path = input("請輸入 txt 檔案的完整路徑: ").strip()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            print(f"讀取檔案失敗: {e}")
            exit(1)
    elif mode == "2":
        prompt = input("請輸入 prompt: ").strip()
    else:
        print("無效的選項，請輸入 1 或 2。")
        exit(1)
    
    try:
        # 呼叫 LLM 並取得回覆的 Markdown 內容
        response_text = get_llm_response(prompt)
    except Exception as e:
        print(f"取得 LLM 回覆失敗: {e}")
        exit(1)
    
    # 設定 PDF 輸出檔案名稱
    output_pdf = "llm_response.pdf"
    
    try:
        # 將 Markdown 內容轉換成 PDF
        markdown_to_pdf(response_text, output_pdf)
        print(f"PDF 已保存至 {output_pdf}")
    except Exception as e:
        print(f"轉換為 PDF 失敗: {e}")
