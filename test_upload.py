import requests

print("=== API ENDPOINT TESTS ===")
print()

print("Test 1 - Health check:")
r = requests.get("http://localhost:8000/api/v1/health")
print(r.json())
print()

print("Test 2 - Upload PDF:")
with open("data/uploads/test.pdf", "rb") as f:
    r = requests.post(
        "http://localhost:8000/api/v1/upload/file",
        files={"file": ("test.pdf", f, "application/pdf")}
    )
print(r.json())
print()

print("Test 3 - Ask a question:")
r = requests.post(
    "http://localhost:8000/api/v1/query",
    json={"question": "What is the purpose of point and figure charts?", "n_results": 5}
)
result = r.json()
print("Answer: " + result["answer"][:300])
print("Citations: " + str(len(result["citations"])) + " sources found")
print()

print("Test 4 - Clear session:")
r = requests.post("http://localhost:8000/api/v1/session/clear")
print(r.json())
print()

print("=== ALL TESTS COMPLETE ===")
