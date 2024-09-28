import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium.webdriver.common.by import By

def scrape_fapello_images(model_name, start_image=1, base_folder="models", driver_name="chromedriver.exe"):
    # Create the base images folder if it doesn't exist
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    # Create a model-specific folder inside the base folder for images and videos
    model_folder = os.path.join(base_folder, model_name)
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    # Create a separate folder for videos inside the model's folder
    videos_folder = os.path.join(model_folder, "videos")
    if not os.path.exists(videos_folder):
        os.makedirs(videos_folder)

    # Set up Selenium WebDriver (Chrome in this case)
    options = Options()
    options.add_argument('--headless')  # Runs Chrome in headless mode.
    options.add_argument('--disable-gpu')  # Disable GPU to reduce resource consumption.
    options.add_argument('--no-sandbox')  # Bypass OS security model, required for some systems.
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems in some environments.
    options.add_argument('--window-size=1920x1080')  # Set window size to avoid issues.
    
    # Suppress logging output from Chrome/FFmpeg
    options.add_argument('--log-level=3')  # Suppresses warnings, errors, and logs.
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Disable logging.

    # Use Service to provide the driver path
    service = Service(driver_name)
    driver = webdriver.Chrome(service=service, options=options)

    img_count = 0  # Counter for images
    video_count = 1  # Independent counter for videos
    img_number = start_image  # Start at the image number provided
    consecutive_failures = 0  # Counter for consecutive failures

    while True:
        try:
            # Construct the image/video URL
            page_url = f"https://fapello.com/{model_name}/{img_number}"
            print(f"Fetching content from: {page_url}")

            # Load the page in Selenium
            driver.get(page_url)
            time.sleep(2)  # Wait for the page to load completely (adjust as needed)

            # Check if the page redirects to fapello.com, indicating missing content
            if driver.current_url == "https://fapello.com/":
                print(f"Content {img_number} not found (redirected to fapello.com), skipping to next.")
                consecutive_failures += 1
            else:
                # Get the page source and parse it with BeautifulSoup
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Look for image using the CSS selector you provided
                img_tag = soup.select_one("html body div#wrapper div.main_content div.container.m-auto div.mx-auto div.bg-white.shadow.rounded-md.dark\\:bg-gray-900.-mx-2.lg\\:mx-0 div.flex.justify-between.items-center a.uk-align-center img")
                
                # Look for video using the CSS path you provided
                video_tag = soup.select_one("html body div#wrapper div.main_content div.container.m-auto div.mx-auto div.bg-white.shadow.rounded-md.dark\\:bg-gray-900.-mx-2.lg\\:mx-0 div.flex.justify-between.items-center video.uk-align-center source")
                
                # If an image is found, download it
                if img_tag:
                    img_url = img_tag.get('src')
                    img_url = urljoin(page_url, img_url)

                    # Attempt to download the image
                    img_response = requests.get(img_url)

                    # Check if the image request was successful
                    if img_response.status_code == 200:
                        # Save the image directly in the model's folder
                        img_name = f"image_{img_number}.jpg"
                        img_path = os.path.join(model_folder, img_name)

                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                            print(f"Downloaded image: {img_name}")

                        img_count += 1  # Increment the count of successfully downloaded images
                        consecutive_failures = 0  # Reset failure counter since this one succeeded
                    else:
                        print(f"Failed to download image {img_number} (HTTP {img_response.status_code})")
                        consecutive_failures += 1  # Failed to download the image
                elif video_tag:
                    # Check if a video is present and save .mp4 or .m4v files
                    video_url = video_tag.get('src')
                    video_url = urljoin(page_url, video_url)
                    if video_url.endswith(('.mp4', '.m4v')):
                        # Attempt to download the video
                        video_response = requests.get(video_url)

                        # Check if the video request was successful
                        if video_response.status_code == 200:
                            # Save the video with a separate numbering sequence in the videos folder
                            video_name = f"video_{video_count}{os.path.splitext(video_url)[1]}"
                            video_path = os.path.join(videos_folder, video_name)

                            with open(video_path, 'wb') as f:
                                f.write(video_response.content)
                                print(f"Downloaded video: {video_name}")

                            video_count += 1  # Increment the video count
                            consecutive_failures = 0  # Reset failure counter since this one succeeded
                        else:
                            print(f"Failed to download video {img_number} (HTTP {video_response.status_code})")
                            consecutive_failures += 1  # Failed to download the video
                else:
                    print(f"No image or video found at: {page_url}")
                    consecutive_failures += 1  # No image or video found

            # If two consecutive images/videos are missing, stop the script
            if consecutive_failures >= 2:
                print("Two consecutive content items not found, stopping the script.")
                break

            # Move on to the next image/video
            img_number += 1

        except Exception as e:
            # If something unexpected happens, print the error and move on to the next one
            print(f"Error fetching content {img_number}: {e}")
            img_number += 1  # Move to the next item
            continue  # Keep the loop running despite the error

    # Quit the Selenium WebDriver once we're done
    driver.quit()

    # Print how many images and videos were successfully downloaded
    print(f"Total images downloaded: {img_count}")
    print(f"Total videos downloaded: {video_count - 1}")

# Example Usage
model_name = input("Enter the Fapello model name (e.g., kinkylilkitty): ")
start_image = int(input("Enter the starting image number (e.g., 1): "))
scrape_fapello_images(model_name, start_image)