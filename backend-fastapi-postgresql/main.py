from fastapi import FastAPI, HTTPException, Depends, Response, status
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from utils import VerifyToken
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse, HTMLResponse
import qrcode
import io
import requests
from fastapi.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime






app = FastAPI()
token_auth_scheme = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.add_middleware(SessionMiddleware, secret_key = "duje")


models.Base.metadata.create_all(bind=engine)


class TicketBase(BaseModel):
    vatin: str
    firstName: str
    lastName: str
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

   
# POST - create a ticket
@app.post("/createTicket")
async def create_ticket(response: Response, ticket: TicketBase, db: db_dependency, token: str = Depends(token_auth_scheme)):

    result = VerifyToken(token.credentials).verify()

    if result.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    
    #Check if there are already 3 tickets with the same VATIN
    tickets = db.query(models.Ticket).all()
    if len([t for t in tickets if t.vatin == ticket.vatin]) == 3:
        return JSONResponse(
            content={"error": "There have already been 3 issued tickets with the same VATIN"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    db_ticket = models.Ticket(vatin=ticket.vatin, firstName=ticket.firstName, lastName=ticket.lastName)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    ticket_url = f"http://localhost:8000/ticket/{db_ticket.id}"
    qr = qrcode.make(ticket_url)

    img_io = io.BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")


      
# GET - get ticket info
@app.get("/ticket/{ticket_id}", response_class=HTMLResponse)
async def get_ticket(request: Request,ticket_id: str, db: db_dependency):
    if "access_token" in request.session:
        access_token = request.session["access_token"]
        user_info_response = requests.get(
            f"https://dev-2anuorhsrl8w0pl6.us.auth0.com/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
            if db_ticket is None:
                raise HTTPException(status_code=404, detail="Ticket not found")
            time_created_str = db_ticket.timeCreated.isoformat() if isinstance(db_ticket.timeCreated, datetime) else str(db_ticket.timeCreated)
            return f"""
            <html>
                <head>
                    <title>Ticket</title>
                </head>
                <body>
                    <h1>Ticket info:</h1>
                    <h2>User Email: {user_info.get("email")}</h2>
                    <h2>VATIN: {db_ticket.vatin}</h2>
                    <h2>First name: {db_ticket.firstName}</h2>
                    <h2>Last name: {db_ticket.lastName}</h2>
                    <h2>Time created: {time_created_str}</h2>
                </body>
            </html>
            """
    
        else:
            return JSONResponse(content={"error": "Failed to fetch user info"}, status_code=400)

    else:
        return f"""
            <html>
                <head>
                    <title>Ticket</title>
                </head>
                <body>
                    <h2>Not logged in, please login to see ticket info.</h2>
                </body>
            </html>
            """
    
                                     

@app.get("/login")
def login():
    return RedirectResponse(
        "https://dev-2anuorhsrl8w0pl6.us.auth0.com/authorize"
        "?response_type=code"
        "&client_id=tYx7tPwwh87UPikur8s11We0K63tFmDt"
        "&redirect_uri=http://localhost:8000/home"
        "&audience=http://localhost:8000/"
        "&scope=offline_access openid profile email"
    )

@app.get("/home", response_class=HTMLResponse)
def home(request: Request, db: db_dependency, code: str = None):

    if code:
        payload = {
            "grant_type": "authorization_code",
            "client_id": "tYx7tPwwh87UPikur8s11We0K63tFmDt",
            "client_secret": "AWIDzmJFZg_6WUzDivFFWbf7L65zdiyuxhjfUzJ5kBMUHFOVW0wdLyX53rvxdcHA",
            "code": code,
            "redirect_uri": "http://localhost:8000/home"
        }

        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://dev-2anuorhsrl8w0pl6.us.auth0.com/oauth/token", data = payload, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            request.session["access_token"] = token_data["access_token"]
            return RedirectResponse(f"/home")
        else:
            return JSONResponse(content=response.json(), status_code=response.status_code)
    
    

    total_tickets = db.query(models.Ticket).count()
    

    if "access_token" in request.session:
        access_token = request.session["access_token"]
        user_info_response = requests.get(
            f"https://dev-2anuorhsrl8w0pl6.us.auth0.com/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            return f"""
            <html>
                <head>
                    <title>Home</title>
                </head>
                <body>
                    <h1>Welcome to the home page, you are logged in!</h1>
                    <h3>Total number of tickets created is {total_tickets} .</h3>
                    <h2>Your email is {user_info.get("email")}.</h2>
                </body>
            </html>
            """
        else:
            return JSONResponse(content={"error": "Failed to fetch user info"}, status_code=400)

    else:
        return f"""
            <html>
                <head>
                    <title>Home</title>
                </head>
                <body>
                    <h1>Welcome to the home page! You are not logged in.</h1>
                    <h3>Total number of tickets created is {total_tickets} .</h3>
            
                </body>
            </html>
            """
    
@app.get("/logout")
async def logout(request: Request):

    request.session.pop("access_token", None)  
    return RedirectResponse(
        "https://dev-2anuorhsrl8w0pl6.us.auth0.com/v2/logout"
        f"?returnTo=http://localhost:8000/home"
        "&client_id=tYx7tPwwh87UPikur8s11We0K63tFmDt"
    )

    
    
    






    