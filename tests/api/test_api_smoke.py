"""Tests d'API — smoke (Atelier 2 quality gate)."""

import pytest

pytestmark = pytest.mark.api


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "minishop_http_requests_total" in r.text


def test_liste_produits(client):
    r = client.get("/products")
    assert r.status_code == 200
    assert {"mug", "tshirt"} <= {p["id"] for p in r.json()}


def test_produit_ok(client):
    r = client.get("/products/mug")
    assert r.status_code == 200
    assert r.json()["id"] == "mug"


def test_produit_inconnu(client):
    r = client.get("/products/licorne")
    assert r.status_code == 404


def test_cart_quote(client):
    r = client.post("/cart/quote", json={"items": [{"product_id": "mug", "qty": 2}]})
    assert r.status_code == 200
    assert r.json()["subtotal"] == "25.00"


def test_cart_quote_produit_inconnu(client):
    r = client.post("/cart/quote", json={"items": [{"product_id": "licorne", "qty": 1}]})
    assert r.status_code == 404


def test_cart_quote_coupon_inconnu(client):
    r = client.post(
        "/cart/quote",
        json={"items": [{"product_id": "mug", "qty": 1}], "coupon": "NOEL"},
    )
    assert r.status_code == 422


def test_create_and_get_order(client):
    created = client.post("/orders", json={"items": [{"product_id": "mug", "qty": 1}]})
    assert created.status_code == 201
    order_id = created.json()["id"]
    fetched = client.get(f"/orders/{order_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == order_id


def test_create_order_panier_vide(client):
    r = client.post("/orders", json={"items": []})
    assert r.status_code == 422


def test_get_order_inconnu(client):
    r = client.get("/orders/does-not-exist")
    assert r.status_code == 404
