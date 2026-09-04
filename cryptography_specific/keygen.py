from coincurve import PrivateKey

PRIVATE_KEY_FUNCTION_CALL = PrivateKey()
PRIVATE_KEY = PRIVATE_KEY_FUNCTION_CALL.secret.hex()
PUBLIC_KEY = PRIVATE_KEY_FUNCTION_CALL.public_key_xonly.format().hex()

print(f"Private key: {PRIVATE_KEY}")
print(f"Public key:  {PUBLIC_KEY}")