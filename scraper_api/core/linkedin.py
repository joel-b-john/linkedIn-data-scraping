import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

COOKIE_FILE = "cookies.json"  # Stored session cookies


def login_and_get_cookies(email, password, save_to_file=True):
    """
    Logs into LinkedIn using Selenium and returns cookies for authenticated requests.
    """
    options = Options()
    options.add_argument('--headless')  # Use non-headless if CAPTCHA triggers
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    try:
        email_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
    except Exception as e:
        driver.quit()
        raise Exception("Login failed or form not found: " + str(e))

    # Get session cookies
    raw_cookies = driver.get_cookies()
    driver.quit()

    cookies = {cookie['name']: cookie['value'] for cookie in raw_cookies}

    if 'li_at' not in cookies or 'JSESSIONID' not in cookies:
        raise Exception("Login failed or required cookies not found")

    if save_to_file:
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f, indent=2)

    return cookies


def load_cookies_if_valid():
    """
    Loads cookies from file and checks if session is still valid by calling /voyager/api/me.
    """
    if not os.path.exists(COOKIE_FILE):
        return None

    with open(COOKIE_FILE, "r") as f:
        cookies = json.load(f)

    li_at = cookies.get('li_at')
    jsessionid = cookies.get('JSESSIONID', '').strip('"')

    if not li_at or not jsessionid:
        return None

    session = requests.Session()
    session.cookies.set('li_at', li_at)
    session.cookies.set('JSESSIONID', f'"{jsessionid}"')

    headers = {
        "csrf-token": jsessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "x-restli-protocol-version": "2.0.0",
        "Accept": "application/json",
    }

    try:
        response = session.get("https://www.linkedin.com/voyager/api/me", headers=headers, allow_redirects=False)
        if response.status_code == 200:
            return cookies
    except:
        pass

    return None


def fetch_profile_data(cookies, start=0, count=50):
    """
    Fetches the logged-in user's profile and a paginated list of connections.
    """
    li_at = cookies.get('li_at')
    jsessionid = cookies.get('JSESSIONID', '').strip('"')

    session = requests.Session()
    session.cookies.set('li_at', li_at)
    session.cookies.set('JSESSIONID', f'"{jsessionid}"')

    headers = {
        "csrf-token": jsessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "x-restli-protocol-version": "2.0.0",
        "Accept": "application/json",
    }

    # 1. Fetch logged-in user's profile
    me_response = session.get("https://www.linkedin.com/voyager/api/me", headers=headers)
    if me_response.status_code != 200:
        raise Exception(f"Failed to fetch profile: {me_response.status_code} - {me_response.text}")

    me_data = me_response.json()
    mini = me_data.get("miniProfile", {})
    first_name = mini.get("firstName", "")
    last_name = mini.get("lastName", "")
    public_id = mini.get("publicIdentifier", "")
    profile_id = me_data.get("plainId", "")

    logged_in_user = {
        "firstName": first_name,
        "lastName": last_name,
        "profileId": profile_id,
        "publicProfileUrl": f"https://www.linkedin.com/in/{public_id}"
    }

    # 2. Fetch user connections
    conn_url = f"https://www.linkedin.com/voyager/api/relationships/connections?start={start}&count={count}"
    conn_response = session.get(conn_url, headers=headers)
    if conn_response.status_code != 200:
        raise Exception(f"Failed to fetch connections: {conn_response.status_code} - {conn_response.text}")

    connections = []
    for conn in conn_response.json().get("elements", []):
        profile = conn.get("miniProfile", {})
        connections.append({
            "firstName": profile.get("firstName", ""),
            "lastName": profile.get("lastName", ""),
            "occupation": profile.get("occupation", ""),
            "publicProfileUrl": f"https://www.linkedin.com/in/{profile.get('publicIdentifier', '')}"
        })

    return {
        "loggedInUser": logged_in_user,
        "connections": connections,
        "pagination": {
            "start": start,
            "count": count,
            "nextStart": start + count
        }
    }
