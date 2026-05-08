# Analyse complète du projet pour présentation PowerPoint

## Sources et périmètre de l'analyse

Cette analyse est basée sur :

- le projet local `QueueLessClinics` ;
- le dépôt distant GitHub : https://github.com/fouratjebali/QueueLessClinics ;
- l'historique Git local associé au dépôt distant `origin` ;
- le lien Trello fourni : https://trello.com/b/78ozVsA1/project-django ;
- les fichiers Angular, Django, PostgreSQL, Docker et de configuration présents dans le projet.

Remarque importante : le tableau Trello n'a pas pu être consulté complètement depuis l'environnement d'analyse, car la page Trello nécessite JavaScript et/ou une session Trello active. Les informations non visibles sur Trello sont donc indiquées par la mention **à compléter par l'étudiant**.

---

## 1. Contexte général du projet

Le projet **QueueLessClinics** est un projet full stack réalisé dans un cadre universitaire, dans la matière **Outils collaboratifs**, à l'**ISSAT de Sousse**.

Il s'agit d'une application web de gestion de files d'attente pour des cliniques. Le projet combine une interface frontend Angular, un backend Django exposant des API REST, et une base de données PostgreSQL.

L'objectif pédagogique principal n'est pas seulement de produire une application fonctionnelle, mais aussi de mettre en pratique des méthodes de collaboration utilisées dans les projets logiciels :

- organisation du travail en tâches ;
- gestion de versions avec Git ;
- collaboration et centralisation du code avec GitHub ;
- suivi de l'avancement avec Trello ;
- intégration progressive des contributions ;
- préparation d'une démonstration et d'une documentation de projet.

Dans ce cadre, le projet permet aux étudiants de simuler un environnement de développement collaboratif proche d'un projet réel.

---

## 2. Problématique

Dans les cliniques, la gestion des files d'attente est souvent réalisée de façon manuelle ou semi-manuelle : prise de ticket papier, appel oral des patients, estimation approximative du temps d'attente, absence de visibilité en temps réel pour les patients.

Ces méthodes classiques présentent plusieurs limites :

- manque de transparence sur la position du patient dans la file ;
- difficulté à estimer le temps d'attente ;
- surcharge du personnel d'accueil ;
- risque d'erreurs dans l'ordre de passage ;
- absence de statistiques fiables sur les flux de patients ;
- difficulté à gérer plusieurs services ou plusieurs cliniques ;
- faible traçabilité des actions effectuées sur les tickets.

Le besoin identifié est donc de proposer une solution numérique permettant de gérer les files d'attente de manière plus claire, plus rapide et plus traçable, aussi bien pour les patients que pour le personnel et les administrateurs.

---

## 3. Idée choisie

L'idée choisie est une plateforme web appelée **QueueLessClinics**, destinée à gérer les files d'attente dans un environnement médical.

La solution propose trois espaces principaux :

- un espace public destiné aux patients ;
- un espace staff destiné au personnel de la clinique ;
- un espace administrateur destiné à la gestion globale des cliniques, utilisateurs, statistiques et paramètres.

La valeur ajoutée du projet est de transformer une file d'attente classique en un système numérique consultable, pilotable et analysable. Le patient peut rejoindre une file, suivre son ticket et consulter un tableau d'affichage public. Le personnel peut gérer les tickets et l'avancement de la file. L'administrateur peut superviser les cliniques, les utilisateurs, les paramètres et les données d'activité.

Le choix de ce sujet est pertinent dans un cadre universitaire, car il permet de travailler plusieurs dimensions :

- conception d'une application full stack ;
- modélisation de données relationnelles ;
- développement d'API REST ;
- développement d'interfaces utilisateur ;
- gestion des rôles et des parcours utilisateurs ;
- collaboration avec Git, GitHub et Trello.

---

## 4. Objectifs du projet

### Objectifs fonctionnels

Les objectifs fonctionnels identifiés dans le code sont :

- permettre à un patient de consulter les cliniques et statistiques publiques ;
- permettre à un patient de rejoindre une file d'attente ;
- générer un ticket avec numéro, position et temps d'attente estimé ;
- permettre au patient de suivre l'état de son ticket ;
- afficher un tableau public des tickets en cours et prochains tickets ;
- permettre au personnel de gérer la file d'attente d'une clinique ;
- permettre au personnel d'appeler, servir, terminer, annuler ou marquer absent un ticket ;
- permettre la création de tickets walk-in pour les patients présents physiquement ;
- gérer les services proposés par une clinique ;
- gérer les paramètres de clinique ;
- permettre à un administrateur de gérer les cliniques ;
- permettre à un administrateur de gérer les utilisateurs ;
- consulter les statistiques et journaux d'audit ;
- gérer les paramètres système.

### Objectifs techniques

