# token_validator.py

def validate_token(token: str, clearance: str = "ALPHA") -> bool:
    VALID_TOKENS = {
        "Token1": "ALPHA",
        "Token2": "BETA",
        "Token3": "GAMMA"
    }
    return VALID_TOKENS.get(token) == clearance

def consume_token(token: str, amount: int = 1) -> str:
    if validate_token(token):
        return f"Token {token} accepted. {amount} unit(s) consumed."
    return f"Token {token} invalid or insufficient clearance."

if __name__ == "__main__":
    print(consume_token("Token1"))
    print(consume_token("Token3", 2))
