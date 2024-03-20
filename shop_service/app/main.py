import os
import uvicorn
from fastapi import FastAPI, Depends, status
from typing import Annotated

from sqlalchemy.orm import Session

from database import shop_database as database
from database.shop_database import ItemDB
from database.shop_database import Logs
import datetime

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    return {'message': 'service alive'}


@app.post("/sell_items")
async def sell_items(item: str, amount: int, db: db_dependency):
    try:
        result = db.query(ItemDB).filter(ItemDB.item_name == item).first()
        if result.amount < amount:
            return "Not enough items"
        result.amount -= amount
        db.commit()
    except Exception as e:
        return "Can't access items database!"
    try:
        log = Logs(item_name=result.item_name,
                   amount=amount,
                   datetime=datetime.datetime.now(),
                   action="sell")
        db.add(log)
        db.commit()
        return "Congrats!"
    except Exception as e:
        return "Can't access logs database!"


@app.get("/get_logs")
async def get_logs(db: db_dependency):
    try:
        result = db.query(Logs).limit(100).all()
        return result
    except Exception as e:
        return "Can't access database!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