Les objectifs techniques sont :

- construire une architecture frontend/backend séparée ;
- exposer des API REST avec Django REST Framework ;
- utiliser PostgreSQL comme base de données relationnelle ;
- structurer le frontend avec Angular 15 ;
- utiliser Angular Material pour les composants d'interface ;
- gérer le routing Angular par espaces : public, staff, admin ;
- préparer un environnement local avec Docker Compose ;
- centraliser les appels API dans un service Angular ;
- gérer la session utilisateur côté frontend ;
- organiser la logique métier autour des entités : clinique, file, ticket, service, utilisateur.

### Objectifs collaboratifs

Les objectifs collaboratifs sont :

- utiliser Git pour suivre l'évolution du code ;
- travailler avec des branches par sprint et par contributeur ;
- intégrer progressivement les fonctionnalités dans `dev` ;
- utiliser GitHub comme dépôt distant et espace de collaboration ;
- utiliser Trello pour organiser les tâches, suivre l'avancement et clarifier les responsabilités ;
- préparer une démonstration finale et une présentation universitaire.

---

## 5. Fonctionnalités principales

### Fonctionnalités côté utilisateur public

Les fonctionnalités publiques visibles dans le frontend sont :

- page d'accueil publique ;
- consultation des statistiques publiques ;
- accès à une page de participation à une file d'attente ;
- saisie des informations patient ;
- choix d'un service ;
- création d'un ticket ;
- suivi d'un ticket ;
- consultation du statut du ticket ;
- annulation d'un ticket ;
- tableau public d'affichage pour une clinique.

### Fonctionnalités côté staff

Les fonctionnalités staff identifiées sont :

- tableau de bord staff ;
- consultation des indicateurs de file ;
- ouverture et fermeture d'une file ;
- gestion des tickets d'une file ;
- appel d'un ticket ;
- démarrage de la prise en charge ;
- clôture d'un ticket ;
- annulation d'un ticket ;
- marquage d'un patient absent ;
- réordonnancement des tickets ;
- ajout d'un patient sans rendez-vous ;
- gestion des services de la clinique ;
- gestion des paramètres de clinique ;
- consultation de l'historique ;
- consultation des rapports ;
- consultation et modification du profil utilisateur.

### Fonctionnalités côté administrateur

Les fonctionnalités administrateur identifiées sont :

- gestion des cliniques ;
- création, modification et activation/désactivation de cliniques ;
- détail d'une clinique ;
- gestion du branding, du logo, des horaires et des règles de file ;
- gestion des services d'une clinique ;
- gestion des utilisateurs ;
- modification des rôles ;
- affectation d'utilisateurs à des cliniques ;
- réinitialisation de mot de passe ;
- consultation des analytics ;
- export CSV/PDF prévu côté API ;
- consultation des logs d'audit ;
- gestion des paramètres système ;
- test de notifications.

### Parcours utilisateur principal

Un parcours principal possible est :

1. Le patient accède à l'espace public.
2. Il choisit une clinique ou rejoint une file via un lien.
3. Il saisit son nom, téléphone, email optionnel, service et notes.
4. Le système crée un ticket avec un numéro et une position.
5. Le patient suit son ticket via une page de statut.
6. Le staff gère la file depuis son dashboard.
7. Le ticket passe par plusieurs états : `WAITING`, `CALLED`, `SERVING`, `COMPLETED`, ou `CANCELLED`.
8. Les statistiques de file sont mises à jour.

---

## 6. Architecture globale

Le projet repose sur une architecture full stack en trois couches.

### Frontend Angular

Le dossier `angular-app/` contient l'application frontend. Angular est utilisé pour :

- afficher les interfaces publiques, staff et admin ;
- gérer la navigation via `app-routing.module.ts` ;
- consommer les API REST via `ApiService` ;
- gérer la session utilisateur via `AuthSessionService` ;
- protéger les routes selon le rôle via `AuthRoleGuard` ;
- construire les écrans avec Angular Material.

### Backend Django

Le dossier `django-backend/` contient le projet Django. Django est utilisé pour :

- définir les modèles métier ;
- exposer les API REST ;
- gérer les règles de file d'attente ;
- gérer les utilisateurs et rôles ;
- centraliser la logique métier côté serveur.

Le backend utilise Django REST Framework pour sérialiser les données et exposer des endpoints.

### Base de données PostgreSQL

PostgreSQL est utilisé pour stocker les données :

- cliniques ;
- paramètres ;
- utilisateurs ;
- services ;
- files ;
- tickets ;
- événements ;
- notifications.

Le fichier `database/schema.sql` définit le schéma SQL initial, et `database/seed.sql` ajoute des données de démonstration.

### Communication frontend/backend

La communication se fait par HTTP via des API REST sous le préfixe `/api/`.

Exemple :

