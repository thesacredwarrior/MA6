import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form
from typing import Annotated
from keycloak import KeycloakOpenID
from sqlalchemy.orm import Session

from database import item_database as database
from database.item_database import ItemDB

from model.item import Item

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)

KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_CLIENT_ID = "testClient"
KEYCLOAK_REALM = "testRealm"
KEYCLOAK_CLIENT_SECRET = "**********"

user_token = ""
keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                  client_id=KEYCLOAK_CLIENT_ID,
                                  realm_name=KEYCLOAK_REALM,
                                  client_secret_key=KEYCLOAK_CLIENT_SECRET)

###########
#Prometheus
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        global user_token
        user_token = token
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")

def user_got_role():
    global user_token
    token = user_token
    try:
        userinfo = keycloak_openid.userinfo(token["access_token"])
        token_info = keycloak_openid.introspect(token["access_token"])
        if "test" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    if (user_got_role()):
        return {'message': 'service alive'}
    else:
        return "Wrong JWT Token"

@app.get("/get_items")
async def get_items(db: db_dependency):
    if (user_got_role()):
        try:
            result = db.query(ItemDB).limit(100).all()
            return result
        except Exception as e:
            return "Can't access database!"
    else:
        return "Wrong JWT Token"

@app.get("/get_item_by_id")
async def get_item_by_id(item_id: int, db: db_dependency):
    if (user_got_role()):
        try:
            result = db.query(ItemDB).filter(ItemDB.id == item_id).first()
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail="Item not found")
    else:
        return "Wrong JWT Token"

@app.post("/add_item")
async def add_item(item: Item, db: db_dependency):
    if (user_got_role()):
        try:
            item_db = ItemDB(
                id=item.id,
                item_name=item.item_name,
                amount=item.amount,
                price=item.price
            )
            db.add(item_db)
            db.commit()
            return item_db
        except Exception as e:
            raise HTTPException(status_code=404, detail="Failed to add item")
    else:
        return "Wrong JWT Token"

@app.put("/update_item")
async def update_item(item_id: int, new_amount: int, new_price: int, db: db_dependency):
    if (user_got_role()):
        try:
            item_db = db.query(ItemDB).filter(ItemDB.id == item_id).first()
            if item_db:
                item_db.amount = new_amount
                item_db.price = new_price
                db.commit()
                return "Item updated successfully"
            else:
                raise HTTPException(status_code=404, detail="Item not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    else:
        return "Wrong JWT Token"

@app.delete("/delete_item")
async def delete_item(item_id: int, db: db_dependency):
    if (user_got_role()):
        try:
            item_db = db.query(ItemDB).filter(ItemDB.id == item_id).first()
            if item_db:
                db.delete(item_db)
                db.commit()
                return "Item deleted successfully"
            else:
                raise HTTPException(status_code=404, detail="Item not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    else:
        return "Wrong JWT Token"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
