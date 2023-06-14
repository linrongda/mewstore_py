# 闲猫MewStore 安卓端ヾ(≧▽≦*)o

> ###### 队伍名：**闲猫吃咸鱼(Android分队)**
>
> 平台名：闲猫MewStore

​        本项目是一个**二手游戏账号交易**平台，主要提供游戏账号交易服务，为玩家提供便利和安全性。本项目前端采用Kotlin原生安卓编写，后端涉及到跨语言，分别为Springboot框架和flask框架编写。

## 合作成员信息

### 安卓端

- ##### 成员： 吴荣榜

- ##### 语言与框架：Kotlin 原生安卓

- ##### 学号：222200314

### 美术

- ##### 成员：马雁语

- ##### 相关软件：XD PS procreate

- ##### 学号：832204101

### 后端

- ##### 成员1：叶宇滟

- ##### 语言与框架：Java (采用Springboot编写)

- ##### 学号：222200307

  

- ##### 成员2：林荣达(本人)

- ##### 语言与框架：Python（Flask）

- ##### 学号：062200237

## 项目仓库地址

Python后端项目地址：https://github.com/linrongda/mewstore_py

## 技术栈

- Flask
- Flask_RESTful
- Flask_SocketIO
- Flask_SQLAlchemy
- PyJWT
- pycryptodome
- pytest
- Faker
- 七牛云SDK
- 阿里云SDK

## 项目目录树

```tree
WorkingDirection/
├────api/
│    ├────b_s_center
│    ├────chat
│    ├────goods
│    ├────home_page
│    └────users
└────utils
```

## 

## 项目亮点

### 技术亮点

+ 接口有较为完备的数据校验
+ 采用相关算法来计算“为你推荐”的游戏商品

### 设计亮点

- 使用雪花算法进行用户、商品等id的设置
- 使用session存储用户短信验证码和时间、实名认证时间
- 用户手机号、实名认证信息、商品游戏密码采用aes加密
- 使用阿里云短信服务进行手机号的验证，通过第三方服务商进行实名认证，使用七牛云存储图片
- 调整pytest各api接口测试顺序以达到一次性完成测试的目的

### 封装亮点

- 不知道（嘿嘿嘿）

## 接口文档
https://console-docs.apipost.cn/preview/9ee328c89b7c6eea/fd7048006ceb2e1f?target_id=8fd76ee6-e270-4026-917b-802fd7970ab5

## 未解决的问题

- pytest未启用flask应用的session，导致后端无法在session中存储验证码等信息，所以相关接口覆盖率不高

## 当前进度

- 剩最后的对接调试

## 加分项

- 支持聊天功能
- 服务安全性能
- 具有高覆盖率的单元测试