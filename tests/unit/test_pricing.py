"""Tests unitaires des règles de prix — Atelier 1."""

from __future__ import annotations

import json
from decimal import Decimal

import allure
import pytest

from minishop.pricing import coupon_discount, line_total, money, quote, shipping_cost

pytestmark = pytest.mark.unit


def test_money_arrondi_commercial():
    """0.125 s'arrondit à 0.13 (ROUND_HALF_UP), pas 0.12."""
    assert money("0.125") == Decimal("0.13")


def test_line_total_sans_remise():
    """Ligne simple : prix unitaire × quantité sans remise volume."""
    assert line_total(Decimal("12.50"), 2) == Decimal("25.00")


def test_quote_panier_vide():
    """Un panier vide coûte 0 € : pas de frais de livraison."""
    q = quote([])
    assert q.total == Decimal("0.00")
    assert q.shipping == Decimal("0.00")


@pytest.mark.parametrize(
    ("qty", "expected"),
    [
        (9, Decimal("112.50")),
        (10, Decimal("118.75")),
    ],
)
def test_remise_volume_seuil(qty, expected):
    """Remise -5 % dès 10 unités, pas avant."""
    assert line_total(Decimal("12.50"), qty) == expected


@pytest.mark.parametrize("qty", [0, -1, 100, "2", True])
def test_quantite_invalide(qty):
    """Quantité hors plage 1–99 ou non entière → ValueError."""
    with pytest.raises(ValueError):
        line_total(Decimal("10"), qty)


@pytest.mark.parametrize(
    ("subtotal", "coupon", "expected"),
    [
        (Decimal("19.99"), "WELCOME10", Decimal("0.00")),
        (Decimal("20.00"), "WELCOME10", Decimal("2.00")),
        (Decimal("29.99"), "FIXED5", Decimal("0.00")),
        (Decimal("30.00"), "FIXED5", Decimal("5.00")),
        (Decimal("10.00"), "FREESHIP", Decimal("0.00")),
        (Decimal("25.00"), None, Decimal("0.00")),
        (Decimal("25.00"), "", Decimal("0.00")),
        (Decimal("20.00"), "welcome10", Decimal("2.00")),
    ],
)
def test_coupon_discount_seuils(subtotal, coupon, expected):
    """Seuils et cas limites des coupons WELCOME10 / FIXED5 / FREESHIP."""
    assert coupon_discount(subtotal, coupon) == expected


def test_coupon_inconnu():
    """Coupon inconnu → ValueError explicite."""
    with pytest.raises(ValueError, match="Coupon inconnu"):
        coupon_discount(Decimal("50"), "NOEL2026")


@pytest.mark.parametrize(
    ("amount", "coupon", "empty", "expected"),
    [
        (Decimal("49.99"), None, False, Decimal("4.90")),
        (Decimal("50.00"), None, False, Decimal("0.00")),
        (Decimal("10.00"), "FREESHIP", False, Decimal("0.00")),
        (Decimal("10.00"), "freeship", False, Decimal("0.00")),
        (Decimal("0.00"), None, True, Decimal("0.00")),
    ],
)
def test_shipping_cost(amount, coupon, empty, expected):
    """Livraison 4,90 €, offerte dès 50 € ou avec FREESHIP ; 0 si panier vide."""
    assert shipping_cost(amount, coupon, empty) == expected


@allure.feature("Panier")
@allure.story("Coupons")
@allure.severity(allure.severity_level.CRITICAL)
def test_quote_welcome10_et_livraison():
    """2 mugs + WELCOME10 → total 27.40 € (sous-total 25, remise 2.50, livraison 4.90)."""
    with allure.step("Calculer le devis"):
        q = quote([{"product_id": "mug", "qty": 2}], coupon="WELCOME10")
    allure.attach(json.dumps(q.as_dict()), "devis", allure.attachment_type.JSON)
    assert q.subtotal == Decimal("25.00")
    assert q.discount == Decimal("2.50")
    assert q.shipping == Decimal("4.90")
    assert q.total == Decimal("27.40")


def test_quote_livraison_offerte_apres_remise():
    """Livraison offerte si total après remise >= 50 €."""
    q = quote([{"product_id": "hoodie", "qty": 1}, {"product_id": "mug", "qty": 1}])
    assert q.subtotal == Decimal("56.50")
    assert q.shipping == Decimal("0.00")
    assert q.total == Decimal("56.50")


@allure.feature("Panier")
@allure.story("Livraison")
@allure.severity(allure.severity_level.NORMAL)
def test_quote_freeship():
    """Coupon FREESHIP annule les frais de livraison."""
    with allure.step("Appliquer FREESHIP sur un petit panier"):
        q = quote([{"product_id": "sticker", "qty": 1}], coupon="FREESHIP")
    allure.attach(json.dumps(q.as_dict()), "devis", allure.attachment_type.JSON)
    assert q.shipping == Decimal("0.00")
    assert q.total == Decimal("2.45")


def test_quote_produit_inconnu():
    """Produit hors catalogue → KeyError."""
    with pytest.raises(KeyError, match="Produit inconnu"):
        quote([{"product_id": "licorne", "qty": 1}])


def test_quote_as_dict():
    """Sérialisation du devis : montants en chaînes et lignes présentes."""
    q = quote([{"product_id": "mug", "qty": 1}])
    data = q.as_dict()
    assert data["subtotal"] == "12.50"
    assert data["lines"][0]["product_id"] == "mug"
    assert data["coupon"] is None


# --- STUDENT15 ---


@allure.feature("Panier")
@allure.story("Coupons")
@allure.severity(allure.severity_level.CRITICAL)
def test_student15_sans_minimum():
    """STUDENT15 : -15 % sans seuil minimum."""
    with allure.step("Appliquer STUDENT15 sur 1 sticker"):
        q = quote([{"product_id": "sticker", "qty": 1}], coupon="STUDENT15")
    allure.attach(json.dumps(q.as_dict()), "devis", allure.attachment_type.JSON)
    assert q.subtotal == Decimal("2.45")
    assert q.discount == Decimal("0.37")
    assert q.shipping == Decimal("4.90")
    assert q.total == Decimal("6.98")


def test_student15_sur_ligne_sans_volume():
    """STUDENT15 s'applique sur une ligne sans remise volume (casse insensible)."""
    q = quote([{"product_id": "mug", "qty": 2}], coupon="student15")
    assert q.subtotal == Decimal("25.00")
    assert q.discount == Decimal("3.75")
    assert q.shipping == Decimal("4.90")
    assert q.total == Decimal("26.15")


def test_student15_non_cumulable_avec_remise_volume():
    """Si une ligne a la remise volume, STUDENT15 ne s'y applique pas."""
    q = quote(
        [
            {"product_id": "mug", "qty": 10},
            {"product_id": "sticker", "qty": 2},
        ],
        coupon="STUDENT15",
    )
    assert q.subtotal == Decimal("123.65")  # 118.75 + 4.90
    assert q.discount == Decimal("0.74")  # 15 % sur stickers seulement
    assert q.shipping == Decimal("0.00")
    assert q.total == Decimal("122.91")


def test_student15_panier_uniquement_volume():
    """Panier 100 % volume : STUDENT15 n'accorde aucune remise."""
    q = quote([{"product_id": "mug", "qty": 10}], coupon="STUDENT15")
    assert q.subtotal == Decimal("118.75")
    assert q.discount == Decimal("0.00")
    assert q.total == Decimal("118.75")
