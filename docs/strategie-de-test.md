# Stratégie de test — MiniShop

> Modèle à compléter pendant l'Atelier 12. Une stratégie de test tient sur 2 pages : si elle est plus longue, personne ne la lit.

## 1. Périmètre et risques
| Zone | Risque métier | Probabilité | Impact | Niveau de test principal |
|---|---|---|---|---|
| Calcul des prix (`pricing.py`) | Mauvais montant facturé | Moyenne | Élevé | Unitaire + génération IA |
| API commandes | Commande perdue | Faible | Élevé | API + contrat |
| Interface | Parcours bloqué | Moyenne | Moyen | E2E + visuel |
| Performance | Abandon de panier | … | … | Charge (Locust/JMeter) |
| Sécurité | Fuite / injection | … | … | SAST, SCA, DAST (ZAP) |

## 2. Pyramide et quality gates
| Étape pipeline | Tests | Seuil bloquant |
|---|---|---|
| PR | lint, unitaires, API | 100 % OK, couverture ≥ 85 % |
| main | + E2E, visuel, sécurité | 0 vulnérabilité HIGH/CRITICAL |
| nocturne | charge, ZAP complet | p95 < 300 ms, erreurs < 1 % |

## 3. Règles pour les tests générés par IA
- Un test généré est **relu** avant fusion (marqueur `@pytest.mark.generated`).
- Il doit échouer si on casse la règle qu'il prétend vérifier (vérifié par mutation).
- Pas de secret ni de donnée client dans les prompts (clés API hors dépôt).
- **Responsable** d'un test généré faux : l'auteur de la PR qui l'intègre (pas le modèle).
- Divergence spec/code : le test suit la **spec**, avec commentaire `# DIVERGENCE SPEC/CODE`.
- Les `test_limite_*` inventés par le LLM ne restent que s'ils ciblent une règle réelle du code.

### Comparaison Atelier 3 (`specs/pricing.feature`)
| Variante | Nb tests | Échecs | Couverture branches | Temps |
|---|---|---|---|---|
| Offline | 12 | 0 | 90 % | < 1 s |
| Anthropic (API) | — | — | — | connexion impossible → repli |
| Prompt + code (relecture guidée) | 28 | 0 | 97 % | relecture manuelle |

### Scores de mutation (`pricing.py`)
| Suite | Score |
|---|---|
| `tests/unit` (Atelier 1) | **87 %** (39/45) |
| `tests/generated` | **82 %** (37/45) |

## 4. Gestion des tests instables (flaky)
- Détection : `ai_tools/test_history.py` (score ≥ 0,6).
- Quarantaine : marqueur `flaky`, ticket ouvert, délai de correction 5 jours.
- Atelier 5 (`data/junit-history`) : flaky = `test_parcours_achat_avec_coupon` (score 0,8) ;
  ralentissement = `test_recherche_produits` (+0,007 s/run).

### Familles d'échecs (Atelier 5)
| Famille | Exemple | Classe | Action |
|---|---|---|---|
| Timeout UI `order-btn` | `TimeoutError` Playwright | Test fragile | Quarantaine + stabiliser waits |
| API down | `httpx.ConnectError` | Infrastructure | Relancer / attendre le service |
| Remise volume | `Decimal 23.27 ≠ 23.28` | Bug applicatif | Corriger le calcul |
| Postgres down | `Connection refused :5432` | Infrastructure | Service DB dans le job CI |

### Anomalies logs (Atelier 5)
| Paramètre | Rappel | Précision | Fenêtres signalées |
|---|---|---|---|
| défaut (`window 30`, `contamination 0.02`, z=6) | 100 % | 100 % | 2 |
| `--contamination 0.10` | 100 % | 100 % | 9 |
| `--window 5` | 100 % | 100 % | 10 |
| seuil z = 3 | 100 % | 91 % | 2 |

Compromis alerte nuit : défaut (peu de fenêtres, précision z-score intacte). Analyse quotidienne :
`.github/workflows/daily-anomalies.yml`. Bonus local : `MINISHOP_BUG=slow` + Locust puis
`log_anomalies.py --window 5` pour vérifier la détection du ralentissement `/cart/*`.

## 5. Indicateurs suivis
Taux de réussite sur main, durée de la suite, nombre de tests flaky, couverture, MTTR d'une régression.

## 6. Modèle de risque et priorisation (Atelier 6)

**Hypothèses vérifiées** sur `data/git-history.csv` (taux de casse global ≈ 16 %) :
1. Les gros commits cassent plus (churn Q4 ≈ 21 % vs Q1 ≈ 11 %) — confirmé.
2. `stock.py` / `pricing.py` sont les zones les plus fragiles (39 % / 36 %) — confirmé.
3. Les commits hors code (README, CSS) cassent rarement — confirmé.

