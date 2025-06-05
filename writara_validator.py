from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json, os
from dotenv import load_dotenv
import stripe

load_dotenv()
app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class TokenValidator:
    VALID_SEAL = "†Ω†Ωᛜ•҂⛽"
    def __init__(self):
        self.tokens = {
            "Token1": {"clearance": "ALPHA", "seal": self.VALID_SEAL, "fuel": 100, "last_refuel": datetime.utcnow(), "refill_rate": 5, "expires": "2025-12-31", "renewable": True, "signature": "K-VALID-0001A"},
            "Token2": {"clearance": "ALPHA", "seal": self.VALID_SEAL, "fuel": 80, "last_refuel": datetime.utcnow(), "refill_rate": 5, "expires": "2025-12-31", "renewable": True, "signature": "K-VALID-0002B"},
            "Token3": {"clearance": "BETA", "seal": self.VALID_SEAL, "fuel": 70, "last_refuel": datetime.utcnow(), "refill_rate": 4, "expires": "2025-12-31", "renewable": True, "signature": "K-VALID-0003C"},
            "Token4": {"clearance": "BETA", "seal": self.VALID_SEAL, "fuel": 70, "last_refuel": datetime.utcnow(), "refill_rate": 4, "expires": "2025-12-31", "renewable": True, "signature": "K-VALID-0004D"},
            "Token5": {"clearance": "GAMMA", "seal": self.VALID_SEAL, "fuel": 60, "last_refuel": datetime.utcnow(), "refill_rate": 3, "expires": "2025-12-31", "renewable": True, "signature": "K-VALID-0005E"}
        }
        self.log_file = "command_log.json"

    def validate_token(self, token_name, signature):
        token = self.tokens.get(token_name)
        if token and token["seal"] == self.VALID_SEAL and token["signature"] == signature:
            expiry = datetime.strptime(token["expires"], "%Y-%m-%d")
            return expiry >= datetime.utcnow()
        return False

    def get_clearance(self, token_name):
        return self.tokens.get(token_name, {}).get("clearance")

    def consume_fuel(self, token_name, amount):
        token = self.tokens.get(token_name)
        if not token:
            return False
        self._refill_token(token_name)
        if token["fuel"] >= amount:
            token["fuel"] -= amount
            self._log(token_name, "consume", amount)
            return True
        return False

    def get_fuel(self, token_name):
        self._refill_token(token_name)
        return self.tokens.get(token_name, {}).get("fuel")

    def renew_token(self, token_name):
        token = self.tokens.get(token_name)
        if token and token.get("renewable"):
            token["expires"] = (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%d")
            self._log(token_name, "renew", 0)
            return True
        return False

    def refuel(self, token_name, amount):
        token = self.tokens.get(token_name)
        if token:
            token["fuel"] += amount
            self._log(token_name, "refuel", amount)
            return True
        return False

    def _refill_token(self, token_name):
        token = self.tokens.get(token_name)
        if not token:
            return
        now = datetime.utcnow()
        minutes_passed = (now - token["last_refuel"]).total_seconds() / 60
        units = int(minutes_passed // 60) * token["refill_rate"]
        if units > 0:
            token["fuel"] += units
            token["last_refuel"] = now

    def _log(self, token, action, amount):
        entry = {"token": token, "action": action, "amount": amount, "timestamp": datetime.utcnow().isoformat()}
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Log failed: {e}")

    def get_logs(self):
        try:
            with open(self.log_file, "r") as f:
                return [json.loads(line.strip()) for line in f]
        except:
            return []

validator = TokenValidator()

@app.route("/validate", methods=["GET"])
def validate():
    token = request.args.get("token")
    signature = request.args.get("signature")
    if validator.validate_token(token, signature):
        return jsonify({"valid": True, "clearance": validator.get_clearance(token)})
    return jsonify({"valid": False}), 403

@app.route("/fuel", methods=["GET"])
def fuel():
    token = request.args.get("token")
    return jsonify({"fuel": validator.get_fuel(token)})

@app.route("/consume", methods=["POST"])
def consume():
    data = request.json
    token = data.get("token")
    amount = int(data.get("amount", 0))
    if validator.consume_fuel(token, amount):
        return jsonify({"status": "success"})
    return jsonify({"status": "insufficient fuel"}), 403

@app.route("/refuel", methods=["POST"])
def refuel():
    data = request.json
    token = data.get("token")
    amount = int(data.get("amount", 0))
    if validator.refuel(token, amount):
        return jsonify({"status": "success", "new_fuel": validator.get_fuel(token)})
    return jsonify({"status": "invalid token"}), 403

@app.route("/clearance", methods=["GET"])
def clearance():
    token = request.args.get("token")
    return jsonify({"clearance": validator.get_clearance(token)})

@app.route("/renew_token", methods=["POST"])
def renew():
    data = request.json
    token = data.get("token")
    if validator.renew_token(token):
        return jsonify({"status": "renewed"})
    return jsonify({"status": "not renewable"}), 403

@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(validator.get_logs())

@app.route("/pay", methods=["GET", "POST"])
def pay():
    if request.method == "POST":
        data = request.json
        token = data.get("token")
        amount = int(data.get("amount", 10))
        try:
            payment = stripe.PaymentIntent.create(
                amount=amount * 5000 // 100,  # $50 per 100 fuel units
                currency="usd",
                description=f"Writara Fuel Recharge: {token}",
                payment_method_types=["card"],
            )
            if validator.refuel(token, amount):
                return jsonify({"client_secret": payment.client_secret})
            return jsonify({"error": "Invalid token"}), 403
        except stripe.error.StripeError as e:
            return jsonify({"error": str(e)}), 400
    return """
    <title>Writara Fuel Payment Portal</title>
    <style>
        body { font-family: Arial; text-align: center; }
        form { margin: 20px auto; max-width: 400px; }
        input, button { margin: 10px; padding: 8px; width: 200px; }
        button { background: #28a745; color: white; border: none; cursor: pointer; }
    </style>
    <h1>Writara Runtime Recharge</h1>
    <p>Recharge fuel credits ($50 per 100 units).</p>
    <form id="payment-form">
        <label>Token: <input id="token" required></label><br>
        <label>Fuel Units: <input id="amount" type="number" min="10" required></label><br>
        <div id="card-element"></div>
        <button type="submit">Pay with Stripe</button>
        <div id="error"></div>
    </form>
    <p><strong>Crypto Options:</strong><br>
    BTC: bc1qexampleaddress0123456789<br>
    ETH: 0xExampleEthAddress123456<br>
    USDT: 0xExampleTetherAddress7890<br>
    Email confirmation to admin@writara.ai</p>
    <script src="https://js.stripe.com/v3/"></script>
    <script>
        const stripe = Stripe('""" + os.getenv("STRIPE_PUBLISHABLE_KEY") + """');
        const elements = stripe.elements();
        const card = elements.create('card');
        card.mount('#card-element');
        document.getElementById('payment-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = document.getElementById('token').value;
            const amount = document.getElementById('amount').value;
            const errorElement = document.getElementById('error');
            try {
                const response = await fetch('/pay', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, amount })
                });
                const data = await response.json();
                if (data.error) {
                    errorElement.textContent = data.error;
                    return;
                }
                const { error, paymentIntent } = await stripe.confirmCardPayment(data.client_secret, {
                    payment_method: { card }
                });
                if (error) {
                    errorElement.textContent = error.message;
                } else {
                    errorElement.textContent = 'Payment successful! Fuel added.';
                }
            } catch (err) {
                errorElement.textContent = 'Payment failed.';
            }
        });
    </script>
    """

if __name__ == "__main__":
    app.run(debug=True)