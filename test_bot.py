import requests
import json

URL = "https://sarafipardis.co.uk/wp-json/pardis/v1/rates"
API_KEY = "PX9k7mN2qR8vL4jH6wE3tY1uI5oP0aS9dF7gK2mN8xZ4cV6bQ1wE3rT5yU8iO0pL"

def send_request(currency, rate):
    payload = {"currency": currency, "rate": rate, "api_key": API_KEY}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        print(f"✅ {currency} sent successfully:")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending {currency}:", e)
    except json.JSONDecodeError:
        print(f"❌ JSON decode error for {currency}")

# توابع مخصوص هر ارز
def send_gbp_buy(rate): return send_request("GBP_BUY", rate)
def send_gbp_sell(rate): return send_request("GBP_SELL", rate)
def send_usdt_buy(rate): return send_request("USDT_BUY", rate)
def send_usdt_sell(rate): return send_request("USDT_SELL", rate)

send_gbp_buy(134000)
send_gbp_sell(143000)
send_usdt_buy(99000)
send_usdt_sell(107000)
