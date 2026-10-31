# T-AppMeteo V4 — Pêche complète

V4 est une copie indépendante de la V3, avec des sections repliables et des listes personnalisables, adaptée à la pêche à l’arrêt sur le lac de Neuchâtel. Elle conserve le carnet, le sondeur manuel Lowrance Hook 5 HDI, les statistiques par espèce et les conseils issus des sorties enregistrées.

## Fonctions de pêche

- Logo vectoriel « Jarod Jacot Fishing », inspiré des couleurs turquoise, crème, anthracite et rouge du bateau.
- Bibliothèque de leurres avec photo, nom, fabricant, taille, poids, profondeur, animation et espèces ciblées (brochet, perche, silure, corégone).
- Inventaire : canne, moulinet, tresse, fil nylon, aucune ligne, hameçon et appât. Le matériel peut être sélectionné dans chaque sortie.
- Carnet avec pêcheur (Jarod, Thomas ou nom ajouté), lieu, prises, météo, observations du sondeur, notes et photos prises sur le moment ou choisies dans la photothèque.
- Détail des prises par espèce, longueur en centimètres et poids en kilogrammes, lié à chaque sortie.
- Cumuls de centimètres par pêcheur et par espèce, coupe du premier poisson enregistré par espèce, poissons d’or selon des seuils modifiables, et record de chaque pêcheur par espèce avec taille, poids, date et lieu.
- Catégories photo : leurre, poisson, ou leurre et poisson ensemble.
- Statistiques par espèce et pistes de spot, technique, animation, leurre et profondeur, fondées sur les sorties enregistrées. Elles ne garantissent pas une prise.

## Listes personnalisées et enregistrement

Les menus des pêcheurs, espèces, techniques, catégories de matériel, fréquences du sondeur, observations de clarté et catégories photo proposent une entrée « Nouvelle… ». Valide-la avec ✓ : elle reste disponible sur cet appareil pour les sorties suivantes. Une saisie non validée ne peut pas être enregistrée dans une sortie ou une fiche matériel.

Les sorties, le matériel, les leurres et réglages de seuils sont conservés dans le stockage du navigateur. Les photos sont dans IndexedDB. Le brouillon de session et les photos en attente sont aussi sauvegardés pour permettre de reprendre après fermeture de l’application.

## Synchroniser plusieurs appareils

Le carnet et les photos restent enregistrés sur l’appareil jusqu’à ce qu’un serveur soit configuré. Une fois l’adresse HTTPS et le jeton du serveur saisis dans **Synchronisation du carnet et des photos**, l’application synchronise les sorties, les fiches de leurres, le matériel, les listes personnalisées et les images au retour du réseau, au retour dans l’application et périodiquement pendant qu’elle est ouverte. Les saisies hors connexion restent sur l’appareil pour le prochain essai.

Le serveur Python fourni ici est un petit service privé, sans dépendance externe. Il doit être installé sur un ordinateur ou NAS toujours joignable. Pour l’accès depuis GitHub Pages, il faut le publier derrière un accès HTTPS avec authentification par jeton. Une option consiste à utiliser un reverse proxy Tailscale avec HTTPS : les appareils peuvent alors le joindre sur le Wi-Fi ou en réseau mobile lorsque Tailscale est connecté. Ne publie pas le port du service directement sur Internet. Les photos et le carnet envoyés au serveur sont des données personnelles.

Exemple de lancement sur le serveur privé (génère un jeton aléatoire unique et garde-le secret) :

```bash
cd v4
export TAPPMETEO_SYNC_TOKEN='remplacer-par-un-secret-aleatoire-de-32-caracteres-ou-plus'
export TAPPMETEO_SYNC_HOST='127.0.0.1'
export TAPPMETEO_SYNC_PORT='8765'
python3 sync_server.py
```

Le service attend `PUT /api/sync` pour le carnet et `GET /api/yvbeach` pour récupérer le relevé public de la station. Dans l’application, saisis l’URL HTTPS complète, par exemple `https://nom-prive.example/api/sync`, ainsi que le même jeton. Tous les appareils doivent utiliser le même serveur et le même jeton. Le serveur fusionne les fiches par date de modification et conserve les suppressions pour les propager. Son fichier de données `t-appmeteo-sync.json` doit être inclus dans les sauvegardes du serveur.

Sans serveur configuré, les photos, le carnet et le matériel ne quittent pas le navigateur. La publication GitHub Pages de l’interface ne crée pas le serveur et ne suffit donc pas à synchroniser les appareils.

## Sources météo et pêche

- **YvBeach, Yvonand** : relevés automatiques dans V4 (pression et tendance, rafales, vent et direction, température de l’air et du lac, humidité, point de rosée, pluie) avec date/heure du relevé. Comme le site ne permet pas la lecture CORS directe depuis GitHub Pages, l’application passe par le serveur privé V4 configuré : la même adresse HTTPS `/api/sync` fournit aussi `/api/yvbeach`, avec le même jeton. Si le serveur n’est pas configuré ou indisponible, l’application garde la dernière mesure mémorisée et le lien vers la station.
- **MeteoNews, Grandson** : prévisions de proximité.
- **AccuWeather, Neuchâtel** et **Windy.app, Neuchâtel** : avis secondaires destinés à la pêche.
- **Port d’Yvonand** : webcam ouverte à la demande.
- **Fishing Points, Yverdon** : ouvrir la prévision puis recopier l’indice éventuel et les périodes majeures/mineures dans V4. L’avis consulté est joint à la sortie suivante ; le pêcheur peut signaler si une prise a eu lieu pendant une période active. Les statistiques comparent ensuite les prises notées pendant/hors période par espèce et par pêcheur. La page ne fournit pas d’API publique vérifiée ; la saisie est volontairement manuelle.

Les liens externes s’ouvrent à la demande. YvBeach est lu par le serveur V4, car son site ne donne pas d’accès navigateur CORS. Fishing Points reste une saisie manuelle, car aucune API publique vérifiée n’a été trouvée.

## Lancer en local

```bash
python3 app.py
```

Puis ouvre [http://localhost:8000](http://localhost:8000). La page peut aussi être publiée sur GitHub Pages.