- frontend Angular : `http://localhost:4200` ;
- backend Django : `http://localhost:8000/api` ;
- configuration Angular : `src/environments/environment.ts` et `environment.prod.ts`.

Le service Angular `ApiService` centralise les appels HTTP vers le backend.

---

## 7. Stack technique

La stack technique identifiée est :

- **Angular 15** : frontend ;
- **Angular Material** : composants UI ;
- **TypeScript** : langage du frontend ;
- **RxJS** : gestion des flux asynchrones Angular ;
- **Django 4.2+** : backend ;
- **Django REST Framework** : API REST ;
- **PostgreSQL 15** : base de données ;
- **Redis 7** : présent dans Docker Compose pour cache ou extension future ;
- **Docker Compose** : environnement local multi-services ;
- **Nginx** : configuration prévue pour servir le frontend en production ;
- **Git** : gestion de versions ;
- **GitHub** : dépôt distant et collaboration ;
- **Trello** : suivi de tâches et organisation du projet.

---

## 8. Structure du projet

### Dossiers principaux

- `angular-app/` : application Angular.
- `django-backend/` : backend Django.
- `database/` : scripts SQL pour schéma et données initiales.
- `docker-compose.yml` : orchestration des services locaux.

### Structure Angular importante

- `src/app/app.module.ts` : déclaration des composants et modules Angular Material.
- `src/app/app-routing.module.ts` : routes publiques, staff et admin.
- `src/app/services/api.service.ts` : appels HTTP vers le backend.
- `src/app/services/auth-session.service.ts` : stockage de la session utilisateur.
- `src/app/auth-role.guard.ts` : protection des routes par rôle.
- `src/app/models.ts` : interfaces TypeScript principales.
- `src/app/layouts/` : layouts public, staff et admin.
- `src/app/pages/public/` : pages publiques.
- `src/app/pages/staff/` : pages staff.
- `src/app/pages/admin/` : pages administrateur.
- `src/app/shared/` : composants partagés, notamment `KpiCardComponent`.
- `src/environments/` : configuration des URLs API.

### Structure Django importante

- `manage.py` : point d'entrée Django.
- `backend/settings.py` : configuration Django, PostgreSQL, CORS, DRF.
- `backend/urls.py` : routage global des API.
- `core/models.py` : modèles métier.
- `core/serializers.py` : serializers DRF.
- `core/views.py` : ViewSets et APIViews.
- `core/admin.py` : configuration de l'administration Django.
- `core/migrations/` : dossier de migrations, actuellement limité à `__init__.py`.

### Fichiers de configuration importants

- `docker-compose.yml` : définit Angular, Django, PostgreSQL, Redis et pgAdmin.
- `angular-app/angular.json` : configuration de build Angular.
- `angular-app/tsconfig.json` : configuration TypeScript stricte.
- `angular-app/package.json` : dépendances frontend.
- `django-backend/requirements.txt` : dépendances backend.
- `database/schema.sql` : schéma SQL initial.
- `database/seed.sql` : données initiales.

---

## 9. Analyse backend Django

### Applications Django

Le projet Django contient une application principale :

- `core` : contient les modèles, serializers, vues et logique métier.

Les applications installées incluent :

- `django.contrib.admin` ;
- `django.contrib.auth` ;
- `django.contrib.sessions` ;
- `rest_framework` ;
- `rest_framework.authtoken` ;
- `corsheaders` ;
- `django.contrib.postgres` ;
- `core`.

### Modèles principaux

Les modèles principaux définis dans `core/models.py` sont :

- `Clinic` : représente une clinique.
- `ClinicSettings` : paramètres liés à une clinique.
- `User` : utilisateur personnalisé avec rôle et clinique associée.
- `Service` : service médical proposé par une clinique.
- `Queue` : file d'attente quotidienne d'une clinique.
- `Ticket` : ticket patient dans une file.
- `QueueEvent` : événement lié à une file ou un ticket.
- `Notification` : notification liée à un ticket.
- `AdminAuditLog` : journal d'audit administrateur.
- `SystemSettings` : paramètres système globaux.

### Logique métier principale

La logique métier importante concerne :

- la création automatique d'une file du jour si nécessaire ;
- la génération du numéro de ticket ;
- le calcul de la position du ticket ;
- le calcul du temps d'attente estimé ;
- la mise à jour des statistiques de file ;
- les transitions d'état d'un ticket ;
- l'enregistrement d'événements dans `QueueEvent` ;
- la gestion des rôles `ADMIN`, `STAFF`, `DOCTOR`, `NURSE`, `RECEPTIONIST`.

### Serializers

Les serializers DRF permettent de transformer les modèles en JSON et inversement. Les serializers importants sont :

