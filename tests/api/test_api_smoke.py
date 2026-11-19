"""Tests d'API — smoke (Atelier 2 quality gate)."""

import pytest

pytestmark = pytest.mark.api


def test_health(client):
    """GET /health renvoie 200 et status ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_home(client):
    """GET / sert la page HTML d'accueil."""
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_metrics(client):
    """GET /metrics expose le compteur Prometheus minishop_http_requests_total."""
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "minishop_http_requests_total" in r.text


def test_liste_produits(client):
    """GET /products contient au moins mug et tshirt."""
    r = client.get("/products")
    assert r.status_code == 200
    assert {"mug", "tshirt"} <= {p["id"] for p in r.json()}


def test_produit_ok(client):
    """GET /products/mug renvoie le produit mug."""
    r = client.get("/products/mug")
    assert r.status_code == 200
    assert r.json()["id"] == "mug"


def test_produit_inconnu(client):
    """GET /products/{id} inconnu → 404."""
    r = client.get("/products/licorne")
    assert r.status_code == 404


def test_cart_quote(client):
    """POST /cart/quote : 2 mugs → sous-total 25.00."""
    r = client.post("/cart/quote", json={"items": [{"product_id": "mug", "qty": 2}]})
    assert r.status_code == 200
    assert r.json()["subtotal"] == "25.00"


def test_cart_quote_produit_inconnu(client):
    """Devis avec produit inconnu → 404."""
    r = client.post("/cart/quote", json={"items": [{"product_id": "licorne", "qty": 1}]})
    assert r.status_code == 404


def test_cart_quote_coupon_inconnu(client):
    """Devis avec coupon inconnu → 422."""
    r = client.post(
        "/cart/quote",
        json={"items": [{"product_id": "mug", "qty": 1}], "coupon": "NOEL"},
    )
    assert r.status_code == 422


def test_create_and_get_order(client):
    """Création puis lecture d'une commande : 201 puis 200 avec le même id."""
    created = client.post("/orders", json={"items": [{"product_id": "mug", "qty": 1}]})
    assert created.status_code == 201
    order_id = created.json()["id"]
    fetched = client.get(f"/orders/{order_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == order_id


def test_create_order_panier_vide(client):
    """Commande avec panier vide → 422."""
    r = client.post("/orders", json={"items": []})
    assert r.status_code == 422


def test_get_order_inconnu(client):
    """GET /orders/{id} inconnu → 404."""
    r = client.get("/orders/does-not-exist")
    assert r.status_code == 404


def test_cart_quote_welcome10_total(client):
    """2 mugs + WELCOME10 → total API 27.40 (aligné pricing)."""
    r = client.post(
        "/cart/quote",
        json={"items": [{"product_id": "mug", "qty": 2}], "coupon": "WELCOME10"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["subtotal"] == "25.00"
    assert body["discount"] == "2.50"
    assert body["shipping"] == "4.90"
    assert body["total"] == "27.40"


@pytest.mark.parametrize("qty", [0, 100])
def test_cart_quote_quantite_invalide(client, qty):
    """Quantité hors plage (0 ou 100) → 422."""
    r = client.post("/cart/quote", json={"items": [{"product_id": "mug", "qty": qty}]})
    assert r.status_code == 422


def test_cart_quote_corps_invalide(client):
    """Corps de devis incomplet (qty manquante) → 422."""
    r = client.post("/cart/quote", json={"items": [{"product_id": "mug"}]})
    assert r.status_code == 422


def test_create_order_matches_quote(client):
    """Le total de la commande créée égale celui du devis pour le même panier."""
    payload = {"items": [{"product_id": "mug", "qty": 2}], "coupon": "WELCOME10"}
    quote = client.post("/cart/quote", json=payload).json()
    created = client.post("/orders", json=payload)
    assert created.status_code == 201
    order = created.json()
    assert order["total"] == quote["total"]
    fetched = client.get(f"/orders/{order['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == order


def test_openapi_contrat_routes_publiques(client):
    """Échoue si une route publique disparaît ou si un type de champ change."""
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    required = {
        "/health": {"get"},
        "/products": {"get"},
        "/products/{product_id}": {"get"},
        "/cart/quote": {"post"},
        "/orders": {"post"},
        "/orders/{order_id}": {"get"},
    }
    for path, methods in required.items():
        assert path in paths, f"Route manquante dans OpenAPI : {path}"
        for method in methods:
            assert method in paths[path], f"Méthode {method.upper()} absente pour {path}"

    health = client.get("/health").json()
    assert isinstance(health["status"], str)
    assert isinstance(health["version"], str)

    product = client.get("/products/mug").json()
    for key, typ in [("id", str), ("name", str), ("price", str), ("stock", int)]:
        assert key in product
        assert isinstance(product[key], typ), f"{key} devrait être {typ.__name__}"
