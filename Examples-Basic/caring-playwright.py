import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os
from llm import get_llm_response

load_dotenv(find_dotenv())
url = os.getenv("MEDICAL_URL")
username = os.getenv("MEDICAL_USER")
password = os.getenv("MEDICAL_PASS")

def llm_parse_datetime(user_input: str) -> datetime:
    """
    利用 LLM 解析自然語言日期輸入，將輸入轉換成固定格式 "YYYY-MM-DD HH:MM"。
    對於未提供的部分，LLM 會自動以今天的日期或時間補齊。
    """
    prompt = (
        "請將以下自然語言描述轉換成格式 'YYYY-MM-DD HH:MM'，"
        "若輸入中缺少日期或時間資訊，請自動以今天的日期或目前時間補齊。描述：\n"
        f"{user_input}，你知需要回傳YYYY-MM-DD HH:MM，不要有其他多餘的字。"
    )
    response = get_llm_response(prompt)
    output_str = response.strip()
    try:
        dt = datetime.strptime(output_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"LLM 回傳的格式不正確，將使用目前時間取代：{output_str}")
        dt = datetime.now()
    return dt

async def login(page):
    """
    依據目標網頁的元素完成登入：
    - 帳號： input[name="ID_T1"]
    - 密碼： input[name="PASS_T2"]
    - 登入按鈕： input[name="B1"]
    """
    await page.goto(url)
    await page.fill('input[name="ID_T1"]', username)
    await page.fill('input[name="PASS_T2"]', password)
    await page.click('input[name="B1"]')
    # 等待網頁載入完成（可根據實際情況調整等待條件）
    await page.wait_for_load_state("networkidle")

async def update_start_date(page, start_date_input):
    """
    利用 LLM 解析使用者輸入的自然語言日期描述，
    並將解析後的日期填入開始日期的下拉選單：
      - select#YY1, select#MM1, select#DD1, select#HH1, select#NN1
    接著點選對應的「選取」按鈕。
    """
    dt = llm_parse_datetime(start_date_input)
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute_str = f"{dt.minute:02d}"  # 補零格式

    await page.select_option("select#YY1", str(year))
    await page.select_option("select#MM1", str(month))
    await page.select_option("select#DD1", str(day))
    await page.select_option("select#HH1", str(hour))
    await page.select_option("select#NN1", minute_str)
    # 點選第一個「選取」按鈕
    await page.click("input.btn[value='選取']")
    await page.wait_for_timeout(1000)

async def update_end_date(page):
    """
    將結束日期自動更新為「今日日期」：
      - 使用 select#YY2, select#MM2, select#DD2, select#HH2, select#NN2
    並點選第二個「選取」按鈕（利用 nth=1 指定）。
    """
    dt = datetime.now()
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute_str = f"{dt.minute:02d}"

    await page.select_option("select#YY2", str(year))
    await page.select_option("select#MM2", str(month))
    await page.select_option("select#DD2", str(day))
    await page.select_option("select#HH2", str(hour))
    await page.select_option("select#NN2", minute_str)
    # 由於有兩個「選取」按鈕，這裡用 nth(1) 點選第二個
    await page.locator("input.btn[value='選取']").nth(1).click()
    await page.wait_for_timeout(1000)

async def main():
    # 提示使用者輸入查詢的「開始日期」，接受自然語言描述（例如："上週五下午三點"）
    start_date_input = input("請輸入查詢的開始日期（自然語言皆可）：")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 一進入網頁就先登入
        await login(page)
        
        # 利用 LLM 解析後更新查詢條件：開始日期及結束日期（以今日為準）
        await update_start_date(page, start_date_input)
        await update_end_date(page)
        
        # 點選查詢按鈕，假設為： <input type="submit" name="B1" value="進行查詢">
        await page.click('input[type="submit"][value="進行查詢"]')
        await page.wait_for_load_state("networkidle")
        
        # 依需求，可在此處加入資料擷取或後續處理；此處示範截圖查詢結果頁面
        await page.screenshot(path="query_result.png")
        print("查詢結果截圖已保存為 query_result.png")
        # await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
