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
