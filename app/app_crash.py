import time

print("checkout-api crash test starting")

time.sleep(5)

print("checkout-api crash test: intentional failure")

raise RuntimeError("Intentional crash for incident simulation")