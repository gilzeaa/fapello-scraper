import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_fapello(model_name, start_image=1, base_folder="models", driver_name="chromedriver.exe"):
    model_folder = os.path.join(base_folder, model_name)
    videos_folder = os.path.join(model_folder, "videos")
    os.makedirs(model_folder, exist_ok=True)
    os.makedirs(videos_folder, exist_ok=True)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(service=Service(driver_name), options=options)

    img_count, video_count, consecutive_failures, img_number = 0, 1, 0, start_image

    while consecutive_failures < 2:
        try:
            driver.get(f"https://fapello.com/{model_name}/{img_number}")
            time.sleep(2)

            if driver.current_url == "https://fapello.com/":
                consecutive_failures += 1
                img_number += 1
                continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            img_tag = soup.select_one("html body div#wrapper div.main_content div.container.m-auto div.mx-auto div.bg-white.shadow.rounded-md.dark\\:bg-gray-900.-mx-2.lg\\:mx-0 div.flex.justify-between.items-center a.uk-align-center img")
            video_tag = soup.select_one("html body div#wrapper div.main_content div.container.m-auto div.mx-auto div.bg-white.shadow.rounded-md.dark\\:bg-gray-900.-mx-2.lg\\:mx-0 div.flex.justify-between.items-center video.uk-align-center source")

            if img_tag:
                img_url = urljoin(driver.current_url, img_tag['src'])
                if requests.get(img_url).status_code == 200:
                    img_name = f"image_{img_number}.jpg"
                    img_path = os.path.join(model_folder, img_name)
                    with open(img_path, 'wb') as f:
                        f.write(requests.get(img_url).content)
                    print(f"Downloaded: {img_name}")
                    img_count += 1
                    consecutive_failures = 0

            elif video_tag:
                video_url = urljoin(driver.current_url, video_tag['src'])
                if requests.get(video_url).status_code == 200:
                    video_name = f"video_{video_count}{os.path.splitext(video_url)[1]}"
                    video_path = os.path.join(videos_folder, video_name)
                    with open(video_path, 'wb') as f:
                        f.write(requests.get(video_url).content)
                    print(f"Downloaded: {video_name}")
                    video_count += 1
                    consecutive_failures = 0

            img_number += 1

        except Exception as e:
            consecutive_failures += 1
            print(f"Error fetching content {img_number}: {e}")

    driver.quit()
    print(f"Total images downloaded: {img_count}")
    print(f"Total videos downloaded: {video_count - 1}")

# Example Usage
model_name = input("Enter the Fapello model name (e.g., kinkylilkitty): ")
start_image = int(input("Enter the starting image number (e.g., 1): "))
scrape_fapello(model_name, start_image)