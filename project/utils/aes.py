# 设置AES加密
from Crypto.Cipher import AES
import base64

# 加密密钥
key = b'mewstoremewstore'
# 初始化向量
iv = b'mewstoremewstore'


# 使用 CBC 模式进行加密
def encrypt(data):
    # 将加密内容填充到16的倍数
    length = 16 - (len(data.encode()) % 16)  # data可能是含中文，而中文字符utf-8编码占3个位置，所以需要以len(s.encode())，而不是len(s)计算补码
    data += chr(length) * length
    # 创建加密器
    aes = AES.new(key, AES.MODE_CBC, iv)
    # 加密数据
    encrypted_data = aes.encrypt(data.encode('utf-8'))
    # 将加密结果进行 base64 编码
    return base64.b64encode(encrypted_data).decode('utf-8')


# 使用 CBC 模式进行解密
def decrypt(encrypted_data):
    # 将加密结果进行 base64 解码
    encrypted_data = base64.b64decode(encrypted_data)
    # 创建解密器
    aes = AES.new(key, AES.MODE_CBC, iv)
    # 解密数据
    decrypted_data = aes.decrypt(encrypted_data)
    # 将解密结果进行去填充操作
    return decrypted_data[:-decrypted_data[-1]].decode('utf-8')
