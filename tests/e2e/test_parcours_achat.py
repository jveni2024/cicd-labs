"""Parcours E2E Playwright — Atelier 8.

Prérequis : application lancée (make run) ; BASE_URL=http://localhost:8000 par défaut.
Lancer :   pytest -m e2e --headed --slowmo 300
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.shop_page import ShopPage

pytestmark = pytest.mark.e2e


@pytest.fixture
def shop(page: Page, app_url: str) -> ShopPage:
    return ShopPage(page, app_url).open()


def test_page_accueil(shop: ShopPage):
    expect(shop.page).to_have_title(re.compile("MiniShop"))
    expect(shop.page.get_by_test_id("products").locator("li")).to_have_count(5)


def test_parcours_achat_avec_coupon(shop: ShopPage):
    shop.add("mug", times=2).apply_coupon("WELCOME10")
    expect(shop.page.get_by_test_id("total")).to_have_text("27.40")
    shop.order()
    expect(shop.confirmation()).to_be_visible()
    expect(shop.confirmation()).to_contain_text("confirmée")


def test_coupon_invalide_affiche_alerte(shop: ShopPage):
    shop.add("mug").apply_coupon("NOPE")
    expect(shop.error_alert()).to_be_visible()
    expect(shop.error_alert()).to_contain_text("Coupon inconnu")


def test_commander_desactive_panier_vide(shop: ShopPage):
    expect(shop.order_button()).to_be_disabled()
    shop.add("mug")
    expect(shop.order_button()).to_be_enabled()
