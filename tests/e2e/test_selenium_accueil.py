"""Comparatif Selenium — Atelier 8.

Prérequis : application lancée (make run).
Manque vs Playwright : attentes explicites WebDriverWait, pas de traces/video natives,
localisateurs moins expressifs (pas de get_by_role / expect web-first).
"""

from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.e2e


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


def test_selenium_accueil_et_ajout_panier(driver, app_url):
    wait = WebDriverWait(driver, 10)
    driver.get(os.getenv("BASE_URL", app_url))
    wait.until(EC.title_contains("MiniShop"))
    assert "MiniShop" in driver.title

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="products"] li')))
    products = driver.find_elements(By.CSS_SELECTOR, '[data-testid="products"] li')
    assert len(products) == 5

    driver.find_element(By.CSS_SELECTOR, '[data-testid="add-mug"]').click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="cart-mug"]')))
    cart_line = driver.find_element(By.CSS_SELECTOR, '[data-testid="cart-mug"]')
    assert "Mug" in cart_line.text
    assert driver.find_element(By.CSS_SELECTOR, '[data-testid="order-btn"]').is_enabled()
