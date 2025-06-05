
from flask import Flask, request, render_template_string
import hashlib
import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import webbrowser
import threading

app = Flask(__name__)

def generate_secure_key(user_input: str) -> str:
    base_key = hashlib.sha256(user_input.encode()).digest()
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac('sha256', base_key, salt, 100000, dklen=32)
    data_to_encrypt = os.urandom(32)
    cipher = AES.new(derived_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data_to_encrypt, AES.block_size))
    encrypted_blob = base64.b64encode(salt + cipher.iv + ct_bytes).decode('utf-8')
    return encrypted_blob

HTML_TEMPLATE = """
<!doctype html>
<title>ForgeKey Generator</title>
<h2>ForgeKey: Generate Secure Keys</h2>
<form method=post>
  <input type=text name=input placeholder="Enter your secret input" size="40">
  <input type=submit value=Generate>
</form>
{% if key %}
<h3>Generated Key:</h3>
<p><textarea rows="4" cols="80">{{ key }}</textarea></p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    key = None
    if request.method == "POST":
        user_input = request.form["input"]
        key = generate_secure_key(user_input)
    return render_template_string(HTML_TEMPLATE, key=key)

if __name__ == "__main__":
    threading.Timer(1.25, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False)
