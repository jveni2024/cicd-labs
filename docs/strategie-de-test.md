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

## 5. Indicateurs suivis
Taux de réussite sur main, durée de la suite, nombre de tests flaky, couverture, MTTR d'une régression.
