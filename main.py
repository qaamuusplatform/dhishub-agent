from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta

from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from passlib.context import CryptContext

import models
import schemas
import secrets
import jwt
import httpx
from httpx import ReadTimeout
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# API
# USER-AGENT API
@app.get("/api/agent-user", tags=["USER-AGENT"])
def userAgent(db: Session = Depends(get_db)):
    user_agents = db.query(models.UserAgent).all()
    return user_agents


@app.post("/api/agent-user", status_code=status.HTTP_201_CREATED, tags=["USER-AGENT"])
def userAgentCreate(request: schemas.UserAgent, db: Session = Depends(get_db)):
    print('asd')
    hashed_password = pwd_context.hash(request.password)
    usage_token_generator = generateExpireToken(expire_time=datetime.now()+timedelta(days=90), number=request.number)
    
    new_user = models.UserAgent(
        number=request.number,
        email=request.email,
        password=hashed_password,
        company_name=request.company_name,
        owner_name=request.owner_name,
        usage_token=usage_token_generator,
        r_package=request.r_package,
        merchantUid=request.merchantUid,
        apiUserId=request.apiUserId,
        apiKey=request.apiKey,
        registred_date=request.registred_date
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# REQUESTS-PACKAGES API
@app.get("/api/requests-package", tags=["REQUESTS-PACKAGE"])
def requestsPackage(db: Session = Depends(get_db)):
    requests_packages = db.query(models.RequestPackage).all()
    return requests_packages


@app.post("/api/requests-package", status_code=status.HTTP_201_CREATED, tags=["REQUESTS-PACKAGE"])
def requestsPackageCreate(request: schemas.RequestPackage, db: Session = Depends(get_db)):
    new_package = models.RequestPackage(
        name=request.name,
        requests_count=request.requests_count,
        price_per_month=request.price_per_month
    )
    db.add(new_package)
    db.commit()
    db.refresh(new_package)
    return new_package


# PIPE APIs
@app.post("/api/pipes/sell-for-me",status_code=status.HTTP_202_ACCEPTED,tags=["PIPES API"])
async def sellForMe(request: schemas.SellMeProducts, db: Session = Depends(get_db)):
    user_agent=db.query(models.UserAgent).filter(models.UserAgent.email==request.agent_number_or_email)
    paymentStatus={}
    if db.query(user_agent.exists()).scalar():
        user_agent=user_agent.first()
        print(f'user agent info {user_agent.id}')
        if is_token_expired(token=user_agent.usage_token):
            paymentStatus=await waafiPaidMoney(request=request,userAgent=user_agent)
            if paymentStatus["responseCode"]==2001:
                new_request_usage=models.RequestUsage(
                    requested_user_id=user_agent.id,
                    type="WAAFI-PAYMENT",
                    status=202,
                    requested_time=datetime.now()
                )
                db.add(new_request_usage)
                db.commit()
                db.refresh(new_request_usage)
            else:
                new_request_usage=models.RequestUsage(
                    requested_user_id=user_agent.id,
                    type="WAAFI-PAYMENT",
                    status=406,
                    requested_time=datetime.now()
                )
                db.add(new_request_usage)
                db.commit()
                db.refresh(new_request_usage)
    return {"paided": paymentStatus["responseCode"]==2001 if True else False,"responseCode":paymentStatus["responseCode"],"responseMsg":paymentStatus["responseMsg"],"description":paymentStatus["description"]}

@app.post("/api/pipes/send-me-messages",status_code=status.HTTP_202_ACCEPTED,tags=["PIPES API"])
async def sendMeMessage(request:schemas.SendMeMessages):
    return request

@app.post("/api/pipes/take-charge")
def takeCharge(request: schemas.RequestPackage, db: Session = Depends(get_db)):
    return {}









# EXTRA FUNCTIONS
async def waafiPaidMoney(request: schemas.SellMeProducts,userAgent:schemas.UserAgent):
    print('sadasdas')
    waafiUrl = 'https://api.waafipay.net/asm'
    jsonData = {
        "schemaVersion": "1.0",
        "requestId": "10111331033",
        "timestamp": "client_timestamp",
        "channelName": "WEB",
        "serviceName": "API_PURCHASE",
        "serviceParams": {
            "merchantUid": "M0910291",
            "apiUserId": "1000416",
            "apiKey": "API-675418888AHX",
            "paymentMethod": "mwallet_account",
            "payerInfo": {"accountNo": '252' + request.client_number},
            "transactionInfo": {
                "referenceId": "12334",
                "invoiceId": "7896504",
                "amount": request.p_price,
                "currency": "USD",
                "description": request.p_title+request.p_info
            }
        }
    }
    async with httpx.AsyncClient(timeout=39) as client:
        try:
            headers = {"Content-Type": "application/json"}
            response = await client.post(waafiUrl, json=jsonData, headers=headers)
            response = response.json()
            
            return {"responseCode":response['responseCode'],"responseMsg":response["responseMsg"],"description":response["params"]["description"]}
        except ReadTimeout:
            # Implement fallback behavior or return an appropriate response
            return {"responseCode":"5310","responseMsg":"Time out","description":"Request timed out"}
        except Exception as e:
            # Handle other exceptions or errors
            print("An error occurred:", str(e))
            # Implement fallback behavior or r
            return {"responseCode":"5310","responseMsg":"Handle error","description":f"An error occurred {str(e)}"}















# HTML-TEMPLATES
templates = Jinja2Templates(directory="templates")

@app.get("/", tags=["HTML-TEMPLATES"])
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html",
                                      {"request": request})


@app.get("/register-agent/", tags=["HTML-TEMPLATES"])
def registerAgent(request: Request, db: Session = Depends(get_db)):
    requests_packages = db.query(models.RequestPackage).all()
    return templates.TemplateResponse("/user-agent/register.html",
                                      {"requests_packages": requests_packages, "request": request})


@app.get("/manage-agents/", tags=["HTML-TEMPLATES"])
def manageAgents(request: Request):
    print(generateExpireToken('252616981411', datetime(
        year=2023, month=12, day=15, hour=16, minute=50)))
    return templates.TemplateResponse("/user-agent/list.html",
                                      {"request": request})


@app.get("/manage-packages/", tags=["HTML-TEMPLATES"])
def managePackages(request: Request):
    return templates.TemplateResponse("manage-packages.html",
                                      {"request": request})


SECRET_KEY = secrets.token_urlsafe(32)


def generateExpireToken(number: str, expire_time: datetime):
    try:
        payload = {
            "number": number,
            "exp": expire_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        raise Exception("Error generating token: " + str(e))


def is_token_expired(token: str) -> bool:
    try:
        decoded_token = jwt.decode(token, verify=False)
        exp_timestamp = decoded_token.get('exp')

        if exp_timestamp is None:
            raise jwt.DecodeError('Expiration time (exp) not found in token')

        current_timestamp = datetime.utcnow().timestamp()
        return current_timestamp > exp_timestamp

    except jwt.ExpiredSignatureError:
        return True
    except jwt.DecodeError:
        return True
    except jwt.InvalidTokenError:
        return True
