# lesupervelo

Quelques scripts utilisant l'API fifteen pour levélo boostant l'expérience utilisateur des vélos en libre-service de Marseille.

## `topbikes.py`

Affiche les 5 vélos les plus proches et leur batterie.
Le script demande votre adresse et ouvre une carte html affichant votre adresse et les 5 vélos. 

*Fonctionne sur Termux également pour une utilisation sur Android !*

**Usage** : 
```bash
> python ./topbikes.py
Entrez votre adresse à Marseille : 56 bd des Capucins
```

**TODO** : Trouver un moyen de lier le bike-id au numéro de vélo affiché sur les QR code