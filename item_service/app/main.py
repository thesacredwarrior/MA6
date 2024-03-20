import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated

from sqlalchemy.orm import Session

from database import item_database as database
from database.item_database import ItemDB

from model.item import Item

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


@app.get("/get_items")
async def get_items(db: db_dependency):
    try:
        result = db.query(ItemDB).limit(100).all()
        return result
    except Exception as e:
        return "Can't access database!"


@app.get("/get_item_by_id")
async def get_item_by_id(item_id: int, db: db_dependency):
    try:
        result = db.query(ItemDB).filter(ItemDB.id == item_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Item not found")


@app.post("/add_item")
async def add_item(item: Item, db: db_dependency):
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


@app.put("/update_item")
async def update_item(item_id: int, new_amount: int, new_price: int, db: db_dependency):
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


@app.delete("/delete_item")
async def delete_item(item_id: int, db: db_dependency):
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
