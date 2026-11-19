# Catalogue des tests

_Généré automatiquement le 19/11/2026 16:41 — ne pas éditer à la main._
**88 tests** — 88 documentés (100%).


## `tests/api/test_api_smoke.py`

Tests d'API — smoke (Atelier 2 quality gate).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_health` | api | GET /health renvoie 200 et status ok. | 0.01s |
| ✅ | `test_home` | api | GET / sert la page HTML d'accueil. | 0.05s |
| ✅ | `test_metrics` | api | GET /metrics expose le compteur Prometheus minishop_http_requests_total. | 0.01s |
| ✅ | `test_liste_produits` | api | GET /products contient au moins mug et tshirt. | 0.01s |
| ✅ | `test_produit_ok` | api | GET /products/mug renvoie le produit mug. | 0.01s |
| ✅ | `test_produit_inconnu` | api | GET /products/{id} inconnu → 404. | 0.01s |
| ✅ | `test_cart_quote` | api | POST /cart/quote : 2 mugs → sous-total 25.00. | 0.01s |
| ✅ | `test_cart_quote_produit_inconnu` | api | Devis avec produit inconnu → 404. | 0.01s |
| ✅ | `test_cart_quote_coupon_inconnu` | api | Devis avec coupon inconnu → 422. | 0.01s |
| ✅ | `test_create_and_get_order` | api | Création puis lecture d'une commande : 201 puis 200 avec le même id. | 0.01s |
| ✅ | `test_create_order_panier_vide` | api | Commande avec panier vide → 422. | 0.01s |
| ✅ | `test_get_order_inconnu` | api | GET /orders/{id} inconnu → 404. | 0.01s |
| ✅ | `test_cart_quote_welcome10_total` | api | 2 mugs + WELCOME10 → total API 27.40 (aligné pricing). | 0.01s |
| ✅ | `test_cart_quote_quantite_invalide` (paramétré) | api, parametrize | Quantité hors plage (0 ou 100) → 422. | 0.02s |
| ✅ | `test_cart_quote_corps_invalide` | api | Corps de devis incomplet (qty manquante) → 422. | 0.01s |
| ✅ | `test_create_order_matches_quote` | api | Le total de la commande créée égale celui du devis pour le même panier. | 0.01s |
| ✅ | `test_openapi_contrat_routes_publiques` | api | Échoue si une route publique disparaît ou si un type de champ change. | 0.02s |

## `tests/e2e/test_parcours_achat.py`

Parcours E2E Playwright — Atelier 8.

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| · | `test_page_accueil` | e2e | Accueil MiniShop : titre et 5 produits listés. | 0.00s |
| · | `test_parcours_achat_avec_coupon` | e2e | Parcours 2 mugs + WELCOME10 → total 27.40 puis confirmation de commande. | 0.00s |
| · | `test_coupon_invalide_affiche_alerte` | e2e | Coupon inconnu affiche une alerte « Coupon inconnu ». | 0.00s |
| · | `test_commander_desactive_panier_vide` | e2e | Bouton Commander désactivé si panier vide, activé après un ajout. | 0.00s |

## `tests/e2e/test_selenium_accueil.py`

Comparatif Selenium — Atelier 8.

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| · | `test_selenium_accueil_et_ajout_panier` | e2e | Selenium : titre MiniShop, 5 produits, ajout mug active Commander. | 0.00s |

## `tests/generated/test_pricing_ai.py`

