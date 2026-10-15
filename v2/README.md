# T-AppMeteo V2 — Pêche en lac

Copie indépendante de T-AppMeteo, avec des conditions météo utiles pour préparer une sortie en lac et un petit carnet d’observations de pêche.

## Paramètres affichés

- Température de l’air, ressenti, humidité et précipitations.
- Vent, direction et rafales, pour évaluer les conditions sur le lac.
- Couverture nuageuse et heures de lever/coucher du soleil.
- Pression atmosphérique et évolution calculée sur les trois dernières heures lorsque les données horaires le permettent.
- Espèce recherchée : brochet, perche, silure ou corégone.
- Module sondeur avec profil Lowrance Hook 5 HDI : température de l’eau, profondeur sous le bateau, profondeur des poissons, vitesse en nœuds et fréquence utilisée. Saisie manuelle, car la page web ne reçoit pas directement les données du sondeur.
- Observations facultatives enregistrées dans le navigateur : température et clarté de l’eau, ainsi que les profondeurs repérées au sondeur.
- Phase de lune et estimation de l’éclairage lunaire.
- Niveau horaire du lac de Neuchâtel à la station de Grandson, via l’API ouverte de l’OFEV ; la dernière mesure peut manquer ou avoir un léger délai.
- Carnet local des sorties : date/heure, lieu ou poste, espèce, leurre/technique, température de l’eau, profondeurs du fond et des poissons, vitesse, fréquence sonar et notes.

## Idées de paramètres spécifiques à chaque espèce

- **Brochet** : température de l’eau, profondeur du poste, végétation et structures proches.
- **Perche** : profondeur des bancs repérée au sondeur, température et clarté de l’eau.
- **Silure** : température de l’eau, profondeur, structure du fond et heure de sortie.
- **Corégone** : température de l’eau et profondeur des bancs ou de la thermocline repérée au sondeur.

La météo vient d’Open-Meteo et le niveau du lac des observations hydrologiques de l’OFEV. Les lectures du sondeur, la température et la clarté de l’eau ainsi que les profondeurs de pêche ne sont pas automatiquement relevées par l’application : elles doivent être saisies ou observées sur place. La phase de lune est une estimation astronomique. Ces indicateurs aident à préparer une sortie ; ils ne prédisent pas les prises.

## Lancer en local

```bash
python3 app.py
```

Puis ouvre [http://localhost:8000](http://localhost:8000). L’application peut aussi être hébergée en HTTPS via GitHub Pages et utilisée sur iPhone ou avec une connexion mobile.

## Localisation et vie privée

Les deux villes suisses initiales restent Yverdon-les-Bains et Yvonand. Le GPS propose la localité détectée avant confirmation. La position, les villes ajoutées et les observations de pêche sont conservées dans le navigateur. Les coordonnées GPS sont envoyées à Nominatim/OpenStreetMap pour identifier la localité, puis à Open-Meteo pour la météo. La localisation réseau facultative utilise ipapi.co.
