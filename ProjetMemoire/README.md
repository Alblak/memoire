# Système de Gestion des Mémoires/Thèses - UAC

## Présentation du Projet

Ce système a été développé pour l'**Université de l'Assomption au Congo (UAC)** afin de digitaliser et optimiser la gestion des mémoires de Licence (L3) et Master (M2). Il offre une plateforme complète intégrant:

- Gestion des soumissions de sujets
- Attribution automatique des directeurs
- Suivi des versions de travail
- Module anti-plagiat avec détection GenAI
- Système de notifications et rappels automatiques
- Dashboard analytique pour le suivi des performances

## Architecture Technique

### Technologies Utilisées
- **Backend**: Python Flask 2.3.3
- **Base de données**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (Responsive Design)
- **Modules spécifiques**:
  - TF-IDF et n-grams pour détection de similarité
  - RapportLab pour génération PDF
  - PyPDF2/python-docx pour extraction texte

### Structure de la Base de Données

8 tables principales:
1. `roles` - Gestion des droits (étudiant/directeur/doyen)
2. `utilisateurs` - Informations utilisateurs
3. `domaines` - Domaines d'étude (SHS, SAE, SEG, ST, SPE)
4. `sujets` - Sujets de mémoire/thèse
5. `versions_travail` - Versions des chapitres
6. `feedback_processus` - Historique des échanges
7. `notifications` - Système d'alertes
8. `suivi_delais` - Monitoring des délais

## Installation et Configuration

### Prérequis
```bash
- Python 3.8+
- MySQL 5.7+
- pip (gestionnaire de paquets Python)

```
Comptes de Test
Rôle  Email Mot de passe
Doyen doyen@uaconline.edu.cd  password123
Directeur paul.tshibangu@uaconline.edu.cd password123
Étudiant  marie.mulumba@uaconline.edu.cd  password123
Fonctionnalités Détaillées
1. Module Étudiant
Soumission de sujet
Formulaire avec titre, description, domaine

Upload du concept paper (PDF, DOC, DOCX, TXT)

Sélection de l'année académique (L3/M2)

Gestion des versions
Soumission des chapitres par version

Suivi des corrections du directeur

Notification automatique des retours

Version finale
Upload du manuscrit complet

Vérification anti-plagiat automatique

Génération de rapport PDF détaillé

Si non-conforme: rejet avec motif et notification doyen/directeur

2. Module Directeur
Dashboard
Vue des étudiants encadrés

Liste des versions à corriger

Historique par année académique

Corrections
Consultation des travaux soumis

Ajout de commentaires détaillés

Validation ou retour pour correction

Suivi des délais de réponse

Validation finale
Examen du manuscrit complet

Consultation du rapport de similarité

Approbation ou rejet avec commentaires

3. Module Doyen
Validation des sujets
Consultation des soumissions

Téléchargement des concept papers

Attribution aux directeurs

Rejet avec motif

Supervision
Dashboard des statistiques faculté

Suivi des retards (étudiants & directeurs)

Consultation des rapports de similarité

Historique
Statistiques par année académique

Performance des directeurs

Taux de finalisation

4. Module Anti-Plagiat
Technologies utilisées
TF-IDF : Mesure de similarité cosinus

N-grams : Détection de similarité structurelle

Heuristiques statistiques : Détection GenAI

Fonctionnalités
Extraction de texte multi-formats (PDF, DOCX, TXT)

Prétraitement linguistique (stop words, tokenisation)

Calcul de score de similarité

Génération de rapport PDF authentique

Détection de contenu généré par IA

Seuils configurables
Similarité: 20% par défaut (ajustable)

GenAI: score composite de 0-100%

5. Système de Notifications
Types de notifications
Sujet approuvé/rejeté

Nouvelle version soumise

Corrections disponibles

Rappels de retard

Validation finale

Canaux
In-app (dashboard)

Emails (configuration SMTP)

Alertes prioritaires (doyen)

6. Gestion des Délais
Paramètres configurables
Soumission chapitre: 14 jours

Correction directeur: 7 jours

Actions automatiques
Vérification quotidienne des retards

Envoi de rappels aux concernés

Escalade au doyen si retard persistant

Sécurité
Authentification
Mots de passe hashés (SHA256)

Sessions sécurisées Flask

Protection CSRF

Contrôle d'accès
Décorateurs de rôle (@role_required)

Vérification des permissions par ressource

Fichiers
Sanitization des noms de fichiers (secure_filename)

Validation des types MIME

Stockage isolé par type
```