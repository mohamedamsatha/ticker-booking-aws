
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1/api/book"

def send_booking(number):
    booking = {
        "event_id": 1,
        "customer_name": f"Load Test Customer {number}",
        "customer_email": f"loadtest{number}@example.com",
        "quantity": 1
    }

    data = json.dumps(booking).encode("utf-8")

    request = urllib.request.Request(
        URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())

            return {
                "customer": number,
                "status": response.status,
                "booking_id": result.get("booking_id")
            }

    except Exception as error:
        return {
            "customer": number,
            "status": "FAILED",
            "error": str(error)
        }

with ThreadPoolExecutor(max_workers=100) as executor:
    results = list(executor.map(send_booking, range(1, 101)))

success = sum(1 for r in results if r["status"] == 202)
failed = 100 - success

print("Total Requests:", len(results))
print("Successful:", success)
print("Failed:", failed)

for result in results:
    print(result)

