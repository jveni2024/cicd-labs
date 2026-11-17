"""Tests pytest du calcul de panier MiniShop (pricing.feature)."""

from decimal import Decimal

import pytest

from minishop.pricing import (
    Line,
    Quote,
    coupon_discount,
    line_total,
    money,
    quote,
    shipping_cost,
)

pytestmark = [pytest.mark.generated, pytest.mark.unit]

D = Decimal


# ---------------------------------------------------------------------------
# Scénarios de la spécification
# ---------------------------------------------------------------------------


def test_panier_vide():
    """Un panier vide a un total nul et aucuns frais de livraison."""
    q = quote([])
    assert q.total == D("0.00")
    assert q.shipping == D("0.00")


def test_achat_simple_avec_frais_de_livraison():
    """Un panier sous 50 € facture les frais de livraison de 4,90 €."""
    q = quote([{"product_id": "mug", "qty": 2}])
    assert q.subtotal == D("25.00")
    assert q.shipping == D("4.90")
    assert q.total == D("29.90")


def test_livraison_offerte_a_partir_de_50_euros():
    """La livraison est offerte lorsque le total après remise atteint 50 €."""
    q = quote([{"product_id": "hoodie", "qty": 1}, {"product_id": "mug", "qty": 1}])
    assert q.shipping == D("0.00")
    assert q.total == D("56.50")


def test_remise_volume_des_10_unites():
    """Une ligne de 10 unités ou plus bénéficie de 5 % de remise."""
    q = quote([{"product_id": "sticker", "qty": 10}])
    assert q.subtotal == D("23.28")


def test_coupon_de_bienvenue():
    """WELCOME10 applique 10 % sur un sous-total d'au moins 20 €."""
    q = quote([{"product_id": "mug", "qty": 2}], coupon="WELCOME10")
    assert q.discount == D("2.50")
    assert q.total == D("27.40")


def test_coupon_de_bienvenue_sous_le_seuil():
    """WELCOME10 n'applique aucune remise sous un sous-total de 20 €."""
    q = quote([{"product_id": "mug", "qty": 1}], coupon="WELCOME10")
    assert q.discount == D("0.00")


def test_coupon_de_livraison_offerte():
    """FREESHIP offre la livraison quel que soit le montant du panier."""
    q = quote([{"product_id": "sticker", "qty": 1}], coupon="FREESHIP")
    assert q.shipping == D("0.00")
    assert q.total == D("2.45")


def test_coupon_inconnu():
    """Un code coupon inconnu lève une erreur 'Coupon inconnu'."""
    with pytest.raises(ValueError, match="Coupon inconnu"):
        quote([{"product_id": "mug", "qty": 1}], coupon="NOEL2026")


def test_produit_inconnu():
    """Un produit absent du catalogue lève KeyError 'Produit inconnu'."""
    # Hallucination LLM corrigée en relecture : le code lève KeyError, pas ValueError.
    with pytest.raises(KeyError, match="Produit inconnu"):
        quote([{"product_id": "licorne", "qty": 1}])


def test_coupon_fixed5_sous_le_seuil():
    """FIXED5 n'applique aucune remise si le sous-total est sous 30 €."""
    q = quote([{"product_id": "book", "qty": 1}], coupon="FIXED5")
    assert q.subtotal == D("29.99")
    assert q.discount == D("0.00")


def test_remise_volume_et_coupon_welcome10():
    """La remise volume s'applique avant le coupon WELCOME10 sur le sous-total."""
    q = quote([{"product_id": "mug", "qty": 10}], coupon="WELCOME10")
    assert q.subtotal == D("118.75")
    assert q.discount == D("11.88")
    assert q.total == D("106.87")


def test_quantite_invalide_zero():
    """Une quantité de zéro lève une erreur 'Quantité hors limites'."""
    with pytest.raises(ValueError, match="Quantité hors limites"):
        quote([{"product_id": "mug", "qty": 0}])


