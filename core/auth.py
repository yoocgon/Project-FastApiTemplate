
import secrets
import random


from pwdlib import PasswordHash

# jwt rolling key store
keys = {}
kids = []
# user password hash
password_hash = None


def init():
    #
    global keys
    global password_hash    
    #
    keys = {}
    #
    for i in range(0, 10):
        kid = str(i)
        secret_key = secrets.token_hex(32)
        keys[kid] = secret_key
    #
    password_hash = PasswordHash.recommended()


def get_recommand_kid():
    #
    i = random.randint(0, len(keys))
    return str(i), keys[str(i)]