- `ClinicSerializer` ;
- `ClinicSettingsSerializer` ;
- `ServiceSerializer` ;
- `QueueSerializer` ;
- `TicketSerializer` ;
- `UserSerializer` ;
- `AdminClinicSerializer` ;
- `AdminUserSerializer` ;
- `AdminAuditLogSerializer` ;
- `SystemSettingsSerializer`.

### Vues et routes API

Le backend utilise deux styles :

- `ModelViewSet` pour les ressources principales ;
- `APIView` pour les actions spécifiques public, staff et admin.

Endpoints principaux identifiés :

- `/api/clinics/`
- `/api/services/`
- `/api/queues/`
- `/api/tickets/`
- `/api/users/`
- `/api/public/stats/`
- `/api/auth/login/`
- `/api/auth/logout/`
- `/api/auth/me/`
- `/api/auth/change-password/`
- `/api/staff/clinic/`
- `/api/staff/queues/`
- `/api/staff/tickets/`
- `/api/staff/services/`
- `/api/admin/clinics/`
- `/api/admin/users/`
- `/api/admin/analytics/overview/`
- `/api/admin/audit-logs/`
- `/api/admin/settings/`

### Remarque de sécurité

Le fichier `settings.py` indique que les permissions DRF par défaut sont `AllowAny`, et que certaines autorisations sont gérées au niveau applicatif via des headers comme `X-User-Role`, `X-User-Id`, `X-User-Email`. Pour un projet académique local, cela permet de démontrer les rôles. Pour une production réelle, il faudrait renforcer cette partie avec une authentification serveur complète, par exemple JWT ou sessions sécurisées.

---

## 10. Analyse frontend Angular

### Organisation générale

Le frontend est organisé autour de trois espaces :

- espace public ;
- espace staff ;
- espace admin.

Chaque espace possède un layout spécifique :

- `PublicLayoutComponent` ;
- `StaffLayoutComponent` ;
- `AdminLayoutComponent`.

### Composants publics

Les composants publics principaux sont :

- `PublicHomePageComponent` ;
- `JoinQueuePageComponent` ;
- `TicketStatusPageComponent` ;
- `TrackTicketPageComponent` ;
- `PublicBoardPageComponent`.

Ils permettent de présenter les cliniques, rejoindre une file, suivre un ticket et afficher un tableau public.

### Composants staff

Les composants staff principaux sont :

- `DashboardPageComponent` ;
- `QueueHistoryPageComponent` ;
- `ReportsPageComponent` ;
- `ClinicSettingsPageComponent` ;
- `ServicesSettingsPageComponent` ;
- `AddEditServiceDialogComponent` ;
- `AddWalkinModalComponent` ;
- `UserProfilePageComponent`.

Ils permettent de gérer la file, les tickets, les services, les paramètres et le profil.

### Composants admin

Les composants admin principaux sont :

- `ClinicsPageComponent` ;
- `ClinicDetailPageComponent` ;
- `UsersManagementPageComponent` ;
- `AnalyticsPageComponent` ;
- `AuditLogsPageComponent` ;
- `SystemSettingsPageComponent`.

Ils permettent la supervision générale de la plateforme.

### Services Angular

Les services principaux sont :

- `ApiService` : centralise tous les appels HTTP ;
- `AuthSessionService` : stocke et récupère le token et l'utilisateur courant ;
- `LocalTicketStoreService` : conserve localement des tickets consultés côté public.

### Routing

Le routing est structuré ainsi :

- `/public` : pages publiques ;
- `/auth/login` : authentification ;
- `/staff` : espace staff protégé ;
- `/admin` : espace admin protégé.

Le guard `AuthRoleGuard` protège les routes selon le rôle utilisateur.

### Communication API

Le frontend consomme le backend avec `HttpClient`. L'URL de base est définie dans :

- `src/environments/environment.ts` ;
- `src/environments/environment.prod.ts`.

Les appels sont regroupés par domaine : public, auth, staff, admin, clinics, users, tickets, analytics, settings.

---

## 11. Analyse base de données PostgreSQL

### Tables principales dans `database/schema.sql`

Les tables SQL explicitement définies sont :

- `clinics` ;
- `clinic_settings` ;
- `users` ;
- `services` ;
- `queues` ;
- `tickets` ;
- `queue_events` ;
- `notifications`.

### Relations principales

Les relations principales sont :

- une clinique possède des paramètres via `clinic_settings` ;
- une clinique possède plusieurs utilisateurs ;
- une clinique possède plusieurs services ;
- une clinique possède plusieurs files ;
- une file possède plusieurs tickets ;
- un ticket appartient à une file, à une clinique et éventuellement à un service ;
- un ticket peut être appelé ou servi par un utilisateur ;
- une file possède plusieurs événements ;
- un ticket peut avoir plusieurs notifications.

### Rôle de la base de données

PostgreSQL assure :