# ---------------------------------------------------------------------------
# Cas limites
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("qty", [-1, 100, 1000])
def test_limite_quantite_hors_bornes(qty):
    """Une quantité hors de l'intervalle 1..99 est rejetée."""
    with pytest.raises(ValueError, match="Quantité hors limites"):
        line_total(D("12.50"), qty)


@pytest.mark.parametrize("qty", [1, 99])
def test_limite_quantite_bornes_acceptees(qty):
    """Les bornes 1 et 99 sont acceptées."""
    assert line_total(D("1.00"), qty) == D("1.00") * qty or line_total(D("1.00"), qty) == money(
        D("1.00") * qty * D("0.95")
    )


@pytest.mark.parametrize("bad", [2.0, "2", True, None])
def test_limite_quantite_non_entiere(bad):
    """Une quantité non entière (float, str, bool, None) est rejetée."""
    with pytest.raises(ValueError):
        line_total(D("12.50"), bad)


@pytest.mark.parametrize(
    "qty, expected",
    [
        (9, D("22.05")),  # 9 × 2,45 = 22,05 : pas de remise
        (10, D("23.28")),  # 24,50 × 0,95 = 23,275 -> 23,28
    ],
)
def test_limite_seuil_remise_volume(qty, expected):
    """La remise volume s'applique exactement à partir de 10 unités."""
    assert line_total(D("2.45"), qty) == expected


def test_limite_remise_volume_arrondi_half_up():
    """La remise volume arrondit le centime en ROUND_HALF_UP (23,275 -> 23,28)."""
    assert line_total(D("2.45"), 10) == D("23.28")


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0.125", D("0.13")),
        ("2.345", D("2.35")),
        ("2.344", D("2.34")),
        (1.005, D("1.01")),
    ],
)
def test_limite_money_arrondi_commercial(monkeypatch, raw, expected):
    """money arrondit au centime en ROUND_HALF_UP."""
    monkeypatch.delenv("MINISHOP_BUG", raising=False)
    assert money(raw) == expected


def test_limite_money_retourne_decimal(monkeypatch):
    """money renvoie toujours un Decimal, même à partir d'un int."""
    monkeypatch.delenv("MINISHOP_BUG", raising=False)
    assert isinstance(money(3), Decimal)
    assert money(3) == D("3.00")


@pytest.mark.parametrize(
    "subtotal, expected",
    [
        (D("19.99"), D("0.00")),
        (D("20.00"), D("2.00")),
        (D("100.00"), D("10.00")),
    ],
)
def test_limite_seuil_welcome10(subtotal, expected):
    """WELCOME10 : seuil 20 € inclus, 19,99 € exclu."""
    assert coupon_discount(subtotal, "WELCOME10") == expected


@pytest.mark.parametrize(
    "subtotal, expected",
    [
        (D("29.99"), D("0.00")),
        (D("30.00"), D("5.00")),
        (D("30.01"), D("5.00")),
    ],
)
def test_limite_seuil_fixed5(subtotal, expected):
    """FIXED5 : seuil 30 € inclus, 29,99 € exclu."""
    assert coupon_discount(subtotal, "FIXED5") == expected


@pytest.mark.parametrize(
    "subtotal, expected",
    [
        (D("49.99"), D("4.90")),
        (D("50.00"), D("0.00")),
        (D("50.01"), D("0.00")),
    ],
)
def test_limite_seuil_livraison_offerte(subtotal, expected):
    """La livraison est offerte à partir de 50 € inclus."""
    assert shipping_cost(subtotal, None, empty=False) == expected


def test_limite_freeship_insensible_a_la_casse():
    """Le code FREESHIP est reconnu quelle que soit la casse ou les espaces."""
    q = quote([{"product_id": "sticker", "qty": 1}], coupon="  freeship ")
    assert q.shipping == D("0.00")
    assert q.coupon == "FREESHIP"