**Piège de l'exactitude** : 83 % en prédisant toujours « ok » (classe majoritaire). L'AUC et le
rappel sur « casse » sont les métriques utiles ; la validation est **temporelle** (passé → futur)
pour éviter de tricher avec l'avenir. Les features historiques sont calculées *avant* chaque ligne
(pas de fuite).

| Variante | AUC | Rappel casse | Précision casse |
|---|---|---|---|
| Gradient boosting (défaut, seuil 0,5) | 0,72 | 7 % | 33 % |
| `class_weight="balanced"` (LR) | **0,75** | **48 %** | 28 % |
| Seuil 0,3 (GB) | 0,72 | 24 % | 38 % |
| `RandomForestClassifier` | 0,72 | 22 % | 41 % |
| GB + churn, seuil 0,3 | 0,72 | 41 % | 26 % |

**Choix** : LR `class_weight=balanced` (ou seuil bas) — un faux négatif coûte ~1 h de debug vs ~2 min
de tests en trop pour un faux positif → maximiser le rappel « casse ».

Job CI `risk-prioritize` (PR) : entraîne, prédit sur le diff, lance d'abord les tests ciblés (`-x`),
puis la suite complète. On **réordonne**, on ne retire jamais de tests.

### Où investir la semaine prochaine
| Module | Couverture | Mutation | Échecs hist. | Taux casse | Priorité |
|---|---|---|---|---|---|
| `stock.py` | ~50 % | — | 2 | 39 % | **HAUTE** |
| `pricing.py` | 97 % | 87 % | 4 | 36 % | Haute (bug Decimal / remise) |
| `api.py` | ~85 % | — | 4 | 27 % | Haute |
| UI `index.html` | ~40 % | — | 5 (flaky) | 16 % | Haute (stabiliser E2E) |
| `search.py` | ~60 % | — | 0 | 18 % | Moyenne |
| `style.css` | faible | — | 0 | 2 % | Basse |

Priorité n°1 : **stock.py** (fort taux de casse + couverture moyenne) et stabiliser le parcours E2E flaky.

## 7. Régression visuelle (Atelier 7)

Baselines locales : `tests/visual/baselines/{accueil,panier}.png` (Chromium Playwright).

| Changement CSS | Détecté ? | % pixels | SSIM |
|---|---|---|---|
| `--accent: #2563eb` (bleu) | oui (pixels) | 1,36 % | **1,0000** |
| `padding: 12px` → `14px` | oui | 1,98 % | 0,919 |
| `font-family: Georgia, serif` | oui | 5,12 % | 0,852 |
| Bouton « Ajouter » `display:none` | timeout fixture (bouton hidden) | — | — |

**Défaut SSIM niveaux de gris** : `_gray()` mélange R/G/B ; un vert et un bleu de luminance
proche donnent SSIM ≈ 1 alors que le diff pixel les voit. Correction : SSIM **par canal**
(moyenne des 3) ou ΔE dans l’espace Lab.

**Baselines en CI** : ne pas committer des PNG Windows puis les comparer sous Linux (polices /
anti-aliasing). Générer dans le job CI (`UPDATE_BASELINES=1`), publier l’artefact, puis
re-comparer dans le même OS image.

**Contenu dynamique** (ex. horloge) : `page.screenshot(mask=[page.locator("#clock")])`.

**Auto-healing** : `get_by_role("button", name="Calculer le total")` survit à un renommage de
`data-testid` ; risque si l’outil « répare » un test qui aurait dû échouer (régression réelle
masquée).

### Grille outils marché (synthèse)
| Outil | IA | Faux positifs | Maintenance | Coût | Données chez fournisseur |
|---|---|---|---|---|---|
| Maison (pixel+SSIM) | non | élevés (AA/polices) | baselines OS | 0 | non |
| Applitools Eyes | Visual AI layout | bas | revue diffs | $$$ | oui (screenshots) |
| Percy | diff intelligent | moyens | baselines cloud | $$ | oui |
| Playwright `toHaveScreenshot` | non | moyens | thresholds | 0 | non |
| Testim / Mabl | auto-healing locators | — | low-code | $$$ | oui (parcours) |

## 8. E2E UI (Atelier 8)

Parcours Playwright (`tests/e2e/`) via Page Object `ShopPage` : achat + WELCOME10 → 27.40,
coupon invalide (`role=alert`), bouton Commander désactivé si panier vide. Workflow
`.github/workflows/e2e.yml` : matrice chromium/firefox, traces/vidéo en cas d’échec.

**Comparatif Selenium vs Playwright** : Selenium exige `WebDriverWait` explicites et n’a pas
de traces/vidéo natives ni de `expect` web-first ; Playwright localise par rôle/`data-testid`
et produit des artefacts de debug. Cypress (JS) non retenu ici — même idée que Playwright côté
attentes auto.
