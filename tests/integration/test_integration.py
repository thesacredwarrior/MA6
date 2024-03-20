import pytest
import psycopg2
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'item_service/app'))
sys.path.append(str(BASE_DIR / 'shop_service/app'))

from item_service.app.main import service_alive as item_status
from shop_service.app.main import service_alive as shop_status


@pytest.mark.asyncio
async def test_item_service_connection():
    r = await item_status()
    assert r == {'message': 'service alive'}

@pytest.mark.asyncio
async def test_shop_service_connection():
    r = await shop_status()
    assert r == {'message': 'service alive'}