def test_limite_coupon_normalise_en_majuscules():
    """Le coupon est normalisé (espaces et casse) dans le devis."""
    q = quote([{"product_id": "mug", "qty": 2}], coupon=" welcome10 ")
    assert q.coupon == "WELCOME10"
    assert q.discount == D("2.50")


@pytest.mark.parametrize("empty_coupon", [None, ""])
def test_limite_absence_de_coupon(empty_coupon):
    """Un coupon absent ou vide n'applique aucune remise."""
    assert coupon_discount(D("100.00"), empty_coupon) == D("0.00")


def test_limite_coupon_inconnu_directement():
    """coupon_discount rejette un code inconnu."""
    with pytest.raises(ValueError, match="Coupon inconnu"):
        coupon_discount(D("100.00"), "NOEL2026")


def test_limite_coupon_inconnu_panier_vide_ignore():
    """Sans ligne dans le panier, le coupon n'est pas évalué (remise nulle)."""
    q = quote([], coupon="NOEL2026")
    assert q.discount == D("0.00")
    assert q.total == D("0.00")


def test_limite_student15_sans_minimum():
    """STUDENT15 s'applique sans montant minimum."""
    lines = [Line("mug", 1, D("12.50"), D("12.50"))]
    assert coupon_discount(D("12.50"), "STUDENT15", lines) == D("1.88")


def test_limite_student15_exclut_lignes_en_remise_volume():
    """STUDENT15 n'agit pas sur les lignes qui bénéficient de la remise volume."""
    lines = (
        [
            Line("mug", 1, D("12.50"), D("12.50")),
            Line("sticker", 10, D("2.45"), D("23.28")),
        ],
    )
    # Note : le tuple ci-dessus est volontairement remplacé ci-dessous
    lines = [
        Line("mug", 1, D("12.50"), D("12.50")),
        Line("sticker", 10, D("2.45"), D("23.28")),
    ]
    assert coupon_discount(D("35.78"), "STUDENT15", lines) == D("1.88")


def test_limite_student15_sans_ligne_eligible():
    """STUDENT15 ne donne aucune remise si toutes les lignes sont en remise volume."""
    lines = [Line("sticker", 10, D("2.45"), D("23.28"))]
    assert coupon_discount(D("23.28"), "STUDENT15", lines) == D("0.00")


def test_limite_remise_nulle_sans_coupon_dans_quote():
    """Sans coupon, la remise et le coupon du devis sont nuls."""
    q = quote([{"product_id": "mug", "qty": 2}])
    assert q.discount == D("0.00")
    assert q.coupon is None


def test_limite_livraison_offerte_apres_remise():
    """Le seuil de livraison s'applique au total après remise, pas au sous-total."""
    # 10 mugs : sous-total 118,75 ; avec WELCOME10 : 106,87 >= 50 -> livraison offerte
    q = quote([{"product_id": "mug", "qty": 10}], coupon="WELCOME10")
    assert q.shipping == D("0.00")


def test_limite_total_egal_somme_des_composantes():
    """Le total vaut sous-total - remise + livraison."""
    q = quote([{"product_id": "mug", "qty": 2}], coupon="WELCOME10")
    assert q.total == q.subtotal - q.discount + q.shipping


def test_limite_as_dict_montants_en_chaine():
    """as_dict expose les montants sous forme de chaînes décimales exactes."""
    q = quote([{"product_id": "mug", "qty": 2}])
    data = q.as_dict()
    assert data["subtotal"] == "25.00"
    assert data["shipping"] == "4.90"
    assert data["total"] == "29.90"
    assert data["coupon"] is None


def test_limite_quote_retourne_un_objet_quote():
    """quote renvoie une instance de Quote avec une ligne par item."""
    q = quote([{"product_id": "mug", "qty": 1}, {"product_id": "book", "qty": 1}])
    assert isinstance(q, Quote)
    assert len(q.lines) == 2
