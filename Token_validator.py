# token_validator.py
def validate_token(token):
    if isinstance(token, str) and token.startswith("WRITARA"):
        return True
    return False

if __name__ == "__main__":
    test_token = "WRITARA-123456789"
    print("Token valid:", validate_token(test_token))
