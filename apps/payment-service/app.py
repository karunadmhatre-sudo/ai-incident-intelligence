
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid


class PaymentHandler(BaseHTTPRequestHandler):

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
                "service": "payment-processing",
                "status": "healthy"
            }

            self.send_json(200, response)

        else:

            self.send_json(
                404,
                {"error": "Not found"}
            )

    def do_POST(self):

        if self.path == "/payments":

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            try:
                request = json.loads(body)

                order_id = request.get("order_id")
                amount = request.get("amount")

                if not order_id or amount is None:
                    self.send_json(
                        400,
                        {
                            "error": "order_id and amount are required"
                        }
                    )
                    return

                payment_id = str(uuid.uuid4())

                response = {
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "amount": amount,
                    "status": "approved",
                    "service": "payment-processing"
                }

                self.send_json(200, response)

            except json.JSONDecodeError:

                self.send_json(
                    400,
                    {"error": "Invalid JSON"}
                )

        else:

            self.send_json(
                404,
                {"error": "Not found"}
            )


server = HTTPServer(
    ("0.0.0.0", 8000),
    PaymentHandler
)

print("payment-service running on port 8000")

server.serve_forever()
