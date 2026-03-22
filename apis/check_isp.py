import requests
def check_isp():
    response = requests.get(f"https://ipinfo.io/json",proxies={"http": "", "https": ""},timeout=4)
    data = response.json()
    print(f"ISP: {data.get('org')}")
    return data.get("org")