---
title: "LES TRUCS & ASTUCES HARVEST O2S - Harvest"
type: page
url: https://www.harvest.fr/les-trucs-astuces-harvest-o2s
updated: 2026-11-03
lang: fr
lang_source: html-lang
content_hash: 09a688c3051a9ac1
words: 1418
published: 2022-11-09
---

## Découvrez des astuces d’utilisation de votre solution O2S

#### Astuce n°2 : exportez facilement vos contacts vers Fidnet, la ressource patrimoniale de référence en ligne

#### Astuce n°3 : importez des portefeuilles modèles Quantalys

#### Astuce n°4 : exportez des situations de comptes vers Quantalys

#### Astuce n°5 : des déclarations d’adéquation encore plus complètes avec la documentation des supports !

#### Astuce n°6 : évaluez et contrôlez la complétude de vos données client grâce à une jauge personnalisable !

## Courrier Gmail dans O2S – Renforcement de l’authentification Google

Dans le but d’empêcher les cyberattaques de grande envergure et renforcer la sécurité des comptes, **Google** a mis en place l’identification renforcée (OAuth 2.0) depuis le **30 mai 2022** ; votre mot de passe Google ne pouvant désormais plus être conservé dans O2S, un nouveau paramétrage doit être effectué.**ATTENTION – Vous devez impérativement mettre en œuvre la procédure ci-dessous pour que la réception et l’envoi des mails via votre compte Gmail dans O2S soient opérationnels**.

Vous devez procéder en 2 temps :

### Activation de la validation en deux étapes

Allez sur www.google.fr puis cliquez sur **> Compte** :

Cliquez sur **Sécurité** dans le menu latéral à gauche. Puis, dans l’encart **Connexion à Google**, cliquez sur **Validation en deux étapes** et suivez les instructions.

Saisissez votre mot de passe Google :

Indiquez votre numéro de téléphone puis choisissez comment vous souhaitez obtenir des codes :

Puis confirmez le bon fonctionnement en saisissant le code qui vous est envoyé sur votre téléphone (le code dans l’exemple ci-dessous ne fonctionnera pas) :

Enfin, activez la validation en deux étapes :

### Activation d’un mot de passe d’application

Cliquez à nouveau sur le damier **> Compte > Sécurité**.

Puis, dans l’encart **Connexion à Google**, cliquez sur **Mots de passe des applications** et suivez les instructions.

Après avoir saisi votre mot de passe Google, choisissez **Messagerie** et sélectionnez l’appareil pour lequel vous voulez générer un mot de passe. Enfin cliquez sur **Générer**.

Copiez-collez le mot de passe qui s’affichera sur ***votre écran*** (le mot de passe dans l’exemple ci-dessous ne fonctionnera pas).

Allez dans **O2S > Services > Emails > Configuration des emails > Emails entrants > Compte utilisateur**, puis remplacez le mot de passe actuel par le mot de passe d’application que Google a généré pour vous, enfin cliquez sur **Enregistrer**.

Si nécessaire, faites de même pour les emails sortants.

Votre accès entre Google et O2S est maintenant opérationnel.

Ce mot de passe sera uniquement employé dans le cadre du lien entre Google et O2S. A tout moment, vous pouvez le gérer en vous rendant sur le site www.google.fr **> votre compte > sécurité**, encart **Connexion à Google**.

## Exportez facilement vos contacts vers Fidnet, la ressource patrimoniale de référence en ligne

**Pour plus d’informations sur les services et produits Fidroit, prenez rdv en cliquant ici.**

## Importez des portefeuilles modèles Quantalys

Tirez parti de la puissance Quantalys ; les portefeuilles modèles peuvent notamment être comparés, testés et suivis dans le temps. Importez-les dans O2S pour les utiliser dans les transactions et projets.

Procédez en 2 étapes :

#### Dans Quantalys

Cliquez sur le menu **Portefeuilles > Portefeuilles modèles**.

Constituez le portefeuille modèle selon vos souhaits ou utilisez l’un des portefeuilles « prêts à l’emploi » proposés.

Pour exporter les portefeuilles modèles, cochez-les dans la liste puis cliquez sur **Export O2S**.

Un fichier .xml est créé, enregistrez-le sur votre poste de travail.

#### Dans O2S

Dans **Outils > Portefeuilles modèles**, cliquez sur le menu « +Ajouter » en haut à droite, puis sur **Importer un portefeuille modèle Quantalys**.

Sélectionnez le fichier .xml que vous avez exporté depuis Quantalys.

Le portefeuille figure alors dans la liste de vos portefeuilles modèles.

Cliquez sur l’icone « Modifier » du portefeuille importé.

Puis, si nécessaire, cliquez sur l’onglet **Composition > Composition** pour saisir les commentaires sur le portefeuille afin que son descriptif soit visible dans la liste des portefeuilles.