Tests pytest du calcul de panier MiniShop (pricing.feature).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_panier_vide` | generated, unit | Un panier vide a un total nul et aucuns frais de livraison. | 0.00s |
| ✅ | `test_achat_simple_avec_frais_de_livraison` | generated, unit | Un panier sous 50 € facture les frais de livraison de 4,90 €. | 0.00s |
| ✅ | `test_livraison_offerte_a_partir_de_50_euros` | generated, unit | La livraison est offerte lorsque le total après remise atteint 50 €. | 0.00s |
| ✅ | `test_remise_volume_des_10_unites` | generated, unit | Une ligne de 10 unités ou plus bénéficie de 5 % de remise. | 0.00s |
| ✅ | `test_coupon_de_bienvenue` | generated, unit | WELCOME10 applique 10 % sur un sous-total d'au moins 20 €. | 0.00s |
| ✅ | `test_coupon_de_bienvenue_sous_le_seuil` | generated, unit | WELCOME10 n'applique aucune remise sous un sous-total de 20 €. | 0.00s |
| ✅ | `test_coupon_de_livraison_offerte` | generated, unit | FREESHIP offre la livraison quel que soit le montant du panier. | 0.00s |
| ✅ | `test_coupon_inconnu` | generated, unit | Un code coupon inconnu lève une erreur 'Coupon inconnu'. | 0.01s |
| ✅ | `test_produit_inconnu` | generated, unit | Un produit absent du catalogue lève KeyError 'Produit inconnu'. | 0.01s |
| ✅ | `test_coupon_fixed5_sous_le_seuil` | generated, unit | FIXED5 n'applique aucune remise si le sous-total est sous 30 €. | 0.00s |
| ✅ | `test_remise_volume_et_coupon_welcome10` | generated, unit | La remise volume s'applique avant le coupon WELCOME10 sur le sous-total. | 0.00s |
| ✅ | `test_quantite_invalide_zero` | generated, unit | Une quantité de zéro lève une erreur 'Quantité hors limites'. | 0.00s |
| ✅ | `test_limite_quantite_hors_bornes` (paramétré) | generated, unit, parametrize | Une quantité hors de l'intervalle 1..99 est rejetée. | 0.01s |
| ✅ | `test_limite_quantite_bornes_acceptees` (paramétré) | generated, unit, parametrize | Les bornes 1 et 99 sont acceptées. | 0.01s |
| ✅ | `test_limite_quantite_non_entiere` (paramétré) | generated, unit, parametrize | Une quantité non entière (float, str, bool, None) est rejetée. | 0.01s |
| ✅ | `test_limite_seuil_remise_volume` (paramétré) | generated, unit, parametrize | La remise volume s'applique exactement à partir de 10 unités. | 0.01s |
| ✅ | `test_limite_remise_volume_arrondi_half_up` | generated, unit | La remise volume arrondit le centime en ROUND_HALF_UP (23,275 -> 23,28). | 0.00s |
| ✅ | `test_limite_money_arrondi_commercial` (paramétré) | generated, unit, parametrize | money arrondit au centime en ROUND_HALF_UP. | 0.02s |
| ✅ | `test_limite_money_retourne_decimal` | generated, unit | money renvoie toujours un Decimal, même à partir d'un int. | 0.00s |
| ✅ | `test_limite_seuil_welcome10` (paramétré) | generated, unit, parametrize | WELCOME10 : seuil 20 € inclus, 19,99 € exclu. | 0.01s |
| ✅ | `test_limite_seuil_fixed5` (paramétré) | generated, unit, parametrize | FIXED5 : seuil 30 € inclus, 29,99 € exclu. | 0.01s |
| ✅ | `test_limite_seuil_livraison_offerte` (paramétré) | generated, unit, parametrize | La livraison est offerte à partir de 50 € inclus. | 0.01s |
| ✅ | `test_limite_freeship_insensible_a_la_casse` | generated, unit | Le code FREESHIP est reconnu quelle que soit la casse ou les espaces. | 0.00s |
| ✅ | `test_limite_coupon_normalise_en_majuscules` | generated, unit | Le coupon est normalisé (espaces et casse) dans le devis. | 0.00s |
| ✅ | `test_limite_absence_de_coupon` (paramétré) | generated, unit, parametrize | Un coupon absent ou vide n'applique aucune remise. | 0.01s |
| ✅ | `test_limite_coupon_inconnu_directement` | generated, unit | coupon_discount rejette un code inconnu. | 0.00s |
| ✅ | `test_limite_coupon_inconnu_panier_vide_ignore` | generated, unit | Sans ligne dans le panier, le coupon n'est pas évalué (remise nulle). | 0.00s |
| ✅ | `test_limite_student15_sans_minimum` | generated, unit | STUDENT15 s'applique sans montant minimum. | 0.00s |
| ✅ | `test_limite_student15_exclut_lignes_en_remise_volume` | generated, unit | STUDENT15 n'agit pas sur les lignes qui bénéficient de la remise volume. | 0.00s |
| ✅ | `test_limite_student15_sans_ligne_eligible` | generated, unit | STUDENT15 ne donne aucune remise si toutes les lignes sont en remise volume. | 0.00s |
| ✅ | `test_limite_remise_nulle_sans_coupon_dans_quote` | generated, unit | Sans coupon, la remise et le coupon du devis sont nuls. | 0.00s |
| ✅ | `test_limite_livraison_offerte_apres_remise` | generated, unit | Le seuil de livraison s'applique au total après remise, pas au sous-total. | 0.00s |
| ✅ | `test_limite_total_egal_somme_des_composantes` | generated, unit | Le total vaut sous-total - remise + livraison. | 0.00s |
| ✅ | `test_limite_as_dict_montants_en_chaine` | generated, unit | as_dict expose les montants sous forme de chaînes décimales exactes. | 0.00s |
| ✅ | `test_limite_quote_retourne_un_objet_quote` | generated, unit | quote renvoie une instance de Quote avec une ligne par item. | 0.00s |

## `tests/generated/test_pricing_offline.py`

Tests générés automatiquement depuis pricing.feature (moteur : offline).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_panier_vide` | generated, unit | Panier vide | 0.00s |
| ✅ | `test_achat_simple_avec_frais_de_livraison` | generated, unit | Achat simple avec frais de livraison | 0.00s |
| ✅ | `test_livraison_offerte_a_partir_de_50_euros` | generated, unit | Livraison offerte à partir de 50 euros | 0.00s |
| ✅ | `test_remise_volume_des_10_unites` | generated, unit | Remise volume dès 10 unités | 0.00s |
| ✅ | `test_coupon_de_bienvenue` | generated, unit | Coupon de bienvenue | 0.00s |
| ✅ | `test_coupon_de_bienvenue_sous_le_seuil` | generated, unit | Coupon de bienvenue sous le seuil | 0.00s |
| ✅ | `test_coupon_de_livraison_offerte` | generated, unit | Coupon de livraison offerte | 0.00s |
| ✅ | `test_coupon_inconnu` | generated, unit | Coupon inconnu | 0.01s |
| ✅ | `test_produit_inconnu` | generated, unit | Produit inconnu | 0.01s |
| ✅ | `test_coupon_fixed5_sous_le_seuil` | generated, unit | Coupon FIXED5 sous le seuil | 0.00s |
| ✅ | `test_remise_volume_et_coupon_welcome10` | generated, unit | Remise volume et coupon WELCOME10 | 0.00s |
| ✅ | `test_quantite_invalide_zero` | generated, unit | Quantité invalide zéro | 0.00s |

