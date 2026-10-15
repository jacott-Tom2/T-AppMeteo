# T-AppMeteo

> **En développement!**

Application météo légère, en français, conçue pour Yverdon-les-Bains (1400), Yvonand et les localités suisses ajoutées par l’utilisateur.

## Fonctionnalités prévues

- Yverdon-les-Bains et Yvonand apparaissent en tête du menu déroulant.
- La météo de la ville choisie s’affiche automatiquement juste sous le menu.
- Un champ permet de rechercher et d’ajouter une ville suisse.
- Chaque nouvelle ville est ajoutée à la suite de la liste et conservée dans le navigateur.
- Bouton GPS à la demande, avec autorisation du téléphone, pour afficher et mémoriser la météo de la position.
- Localisation réseau facultative par adresse IP pour estimer une ville lorsque le GPS n’est pas utilisé ; elle peut être imprécise.
- Affichage des conditions actuelles : température, ressenti, humidité, vent et précipitations.
- Interface responsive, adaptée à Safari sur iPhone 15 Pro Max comme aux anciens iPhone et petits écrans.
- Zones sûres de l’écran respectées, champs sans zoom automatique au toucher, boutons tactiles d’au moins 48 px.
- Fonctionne avec les connexions mobiles 3G, 4G et 5G.
- Cache de session, chargement à la demande et délais d’attente pour mieux gérer les réseaux lents.
- Aucune clé API ni dépendance Python externe.

## Lancer en local

Python 3 est requis.

```bash
python3 app.py
```

Ouvre ensuite [http://localhost:8000](http://localhost:8000).

Pour tester depuis un autre appareil du même réseau local, lance le serveur avec `--host 0.0.0.0`, puis ouvre l’adresse IP de l’ordinateur suivie de `:8000` sur le téléphone.

## Accès via le réseau mobile

Pour l’utiliser depuis une connexion mobile en dehors du réseau local, héberge les fichiers sur un serveur accessible publiquement en HTTPS. `index.html` est un site statique léger et peut être publié avec GitHub Pages. Le script Python sert surtout à tester le projet ou à le lancer sur un serveur Python.

Le GPS du navigateur nécessite une connexion sécurisée HTTPS (ou `localhost`) et l’autorisation de l’utilisateur. La position GPS ajoutée est enregistrée dans le stockage local du navigateur ; ses coordonnées sont envoyées à Open-Meteo pour obtenir la météo. L’option réseau envoie la requête à [ipapi.co](https://ipapi.co/api/) : ce service reçoit l’adresse IP publique et retourne une estimation de la ville, qui peut être inexacte sur un réseau mobile.

## Données météo

Les données et la recherche des localités utilisent les API d’[Open-Meteo](https://open-meteo.com/). Une connexion Internet est nécessaire pour obtenir les données actuelles.
