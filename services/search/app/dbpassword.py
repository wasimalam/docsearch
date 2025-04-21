import bcrypt

# Hashing a password
password = "my_secure_password".encode('utf-8')
password_hash = bcrypt.hashpw(password, bcrypt.gensalt())

print("Password Hash:", password_hash.decode('utf-8'))

# Verifying a password
password_to_check = "my_secure_password".encode('utf-8')
if bcrypt.checkpw(password_to_check, password_hash):
    print("Password matches")
else:
    print("Password does not match")