- la persistance des données métier ;
- la cohérence relationnelle ;
- l'historique des files et tickets ;
- la traçabilité des événements ;
- les statistiques nécessaires aux dashboards et analytics.

### Remarque sur la cohérence schéma/modèles

Le fichier `core/models.py` contient aussi les modèles `AdminAuditLog` et `SystemSettings`. Cependant, `database/schema.sql` ne contient pas explicitement les tables `admin_audit_logs` et `system_settings` au moment de l'analyse. Comme le dossier `core/migrations/` ne contient que `__init__.py`, il faut vérifier comment ces tables sont créées en local.

Mention recommandée dans la soutenance : **à compléter par l'étudiant** si la base locale contient ces tables via un autre script ou une migration non versionnée.

---

## 12. Analyse Git et GitHub

### Dépôt distant

Le dépôt distant configuré localement est :

- `origin` : https://github.com/fouratjebali/QueueLessClinics.git

Le dépôt GitHub est public. La page GitHub consultée indique que la branche par défaut affichée est `main`. Localement, le travail principal d'intégration se fait sur la branche `dev`.

### Branches existantes observées localement

Branches locales :

- `dev`
- `main`
- `sprint1-Fourat`
- `sprint2-Fourat`
- `sprint3-Fourat`
- `sprint4-Fourat`
- `sprint5-Fourat`
- `sprint6-Fourat`

Branches distantes observées :

- `origin/dev`
- `origin/main`
- `origin/project-setup`
- `origin/spring1-selim`
- `origin/sprint1-Fourat`
- `origin/sprint1-medamin`
- `origin/sprint2-Fourat`
- `origin/sprint2-medamin`
- `origin/sprint2-selim`
- `origin/sprint3-Fourat`
- `origin/sprint3-medamin`
- `origin/sprint3-selim`
- `origin/sprint4-Fourat`
- `origin/sprint4-medamin`
- `origin/sprint4-selim`
- `origin/sprint5-Fourat`
- `origin/sprint5-medamin`
- `origin/sprint5-selim`
- `origin/sprint6-Fourat`
- `origin/sprint6-medamin`

### Rôle des branches

D'après les noms des branches, le projet utilise une organisation par :

- branche `main` : branche initiale ou branche principale par défaut du dépôt ;
- branche `dev` : branche d'intégration du développement ;
- branches `sprintX-nom` : branches de travail par sprint et par contributeur ;
- branche `project-setup` : configuration initiale du projet.

Cette organisation montre une démarche collaborative par étapes de développement, où chaque sprint regroupe des tâches ou fonctionnalités avant intégration dans `dev`.

### Commits importants observés

Exemples de commits et merges importants observés dans l'historique local :

- `69868ad` : Initial commit - Project initialization ;
- `25f8cba` : scaffold Angular 15 frontend ;
- `7357a1a` : scaffold Django backend and core app ;
- `2be850b` : add Docker setup and repo config ;
- `5dd1c65` : docs: Add initial README with project description and tech stack ;
- `0ea2dd0` : Add sprint 1 backend updates ;
- `b19add9` : Add sprint 2 layout components ;
- `8add227` : Merge branch `sprint3-Fourat` into `dev` ;
- `07cb5a1` : feat: styliser user profile page ;
- `d516911` : feat: styliser page user mgmt ;
- `30e2e04` : feat: conf prod env ;
- `0153e6f` : Merge pull request #11 from `sprint6-selim`.

L'historique local contient 79 commits sur `dev` au moment de l'analyse.

### Evolution du projet

L'évolution du projet peut être résumée ainsi :

1. Initialisation du dépôt.
2. Scaffold Angular.
3. Scaffold Django.
4. Ajout de Docker Compose et de la configuration locale.
5. Mise en place de la base de données.
6. Ajout progressif du backend et des endpoints.
7. Ajout des layouts Angular.
8. Ajout des pages publiques.
9. Ajout des pages staff.
10. Ajout des pages admin.
11. Ajout de la session, des rôles et de l'environnement.
12. Intégration progressive dans `dev`.

### Utilisation de Git

Git a servi à :

- sauvegarder les versions successives ;
- créer des branches de travail ;
- isoler les développements de chaque sprint ;
- revenir à un état stable si nécessaire ;
- comparer les changements ;
- fusionner les contributions.

### Utilisation de GitHub

GitHub a servi à :

- centraliser le dépôt distant ;
- partager le code entre les membres ;
- pousser les branches de sprint ;
- intégrer les branches dans `dev` ;
- garder une trace des commits et pull requests ;
- sécuriser le projet en ligne.

Informations GitHub non visibles ou à confirmer depuis l'interface complète :

