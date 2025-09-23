from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    start_time = time.time()
    page.goto("http://127.0.0.1:5001", timeout=60000)
    end_time = time.time()
    print(f"Page loaded in {end_time - start_time} seconds")
    page.wait_for_load_state("networkidle")
    page.screenshot(path="jules-scratch/verification/verification.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
