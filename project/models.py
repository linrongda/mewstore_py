from exts import db  # 奇怪的db导入方法，我也不知道为什么，但是这样用就对了


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.BigInteger, primary_key=True)  # 用户id
    nickname = db.Column(db.String(50))  # 昵称
    username = db.Column(db.String(50))  # 用户名
    profile_photo = db.Column(db.String(56))  # 头像
    password = db.Column(db.String(102))  # 密码
    phone_number = db.Column(db.String(11))  # 手机号
    money = db.Column(db.Numeric(20, 2))  # 余额
    status = db.Column(db.Integer)  # 0为正常用户，1为黑户，2为被冻结状态，3为管理员
    name = db.Column(db.String(50))  # 真实姓名
    id_card = db.Column(db.String(18))  # 身份证号


class Good(db.Model):
    __tablename__ = "good"
    id = db.Column(db.BigInteger, primary_key=True)
    view = db.Column(db.Integer)  # 收藏量
    game = db.Column(db.String(50))  # 游戏，目前有“王者荣耀”、“英雄联盟”、“原神”、“绝地求生”、“和平精英”、“第五人格”，6款游戏
    title = db.Column(db.String(50))  # 账号标题
    content = db.Column(db.Text)  # 账号简介
    picture = db.Column(db.Text)  # 商品图片
    account = db.Column(db.String(50))  # 账号
    password = db.Column(db.String(50))  # 账号密码
    add_time = db.Column(db.TIMESTAMP)  # 添加时间
    status = db.Column(db.Integer)  # 商品状态未审核为0，审核通过为1，审核不通过为-1,被下架为2，已售出或已出价为3
    seller_id = db.Column(db.BigInteger)  # 卖家id
    price = db.Column(db.Numeric(10, 2))  # 价格


# class Orders(db.Model):
#     __tablename__ = "orders"
#     id = db.Column(db.BigInteger, primary_key=True)
#     status = db.Column(db.Integer)  # 订单存在为1，不存在为0
#     buyer_id = db.Column(db.BigInteger)  # 买方id
#     seller_id = db.Column(db.BigInteger)  # 卖方id
#     good_id = db.Column(db.BigInteger)  # 商品id
#     generate_time = db.Column(db.TIMESTAMP)  # 生成订单的时间
#     buyer_status = db.Column(db.Integer)  # 买方付款为1，未付款为0
#     seller_status = db.Column(db.Integer)  # 卖方确认订单为1，未确认为0,拒绝为-1
#     price = db.Column(db.Numeric(10, 2))  # 价格


# class Report(db.Model):
#     __tablename__ = "report"
#     id = db.Column(db.BigInteger, primary_key=True)  # 举报信息的id
#     reported_id = db.Column(db.BigInteger)  # 被举报者的id
#     report_order = db.Column(db.BigInteger)  # 被举报的订单
#     reporter_id = db.Column(db.BigInteger)  # 举报者的id
#     status = db.Column(db.Integer)  # 举报信息的处理情况，-1为未通过，0为未处理，1为通过举报
#     content = db.Column(db.Text)  # 举报的原因和描述
#     type = db.Column(db.Integer)  # 举报的类型


class Favorite(db.Model):
    __tablename__ = "favorite"
    user_id = db.Column(db.BigInteger, primary_key=True)  # 用户id
    good_id = db.Column(db.BigInteger, primary_key=True)  # 商品id


class Messages(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.BigInteger, primary_key=True)  # 消息id
    isSystem = db.Column(db.Boolean)  # 是否为系统消息，0为否，1为是
    send_id = db.Column(db.BigInteger)  # 发送者id
    receive_id = db.Column(db.BigInteger)  # 接收者id
    message = db.Column(db.Text)  # 消息内容
    send_time = db.Column(db.TIMESTAMP)  # 发送时间
    type = db.Column(db.Integer)  # 消息类型，0为文本，1为图片
    is_read = db.Column(db.Boolean)  # 是否已读，0为否，1为是

# with app.app_context(): #使用架构时不需要此代码
#     # db.drop_all()  # 初始化表格，需要时再用
#     db.create_all()