- répartition exacte des pull requests par membre : **à compléter par l'étudiant** ;
- discussions ou revues de code GitHub : **à compléter par l'étudiant** ;
- issues GitHub utilisées ou non : **à compléter par l'étudiant**.

---

## 13. Analyse Trello

Le tableau Trello fourni est :

- https://trello.com/b/78ozVsA1/project-django

L'accès complet au tableau n'a pas été possible depuis l'environnement d'analyse, car Trello exige JavaScript et/ou une session active. Les informations ci-dessous doivent donc être complétées à partir du tableau réel par l'étudiant.

### Listes / colonnes utilisées

Listes visibles : **à compléter par l'étudiant**.

Exemples de listes attendues dans un projet collaboratif :

- Backlog ;
- À faire ;
- En cours ;
- En test ;
- Terminé ;
- Documentation / Présentation.

Ces noms sont des exemples de structure possible et doivent être remplacés par les noms réellement présents dans le board.

### Cartes créées

Cartes visibles : **à compléter par l'étudiant**.

À compléter avec les cartes réellement présentes dans Trello, par exemple :

- analyse et conception ;
- préparation de l'environnement ;
- développement backend ;
- développement frontend ;
- intégration API ;
- base de données ;
- tests ;
- documentation ;
- préparation de la présentation.

### Tâches planifiées

Tâches planifiées visibles : **à compléter par l'étudiant**.

### Tâches terminées

Tâches terminées visibles : **à compléter par l'étudiant**.

### Répartition du travail

La présentation ne doit pas dire que le travail a été divisé par fichiers. La répartition doit être présentée par responsabilités ou étapes :

- analyse et conception ;
- modélisation de la base de données ;
- développement backend ;
- développement frontend public ;
- développement espace staff ;
- développement espace admin ;
- intégration frontend/backend ;
- tests et correction ;
- documentation ;
- préparation de la soutenance.

Répartition exacte entre les membres : **à compléter par l'étudiant**.

### Utilisation de Trello comme outil collaboratif

Trello a pour rôle attendu :

- visualiser l'avancement du projet ;
- organiser les tâches par priorité ;
- suivre les tâches terminées et restantes ;
- répartir les responsabilités ;
- éviter les oublis ;
- faciliter la coordination entre les membres.

Informations exactes à compléter depuis le board :

- noms des colonnes ;
- cartes principales ;
- membres affectés ;
- dates limites ;
- checklists ;
- commentaires ;
- pièces jointes.

---

## 14. Difficultés rencontrées

### Difficultés techniques

Difficultés identifiées ou probables à partir du code :

- coordination entre Angular, Django et PostgreSQL ;
- configuration des environnements Angular (`environment.ts`, `environment.prod.ts`) ;
- gestion stricte des templates Angular avec `strictTemplates` ;
- dépassement de budgets SCSS en build production Angular ;
- synchronisation entre modèles Django, interfaces TypeScript et schéma PostgreSQL ;
- gestion des rôles et sessions utilisateur ;
- structuration d'un grand nombre de composants frontend.

### Difficultés d'intégration frontend/backend

Les difficultés d'intégration possibles sont :

- aligner les noms de champs entre API Django et interfaces Angular ;
- gérer les URLs API selon l'environnement ;
- gérer les réponses paginées ou non paginées ;
- gérer les erreurs HTTP côté interface ;
- sécuriser les routes selon les rôles ;
- maintenir la cohérence des types dans `models.ts`.

### Difficultés liées à la base de données

Difficultés possibles :

- création correcte des tables PostgreSQL ;
- gestion des relations entre cliniques, queues, tickets et services ;
- calcul des statistiques ;
- cohérence entre `schema.sql` et les modèles Django ;
- absence de migrations Django détaillées dans le dépôt au moment de l'analyse.

### Difficultés liées à Git, GitHub et Trello

Difficultés possibles :

- synchroniser les branches avec `dev` ;
- éviter les conflits lors des merges ;
- pousser les branches au bon moment ;
- organiser les commits ;
- garder Trello à jour ;
- faire correspondre les tâches Trello aux branches et commits.

### Solutions appliquées

Solutions observées :

- utilisation de branches de sprint ;
- merges progressifs dans `dev` ;
- utilisation de Docker Compose pour standardiser l'environnement ;
- centralisation des appels API dans `ApiService` ;
- création d'interfaces TypeScript ;
- utilisation de guards Angular pour les rôles ;
- ajout de fichiers `environment.ts` et `environment.prod.ts` ;
- vérification locale par build Angular.

---

## 15. Résultat final

### Etat actuel du projet

Le projet local est structuré et contient :

- frontend Angular complet avec plusieurs espaces ;
- backend Django avec API REST ;
- base PostgreSQL avec scripts SQL ;
- environnement Docker Compose ;
- branches Git organisées par sprint ;
- intégration GitHub.

### Ce qui fonctionne selon l'analyse locale

