import random
import math
from typing import Tuple, Dict

class RSA:
    def __init__(self, key_size=512):
        """Initialize RSA encryption with a given key size"""
        self.key_size = key_size
        self.public_key = None  # (e, n)
        self.private_key = None  # (d, n)
        self.other_public_keys = {}  # Store other users' public keys {username: (e, n)}
        
    def generate_keys(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Generate public and private key pair"""
        # Step 1: Choose two prime numbers p and q
        p = self._generate_prime(self.key_size // 2)
        q = self._generate_prime(self.key_size // 2)
        
        # Step 2: Compute n = p * q
        n = p * q
        
        # Step 3: Compute Carmichael's totient function λ(n)
        # For RSA, λ(n) = lcm(p-1, q-1)
        lambda_n = self._lcm(p - 1, q - 1)
        
        # Step 4: Choose an integer e such that 1 < e < λ(n) and gcd(e, λ(n)) = 1
        e = self._find_e(lambda_n)
        
        # Step 5: Compute d as the modular multiplicative inverse of e modulo λ(n)
        d = self._mod_inverse(e, lambda_n)
        
        # Set public and private keys
        self.public_key = (e, n)
        self.private_key = (d, n)
        
        return self.public_key, self.private_key
    
    def add_public_key(self, username: str, public_key: Tuple[int, int]) -> None:
        """Store another user's public key"""
        self.other_public_keys[username] = public_key
    
    def encrypt(self, message: str, public_key: Tuple[int, int]) -> list:
        """Encrypt a message using a public key"""
        e, n = public_key
        # Convert message to a list of integers (each character's ASCII value)
        # Then encrypt each integer with the formula: c = m^e mod n
        encrypted = [pow(ord(char), e, n) for char in message]
        return encrypted
    
    def decrypt(self, encrypted_message: list) -> str:
        """Decrypt a message using own private key"""
        if not self.private_key:
            raise ValueError("Private key not generated")
        
        d, n = self.private_key
        # Decrypt each number and convert back to character
        # Using the formula: m = c^d mod n
        decrypted = ''.join([chr(pow(char, d, n)) for char in encrypted_message])
        return decrypted
    
    def encrypt_for_user(self, message: str, username: str) -> list:
        """Encrypt a message for a specific user using their public key"""
        if username not in self.other_public_keys:
            raise ValueError(f"Public key for user {username} not found")
        
        return self.encrypt(message, self.other_public_keys[username])
    
    def _is_prime(self, n: int, k: int = 5) -> bool:
        """Miller-Rabin primality test"""
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False
        
        # Find r and s where n-1 = 2^s * r
        r, s = n - 1, 0
        while r % 2 == 0:
            r //= 2
            s += 1
        
        # Witness loop
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, r, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def _generate_prime(self, bits: int) -> int:
        """Generate a prime number with a specific bit length"""
        while True:
            # Generate a random odd number with the specified bit length
            p = random.getrandbits(bits) | (1 << bits - 1) | 1
            if self._is_prime(p):
                return p
    
    def _gcd(self, a: int, b: int) -> int:
        """Compute the greatest common divisor of a and b"""
        while b:
            a, b = b, a % b
        return a
    
    def _lcm(self, a: int, b: int) -> int:
        """Compute the least common multiple of a and b"""
        return a * b // self._gcd(a, b)
    
    def _find_e(self, lambda_n: int) -> int:
        """Find a suitable e value"""
        # Common choice for e is 65537 (a prime number)
        e = 65537
        # Make sure e is coprime with lambda_n
        while self._gcd(e, lambda_n) != 1:
            e += 2
        return e
    
    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean Algorithm to find gcd and Bézout coefficients"""
        if a == 0:
            return b, 0, 1
        else:
            gcd, x1, y1 = self._extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
    
    def _mod_inverse(self, e: int, lambda_n: int) -> int:
        """Find the modular multiplicative inverse of e modulo lambda_n"""
        gcd, x, y = self._extended_gcd(e, lambda_n)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        else:
            return x % lambda_n
