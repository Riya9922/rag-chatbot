import urllib.request
import json
import traceback

data = json.dumps({"question": "whats nav of"}).encode("utf-8")
req = urllib.request.Request("http://localhost:8000/query", data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode())
except Exception as e:
    print("Other Error:", e)
    traceback.print_exc()
