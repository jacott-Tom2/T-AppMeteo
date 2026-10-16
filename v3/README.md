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

Le carnet enregistre le pêcheur (Jarod, Thomas ou un nom ajouté), l’espèce, le spot, le nombre de prises, la technique, l’animation, le leurre, les observations au sondeur, les notes et la météo disponible au moment de la sortie.

Les photos peuvent être prises avec l’appareil photo ou choisies dans la photothèque. Chaque photo est classée comme **leurre**, **poisson** ou **leurre et poisson ensemble**. Les images sont réduites et conservées dans le stockage local de ce navigateur ; elles ne sont pas téléversées.

Les statistiques classent les résultats par espèce et proposent des pistes pour le spot, la technique, le leurre, l’animation et la profondeur des poissons repérés. Elles favorisent les sorties avec météo proche et prennent aussi en compte, lorsque les valeurs ont été notées, la température et la clarté de l’eau ainsi que la profondeur des poissons. Les indications reposent sur les sorties enregistrées : elles restent provisoires avec peu de données et ne garantissent pas une prise. Les données du carnet et les photos ne sont pas synchronisées entre appareils.

Le choix ou la recherche de ville, le GPS et la localisation réseau sont regroupés en haut de l’application, avant la météo et le carnet.

## Logo et bibliothèque de leurres

Le logo vectoriel « Jarod Jacot Fishing » reprend le turquoise, le crème, l’anthracite et le rouge visibles sur le bateau. La bibliothèque permet d’ajouter une photo prise sur le moment ou choisie dans la photothèque, puis de noter le nom, le fabricant, la taille, le poids, la profondeur d’utilisation, l’animation et les espèces ciblées. Elle peut être filtrée par espèce et triée par nom, fabricant, poids ou profondeur.

Les fiches et images de la bibliothèque sont conservées dans le navigateur de l’appareil. Aucune fiche de leurre n’est préremplie : les photos fournies représentent le bateau et une sortie, pas les modèles de leurres.

## Lancer en local

```bash
python3 app.py
```

Puis ouvre [http://localhost:8000](http://localhost:8000). La page peut également être publiée sur GitHub Pages et utilisée sur iPhone.

## Données et confidentialité

La webcam, les prévisions et indices externes ne sont pas chargés automatiquement. Un clic ouvre le site concerné dans un nouvel onglet. Les données du carnet restent localement dans le navigateur.
