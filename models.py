from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean,Double
from sqlalchemy.orm import relationship
from database import Base


class RequestPackage(Base):
    __tablename__ = 'request_packages'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    requests_count = Column(Integer)
    price_per_month = Column(Double)


class UserAgent(Base):
    __tablename__ = 'user_agents'

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, default='25261')
    email = Column(String)
    password = Column(String)
    company_name = Column(String)
    owner_name = Column(String)
    r_package = Column(Integer, ForeignKey('request_packages.id'))
    usage_token=Column(String,nullable=True,default="")

    merchantUid = Column(String)
    apiUserId = Column(String)
    apiKey = Column(String)

    status = Column(Boolean, default=False)
    registred_date = Column(DateTime)


class PaymentInfo(Base):
    __tablename__='subscription_info'
    id = Column(Integer, primary_key=True, index=True)
    user_agent_id = Column(Integer, ForeignKey('user_agents.id'))
    paided_money=Column(Double)
    datetime= Column(DateTime)

class RequestUsage(Base):
    __tablename__ = 'request_usages'
    id = Column(Integer, primary_key=True, index=True)  # Primary key column added
    requested_user_id = Column(Integer, ForeignKey('user_agents.id'))
    type = Column(String)
    status = Column(Integer)
    requested_time = Column(DateTime)


