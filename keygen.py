from coincurve import PrivateKey

private_key = PrivateKey().secret.hex()
input(private_key.secret.hex())
public_key = private_key.public_key_xonly.hex()

print(f"Private key: {private_key.secret.hex()}")
print(f"Public key:  {public_key}")
