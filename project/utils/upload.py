import qiniu


def upload_photo(photo):
    access_key = 'FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b'
    secret_key = 'UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9'
    bucket = 'mewstore'
    auth = qiniu.Auth(access_key, secret_key)
    uptoken = auth.upload_token(bucket)
    ret, info = qiniu.put_data(uptoken, None, photo.read())
    return ret['key']
