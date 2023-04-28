from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# engine = create_engine("mysql+pymysql://mew_store:114514@106.14.35.23:3306/mew_store", echo=True)
engine = create_engine("mysql+pymysql://root:123456@localhost:3306/mewfish", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    nickname = Column(String(50))
    name = Column(String(50))
    profile_photo = Column(String(50))
    password = Column(String(50))
    phone_number = Column(String(50))
    money = Column(Integer)
    status = Column(Integer)    # 0为正常用户，1为黑户，2为被冻结状态，3为管理员

    def __repr__(self):
        ID = self.id
        NICKNAME = self.nickname
        NAME = self.name
        PROFILE_PHOTO = self.profile_photo
        PASSWORD = self.password
        PHONE_NUMBER = self.phone_number
        STATUS = self.status
        MONEY = self.money
        return f"User:id:{ID},nickname:{NICKNAME},name:{NAME},profile_photo:{PROFILE_PHOTO}," \
               f"password:{PASSWORD},phone_number：{PHONE_NUMBER}，status:{STATUS}," \
               f"money:{MONEY}"


class Good(Base):
    __tablename__ = "good"
    id = Column(Integer, primary_key=True)
    content = Column(String(50))    # 账号简介
    game = Column(String(50))   # 游戏
    title = Column(String(50))  # 账号标题
    account = Column(String(50))    # 账号
    password = Column(String(50))   # 账号密码
    status = Column(Integer)    # 商品状态未审核为0，审核通过为1，审核不通过为-1,被下架为2，已售出为3
    sell_id = Column(Integer)   # 卖家id

    def __repr__(self):
        ID = self.id
        CONTENT = self.content
        GAME = self.game
        TITLE = self.title
        ACCOUNT = self.account
        PASSWORD = self.account
        SELL_ID = self.sell_id
        return f"Good:id:{ID},content:{CONTENT},game:{GAME},title:{TITLE},account:{ACCOUNT}," \
               f"password:{PASSWORD},sell_id:{SELL_ID}"


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    view = Column(Integer)  # 点击量
    status = Column(Integer)    # 订单存在为1，不存在为0，被收藏为2
    buyer_id = Column(Integer)  # 买方id
    seller_id = Column(Integer)     # 卖方id
    good_id = Column(Integer)   # 商品id
    buyer_status = Column(Integer)  # 买方付款为1，未付款为0
    seller_status = Column(Integer)  # 卖方确认订单为1，未确认为0
    money = Column(Integer)     # 价格

    def __repr__(self):
        ID = self.id
        VIEW = self.view
        STATUS = self.status
        BUYER_ID = self.buyer_id
        SELLER_ID = self.seller_id
        GOOD_ID = self.good_id
        BUYER_STATUS = self.buyer_status
        SELLER_STATUS = self.seller_status
        MONEY = self.money
        return f"Order:id:{ID},view:{VIEW},status:{STATUS},buyer_id:{BUYER_ID},seller_id:{SELLER_ID}," \
               f"good_id:{GOOD_ID},buyer_status:{BUYER_STATUS},seller.status:{SELLER_STATUS},money:{MONEY}"


class Report(Base):
    __tablename__ = "report"
    id = Column(Integer, primary_key=True)  # 举报信息的id
    report_id = Column(Integer)     # 被举报者的id
    status = Column(Integer)     # 举报信息的处理情况，-1为未通过，0为未处理，1为通过举报
    send_id = Column(Integer)  # 举报者的id
    content = Column(String(50))  # 举报的原因和描述

    def __repr__(self):
        ID = self.id
        REPORT_ID = self.report_id
        STATUS = self.status
        SEND_ID = self.send_id
        CONTENT = self.content
        return f"Report:id:{ID},report_id:{REPORT_ID},status:{STATUS},send_id:{SEND_ID}," \
               f"content:{CONTENT}"

# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)