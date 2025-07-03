import requests
import json
import urllib.parse
import os
from datetime import datetime

# --- Step 0: Set session, cookies, headers ---
csrf_token = "6ac0d866777b3a9729a4991089e5c39b"  # Your current CSRF token
cookies = {
    "_ga": "GA1.3.1470020755.1749466507",
    "csrf_gem_cookie": csrf_token,
    "GeM": "1542078820.20480.0000",
    "TS0123c430": "01e393167dc6369be6f24ed82f89efd2b3178b7b027b1661a180a4e400ea215e3484bb64f8757da9fff6335d59c63fa51d855a9915a987773d5da90b762bee885b4066de732a8e52203033e5df5537ea9d2e40a672",
    "TS94d6e986027": "082c9b9876ab2000a72f50823a969086cc9bf4213a12f555aaf84ce152b0d5583c296f13663a59ab08deea59031130005c75b047e240e3f0f4ccecc4dcc131ea07d1110d8f836a20731e250aafda6aefa9951eadfd5be410a74770048774eec6"
}

headers = {
    "accept": "/",
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

# --- Step 4: Final tender request with date filtering ---
search_url = "https://bidplus.gem.gov.in/advance-search"
final_headers = headers.copy()
final_headers["Content-Type"] = "application/json"

from_date = "01-06-2025"
to_date = "30-06-2025"

payload = {
    "ministry": selected_ministry,
    "organization": org_list[0],
    "fromDate": from_date,
    "toDate": to_date,
    "csrf_bd_gem_nk": csrf_token
}

response = session.post(search_url, headers=final_headers, json=payload)

print("\nServer Response Headers:")
for k, v in response.headers.items():
    print(f"{k}: {v}")

print("\nTender Data:")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)

# --- Step 6: Fetch detailed bids using /search-bids endpoint ---
search_bids_url = "https://bidplus.gem.gov.in/search-bids"
detailed_payload = {
    "searchType": "ministry-search",
    "ministry": "Ministry of Consumer Affairs Food and Public Distribution",
    "buyerState": "",
    "organization": "Central Warehousing Corporation (CWC)",
    "department": "Department of Food and Public Distribution",
    "bidEndFromMin": "2025-07-01",
    "bidEndToMin": "2025-07-31",
    "page": 1
}

encoded_payload = urllib.parse.urlencode({
    "payload": json.dumps(detailed_payload),
    "csrf_bd_gem_nk": csrf_token
})

search_bids_headers = headers.copy()
search_bids_headers["accept"] = "application/json, text/javascript, */*; q=0.01"
search_bids_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"

search_bids_response = session.post(search_bids_url, headers=search_bids_headers, data=encoded_payload)

print("\n--- Final Search Bids Response ---")
try:
    print(json.dumps(search_bids_response.json(), indent=2))
except Exception:
    print(search_bids_response.text)

# --- Step 7: Filter tenders based on keywords ---
keywords = ["ITSM", "HRMS", "NMS", "ITAM", "SIEE", "ESS", "Dashboard Reporting", "Software Services", "ITOM", "Service Deska"]

try:
    tenders = search_bids_response.json().get("data", [])
    print(f"\nTotal tenders found: {len(tenders)}")

    filtered_tenders = []
    for tender in tenders:
        title = tender.get("itemTitle", "").lower()
        if any(keyword.lower() in title for keyword in keywords):
            bid_id = tender.get("bidNumber", "")
            tender["downloadLink"] = f"https://bidplus.gem.gov.in/showbidDocument/{bid_id}"
            filtered_tenders.append(tender)

    print(f"Filtered tenders matching keywords: {len(filtered_tenders)}")

    for idx, tender in enumerate(filtered_tenders, start=1):
        bid_number = tender.get("bidNumber")
        print(f"\n--- Tender #{idx} ---")
        print(f"Bid Number     : {bid_number}")
        print(f"Title          : {tender.get('itemTitle')}")
        print(f"Start Date     : {tender.get('bidStartDate')}")
        print(f"End Date       : {tender.get('bidEndDate')}")
        print(f"Quantity       : {tender.get('quantity')}")
        print(f"Dept           : {tender.get('departmentName')}")
        print(f"Org            : {tender.get('organizationName')}")
        print(f"State          : {tender.get('stateName')}, City: {tender.get('cityName')}")
        print(f"Download Link  : https://bidplus.gem.gov.in/showbidDocument/{bid_number}")

    # --- Step 8: Save filtered tenders to a .json file ---
    output_dir = "gem_tender_results"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"filtered_tenders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(filtered_tenders, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Filtered tenders saved to: {filepath}")

except Exception as e:
    print("❌ Failed to filter tenders:", e)
    # --- Step 9: Download bid documents as PDFs ---
    pdf_dir = os.path.join(output_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    for tender in filtered_tenders:
        bid_id = tender.get("bidNumber")
        pdf_url = f"https://bidplus.gem.gov.in/showbidDocument/{bid_id}"
        pdf_path = os.path.join(pdf_dir, f"{bid_id}.pdf")

        try:
            pdf_resp = session.get(pdf_url, headers={"Referer": "https://bidplus.gem.gov.in/advance-search"})
            if pdf_resp.status_code == 200 and b"%PDF" in pdf_resp.content[:1024]:
                with open(pdf_path, "wb") as pdf_file:
                    pdf_file.write(pdf_resp.content)
                print(f"📄 Downloaded PDF for Bid ID {bid_id} -> {pdf_path}")
            else:
                print(f"⚠️  Skipped (not a valid PDF or forbidden): {bid_id}")
        except Exception as err:
            print(f"❌ Error downloading PDF for {bid_id}:", err)
            
# --- Step 10: Summarize downloaded PDFs using Gemini ---
for tender in filtered_tenders:
    bid_id = tender.get("bidNumber")
    pdf_path = os.path.join(pdf_dir, f"{bid_id}.pdf")

    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        continue

    summary = summarize_pdf_with_gemini(text, bid_id)
    if summary:
        try:
            summary_json = json.loads(summary)
            tender.update({
                "summary": summary_json
            })
            print(f"📝 Summary extracted for Bid ID {bid_id}")
        except json.JSONDecodeError:
            print(f"⚠️  Could not parse Gemini response for {bid_id}")


