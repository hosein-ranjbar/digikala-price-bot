import sys
import os
import re
import time
import threading
import webbrowser
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QScrollArea, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

product_links = [
    "https://www.digikala.com/product/dkp-15235017",
    "https://www.digikala.com/product/dkp-18564542",
    "https://www.digikala.com/product/dkp-3172231",
    "https://www.digikala.com/product/dkp-3296717",
    "https://www.digikala.com/product/dkp-18675096",
    "https://www.digikala.com/product/dkp-18430833",
    "https://www.digikala.com/product/dkp-17937131",
    "https://www.digikala.com/product/dkp-15658374",
    "https://www.digikala.com/product/dkp-9347586",
    "https://www.digikala.com/product/dkp-18278628",
    "https://www.digikala.com/product/dkp-13959550",
    "https://www.digikala.com/product/dkp-15235017",
    "https://www.digikala.com/product/dkp-19489210",
    "https://www.digikala.com/product/dkp-17011092",
    "https://www.digikala.com/product/dkp-19330937",
    "https://www.digikala.com/product/dkp-19214260",
    "https://www.digikala.com/product/dkp-16029106",
    "https://www.digikala.com/product/dkp-15375902",
    "https://www.digikala.com/product/dkp-17009352",
    "https://www.digikala.com/product/dkp-11202573",
    "https://www.digikala.com/product/dkp-5519818",
    "https://www.digikala.com/product/dkp-18496625",
    "https://www.digikala.com/product/dkp-5488584",
    "https://www.digikala.com/product/dkp-16740022",
    "https://www.digikala.com/product/dkp-13705546",
    "https://www.digikala.com/product/dkp-17358727",
    "https://www.digikala.com/product/dkp-19279580",
    "https://www.digikala.com/product/dkp-7669005",
    "https://www.digikala.com/product/dkp-6982667",
    "https://www.digikala.com/product/dkp-18429020",
    "https://www.digikala.com/product/dkp-16724003",
    "https://www.digikala.com/product/dkp-18430175",
    "https://www.digikala.com/product/dkp-17655813",
    "https://www.digikala.com/product/dkp-17359131",



]

def get_info(url):
    chrome_path = os.path.join(os.getcwd(), "chromedriver.exe")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--lang=fa-IR')
    driver = webdriver.Chrome(service=Service(chrome_path), options=options)
    try:
        driver.get(url)
        time.sleep(5)
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        price_div = driver.find_element(By.CSS_SELECTOR, "div.w-full.flex.gap-1.item-center.justify-end")
        price = price_div.text.strip()
        return title, price
    except Exception:
        return "خطا در خواندن اطلاعات", "قیمت پیدا نشد"
    finally:
        driver.quit()

def extract_dkp(url):
    match = re.search(r'dkp-(\d+)', url)
    return match.group(1) if match else "---"

class ProductCard(QFrame):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.dkp = extract_dkp(url)
        self.old_price = ""

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 10px; padding: 10px; }")
        layout = QVBoxLayout(self)

        self.title_lbl = QLabel("در حال دریافت عنوان...")
        self.price_lbl = QLabel("در حال دریافت قیمت...")
        self.old_price_lbl = QLabel("")
        self.tick_lbl = QLabel("")

        self.dkp_lbl = QLabel(f"کد محصول: {self.dkp}")
        self.copy_btn = QPushButton("📋 کپی")
        self.refresh_btn = QPushButton("🔄")
        self.open_btn = QPushButton("🌐 باز کردن در مرورگر")

        font = QFont("B Nazanin", 11)
        for widget in [self.title_lbl, self.price_lbl, self.dkp_lbl]:
            widget.setFont(font)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.open_btn)

        price_layout = QHBoxLayout()
        price_layout.addWidget(self.price_lbl)
        price_layout.addWidget(self.tick_lbl)
        price_layout.addWidget(self.old_price_lbl)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.dkp_lbl)
        layout.addLayout(btn_layout)
        layout.addLayout(price_layout)

        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.refresh_btn.clicked.connect(self.manual_refresh)
        self.open_btn.clicked.connect(self.open_in_browser)

    def update_info(self, title, price):
        if title == "خطا در خواندن اطلاعات":
            self.title_lbl.setText("خطا در خواندن اطلاعات")
            self.price_lbl.setText("---")
            return

        self.title_lbl.setText(f"🛒 {title[:65]}{'...' if len(title) > 65 else ''}")
        self.price_lbl.setText(f"💰 {price}")

        if self.old_price and self.old_price != price:
            self.tick_lbl.setText("✅")
            self.old_price_lbl.setText(f"← {self.old_price}")
        else:
            self.tick_lbl.setText("")
            self.old_price_lbl.setText("")

        self.old_price = price

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.dkp)

    def manual_refresh(self):
        threading.Thread(target=self.fetch_and_update).start()

    def fetch_and_update(self):
        title, price = get_info(self.url)
        self.update_info(title, price)

    def open_in_browser(self):
        webbrowser.open(self.url)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بررسی قیمت محصولات دیجی‌کالا")
        self.setMinimumSize(1100, 700)

        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        content = QWidget()
        self.grid = QVBoxLayout(content)

        self.cards = []
        for url in product_links:
            card = ProductCard(url)
            self.grid.addWidget(card)
            self.cards.append(card)

        self.scroll.setWidget(content)
        self.layout.addWidget(self.scroll)

        self.timer_lbl = QLabel()
        self.timer_lbl.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.timer_lbl)

        self.remaining_time = 600  # ⏱ ده دقیقه
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.start_fetch_loop()

    def update_timer(self):
        self.remaining_time -= 1
        mins, secs = divmod(self.remaining_time, 60)
        self.timer_lbl.setText(f"🔁 بروزرسانی بعدی: {mins:02}:{secs:02}")
        if self.remaining_time <= 0:
            self.start_fetch_loop()

    def start_fetch_loop(self):
        self.remaining_time = 600
        threading.Thread(target=self.update_all).start()

    def update_all(self):
        for card in self.cards:
            title, price = get_info(card.url)
            card.update_info(title, price)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
