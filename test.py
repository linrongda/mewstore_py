import qiniu

accessKey = "FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b"
secretKey = "UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9"


# # 解析结果
# def parseRet(retData, respInfo):
#     if retData != None:
#         print("Upload file success!")
#         print("Hash: " + retData["hash"])
#         print("Key: " + retData["key"])
#
#         # 检查扩展参数
#         for k, v in retData.items():
#             if k[:2] == "x:":
#                 print(k + ":" + v)
#
#         # 检查其他参数
#         for k, v in retData.items():
#             if k[:2] == "x:" or k == "hash" or k == "key":
#                 continue
#             else:
#                 print(k + ":" + str(v))
#     else:
#         print("Upload file failed!")
#         print("Error: " + respInfo.text_body)
#
#
# # 无key上传，http请求中不指定key参数
# def upload_without_key(bucket, filePath):
#     # 生成上传凭证
#     auth = qiniu.Auth(accessKey, secretKey)
#     upToken = auth.upload_token(bucket, key=None)
#
#     # 上传文件
#     retData, respInfo = qiniu.put_file(upToken, None, filePath)
#
#     # 解析结果
#     parseRet(retData, respInfo)
#
#
# def main():
#     bucket = "mewstore"
#     filePath = "/Users/Administrator/PycharmProjects/pythonProject/4/music/晴天-周杰伦.mp3"
#     upload_without_key(bucket, filePath)
#
#
# if __name__ == "__main__":
#     main()
def upload(bucket, path, filename, key):
    token = key.upload_token(bucket, filename, 3600)
    print('正在上传..')
    reform, inform = qiniu.put_file(token, filename, path)
    if reform != None:
        print('已经成功地将{}->>{}'.format(filename, bucket))
    else:
        print('这里出现了一个小错误.')


def main():
    bucket = "mewstore"
    Path = "/Users/Administrator/PycharmProjects/pythonProject/1.py"
    upload(bucket, Path, 'profile_photo/1.py', qiniu.Auth(accessKey, secretKey))


if __name__ == "__main__":
    main()