**Attention !** N’oubliez pas de compléter les informations concernant l’éligibilité du portefeuille modèle : cliquez sur l’onglet **Eligibilité aux projets**, et définissez les critères permettant au portefeuille modèle d’être utilisé dans les projets.

Dans vos transactions et projets, si les critères d’éligibilité sont respectés, vous pouvez alors utiliser le portefeuille modèle Quantalys.

## Exportez des situations de comptes vers Quantalys

Alliez la force de l’agrégation d’O2S à la puissance des outils financiers de Quantalys : exportez les situations de comptes de vos clients O2S et optimisez les allocations dans Quantalys !

Voici comment procéder :

#### **Dans O2S**

Dans les résultats de vos requêtes sur des contacts ou des comptes, cochez les éléments de votre choix puis cliquez sur **Export des situations de comptes au format Quantalys (xml)**.

Afin de retrouver la composition du compte à une date spécifique, précisez la date d’export, sinon validez directement.

Un fichier .xml contenant le code ISIN et la devise des fonds, ainsi que leur poids, est généré. Récupérez-le dans votre dossier de téléchargements.

Dans Quantalys

Allez dans le menu **Clients**, puis cliquez sur **Import O2S** en bas à droite.

Cliquez sur **Choisir un fichier**, puis sélectionnez le fichier .xml exporté depuis O2S.

Cliquez sur **Valider**.

Suite à l’import, les portefeuilles mis à jour ou créés s’affichent dans la liste des clients.

***Note*** : s*i un compte détenu par un contact O2S a un identifiant identique à celui d’un contact/client dans Quantalys, ce compte est alors rattaché à ce portefeuille client : le portefeuille est mis à jour.Si l’identifiant d’un contact O2S n’existe pas dans Quantalys, le client est créé.*

## Des déclarations d’adéquation encore plus complètes avec la documentation des supports !

Dans ***Outils > Bibliothèque > Supports***, ajoutez dans le dossier **Annexes déclaration d’adéquation** de la GED de chaque support, les documents que vous souhaitez joindre à la déclaration d’adéquation.

Il vous suffit de cliquer sur + puis de sélectionner les fichiers…

…Au moment d’imprimer la déclaration d’adéquation, les documents afférents aux supports utilisés dans l’allocation du projet ou de la proposition sont automatiquement joints en annexe :

## Evaluez et contrôlez la complétude de vos données client grâce à une jauge personnalisable !

Dans chaque fiche contact, O2S vous affiche le taux de complétude du dossier

La complétude est assurée par un certain nombre de données, que vous avez la possibilité de personnaliser !

Chaque donnée correspond à un nombre de points plus ou moins important, vous permettant ainsi d’identifier celle qui a plus de poids que les autres !

Pour personnaliser les données à prendre en compte, rien de plus simple !

Rendez-vous dans le menu *Services > Personnalisation > Paramétrage > Contact > Complétude du contact*

Cocher les données à retenir, les points à affecter, activer l’utilisation de cet indicateur et cliquer sur le bouton *Enregistrer*

**Dernière astuce** : il est possible de réaliser une **Requête contacts** et d’extraire le taux de complétude de tous vos dossiers clients !

## Créez un emailing pour la mise à jour de vos données clients avec O2S

Pour vous accompagner dans la mise à jour des données KYC client, O2S vous offre la possbilité de créer un emailing afin d’adresser à vos clients leur recueil d’information en pdf remplissable pré complétés et ainsi permettre une mise à jour rapide de leurs informations.

Retrouvez ci-après les étapes à suivre pour réaliser cet emailing :

- Rendez-vous depuis le menu
- Cliquez sur le bouton   puis ***Nouvelle requête contacts***
- Dans la sélection des filtres, sélectionnez les contacts pour lesquels une adresse email est bien présent (Filtre ***Contact ½ > Email******> Oui*** ) et ajoutez les autres filtres vous permettant de cibler vos contacts

- Cliquez sur le bouton   
- Sélectionnez vos contacts grâce aux cases présentes à gauche puis rendez-vous dans le menu  ***> Email > Envoyer le Recueil d’informations Client renseigné (PDF remplissable) par emailing***

*A noter :  La même fonctionnalité est disponible pour la mise à jour du profil investisseur !*

## Optez pour une vue consolidée des portefeuilles de vos clients sur O2S

Avoir personnels ou professionnels, grâce à l’onglet ***Relations***, rattachez les fiches contacts O2S d’un même cercle relationnel pour obtenir une vision globale du portefeuille financier !

Temps nécessaire : 5 minutes

Comment optimiser la vue des portefeuilles de vos clients

1. **Dans votre fiche client O2S, rendez-vous dans le menu ***Dossier > Relations*****
2. **Cliquez sur le bouton et recherchez dans votre base de données O2S le contact à associer**
3. **Pensez à bien cliquer sur le bouton enregistrer pour valider le rattachement des fiches contact !** 

Et voilà le résultat !
