from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .base_connector import HermesConnector
import time

class WebConnector(HermesConnector):
    def get_supported_actions(self):
        return ["web_search", "scrape_url"]

    def execute(self, action_type: str, target: str) -> str:
        # Launch an invisible, silent browser
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--log-level=3') # Suppress warnings
        
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            if action_type == "web_search":
                driver.get(f"https://html.duckduckgo.com/html/?q={target}")
                time.sleep(1)
                results = driver.find_elements(By.CLASS_NAME, "result__snippet")
                text = " ".join([res.text for res in results[:2]]) # Grab top 2 results
                return f"Live web search results for '{target}': {text}"
                
            elif action_type == "scrape_url":
                driver.get(target)
                time.sleep(2)
                body = driver.find_element(By.TAG_NAME, 'body').text
                return f"Scraped content: {body[:1500]}" # Return first 1500 chars to avoid overwhelming the LLM
        except Exception as e:
            return f"Web Automation Error: {e}"
        finally:
            try: driver.quit()
            except: pass