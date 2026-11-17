"""Tests générés automatiquement depuis pricing.feature (moteur : offline).

NE PAS MODIFIER À LA MAIN : régénérer avec ai_tools/generate_tests.py
"""

from decimal import Decimal

import pytest

from minishop.pricing import quote

pytestmark = [pytest.mark.generated, pytest.mark.unit]


def test_panier_vide():
    """Panier vide"""
    q = quote([], None)
    assert q.total == Decimal("0.00")
    assert q.shipping == Decimal("0.00")


def test_achat_simple_avec_frais_de_livraison():
    """Achat simple avec frais de livraison"""
    q = quote([{"product_id": "mug", "qty": 2}], None)
    assert q.subtotal == Decimal("25.00")
    assert q.shipping == Decimal("4.90")
    assert q.total == Decimal("29.90")


def test_livraison_offerte_a_partir_de_50_euros():
    """Livraison offerte à partir de 50 euros"""
    q = quote([{"product_id": "hoodie", "qty": 1}, {"product_id": "mug", "qty": 1}], None)
    assert q.shipping == Decimal("0.00")
    assert q.total == Decimal("56.50")


def test_remise_volume_des_10_unites():
    """Remise volume dès 10 unités"""
    q = quote([{"product_id": "sticker", "qty": 10}], None)
    assert q.subtotal == Decimal("23.28")


def test_coupon_de_bienvenue():
    """Coupon de bienvenue"""
    q = quote([{"product_id": "mug", "qty": 2}], "WELCOME10")
    assert q.discount == Decimal("2.50")
    assert q.total == Decimal("27.40")


def test_coupon_de_bienvenue_sous_le_seuil():
    """Coupon de bienvenue sous le seuil"""
    q = quote([{"product_id": "mug", "qty": 1}], "WELCOME10")
    assert q.discount == Decimal("0.00")


def test_coupon_de_livraison_offerte():
    """Coupon de livraison offerte"""
    q = quote([{"product_id": "sticker", "qty": 1}], "FREESHIP")
    assert q.shipping == Decimal("0.00")
    assert q.total == Decimal("2.45")


def test_coupon_inconnu():
    """Coupon inconnu"""
    with pytest.raises(ValueError, match="Coupon inconnu"):
        quote([{"product_id": "mug", "qty": 1}], "NOEL2026")


def test_produit_inconnu():
    """Produit inconnu"""
    with pytest.raises(KeyError, match="Produit inconnu"):
        quote([{"product_id": "licorne", "qty": 1}], None)


def test_coupon_fixed5_sous_le_seuil():
    """Coupon FIXED5 sous le seuil"""
    q = quote([{"product_id": "book", "qty": 1}], "FIXED5")
    assert q.subtotal == Decimal("29.99")
    assert q.discount == Decimal("0.00")


def test_remise_volume_et_coupon_welcome10():
    """Remise volume et coupon WELCOME10"""
    q = quote([{"product_id": "mug", "qty": 10}], "WELCOME10")
    assert q.subtotal == Decimal("118.75")
    assert q.discount == Decimal("11.88")
    assert q.total == Decimal("106.87")


def test_quantite_invalide_zero():
    """Quantité invalide zéro"""
    with pytest.raises(ValueError, match="Quantité hors limites"):
        quote([{"product_id": "mug", "qty": 0}], None)
