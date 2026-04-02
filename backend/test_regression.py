import urllib.request, json, time

BASE_URL = "http://localhost:8000/query"

def wait_for_server():
    print("Waiting for server to be ready...")
    for i in range(15):
        try:
            # Simple probe
            data = json.dumps({"query": "health check"}).encode()
            req = urllib.request.Request(BASE_URL, method="POST",
                  headers={"Content-Type": "application/json"}, data=data)
            urllib.request.urlopen(req, timeout=5)
            print("Server is UP!")
            return True
        except:
            time.sleep(2)
    print("Server failed to start.")
    return False

def ask(label, query, expected_contains=None):
    try:
        data = json.dumps({"query": query}).encode()
        req = urllib.request.Request(BASE_URL, method="POST",
              headers={"Content-Type": "application/json"}, data=data)
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
        answer = res.get("answer", "")
        
        if isinstance(expected_contains, str):
            expectations = [expected_contains]
        else:
            expectations = expected_contains

        status = "PASS"
        if expectations:
            any_matched = False
            for exp in expectations:
                if exp.lower() in answer.lower():
                    any_matched = True
                    break
            if not any_matched:
                status = "FAIL"
        
        print(f"[{status}] {label}")
        print(f"  Q: {query}")
        print(f"  A: {answer}")
    except Exception as e:
        print(f"[RETRYING] {label} - {e}")
        time.sleep(2)
        try:
             # One retry for stability
             data = json.dumps({"query": query}).encode()
             req = urllib.request.Request(BASE_URL, method="POST",
                   headers={"Content-Type": "application/json"}, data=data)
             res = json.loads(urllib.request.urlopen(req, timeout=30).read())
             answer = res.get("answer", "")
             status = "PASS"
             # re-check expectations
             any_matched = False
             for exp in (expectations if isinstance(expectations, list) else [expectations]):
                 if exp.lower() in answer.lower(): any_matched = True; break
             if not any_matched: status = "FAIL"
             print(f"[{status}] {label} (RETRY SUCCESS)")
             print(f"  A: {answer}")
        except Exception as e2:
             print(f"[ERROR] {label}: {e2}")

if wait_for_server():
    print("\n--- STARTING EXHAUSTIVE RAG STRESS TEST ---")
    ask("TC-01: 49F chol 180 (Should be YES)", "Does the 49-year-old female with cholesterol 180 have heart disease?", "yes")
    ask("TC-02: 37M man chol 207 (Should be YES)", "Tell me about the 37-year-old man with 207 cholesterol. Heart disease?", "yes")
    ask("TC-03: 54F lady chol 273 (Should be NO)", "Does the 54-year-old lady with 273 cholesterol have heart disease?", "no")
    ask("TC-04: Multiple 38F with 0 Chol", "Tell me about the 38-year-old female patients with 0 cholesterol.", ["38", "female", "0", "exist", "yes"])
    ask("TC-05: Total count", "How many patients are in the dataset in total?", "918")
    ask("TC-06: Count with HD", "How many patients have heart disease?", "508")
    ask("TC-11: 40M with 0 Chol (Should be YES?)", "Does the 40-year-old male with 0 cholesterol have heart disease?", "yes")
    ask("TC-12: 28-year-old (Youngest)", "Does the 28-year-old patient have heart disease?", "no")
    ask("TC-15: Off-topic block", "What is the capital of Japan?", ["country", "dataset", "cannot", "only"])
    ask("TC-18: Average HD (Distribution)", "What is the distribution of heart disease?", ["508", "918", "out of"])
    ask("TC-19: 40M chol 289", "Does the 40-year-old male with cholesterol 289 have heart disease?", "no")
    print("\n--- TEST COMPLETE ---")
