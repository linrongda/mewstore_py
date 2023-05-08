import datetime
import jwt
from project.config import JWT_SECRET_KEY, JWT_EXPIRATION_DELTA

def generate_token(user):
    payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
               'id': user.id, 'status': user.status}
    # 生成JWT令牌
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token