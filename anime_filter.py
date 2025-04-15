"""動漫更新網頁過濾器"""
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import webbrowser
import os

class AnimeFilter: #所有邏輯和數據封裝在一起
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        self.base_url = "https://www.iyf.tv/list/anime?orderBy=1&page="
        self.driver = None
        self.anime_list = []

    def setup_driver(self):
        options = wb.ChromeOptions()
        options.add_argument(f"--user-agent={self.user_agent}")
        options.add_argument("--headless")  # 如果需要無頭模式，取消註解此行
        self.driver = wb.Chrome(options=options)

    def get_anime_data(self, start=1, page=1):
        try:
            self.setup_driver()

            url = self.base_url + str(page)
            self.driver.get(url)
            self.driver.implicitly_wait(3)
            self.driver.set_window_size(800, 600)  # 調整視窗大小為更適中的尺寸

            # 滾動頁面以加載更多動畫項目
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while True:
                # 滾動到頁面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待新內容加載

                # 計算新的頁面高度並檢查是否已經到達底部
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break  # 到達底部，退出循環
                last_height = new_height

            # 等待並獲取動畫列表
            list_page = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "list-page"))
            )

            # 獲取所有動畫項目
            anime_items = WebDriverWait(list_page, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#list-page > div"))
            )

            for item in anime_items:
                try:
                    link_element = item.find_element(By.CSS_SELECTOR, "a")
                    title = link_element.get_attribute("title")
                    link = link_element.get_attribute("href")
                    image = item.find_element(By.CSS_SELECTOR, "img.poster.d-block")
                    img_url = image.get_attribute("src")
                    episode = item.find_element(By.CLASS_NAME, "status-text").text

                    anime_info = {
                        "title": title,
                        "link": link,
                        "image": img_url,
                        "newepisode": episode
                    }
                    self.anime_list.append(anime_info)
                except NoSuchElementException:
                    continue

            time.sleep(2)  # 避免請求過於頻繁

        except Exception as e:
            print(f"爬取過程中發生錯誤: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

        return self.anime_list

    def get_anime_list(self):
        return self.anime_list
#當腳本直接運行時：這個區塊內的代碼將會執行。在這種情況下，它會創建 AnimeFilter 的實例，提示用戶輸入要抓取的頁數，然後調用 get_anime_data 方法來獲取動畫數據。
#當腳本被導入時：這個區塊內的代碼將不會執行。這對於重用代碼而不運行主要腳本邏輯是非常有用的。
if __name__ == "__main__":
    filter = AnimeFilter()
    page = int(input("請輸入加載頁數: "))
    anime_list = filter.get_anime_data(1, page)
    print(f"共爬取到 {len(anime_list)} 部動畫")
    
class AnimePlayer:
    def __init__(self, root):
        self.root = root
        self.root.title('愛壹帆動畫播放器')
        self.root.geometry('1200x800')

        # 初始化動畫列表
        self.anime_data = []
        self.current_image = None

        # 創建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 創建左側動畫列表框架
        self.list_frame = ttk.Frame(self.main_frame, width=300)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 創建搜索框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.list_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)

        # 創建更新按鈕和頁數輸入框
        self.control_frame = ttk.Frame(self.list_frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.page_label = ttk.Label(self.control_frame, text='頁數：')
        self.page_label.pack(side=tk.LEFT)

        self.page_var = tk.StringVar(value='1')
        self.page_entry = ttk.Entry(self.control_frame, textvariable=self.page_var, width=5)
        self.page_entry.pack(side=tk.LEFT, padx=2)

        self.update_button = ttk.Button(self.control_frame, text='更新列表', command=self.update_anime_data)
        self.update_button.pack(side=tk.LEFT, padx=5)

        # 創建動畫列表
        self.listbox_frame = ttk.Frame(self.list_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.anime_listbox = tk.Listbox(self.listbox_frame, font=('Arial', 10))
        self.anime_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滾動條
        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.anime_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.anime_listbox.configure(yscrollcommand=self.scrollbar.set)

        # 創建右側內容框架
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 創建圖片預覽區域
        self.image_frame = ttk.Frame(self.content_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 創建動畫信息區域
        self.info_frame = ttk.Frame(self.content_frame)
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.title_label = ttk.Label(self.info_frame, text='標題：', font=('Arial', 12, 'bold'))
        self.title_label.pack(fill=tk.X)

        self.episode_label = ttk.Label(self.info_frame, text='集數：', font=('Arial', 10))
        self.episode_label.pack(fill=tk.X)

        self.link_label = ttk.Label(self.info_frame, text='連結：', font=('Arial', 10), cursor='hand2', foreground='blue')
        self.link_label.pack(fill=tk.X)
        self.link_label.bind('<Button-1>', lambda e: self.open_link())

        self.link_button = ttk.Button(self.info_frame, text='觀看動畫', command=self.open_link)
        self.link_button.pack(pady=5)

        self.current_link = ''

        # 綁定事件
        self.anime_listbox.bind('<<ListboxSelect>>', self.on_select_anime)
        self.search_var.trace('w', self.on_search_change)

        # 初始加載數據
        self.update_anime_data()

    def update_anime_data(self):
        """從網站更新動畫數據"""
        def fetch_data():
            try:
                self.update_button.config(state='disabled')
                page_num = max(1, int(self.page_var.get()))
                filter = AnimeFilter()
                self.anime_data = filter.get_anime_data(1, page_num)
                self.update_anime_listbox()
                messagebox.showinfo('成功', f'成功加載{len(self.anime_data)}部動畫')
            except ValueError:
                messagebox.showerror('錯誤', '請輸入有效的頁數')
            except Exception as e:
                messagebox.showerror('錯誤', f'更新數據時發生錯誤：{str(e)}')
            finally:
                self.update_button.config(state='normal')

        thread = threading.Thread(target=fetch_data)
        thread.start()

    def update_anime_listbox(self):
        """更新動畫列表顯示"""
        self.anime_listbox.delete(0, tk.END)
        search_text = self.search_var.get().lower()

        for anime in self.anime_data:
            if search_text in anime['title'].lower():
                self.anime_listbox.insert(tk.END, anime['title'])

    def load_image(self, url):
        """從URL加載圖片"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            # 保持寬高比例縮放
            width = 300
            ratio = width / img.width
            height = int(img.height * ratio)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.current_image = photo
            return photo
        except Exception as e:
            print(f"加載圖片時發生錯誤：{str(e)}")
            return None

    def on_select_anime(self, event):
        """當選擇動畫時更新顯示信息"""
        selection = self.anime_listbox.curselection()
        if selection and self.anime_data:
            title = self.anime_listbox.get(selection[0])
            selected_anime = next((anime for anime in self.anime_data if anime['title'] == title), None)
            if selected_anime:
                self.title_label.config(text=f'標題：{selected_anime["title"]}')
                self.episode_label.config(text=f'集數：{selected_anime["newepisode"]}')
                self.current_link = selected_anime["link"]
                self.link_label.config(text=f'連結：{self.current_link}')

                def load_image_thread():
                    photo = self.load_image(selected_anime['image'])
                    if photo:
                        self.image_label.config(image=photo)
                    else:
                        self.image_label.config(image='')
                        messagebox.showerror('錯誤', '無法加載圖片')

                thread = threading.Thread(target=load_image_thread)
                thread.start()

    def open_link(self):
        """打開動畫連結"""
        if self.current_link:
            webbrowser.open(self.current_link)
        else:
            messagebox.showinfo('提示', '請先選擇一部動畫')

    def on_search_change(self, *args):
        """當搜索文本改變時更新列表"""
        self.update_anime_listbox()

if __name__ == '__main__':
    root = tk.Tk()
    app = AnimePlayer(root)
    root.mainloop()
