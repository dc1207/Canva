"""動漫更新網頁過濾器"""
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logging.basicConfig(level=logging.INFO)

class AnimeFilter: #所有邏輯和數據封裝在一起
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        self.base_url = "https://www.iyf.tv/list/anime?orderBy=1&page="
        self.driver = None
        self.anime_list = []

    def setup_driver(self):
        options = wb.ChromeOptions()
        options.add_argument(f"--user-agent={self.user_agent}")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = wb.Chrome(service=service, options=options)
        except Exception as e:
            logging.error(f"設置瀏覽器驅動時發生錯誤: {str(e)}")
            raise

    def get_anime_data(self, start_page=1, end_page=1, max_retries=3):
        try:
            self.setup_driver()
            for page in range(start_page, end_page + 1):
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        url = self.base_url + str(page)
                        logging.info(f"正在爬取第 {page} 頁")
                        
                        self.driver.get(url)
                        self.driver.set_window_size(800, 600)
                        
                        # 等待並獲取動畫列表
                        list_page = WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.ID, "list-page"))
                        )
                        
                        # 獲取所有動畫項目
                        anime_items = WebDriverWait(list_page, 15).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#list-page > div"))
                        )
                        
                        for item in anime_items:
                            try:
                                link_element = WebDriverWait(item, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "a"))
                                )
                                title = link_element.get_attribute("title")
                                link = link_element.get_attribute("href")
                                
                                image = WebDriverWait(item, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "img.poster.d-block"))
                                )
                                img_url = image.get_attribute("src")
                                
                                episode = WebDriverWait(item, 5).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "status-text"))
                                ).text
                                
                                if all([title, link, img_url, episode]):
                                    anime_info = {
                                        "title": title,
                                        "link": link,
                                        "image": img_url,
                                        "newepisode": episode
                                    }
                                    self.anime_list.append(anime_info)
                                    logging.info(f"成功爬取動畫: {title}")
                            except (NoSuchElementException, TimeoutException) as e:
                                logging.warning(f"爬取動畫項目時發生錯誤: {str(e)}")
                                continue
                        
                        # 成功爬取當前頁面，跳出重試循環
                        break
                        
                    except (TimeoutException, WebDriverException) as e:
                        retry_count += 1
                        logging.error(f"第 {page} 頁爬取失敗 (嘗試 {retry_count}/{max_retries}): {str(e)}")
                        if retry_count < max_retries:
                            time.sleep(5)  # 重試前等待
                        else:
                            logging.error(f"第 {page} 頁爬取失敗，已達到最大重試次數")
                
                # 避免請求過於頻繁
                time.sleep(3)
                
        except Exception as e:
            logging.error(f"爬取過程中發生錯誤: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("瀏覽器已關閉")

        return self.anime_list

    def get_anime_list(self):
        return self.anime_list
#當腳本直接運行時：這個區塊內的代碼將會執行。在這種情況下，它會創建 AnimeFilter 的實例，提示用戶輸入要抓取的頁數，然後調用 get_anime_data 方法來獲取動畫數據。
#當腳本被導入時：這個區塊內的代碼將不會執行。這對於重用代碼而不運行主要腳本邏輯是非常有用的。
if __name__ == "__main__":   
    filter = AnimeFilter()
    end_page = int(input("請輸入加載頁數: "))
    anime_list = filter.get_anime_data(1, end_page)
    print(f"共爬取到 {len(anime_list)} 部動畫")