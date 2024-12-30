import dns.resolver
import requests
from selenium import webdriver
from time import sleep





def get_mx(domain):
    mx_records = []
    for x in dns.resolver.resolve(domain, 'MX'):
        mx_records.append(x.to_text())
    return mx_records





def screenshot_url(url, sleep_time=1):
    #fixme #this is unsafe
    #selenium is nice but we need ephmeral instance2
    #https://dev.to/shadow_b/capturing-full-webpage-screenshots-with-selenium-in-python-a-step-by-step-guide-187f
    #https://pytutorial.com/exploring-different-ways-to-capture-web-page-screenshots-in-python/#google_vignette
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(sleep_time)
    return driver.get_screenshot_as_png()
