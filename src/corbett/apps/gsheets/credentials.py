import json
from corbett.models import Connection
from corbett.services import EncryptionService
from corbett import config


encryption_service = EncryptionService.from_arn(config.secrets_arn)


def get_credentials(event=None, context=None):
    user_id = event['headers']['sf-custom-corbett-user-id']
    app_id = event['headers']['sf-custom-corbett-app-id']
    conn = Connection.get(user_id, app_id)
    decrypted_credentials = json.loads(encryption_service.decrypt(conn.credentials_encrypted))
    return decrypted_credentials
