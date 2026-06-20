-- ============================================================================
-- BASE DE DONNÉES DU SYSTÈME DE GESTION DES MÉMOIRES/THÈSES - UAAC
-- Université Adventiste de l'Afrique Centrale
-- Version complète avec toutes les tables et relations
-- ============================================================================

-- Supprimer la base si elle existe (attention: supprime toutes les données!)
DROP DATABASE IF EXISTS uac_thesis_manager;

-- Créer la base de données avec l'encodage UTF-8 pour support complet du français
CREATE DATABASE uac_thesis_manager 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE uac_thesis_manager;

-- ============================================================================
-- TABLE 1: rôles utilisateurs
-- Définit les droits et permissions dans le système
-- ============================================================================
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant unique du rôle',
    nom VARCHAR(50) UNIQUE NOT NULL COMMENT 'Nom du rôle (etudiant, directeur, doyen)',
    description TEXT COMMENT 'Description détaillée du rôle',
    permissions JSON COMMENT 'Permissions spécifiques (format JSON)',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
    date_modification DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT 'Date de dernière modification'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table des rôles utilisateurs';

-- ============================================================================
-- TABLE 2: utilisateurs
-- Stocke toutes les informations des personnes utilisant le système
-- ============================================================================
CREATE TABLE utilisateurs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant unique utilisateur',
    matricule VARCHAR(50) UNIQUE NOT NULL COMMENT 'Matricule universitaire',
    nom VARCHAR(100) NOT NULL COMMENT 'Nom de famille',
    prenom VARCHAR(100) NOT NULL COMMENT 'Prénom(s)',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Email institutionnel',
    mot_de_passe VARCHAR(255) NOT NULL COMMENT 'Mot de passe hashé (SHA256)',
    role_id INT NOT NULL COMMENT 'ID du rôle (FK)',
    telephone VARCHAR(20) COMMENT 'Numéro de téléphone',
    domaine_id INT COMMENT 'Domaine d\'étude (pour étudiants)',
    domaine_responsable_id INT NULL COMMENT 'Domaine dont le doyen est responsable (UNIQUEMENT pour doyens)',
    annee_academique VARCHAR(20) COMMENT 'Année académique (L3, M2)',
    photo_profil VARCHAR(255) COMMENT 'Chemin photo de profil',
    est_actif BOOLEAN DEFAULT TRUE COMMENT 'Compte actif ou désactivé',
    premiere_connexion BOOLEAN DEFAULT TRUE COMMENT 'Première connexion (force changement mot de passe)',
    date_derniere_connexion DATETIME COMMENT 'Date dernière connexion',
    date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date d\'inscription',
    preferences JSON COMMENT 'Préférences utilisateur (thème, notifications, etc.)',
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    FOREIGN KEY (domaine_id) REFERENCES domaines(id) ON DELETE SET NULL,
    FOREIGN KEY (domaine_responsable_id) REFERENCES domaines(id) ON DELETE SET NULL,
    INDEX idx_email (email),
    INDEX idx_matricule (matricule),
    INDEX idx_role (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table des utilisateurs du système';

-- ============================================================================
-- TABLE 3: domaines d'étude
-- Domaines académiques de l'UAAC (basés sur le site officiel)
-- ============================================================================
CREATE TABLE domaines (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant domaine',
    code VARCHAR(20) UNIQUE NOT NULL COMMENT 'Code domaine (SHS, SAE, SEG, ST, SPE)',
    nom VARCHAR(100) NOT NULL COMMENT 'Nom complet du domaine',
    description TEXT COMMENT 'Description du domaine',
    doyen_id INT NULL COMMENT 'ID du doyen responsable du domaine (FK vers utilisateurs)',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doyen_id) REFERENCES utilisateurs(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Domaines d\'étude UAAC';

-- ============================================================================
-- TABLE 4: sujets de mémoire/thèse
-- Gère les sujets soumis par les étudiants
-- ============================================================================
CREATE TABLE sujets (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant sujet',
    titre VARCHAR(255) NOT NULL COMMENT 'Titre du mémoire/thèse',
    description TEXT COMMENT 'Description détaillée',
    mots_cles TEXT COMMENT 'Mots-clés séparés par des virgules',
    domaine_id INT NOT NULL COMMENT 'Domaine concerné',
    etudiant_id INT NOT NULL COMMENT 'Étudiant auteur',
    directeur_id INT COMMENT 'Directeur attribué',
    co_directeur_id INT COMMENT 'Co-directeur (optionnel)',
    fichier_concept VARCHAR(255) COMMENT 'Chemin fichier concept paper',
    statut ENUM('en_attente', 'approuve', 'rejete', 'en_cours', 'finalise', 'soutenu') 
        DEFAULT 'en_attente' COMMENT 'Statut du sujet',
    motif_rejet TEXT COMMENT 'Motif si rejeté',
    date_soumission DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date soumission',
    date_validation DATETIME COMMENT 'Date validation par doyen',
    date_attribution DATETIME COMMENT 'Date attribution directeur',
    date_finalisation DATETIME COMMENT 'Date finalisation mémoire',
    annee_academique VARCHAR(20) COMMENT 'Année académique',
    notes_internes TEXT COMMENT 'Notes internes (doyen/directeur)',
    
    -- ============================================================================
    -- COLONNES POUR LE SUIVI SÉQUENTIEL DES CHAPITRES
    -- ============================================================================
    chapitre_courant INT DEFAULT 1 COMMENT 'Chapitre actuel à travailler (1=Ch1, 2=Ch2, ... 5=Conclusion)',
    chapitre_max INT DEFAULT 5 COMMENT 'Nombre total de chapitres prévus',
    chapitre_1_titre VARCHAR(200) DEFAULT 'Introduction' COMMENT 'Titre du chapitre 1',
    chapitre_2_titre VARCHAR(200) DEFAULT 'Revue de littérature' COMMENT 'Titre du chapitre 2',
    chapitre_3_titre VARCHAR(200) DEFAULT 'Méthodologie' COMMENT 'Titre du chapitre 3',
    chapitre_4_titre VARCHAR(200) DEFAULT 'Résultats et analyses' COMMENT 'Titre du chapitre 4',
    chapitre_5_titre VARCHAR(200) DEFAULT 'Discussion et recommandations' COMMENT 'Titre du chapitre 5',
    chapitre_1_valide BOOLEAN DEFAULT FALSE COMMENT 'Chapitre 1 validé par directeur',
    chapitre_2_valide BOOLEAN DEFAULT FALSE COMMENT 'Chapitre 2 validé par directeur',
    chapitre_3_valide BOOLEAN DEFAULT FALSE COMMENT 'Chapitre 3 validé par directeur',
    chapitre_4_valide BOOLEAN DEFAULT FALSE COMMENT 'Chapitre 4 validé par directeur',
    chapitre_5_valide BOOLEAN DEFAULT FALSE COMMENT 'Chapitre 5 validé par directeur',
    structure_chapitres JSON COMMENT 'Structure complète des chapitres (format JSON)',
    
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_directeur (directeur_id),
    INDEX idx_statut (statut),
    INDEX idx_domaine (domaine_id),
    INDEX idx_chapitre_courant (chapitre_courant),
    FOREIGN KEY (domaine_id) REFERENCES domaines(id),
    FOREIGN KEY (etudiant_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (directeur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (co_directeur_id) REFERENCES utilisateurs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Sujets de mémoire/thèse avec suivi séquentiel des chapitres';

-- ============================================================================
-- TABLE 5: versions de travail
-- Suivi des différentes versions des chapitres
-- ============================================================================
CREATE TABLE versions_travail (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant version',
    sujet_id INT NOT NULL COMMENT 'Sujet associé',
    numero_version INT NOT NULL COMMENT 'Numéro de version (1,2,3...)',
    chapitre VARCHAR(50) COMMENT 'Numéro/nom du chapitre',
    titre_chapitre VARCHAR(200) COMMENT 'Titre du chapitre',
    contenu LONGTEXT COMMENT 'Contenu texte du chapitre',
    fichier_chemin VARCHAR(255) COMMENT 'Chemin fichier uploadé',
    commentaire_directeur TEXT COMMENT 'Commentaires du directeur',
    statut ENUM('brouillon', 'soumis', 'corrige', 'valide', 'approuve') 
        DEFAULT 'brouillon' COMMENT 'Statut version',
    taux_similarite FLOAT DEFAULT 0 COMMENT 'Taux de similarité (%)',
    rapport_similarite VARCHAR(255) COMMENT 'Chemin rapport similarité',
    score_genai FLOAT DEFAULT 0 COMMENT 'Score détection IA (0-1)',
    date_soumission DATETIME COMMENT 'Date soumission',
    date_correction DATETIME COMMENT 'Date correction par directeur',
    date_validation DATETIME COMMENT 'Date validation',
    est_version_finale BOOLEAN DEFAULT FALSE COMMENT 'Version finale?',
    version_precedente_id INT COMMENT 'Version précédente (pour historique)',
    metadonnees JSON COMMENT 'Métadonnées supplémentaires',
    INDEX idx_sujet (sujet_id),
    INDEX idx_statut (statut),
    INDEX idx_chapitre (chapitre),
    FOREIGN KEY (sujet_id) REFERENCES sujets(id) ON DELETE CASCADE,
    FOREIGN KEY (version_precedente_id) REFERENCES versions_travail(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Versions des travaux';

-- ============================================================================
-- TABLE 6: historique des feedbacks
-- Traçage complet des échanges étudiants-directeurs
-- ============================================================================
CREATE TABLE feedback_processus (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant feedback',
    version_travail_id INT NOT NULL COMMENT 'Version concernée',
    emetteur_id INT NOT NULL COMMENT 'Qui envoie',
    destinataire_id INT NOT NULL COMMENT 'Qui reçoit',
    message TEXT NOT NULL COMMENT 'Message du feedback',
    type_feedback ENUM('commentaire', 'correction', 'validation', 'rejet') 
        DEFAULT 'commentaire',
    fichier_joindre VARCHAR(255) COMMENT 'Fichier joint',
    date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date envoi',
    date_lecture DATETIME COMMENT 'Date lecture par destinataire',
    est_urgent BOOLEAN DEFAULT FALSE COMMENT 'Urgent?',
    rappel_envoye BOOLEAN DEFAULT FALSE COMMENT 'Rappel déjà envoyé?',
    rappel_date DATETIME COMMENT 'Date dernier rappel',
    temps_reponse INT COMMENT 'Temps réponse (secondes)',
    INDEX idx_version (version_travail_id),
    INDEX idx_emetteur (emetteur_id),
    INDEX idx_destinataire (destinataire_id),
    FOREIGN KEY (version_travail_id) REFERENCES versions_travail(id) ON DELETE CASCADE,
    FOREIGN KEY (emetteur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (destinataire_id) REFERENCES utilisateurs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historique des feedbacks';

-- ============================================================================
-- TABLE 7: notifications
-- Système complet de notifications utilisateurs
-- ============================================================================
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant notification',
    utilisateur_id INT NOT NULL COMMENT 'Utilisateur destinataire',
    titre VARCHAR(200) NOT NULL COMMENT 'Titre notification',
    message TEXT NOT NULL COMMENT 'Message détaillé',
    type ENUM('info', 'success', 'warning', 'danger', 'email', 'sms') 
        DEFAULT 'info' COMMENT 'Type notification',
    priorite ENUM('basse', 'normale', 'haute', 'urgente') DEFAULT 'normale',
    est_lu BOOLEAN DEFAULT FALSE COMMENT 'Lue par utilisateur?',
    est_envoye_email BOOLEAN DEFAULT FALSE COMMENT 'Email envoyé?',
    est_envoye_sms BOOLEAN DEFAULT FALSE COMMENT 'SMS envoyé?',
    lien VARCHAR(255) COMMENT 'Lien de redirection',
    icone VARCHAR(50) COMMENT 'Icône FontAwesome',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date création',
    date_lecture DATETIME COMMENT 'Date lecture',
    metadonnees JSON COMMENT 'Données supplémentaires',
    INDEX idx_utilisateur (utilisateur_id),
    INDEX idx_non_lu (utilisateur_id, est_lu),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notifications utilisateurs';

-- ============================================================================
-- TABLE 8: suivi des délais et rappels
-- Gestion automatique des deadlines
-- ============================================================================
CREATE TABLE suivi_delais (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant suivi',
    sujet_id INT NOT NULL COMMENT 'Sujet concerné',
    etape VARCHAR(100) NOT NULL COMMENT 'Étape du processus',
    type_delai ENUM('soumission', 'correction', 'validation', 'finalisation') NOT NULL,
    delai_jours INT NOT NULL COMMENT 'Délai en jours',
    date_debut DATETIME NOT NULL COMMENT 'Date début',
    date_fin_prevue DATETIME NOT NULL COMMENT 'Date fin prévue',
    date_fin_reelle DATETIME COMMENT 'Date fin réelle',
    est_en_retard BOOLEAN DEFAULT FALSE COMMENT 'En retard?',
    jours_retard INT DEFAULT 0 COMMENT 'Nombre jours retard',
    notification_24h_envoyee BOOLEAN DEFAULT FALSE COMMENT 'Rappel 24h avant?',
    notification_depassement_envoyee BOOLEAN DEFAULT FALSE COMMENT 'Rappel dépassement?',
    notification_7j_envoyee BOOLEAN DEFAULT FALSE COMMENT 'Rappel 7 jours retard?',
    escalade_doyen BOOLEAN DEFAULT FALSE COMMENT 'Escaladé au doyen?',
    INDEX idx_sujet (sujet_id),
    INDEX idx_retard (est_en_retard),
    FOREIGN KEY (sujet_id) REFERENCES sujets(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Suivi des délais';

-- ============================================================================
-- TABLE 9: logs système
-- Journalisation de toutes les actions importantes
-- ============================================================================
CREATE TABLE logs_systeme (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant log',
    utilisateur_id INT COMMENT 'Utilisateur (peut être NULL pour système)',
    action VARCHAR(100) NOT NULL COMMENT 'Action effectuée',
    entite VARCHAR(50) COMMENT 'Entité concernée (sujet, version, etc.)',
    entite_id INT COMMENT 'ID de l\'entité',
    details JSON COMMENT 'Détails de l\'action',
    adresse_ip VARCHAR(45) COMMENT 'Adresse IP utilisateur',
    user_agent TEXT COMMENT 'User Agent navigateur',
    date_action DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date action',
    INDEX idx_utilisateur (utilisateur_id),
    INDEX idx_action (action),
    INDEX idx_date (date_action),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Logs système';

-- ============================================================================
-- TABLE 10: résultats vérifications anti-plagiat
-- Stocke tous les résultats des vérifications
-- ============================================================================
CREATE TABLE verifications_plagiat (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Identifiant vérification',
    version_travail_id INT NOT NULL COMMENT 'Version vérifiée',
    methode VARCHAR(50) NOT NULL COMMENT 'Méthode utilisée',
    score_similarite FLOAT NOT NULL COMMENT 'Score similarité (%)',
    score_genai FLOAT COMMENT 'Score GenAI (0-1)',
    sources JSON COMMENT 'Sources trouvées',
    rapport_chemin VARCHAR(255) COMMENT 'Chemin rapport complet',
    temps_traitement FLOAT COMMENT 'Temps traitement (secondes)',
    est_conforme BOOLEAN COMMENT 'Conforme au seuil?',
    date_verification DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadonnees JSON COMMENT 'Métadonnées vérification',
    INDEX idx_version (version_travail_id),
    FOREIGN KEY (version_travail_id) REFERENCES versions_travail(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Résultats vérifications plagiat';

-- ============================================================================
-- TABLE 11: historique des connexions
-- Suivi des connexions utilisateurs
-- ============================================================================
CREATE TABLE historique_connexions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    utilisateur_id INT NOT NULL,
    date_connexion DATETIME DEFAULT CURRENT_TIMESTAMP,
    adresse_ip VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(128),
    succes BOOLEAN DEFAULT TRUE,
    motif_echec VARCHAR(255),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_utilisateur (utilisateur_id),
    INDEX idx_date (date_connexion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historique des connexions';

-- ============================================================================
-- TABLE 12: configuration système
-- Paramètres dynamiques modifiables via interface
-- ============================================================================
CREATE TABLE configuration (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cle VARCHAR(100) UNIQUE NOT NULL COMMENT 'Clé paramètre',
    valeur TEXT COMMENT 'Valeur paramètre',
    type VARCHAR(20) DEFAULT 'string' COMMENT 'Type: string, int, bool, json',
    description TEXT COMMENT 'Description paramètre',
    modifiable_par ENUM('admin', 'doyen', 'aucun') DEFAULT 'admin',
    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cle (cle)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Configuration système';

-- ============================================================================
-- INSERTION DES DONNÉES INITIALES
-- ============================================================================

-- Insertion des rôles
INSERT INTO roles (nom, description, permissions) VALUES
('etudiant', 'Étudiant finaliste (L3 ou M2) soumettant un mémoire/thèse', 
 '{"soumettre_sujet": true, "soumettre_version": true, "voir_dashboard": true}'),
('directeur', 'Directeur encadrant les étudiants', 
 '{"corriger_travaux": true, "valider_final": true, "voir_statistiques": true}'),
('doyen', 'Doyen de faculté supervisant le processus (un doyen par faculté)', 
 '{"valider_sujets": true, "attribuer_directeurs": true, "voir_faculte": true, "exporter_rapports": true}');

-- Insertion des domaines UAAC
INSERT INTO domaines (code, nom, description) VALUES
('SHS', 'Sciences Humaines et Sociales', 
 'Département des Sciences Humaines et Sociales - Philosophie, Théologie, Psychologie, Sociologie'),
('SAE', 'Sciences Administratives et Économiques', 
 'Département des Sciences Administratives et Économiques - Gestion, Comptabilité, Économie'),
('SEG', 'Sciences de l\'Environnement et Géomatique', 
 'Département des Sciences de l\'Environnement et Géomatique'),
('ST', 'Sciences de la Terre', 
 'Département des Sciences de la Terre - Géologie, Géographie physique'),
('SPE', 'Sciences Physiques et des Energies', 
 'Département des Sciences Physiques et des Energies - Physique, Chimie, Énergies');

-- ============================================================================
-- INSERTION DES DOYENS PAR FACULTÉ (un doyen par domaine)
-- Chaque doyen n'aura accès qu'aux données de SA propre faculté
-- Mot de passe par défaut: 'password123' hashé en SHA256
-- Hash: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
-- ============================================================================

-- Insertion des doyens d'abord (sans domaine_responsable_id car les domaines n'ont pas encore d'ID)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, premiere_connexion) VALUES
('DOYEN_SHS', 'MAMBU', 'Antoine', 'doyen_shs@uaconline.edu.cd', 
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 
 (SELECT id FROM roles WHERE nom = 'doyen'), FALSE),
('DOYEN_SAE', 'KALONJI', 'Béatrice', 'doyen_sae@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'doyen'), FALSE),
('DOYEN_SEG', 'MUKENDI', 'Joseph', 'doyen_seg@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'doyen'), FALSE),
('DOYEN_ST', 'NZUZI', 'Rachel', 'doyen_st@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'doyen'), FALSE),
('DOYEN_SPE', 'LUFUNGA', 'Christian', 'doyen_spe@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'doyen'), FALSE);

-- Mise à jour des domaines avec leurs doyens respectifs
UPDATE domaines SET doyen_id = (SELECT id FROM utilisateurs WHERE email = 'doyen_shs@uaconline.edu.cd') WHERE code = 'SHS';
UPDATE domaines SET doyen_id = (SELECT id FROM utilisateurs WHERE email = 'doyen_sae@uaconline.edu.cd') WHERE code = 'SAE';
UPDATE domaines SET doyen_id = (SELECT id FROM utilisateurs WHERE email = 'doyen_seg@uaconline.edu.cd') WHERE code = 'SEG';
UPDATE domaines SET doyen_id = (SELECT id FROM utilisateurs WHERE email = 'doyen_st@uaconline.edu.cd') WHERE code = 'ST';
UPDATE domaines SET doyen_id = (SELECT id FROM utilisateurs WHERE email = 'doyen_spe@uaconline.edu.cd') WHERE code = 'SPE';

-- Mise à jour des utilisateurs doyens avec leur domaine de responsabilité
UPDATE utilisateurs SET domaine_responsable_id = (SELECT id FROM domaines WHERE code = 'SHS') WHERE email = 'doyen_shs@uaconline.edu.cd';
UPDATE utilisateurs SET domaine_responsable_id = (SELECT id FROM domaines WHERE code = 'SAE') WHERE email = 'doyen_sae@uaconline.edu.cd';
UPDATE utilisateurs SET domaine_responsable_id = (SELECT id FROM domaines WHERE code = 'SEG') WHERE email = 'doyen_seg@uaconline.edu.cd';
UPDATE utilisateurs SET domaine_responsable_id = (SELECT id FROM domaines WHERE code = 'ST') WHERE email = 'doyen_st@uaconline.edu.cd';
UPDATE utilisateurs SET domaine_responsable_id = (SELECT id FROM domaines WHERE code = 'SPE') WHERE email = 'doyen_spe@uaconline.edu.cd';

-- Insertion des directeurs (un par domaine pour l'exemple)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, premiere_connexion, domaine_id) VALUES
('DIR_SHS', 'TSHIBANGU', 'Paul', 'directeur_shs@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'directeur'), FALSE, (SELECT id FROM domaines WHERE code = 'SHS')),
('DIR_SAE', 'MUMBALA', 'Claire', 'directeur_sae@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'directeur'), FALSE, (SELECT id FROM domaines WHERE code = 'SAE')),
('DIR_SEG', 'KASONGO', 'Pierre', 'directeur_seg@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'directeur'), FALSE, (SELECT id FROM domaines WHERE code = 'SEG')),
('DIR_ST', 'LUMUMBA', 'Grace', 'directeur_st@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'directeur'), FALSE, (SELECT id FROM domaines WHERE code = 'ST')),
('DIR_SPE', 'KABILA', 'Fabrice', 'directeur_spe@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'directeur'), FALSE, (SELECT id FROM domaines WHERE code = 'SPE'));

-- Insertion des étudiants par domaine
-- Étudiant SHS (L3)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, annee_academique, domaine_id) VALUES
('ETU_SHS001', 'MULUMBA', 'Marie', 'marie.mulumba@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'etudiant'), 'L3', 
 (SELECT id FROM domaines WHERE code = 'SHS'));

-- Étudiant SAE (M2)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, annee_academique, domaine_id) VALUES
('ETU_SAE001', 'KASONGO', 'David', 'david.kasongo@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'etudiant'), 'M2',
 (SELECT id FROM domaines WHERE code = 'SAE'));

-- Étudiant SEG (L3)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, annee_academique, domaine_id) VALUES
('ETU_SEG001', 'MBAYO', 'Joseph', 'joseph.mbayo@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'etudiant'), 'L3',
 (SELECT id FROM domaines WHERE code = 'SEG'));

-- Étudiant ST (M2)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, annee_academique, domaine_id) VALUES
('ETU_ST001', 'NGOMA', 'Rachel', 'rachel.ngoma@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'etudiant'), 'M2',
 (SELECT id FROM domaines WHERE code = 'ST'));

-- Étudiant SPE (L3)
INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role_id, annee_academique, domaine_id) VALUES
('ETU_SPE001', 'LUFUNGA', 'Christian', 'christian.lufunga@uaconline.edu.cd',
 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 (SELECT id FROM roles WHERE nom = 'etudiant'), 'L3',
 (SELECT id FROM domaines WHERE code = 'SPE'));

-- ============================================================================
-- INSERTION DE SUJETS DE TEST PAR DOMAINE
-- ============================================================================

-- Sujet pour SHS
INSERT INTO sujets (titre, description, domaine_id, etudiant_id, statut, annee_academique, 
                   chapitre_courant, chapitre_max, 
                   chapitre_1_titre, chapitre_2_titre, chapitre_3_titre, 
                   chapitre_4_titre, chapitre_5_titre,
                   date_soumission) VALUES
('Impact des réseaux sociaux sur la cohésion sociale en milieu universitaire', 
 'Cette recherche examine l\'influence des réseaux sociaux sur les relations interpersonnelles et la cohésion sociale parmi les étudiants de l\'UAAC. L\'étude utilise une approche mixte.', 
 (SELECT id FROM domaines WHERE code = 'SHS'),
 (SELECT id FROM utilisateurs WHERE matricule = 'ETU_SHS001'),
 'en_attente', 'L3', 
 1, 5,
 'Introduction générale',
 'Revue de littérature',
 'Méthodologie',
 'Résultats et analyses',
 'Discussion et recommandations',
 NOW());

-- Sujet pour SAE
INSERT INTO sujets (titre, description, domaine_id, etudiant_id, statut, annee_academique,
                   chapitre_courant, chapitre_max,
                   chapitre_1_titre, chapitre_2_titre, chapitre_3_titre,
                   chapitre_4_titre, chapitre_5_titre,
                   date_soumission) VALUES
('Optimisation de la chaîne logistique dans les entreprises congolaises', 
 'Cette recherche propose un modèle d\'optimisation de la chaîne logistique adapté au contexte congolais, avec une étude de cas dans trois entreprises de Kinshasa.', 
 (SELECT id FROM domaines WHERE code = 'SAE'),
 (SELECT id FROM utilisateurs WHERE matricule = 'ETU_SAE001'),
 'en_attente', 'M2',
 1, 5,
 'Introduction générale',
 'Revue de littérature',
 'Méthodologie',
 'Résultats et analyses',
 'Discussion et recommandations',
 NOW());

-- ============================================================================
-- INSERTION DE LA CONFIGURATION SYSTÈME
-- ============================================================================

INSERT INTO configuration (cle, valeur, type, description, modifiable_par) VALUES
('seuil_similarite', '20', 'int', 'Seuil maximum de similarité autorisé (%)', 'doyen'),
('seuil_genai', '0.6', 'float', 'Seuil détection contenu IA (0-1)', 'doyen'),
('delai_soumission_chapitre', '14', 'int', 'Délai pour soumettre un chapitre (jours)', 'doyen'),
('delai_correction_directeur', '7', 'int', 'Délai correction directeur (jours)', 'doyen'),
('notifications_email', 'true', 'bool', 'Activer notifications email', 'admin'),
('notifications_sms', 'false', 'bool', 'Activer notifications SMS', 'admin'),
('maintenance_mode', 'false', 'bool', 'Mode maintenance', 'admin'),
('max_upload_size_mb', '50', 'int', 'Taille maximale des fichiers uploadés (MB)', 'admin');

-- ============================================================================
-- VUES SPÉCIFIQUES PAR FACULTÉ (pour optimisation)
-- ============================================================================

-- Vue: Statistiques par faculté (pour le doyen)
CREATE OR REPLACE VIEW vue_stats_par_faculte AS
SELECT 
    d.id as domaine_id,
    d.code as domaine_code,
    d.nom as domaine_nom,
    COUNT(DISTINCT s.id) as total_sujets,
    SUM(CASE WHEN s.statut = 'en_attente' THEN 1 ELSE 0 END) as en_attente,
    SUM(CASE WHEN s.statut = 'approuve' THEN 1 ELSE 0 END) as approuves,
    SUM(CASE WHEN s.statut = 'en_cours' THEN 1 ELSE 0 END) as en_cours,
    SUM(CASE WHEN s.statut = 'finalise' THEN 1 ELSE 0 END) as finalises,
    SUM(CASE WHEN s.statut = 'rejete' THEN 1 ELSE 0 END) as rejetes,
    COUNT(DISTINCT s.directeur_id) as directeurs_actifs,
    COUNT(DISTINCT s.etudiant_id) as etudiants_actifs
FROM domaines d
LEFT JOIN sujets s ON d.id = s.domaine_id
WHERE YEAR(s.date_soumission) = YEAR(CURDATE()) OR s.date_soumission IS NULL
GROUP BY d.id;

-- Vue: Progression des étudiants par chapitre
CREATE OR REPLACE VIEW vue_progression_etudiants AS
SELECT 
    s.id as sujet_id,
    s.titre,
    CONCAT(e.prenom, ' ', e.nom) as etudiant_nom,
    s.chapitre_courant,
    s.chapitre_max,
    s.chapitre_1_valide,
    s.chapitre_2_valide,
    s.chapitre_3_valide,
    s.chapitre_4_valide,
    s.chapitre_5_valide,
    ROUND(((s.chapitre_1_valide + s.chapitre_2_valide + s.chapitre_3_valide + 
            s.chapitre_4_valide + s.chapitre_5_valide) / s.chapitre_max) * 100, 2) as pourcentage_completion
FROM sujets s
JOIN utilisateurs e ON s.etudiant_id = e.id;

-- Vue: Alertes par faculté
CREATE OR REPLACE VIEW vue_alertes_par_faculte AS
SELECT 
    d.id as domaine_id,
    d.code as domaine_code,
    s.id as sujet_id,
    s.titre as sujet_titre,
    CONCAT(e.prenom, ' ', e.nom) as etudiant_nom,
    CONCAT(dr.prenom, ' ', dr.nom) as directeur_nom,
    sd.etape,
    sd.jours_retard,
    sd.date_fin_prevue
FROM suivi_delais sd
JOIN sujets s ON sd.sujet_id = s.id
JOIN domaines d ON s.domaine_id = d.id
JOIN utilisateurs e ON s.etudiant_id = e.id
JOIN utilisateurs dr ON s.directeur_id = dr.id
WHERE sd.est_en_retard = TRUE AND sd.date_fin_reelle IS NULL;

-- ============================================================================
-- INDEX SUPPLÉMENTAIRES POUR OPTIMISATION DES REQUÊTES PAR FACULTÉ
-- ============================================================================

-- Index pour les requêtes filtrées par domaine
CREATE INDEX idx_sujets_domaine_statut ON sujets(domaine_id, statut);
CREATE INDEX idx_sujets_domaine_date ON sujets(domaine_id, date_soumission DESC);
CREATE INDEX idx_utilisateurs_domaine_role ON utilisateurs(domaine_id, role_id);
CREATE INDEX idx_sujets_chapitre_courant ON sujets(chapitre_courant);
CREATE INDEX idx_sujets_chapitre_valide ON sujets(chapitre_1_valide, chapitre_2_valide, chapitre_3_valide, chapitre_4_valide, chapitre_5_valide);

-- ============================================================================
-- PROCÉDURE POUR DÉBLOQUER LE CHAPITRE SUIVANT
-- ============================================================================

DELIMITER //
CREATE PROCEDURE deverrouiller_chapitre_suivant(IN p_sujet_id INT, IN p_chapitre_valide INT)
BEGIN
    DECLARE v_chapitre_courant INT;
    DECLARE v_chapitre_max INT;
    
    -- Récupérer les informations du sujet
    SELECT chapitre_courant, chapitre_max INTO v_chapitre_courant, v_chapitre_max
    FROM sujets WHERE id = p_sujet_id;
    
    -- Si le chapitre validé correspond au chapitre courant, passer au suivant
    IF p_chapitre_valide = v_chapitre_courant AND v_chapitre_courant < v_chapitre_max THEN
        UPDATE sujets 
        SET chapitre_courant = chapitre_courant + 1
        WHERE id = p_sujet_id;
    END IF;
END//
DELIMITER ;

-- ============================================================================
-- TRIGGER POUR METTRE À JOUR LA PROGRESSION APRÈS VALIDATION
-- ============================================================================

DELIMITER //
CREATE TRIGGER after_version_validee
AFTER UPDATE ON versions_travail
FOR EACH ROW
BEGIN
    DECLARE v_numero_chapitre INT;
    
    -- Si la version vient d'être validée
    IF NEW.statut = 'valide' AND OLD.statut != 'valide' THEN
        -- Extraire le numéro du chapitre
        SET v_numero_chapitre = CAST(SUBSTRING_INDEX(NEW.chapitre, ' ', -1) AS UNSIGNED);
        
        -- Mettre à jour le flag de validation dans sujets
        IF v_numero_chapitre = 1 THEN
            UPDATE sujets SET chapitre_1_valide = TRUE WHERE id = NEW.sujet_id;
        ELSEIF v_numero_chapitre = 2 THEN
            UPDATE sujets SET chapitre_2_valide = TRUE WHERE id = NEW.sujet_id;
        ELSEIF v_numero_chapitre = 3 THEN
            UPDATE sujets SET chapitre_3_valide = TRUE WHERE id = NEW.sujet_id;
        ELSEIF v_numero_chapitre = 4 THEN
            UPDATE sujets SET chapitre_4_valide = TRUE WHERE id = NEW.sujet_id;
        ELSEIF v_numero_chapitre = 5 THEN
            UPDATE sujets SET chapitre_5_valide = TRUE WHERE id = NEW.sujet_id;
        END IF;
        
        -- Déverrouiller le chapitre suivant
        CALL deverrouiller_chapitre_suivant(NEW.sujet_id, v_numero_chapitre);
    END IF;
END//
DELIMITER ;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

SELECT 'Base de données UAC créée avec succès!' as message;
SELECT 'Doyens par faculté configurés:' as info;
SELECT u.nom as doyen, d.code as faculte 
FROM utilisateurs u 
JOIN domaines d ON u.domaine_responsable_id = d.id 
WHERE u.role_id = (SELECT id FROM roles WHERE nom = 'doyen');

SELECT 'Système de progression des chapitres activé' as progression_status;