La build Angular en configuration development passe après correction locale des erreurs de typage strict :

```bash
npx ng build --configuration development
```

Fonctionnalités présentes dans le code :

- pages publiques ;
- création et suivi de tickets ;
- dashboard staff ;
- gestion des files et tickets ;
- gestion de services ;
- pages admin ;
- analytics et audit logs côté API/interface ;
- configuration des environnements API ;
- gestion de session côté frontend.

### Limites éventuelles

Limites à mentionner :

- le build production peut être bloqué par les budgets SCSS définis dans `angular.json` ;
- la sécurité backend devrait être renforcée pour un usage réel ;
- le schéma SQL doit être vérifié par rapport aux derniers modèles Django ;
- Trello doit être documenté avec des captures ou détails visibles ;
- les migrations Django complètes sont à vérifier ;
- les tests automatisés ne sont pas visibles comme axe principal dans le dépôt.

### Améliorations possibles

Améliorations proposées :

- ajouter une authentification JWT complète côté backend ;
- ajouter des migrations Django versionnées ;
- aligner totalement `schema.sql` et `models.py` ;
- ajouter des tests backend et frontend ;
- améliorer le responsive design ;
- intégrer des notifications réelles SMS/email ;
- ajouter un déploiement cloud ;
- ajouter une documentation API ;
- ajouter des captures d'écran dans le README ;
- améliorer le suivi Trello avec labels, checklists et dates.

---

## 16. Apport des outils collaboratifs

### Git

Git a permis :

- de suivre toutes les versions du projet ;
- d'isoler le travail par branche ;
- de sécuriser les modifications ;
- de comparer les changements ;
- de fusionner les contributions ;
- de garder un historique exploitable pour la soutenance.

### GitHub

GitHub a permis :

- de centraliser le code ;
- de partager le projet avec les membres ;
- de sauvegarder le projet à distance ;
- de créer et pousser les branches ;
- de suivre les pull requests et merges ;
- de garder une trace de l'évolution du projet.

### Trello

Trello a permis ou doit permettre :

- de planifier les tâches ;
- de suivre l'avancement ;
- de visualiser ce qui reste à faire ;
- de répartir les responsabilités ;
- de faciliter la coordination ;
- de documenter l'organisation du travail.

Les détails précis du board Trello sont **à compléter par l'étudiant** à partir de l'interface Trello.

### Synthèse

Dans ce projet, les outils collaboratifs ont joué un rôle central. Git a assuré la gestion des versions, GitHub a servi de plateforme commune pour le code et Trello a servi d'outil de planification. Ensemble, ils ont permis de structurer un projet full stack complexe en étapes plus simples, de coordonner les membres et de préparer une présentation cohérente du travail réalisé.

---

# Proposition de plan PowerPoint : 14 slides

## Slide 1 - Page de garde

### Points clés

- QueueLessClinics
- Projet full stack Angular, Django, PostgreSQL
- Matière : Outils collaboratifs
- ISSAT de Sousse
- Réalisé par : à compléter par l'étudiant
- Année universitaire : à compléter par l'étudiant

### Visuels recommandés

- Logo ou capture de la page d'accueil.
- Icônes Angular, Django, PostgreSQL, GitHub, Trello.

### Notes orales possibles

Présenter brièvement le projet comme une application web de gestion de files d'attente pour cliniques, réalisée dans le cadre de la matière Outils collaboratifs.

---

## Slide 2 - Contexte du projet

### Points clés

- Projet universitaire.
- Travail collaboratif.
- Application full stack.
- Mise en pratique de Git, GitHub et Trello.

### Visuels recommandés

- Schéma simple : Université -> Equipe -> Projet -> Outils collaboratifs.

### Notes orales possibles

Expliquer que le projet vise à développer une application, mais aussi à montrer la capacité de l'équipe à organiser, versionner et suivre le travail.

---

## Slide 3 - Problématique

### Points clés

- Files d'attente souvent gérées manuellement.
- Manque de visibilité pour les patients.
- Difficulté de suivi pour le staff.
- Peu de statistiques fiables.

### Visuels recommandés

- Illustration d'une file d'attente classique.
- Comparaison manuel vs numérique.

### Notes orales possibles

Décrire les limites des méthodes classiques et expliquer pourquoi une solution numérique apporte de la valeur.

---

## Slide 4 - Idée choisie

### Points clés

- Plateforme QueueLessClinics.
- Gestion numérique des files d'attente.
- Trois espaces : public, staff, admin.
- Suivi du ticket en temps réel.

### Visuels recommandés

- Diagramme montrant les trois espaces de l'application.

### Notes orales possibles

Présenter la solution choisie comme une plateforme qui connecte patients, personnel et administrateurs autour d'un même système.

---

## Slide 5 - Objectifs du projet

