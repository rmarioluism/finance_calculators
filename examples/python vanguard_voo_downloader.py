# This script uses Selenium to navigate to the Vanguard VOO ETF profile page,
# find the "Portfolio Composition File" link within the "Holding Details" section,
# and automatically click it to download the file.

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def download_portfolio_composition(url):
    """
    Navigates to the Vanguard VOO profile, clicks the Holding Details tab,
    and downloads the Portfolio Composition File.
    """
    # Define the directory where files should be downloaded
    download_dir = os.getcwd()
    print(f"Files will be downloaded to: {download_dir}")

    # --- 1. WebDriver Configuration ---
    # Configure Chrome options to automatically handle the download
    chrome_options = webdriver.ChromeOptions()
    # Set preferences to download files automatically to the specified directory
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # Run in headless mode (no visible browser UI) for servers/efficiency. 
    # Comment the next line out if you want to see the browser pop up.
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("start-maximized")

    # Initialize the WebDriver using ChromeDriverManager for automatic driver handling
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Please ensure you have Google Chrome installed.")
        return

    try:
        print(f"Navigating to URL: {url}")
        driver.get(url)

        # Use WebDriverWait for element visibility and interaction
        wait = WebDriverWait(driver, 20)
        
        # --- 2. Navigate to Holding Details Tab ---
        # The link fragment should already be in the URL, but we click the tab
        # explicitly to ensure the content is loaded/visible.
        # This tab is usually identified by its text content "Holding Details" or similar.
        
        # Look for the tab that contains the text 'Holdings' or 'Holding Details'
        # The website uses the anchor with 'Holding Details' text as the main tab.
        try:
            holding_details_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Holding Details')]"))
            )
            print("Clicking 'Holding Details' tab...")
            holding_details_tab.click()
            # A short pause might be needed for the content under the tab to load fully
            time.sleep(2) 
        except Exception as e:
            print("Could not find or click 'Holding Details' tab. Assuming the anchor link pre-activated the section.")

        # View the PCF for this Vanguard ETF
        # Terms and conditions of use of the PCF
        # Accept


        # --- 3. Locate and Click the Download Link ---
        # The target link is usually named 'Portfolio Composition File'
        
        # We search for an <a> tag that contains the text "Portfolio Composition File"
        download_link = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Portfolio Composition File"))
        )
        
        print("Clicking 'Portfolio Composition File' link...")
        download_link.click()

        print("Download initiated. Waiting a few seconds for file transfer...")
        # Give time for the download to complete. 
        # A full check for file completion is complex, so we use a simple sleep.
        time.sleep(10) 
        print("Script finished. Check the current directory for the downloaded file.")

    except Exception as e:
        print(f"An error occurred during navigation or clicking: {e}")
        # Optionally, save a screenshot for debugging
        # driver.save_screenshot("error_screenshot.png")

    finally:
        # --- 4. Cleanup ---
        print("Closing the browser.")
        driver.quit()

if __name__ == "__main__":
    VANGUARD_VOO_URL = "https://investor.vanguard.com/investment-products/etfs/profile/voo#portfolio-composition"
    download_portfolio_composition(VANGUARD_VOO_URL)