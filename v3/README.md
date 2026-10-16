# T-AppMeteo V3 — Pêche complète

V3 est une copie indépendante de la V2, adaptée à la pêche à l’arrêt sur le lac de Neuchâtel. Elle conserve le carnet, le sondeur manuel Lowrance Hook 5 HDI, les statistiques par espèce et les conseils issus des sorties enregistrées.

## Sources ajoutées

- **YvBeach, Yvonand** : lien vers les relevés de la station locale.
- **MeteoNews, Grandson** : accès aux prévisions de proximité.
- **AccuWeather, Neuchâtel** : avis météo destiné à la pêche.
- **Windy.app, Neuchâtel** : prévision et indice de mordant. Le point du lien fourni se situe à Neuchâtel, pas à Yvonand.
- **Port d’Yvonand** : ouverture de la webcam uniquement après sélection du bouton.

Les liens tiers sont ouverts à la demande. La météo principale affichée par l’application et ses statistiques restent séparées des avis de ces sites. Aucun indice externe n’est présenté comme une garantie de prise. L’application ne récupère pas automatiquement les relevés des sites qui ne fournissent pas d’accès de données vérifié.

## Carnet et statistiques

Le carnet enregistre l’espèce, le spot, le nombre de prises, la technique, l’animation, le leurre, les notes et la météo disponible au moment de la sortie. Les statistiques classent les résultats par espèce et proposent des pistes selon les sorties enregistrées et les conditions météo comparables. Les résultats restent dans le stockage local du navigateur et ne sont pas synchronisés entre appareils.

## Lancer en local

```bash
python3 app.py
```

Puis ouvre [http://localhost:8000](http://localhost:8000). La page peut également être publiée sur GitHub Pages et utilisée sur iPhone.

## Données et confidentialité

La webcam, les prévisions et indices externes ne sont pas chargés automatiquement. Un clic ouvre le site concerné dans un nouvel onglet. Les données du carnet restent localement dans le navigateur.