### Points clés

- Objectifs fonctionnels : tickets, files, services, utilisateurs.
- Objectifs techniques : Angular, Django, PostgreSQL, API REST.
- Objectifs collaboratifs : Git, GitHub, Trello.

### Visuels recommandés

- Tableau en trois colonnes : fonctionnel, technique, collaboratif.

### Notes orales possibles

Insister sur le fait que le projet répond à la fois à un besoin applicatif et à un objectif pédagogique lié aux outils collaboratifs.

---

## Slide 6 - Fonctionnalités principales

### Points clés

- Patient : rejoindre une file, suivre un ticket.
- Staff : gérer tickets, files, services.
- Admin : gérer cliniques, utilisateurs, analytics, paramètres.

### Visuels recommandés

- Captures des pages public, staff et admin.
- Icônes par type d'utilisateur.

### Notes orales possibles

Présenter les fonctionnalités par rôle, sans entrer dans les détails techniques.

---

## Slide 7 - Architecture générale

### Points clés

- Frontend Angular.
- Backend Django REST Framework.
- Base PostgreSQL.
- Communication HTTP/REST.
- Docker Compose pour l'environnement local.

### Visuels recommandés

- Schéma d'architecture : Angular -> API Django -> PostgreSQL.
- Ajouter Redis et pgAdmin comme services de l'environnement local.

### Notes orales possibles

Expliquer le flux : l'utilisateur interagit avec Angular, Angular appelle les API Django, Django lit et écrit dans PostgreSQL.

---

## Slide 8 - Stack technique

### Points clés

- Angular 15.
- Angular Material.
- Django 4.2+.
- Django REST Framework.
- PostgreSQL 15.
- Docker Compose.
- Git, GitHub, Trello.

### Visuels recommandés

- Logos des technologies.

### Notes orales possibles

Justifier le choix de chaque technologie : Angular pour l'interface, Django pour les API, PostgreSQL pour les données relationnelles, Git/GitHub/Trello pour la collaboration.

---

## Slide 9 - Utilisation de Trello

### Points clés

- Organisation des tâches.
- Suivi de l'avancement.
- Répartition par responsabilités.
- Planification des étapes.
- Détails du board : à compléter par l'étudiant.

### Visuels recommandés

- Capture réelle du board Trello.
- Colonnes Trello : à compléter par l'étudiant.

### Notes orales possibles

Expliquer que Trello a été utilisé pour visualiser les tâches du projet et suivre leur progression. Compléter oralement avec les colonnes et cartes réellement présentes.

---

## Slide 10 - Utilisation de Git

### Points clés

- Branches de sprint.
- Commits réguliers.
- Historique du projet.
- Isolation du travail avant merge.

### Visuels recommandés

- Capture de `git log --graph`.
- Schéma branches -> dev.

### Notes orales possibles

Expliquer que Git a permis de conserver un historique précis et de travailler sans écraser les contributions des autres.

---

## Slide 11 - Utilisation de GitHub

### Points clés

- Dépôt distant centralisé.
- Branches poussées sur GitHub.
- Pull requests et merges vers `dev`.
- Sauvegarde et collaboration.

### Visuels recommandés

- Capture du dépôt GitHub.
- Capture des branches ou pull requests.

### Notes orales possibles

Montrer que GitHub a servi de point de synchronisation entre les membres et de preuve de l'évolution du projet.

---

## Slide 12 - Démonstration du projet

### Points clés

- Page publique.
- Rejoindre une file.
- Suivi du ticket.
- Dashboard staff.
- Gestion admin.

### Visuels recommandés

- Captures d'écran ou courte séquence de démonstration.
- Parcours patient -> staff -> admin.

### Notes orales possibles

Faire une démonstration courte et structurée : patient crée un ticket, staff le traite, admin consulte la gestion ou les statistiques.

---

## Slide 13 - Difficultés et solutions

### Points clés

- Intégration frontend/backend.
- Configuration API environments.
- Typage strict Angular.
- Gestion des branches Git.
- Cohérence base/modèles.

### Visuels recommandés

- Tableau difficulté / solution.

### Notes orales possibles

Expliquer que les difficultés rencontrées sont normales dans un projet full stack collaboratif et montrer les solutions appliquées.

---

## Slide 14 - Conclusion et perspectives

### Points clés

- Application fonctionnelle localement.
- Objectifs collaboratifs atteints.
- Expérience pratique avec Git, GitHub, Trello.
- Perspectives : sécurité, tests, déploiement, notifications réelles.

### Visuels recommandés

- Schéma final du projet ou capture de l'application.
- Liste courte des perspectives.

### Notes orales possibles

Conclure sur l'apport du projet : apprentissage technique, organisation collaborative et production d'une application complète exploitable comme base d'amélioration.