## `tests/unit/test_pricing.py`

Tests unitaires des règles de prix — Atelier 1.

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| ✅ | `test_money_arrondi_commercial` | unit | 0.125 s'arrondit à 0.13 (ROUND_HALF_UP), pas 0.12. | 0.00s |
| ✅ | `test_line_total_sans_remise` | unit | Ligne simple : prix unitaire × quantité sans remise volume. | 0.00s |
| ✅ | `test_quote_panier_vide` | unit | Un panier vide coûte 0 € : pas de frais de livraison. | 0.00s |
| ✅ | `test_remise_volume_seuil` (paramétré) | unit, parametrize | Remise -5 % dès 10 unités, pas avant. | 0.01s |
| ✅ | `test_quantite_invalide` (paramétré) | unit, parametrize | Quantité hors plage 1–99 ou non entière → ValueError. | 0.01s |
| ✅ | `test_coupon_discount_seuils` (paramétré) | unit, parametrize | Seuils et cas limites des coupons WELCOME10 / FIXED5 / FREESHIP. | 0.04s |
| ✅ | `test_coupon_inconnu` | unit | Coupon inconnu → ValueError explicite. | 0.01s |
| ✅ | `test_shipping_cost` (paramétré) | unit, parametrize | Livraison 4,90 €, offerte dès 50 € ou avec FREESHIP ; 0 si panier vide. | 0.03s |
| ✅ | `test_quote_welcome10_et_livraison` | unit | 2 mugs + WELCOME10 → total 27.40 € (sous-total 25, remise 2.50, livraison 4.90). | 0.00s |
| ✅ | `test_quote_livraison_offerte_apres_remise` | unit | Livraison offerte si total après remise >= 50 €. | 0.00s |
| ✅ | `test_quote_freeship` | unit | Coupon FREESHIP annule les frais de livraison. | 0.00s |
| ✅ | `test_quote_produit_inconnu` | unit | Produit hors catalogue → KeyError. | 0.00s |
| ✅ | `test_quote_as_dict` | unit | Sérialisation du devis : montants en chaînes et lignes présentes. | 0.00s |
| ✅ | `test_student15_sans_minimum` | unit | STUDENT15 : -15 % sans seuil minimum. | 0.00s |
| ✅ | `test_student15_sur_ligne_sans_volume` | unit | STUDENT15 s'applique sur une ligne sans remise volume (casse insensible). | 0.00s |
| ✅ | `test_student15_non_cumulable_avec_remise_volume` | unit | Si une ligne a la remise volume, STUDENT15 ne s'y applique pas. | 0.00s |
| ✅ | `test_student15_panier_uniquement_volume` | unit | Panier 100 % volume : STUDENT15 n'accorde aucune remise. | 0.00s |

## `tests/visual/test_visual.py`

Tests de régression visuelle (Atelier 7).

| Statut | Test | Marqueurs | Description | Durée |
|---|---|---|---|---|
| · | `test_accueil` | visual | Régression visuelle pleine page de l'accueil vs baseline. | 0.00s |
| · | `test_panier_avec_total` | visual | Régression visuelle du panneau panier après devis mug + tshirt. | 0.00s |
