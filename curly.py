import requests
import json
from datetime import datetime, timedelta

# --- Step 0: Set session, cookies, headers ---
csrf_token = "29b897538a6a723e9a8506d25a85dc25"  # Your current CSRF token
cookies = {
    "_ga": "GA1.3.1470020755.1749466507",
    "csrf_gem_cookie": csrf_token,
    "GeM": "1542078820.20480.0000",
    "TS0123c430": "01e393167dc6369be6f24ed82f89efd2b3178b7b027b1661a180a4e400ea215e3484bb64f8757da9fff6335d59c63fa51d855a9915a987773d5da90b762bee885b4066de732a8e52203033e5df5537ea9d2e40a672",
    "TS94d6e986027": "082c9b9876ab2000a72f50823a969086cc9bf4213a12f555aaf84ce152b0d5583c296f13663a59ab08deea59031130005c75b047e240e3f0f4ccecc4dcc131ea07d1110d8f836a20731e250aafda6aefa9951eadfd5be410a74770048774eec6"
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://bidplus.gem.gov.in/advance-search"
}

# --- Step 1: Start session ---
session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

# --- Step 2: Get ministry list ---
ministry_url = "https://bidplus.gem.gov.in/ministry-list-adv"
ministry_payload = f"csrf_bd_gem_nk={csrf_token}"
resp_min = session.post(ministry_url, data=ministry_payload)
print("Ministries:", resp_min.json())

# --- Step 3: Get organizations for selected ministry ---
selected_ministry = "Autonomous Body"
org_url = "https://bidplus.gem.gov.in/org-list-adv"
org_payload = f"ministry={selected_ministry.replace(' ', '+')}&csrf_bd_gem_nk={csrf_token}"
resp_org = session.post(org_url, data=org_payload)
org_list = resp_org.json()
print("\nOrganizations:", org_list)

# --- Step 4: Date Range Calculation ---
today = datetime.now()
two_months_ago = today - timedelta(days=60)
start_date = two_months_ago.strftime('%d-%m-%Y')
end_date = today.strftime('%d-%m-%Y')

# --- Step 5: Final search for tenders ---
search_url = "https://bidplus.gem.gov.in/advance-search"
final_headers = headers.copy()
final_headers["Content-Type"] = "application/json"

payload = {
    "ministry": selected_ministry,
    "organization": org_list[0],  # First organization
    "fromDate": start_date,
    "toDate": end_date,
    "csrf_bd_gem_nk": csrf_token
}

response = session.post(search_url, headers=final_headers, json=payload)

# --- Step 6: Show response ---
print("\nServer Response Headers:")
for k, v in response.headers.items():
    print(f"{k}: {v}")

print("\nTender Data:")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)
