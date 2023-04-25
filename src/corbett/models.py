from pynamodb.models import Model as DynamoModel
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from corbett import config
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Connection(DynamoModel):
    class Meta:
        table_name = config.connection_table_name
        region = config.region

    user_id = UnicodeAttribute(hash_key=True)
    app_id = UnicodeAttribute(range_key=True)
    app_type = UnicodeAttribute()
    api_key_hash = UnicodeAttribute()
    credentials_encrypted = UnicodeAttribute(null=True)
    created_at = UTCDateTimeAttribute()

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "app_id": str(self.app_id),
            "app_type": self.app_type,
            "created_at": self.created_at,
            "credentials": self.credentials_encrypted is not None,
        }

    def check_api_key(self, api_key):
        pwhasher = PasswordHasher(
            time_cost=1, memory_cost=8, parallelism=1, salt_len=8, hash_len=32
        )
        try:
            pwhasher.verify(self.api_key_hash, api_key)
            return True
        except VerifyMismatchError:
            return False
