import urllib.request
import json
import time
import concurrent.futures

# The payload we will send
data = json.dumps({"question": "What is the NAV of HDFC Mid Cap?"}).encode("utf-8")

def make_request(request_id):
    """Sends a single request to the server and returns the elapsed time."""
    req = urllib.request.Request("http://localhost:8000/query", data=data, headers={"Content-Type": "application/json"})
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            response.read() # Read the response
            elapsed = time.time() - start_time
            return f"Request {request_id} completed in {elapsed:.2f} seconds (Status: {response.status})"
    except Exception as e:
        elapsed = time.time() - start_time
        return f"Request {request_id} FAILED in {elapsed:.2f} seconds. Error: {e}"

if __name__ == "__main__":
    print("🚀 Firing 10 concurrent requests to the server...")
    start_total = time.time()
    
    # We use a ThreadPoolExecutor to spawn 10 concurrent threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # submit all 10 requests at the exact same time
        futures = [executor.submit(make_request, i) for i in range(1, 11)]
        
        # wait for them to complete and print results
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            
    print(f"✅ All 10 concurrent requests finished in {time.time() - start_total:.2f} seconds total!")
