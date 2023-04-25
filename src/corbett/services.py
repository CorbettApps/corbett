import json
from cryptography.fernet import Fernet


class EncryptionService:
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.fernet = Fernet(self.secret_key)

    @classmethod
    def from_arn(cls, arn: str):
        import boto3
        client = boto3.client('secretsmanager')
        resp = client.get_secret_value(SecretId=arn)
        secret_key = json.loads(resp['SecretString'])['SECRET_KEY']
        return cls(secret_key=secret_key.encode())

    def encrypt(self, data: str) -> str:
        encoded_data = data.encode()
        encrypted_data = self.fernet.encrypt(encoded_data)
        return encrypted_data.decode()
    
    def decrypt(self, data: str) -> str:
        encoded_data = data.encode()
        decrypted_data = self.fernet.decrypt(encoded_data)
        return decrypted_data.decode()
