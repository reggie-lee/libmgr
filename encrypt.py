#!/bin/python3
import random
import string
import crypt

crypt.mksalt('SHA256')

def randomString(stringLength, letters=string.ascii_letters + string.digits):
    """Generate a random string with the combination of lowercase and uppercase letters """
    return ''.join(random.choice(letters) for _ in range(stringLength))

