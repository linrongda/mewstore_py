# import qiniu
#
# accessKey = "FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b"
# secretKey = "UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9"
#

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

# def upload(bucket, path, filename, key):
#     token = key.upload_token(bucket, filename, 3600)
#     print('正在上传..')
#     reform, inform = qiniu.put_file(token, filename, path)
#     # if reform != None:
#     #     print('已经成功地将{}->>{}'.format(filename, bucket))
#     # else:
#     #     print('这里出现了一个小错误.')
#     print(reform['key'])
#
#
# def main():
#     bucket = "mewstore"
#     Path = "/Users/Administrator/PycharmProjects/pythonProject/t.png"
#     upload(bucket, Path, None, qiniu.Auth(accessKey, secretKey))
#
#
# if __name__ == "__main__":
#     main()
# q = qiniu.Auth(accessKey, secretKey)
# #初始化BucketManager
# bucket = qiniu.BucketManager(q)
# #你要测试的空间， 并且这个key在你空间中存在
# bucket_name = 'mewstore'
# key = 'FgQuh8Z8hTTTHt4pMtSlsiugZfHk'
# #获取文件的状态信息
# ret, info = bucket.stat(bucket_name, key)
# print(info)
# Path = "/Users/Administrator/PycharmProjects/pythonProject/t.png"
# print(qiniu.etag(Path))

from snowflake import id_generate

print(id_generate(1,1))
