"""Page Object MiniShop pour les tests E2E Playwright (Atelier 8)."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class ShopPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def open(self) -> ShopPage:
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("products").locator("li")).to_have_count(5)
        return self

    def add(self, product_id: str, times: int = 1) -> ShopPage:
        btn = self.page.get_by_test_id(f"add-{product_id}")
        for _ in range(times):
            btn.click()
        return self

    def apply_coupon(self, code: str) -> ShopPage:
        self.page.get_by_test_id("coupon").fill(code)
        self.page.get_by_role("button", name="Calculer le total").click()
        return self

    def compute_total(self) -> ShopPage:
        self.page.get_by_role("button", name="Calculer le total").click()
        return self

    def total(self) -> str:
        expect(self.page.get_by_test_id("summary")).to_be_visible()
        return self.page.get_by_test_id("total").inner_text()

    def order(self) -> ShopPage:
        self.page.get_by_role("button", name="Commander").click()
        return self

    def confirmation(self):
        return self.page.get_by_test_id("confirmation")

    def error_alert(self):
        return self.page.get_by_role("alert")

    def order_button(self):
        return self.page.get_by_test_id("order-btn")
