import requests

item_url = 'http://localhost:8000'
get_items_url = f'{item_url}/get_items'
get_item_by_id_url = f'{item_url}/get_item_by_id'
add_item_url = f'{item_url}/add_item'
update_item_url = f'{item_url}/update_item'
delete_item_url = f'{item_url}/delete_item'

shop_url = 'http://localhost:8001'
get_kinopoisk_movie_by_id_url = f'{shop_url}/get_movie_by_id'

new_item = {
    "id": 666,
    "item_name": "testName",
    "amount": 999,
    "price": 666,
}

def test_1_add_item():
    res = requests.post(f"{add_item_url}", json=new_item)
    assert res.status_code == 200

def test_2_get_items():
    res = requests.get(f"{get_items_url}").json()
    assert new_item in res

def test_3_get_item_by_id():
    res = requests.get(f"{get_item_by_id_url}?item_id=666").json()
    assert res == new_item

def test_5_update_item():
    res = requests.put(f"{update_item_url}?item_id=666&new_amount=10&new_price=10")
    assert res.text == '"Item updated successfully"'

def test_6_delete_item():
    res = requests.delete(f"{delete_item_url}?item_id=666")
    assert res.text == '"Item deleted successfully"'