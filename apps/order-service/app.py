
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.request
import uuid


PAYMENT_SERVICE_URL = "http://localhost:8000/payments"


class OrderHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, response):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(
            json.dumps(response).encode()
        )

    def do_GET(self):

        if self.path == "/health":

            response = {
                "service": "order-processing",
                "status": "healthy"
            }

            self.send_json(200, response)

        else:

            self.send_json(
                404,
                {"error": "Not found"}
            )

    def do_POST(self):

        if self.path == "/orders":

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            try:
                request = json.loads(body)

                amount = request.get("amount")

                if amount is None:
                    self.send_json(
                        400,
                        {"error": "amount is required"}
                    )
                    return

                order_id = str(uuid.uuid4())

                payment_payload = {
                    "order_id": order_id,
                    "amount": amount
                }

                payment_data = json.dumps(
                    payment_payload
                ).encode()

                payment_request = urllib.request.Request(
                    PAYMENT_SERVICE_URL,
                    data=payment_data,
                    headers={
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(
                    payment_request,
                    timeout=5
                ) as response:

                    payment_response = json.loads(
                        response.read().decode()
                    )

                response = {
                    "order_id": order_id,
                    "amount": amount,
                    "status": "created",
                    "payment": payment_response,
                    "service": "order-processing"
                }

                self.send_json(200, response)

            except Exception as error:

                self.send_json(
                    502,
                    {
                        "error": "Order service unavailable",
                        "details": str(error)
                    }
                )

        else:

            self.send_json(
                404,
                {"error": "Not found"}
            )


server = HTTPServer(
    ("0.0.0.0", 8001),
    OrderHandler
)

print("order-service running on port 8001")

server.serve_forever()

