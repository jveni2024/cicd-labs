# ADR 0002 — Politique de blocage sécurité dans la CI

- **Statut** : accepté
- **Date** : 2026-11-19

## Contexte
L’atelier 11 introduit SAST, SCA, scan d’image et DAST. Il faut décider ce qui **bloque**
une PR / un merge, sans noyer l’équipe sous des faux positifs (CVE OS sans patch, ZAP bruyant).

## Options étudiées
| Contrôle | Bloquer toujours | Bloquer si correctif | Rapport seulement |
|---|---|---|---|
| Bandit HIGH | clair, rapide | — | trop permissif |
| pip-audit | peut casser sur bruit | idéal | risque d’oublier |
| Trivy | faux positifs OS | **ignore-unfixed** | SBOM utile même sans blocage |
| ZAP baseline | flaky / WARN | FAIL sur règles corrigées | scan nocturne pour le reste |

## Décision
- **Bloquent PR/main** : Bandit HIGH, pip-audit, Trivy HIGH/CRITICAL **avec correctif disponible**.
- **ZAP baseline** : rapport sur PR ; règles 10021/10038 en FAIL (régression d’en-têtes).
- **ZAP API** : nocturne uniquement (durée).

## Conséquences
- Workflow `.github/workflows/security.yml` reflète cette matrice.
- Dependabot reste la source de PRs de bump ; la CI valide, ne remplace pas la revue humaine.
