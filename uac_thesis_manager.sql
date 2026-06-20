-- phpMyAdmin SQL Dump
-- version 4.7.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le :  mer. 27 mai 2026 à 18:03
-- Version du serveur :  5.7.17
-- Version de PHP :  5.6.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `uac_thesis_manager`
--

DELIMITER $$
--
-- Procédures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `deverrouiller_chapitre_suivant` (IN `p_sujet_id` INT, IN `p_chapitre_valide` INT)  BEGIN
    DECLARE v_chapitre_courant INT;
    DECLARE v_chapitre_max INT;
    
    SELECT chapitre_courant, chapitre_max INTO v_chapitre_courant, v_chapitre_max
    FROM sujets WHERE id = p_sujet_id;
    
        IF p_chapitre_valide = v_chapitre_courant AND v_chapitre_courant < v_chapitre_max THEN
        UPDATE sujets 
        SET chapitre_courant = chapitre_courant + 1
        WHERE id = p_sujet_id;
    END IF;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `configuration`
--

CREATE TABLE `configuration` (
  `id` int(11) NOT NULL,
  `cle` varchar(100) NOT NULL COMMENT 'Clé paramètre',
  `valeur` text COMMENT 'Valeur paramètre',
  `type` varchar(20) DEFAULT 'string' COMMENT 'Type: string, int, bool, json',
  `description` text COMMENT 'Description paramètre',
  `modifiable_par` enum('admin','doyen','aucun') DEFAULT 'admin',
  `date_modification` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Configuration système';

--
-- Déchargement des données de la table `configuration`
--

INSERT INTO `configuration` (`id`, `cle`, `valeur`, `type`, `description`, `modifiable_par`, `date_modification`) VALUES
(1, 'seuil_similarite', '20', 'int', 'Seuil maximum de similarité autorisé (%)', 'doyen', '2026-05-27 00:30:45'),
(2, 'seuil_genai', '0.6', 'float', 'Seuil détection contenu IA (0-1)', 'doyen', '2026-05-27 00:30:45'),
(3, 'delai_soumission_chapitre', '14', 'int', 'Délai pour soumettre un chapitre (jours)', 'doyen', '2026-05-27 00:30:45'),
(4, 'delai_correction_directeur', '7', 'int', 'Délai correction directeur (jours)', 'doyen', '2026-05-27 00:30:45'),
(5, 'notifications_email', 'true', 'bool', 'Activer notifications email', 'admin', '2026-05-27 00:30:45'),
(6, 'notifications_sms', 'false', 'bool', 'Activer notifications SMS', 'admin', '2026-05-27 00:30:45'),
(7, 'maintenance_mode', 'false', 'bool', 'Mode maintenance', 'admin', '2026-05-27 00:30:45'),
(8, 'max_upload_size_mb', '50', 'int', 'Taille maximale des fichiers uploadés (MB)', 'admin', '2026-05-27 00:30:45');

-- --------------------------------------------------------

--
-- Structure de la table `domaines`
--

CREATE TABLE `domaines` (
  `id` int(11) NOT NULL COMMENT 'Identifiant domaine',
  `code` varchar(20) NOT NULL COMMENT 'Code domaine (SHS, SAE, SEG, ST, SPE)',
  `nom` varchar(100) NOT NULL COMMENT 'Nom complet du domaine',
  `description` text COMMENT 'Description du domaine',
  `doyen_id` int(11) DEFAULT NULL COMMENT 'ID du doyen responsable du domaine (FK vers utilisateurs)',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Domaines d''étude UAAC';

--
-- Déchargement des données de la table `domaines`
--

INSERT INTO `domaines` (`id`, `code`, `nom`, `description`, `doyen_id`, `date_creation`) VALUES
(1, 'SHS', 'Sciences Humaines et Sociales', 'Domaines de philosophie et communication', 1, '2026-05-27 00:30:45'),
(2, 'SAE', 'Sciences Agronomiques et Environnement', 'Départements de développement', 2, '2026-05-27 00:30:45'),
(3, 'SEG', 'Sciences Economique et Gestion', 'Les domaines de gestion et informatique', 3, '2026-05-27 00:30:45'),
(4, 'ST', 'Sciences et Technologie', 'Domaines de polytechnique', 4, '2026-05-27 00:30:45'),
(5, 'SPE', 'Sciences Psychologiques et Education', 'Département de psychologie', 5, '2026-05-27 00:30:45');

-- --------------------------------------------------------

--
-- Structure de la table `feedback_processus`
--

CREATE TABLE `feedback_processus` (
  `id` int(11) NOT NULL COMMENT 'Identifiant feedback',
  `version_travail_id` int(11) NOT NULL COMMENT 'Version concernée',
  `emetteur_id` int(11) NOT NULL COMMENT 'Qui envoie',
  `destinataire_id` int(11) NOT NULL COMMENT 'Qui reçoit',
  `message` text NOT NULL COMMENT 'Message du feedback',
  `type_feedback` enum('commentaire','correction','validation','rejet') DEFAULT 'commentaire',
  `fichier_joindre` varchar(255) DEFAULT NULL COMMENT 'Fichier joint',
  `date_envoi` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Date envoi',
  `date_lecture` datetime DEFAULT NULL COMMENT 'Date lecture par destinataire',
  `est_urgent` tinyint(1) DEFAULT '0' COMMENT 'Urgent?',
  `rappel_envoye` tinyint(1) DEFAULT '0' COMMENT 'Rappel déjà envoyé?',
  `rappel_date` datetime DEFAULT NULL COMMENT 'Date dernier rappel',
  `temps_reponse` int(11) DEFAULT NULL COMMENT 'Temps réponse (secondes)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historique des feedbacks';

-- --------------------------------------------------------

--
-- Structure de la table `historique_connexions`
--

CREATE TABLE `historique_connexions` (
  `id` bigint(20) NOT NULL,
  `utilisateur_id` int(11) NOT NULL,
  `date_connexion` datetime DEFAULT CURRENT_TIMESTAMP,
  `adresse_ip` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `session_id` varchar(128) DEFAULT NULL,
  `succes` tinyint(1) DEFAULT '1',
  `motif_echec` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historique des connexions';

-- --------------------------------------------------------

--
-- Structure de la table `logs_systeme`
--

CREATE TABLE `logs_systeme` (
  `id` bigint(20) NOT NULL COMMENT 'Identifiant log',
  `utilisateur_id` int(11) DEFAULT NULL COMMENT 'Utilisateur (peut être NULL pour système)',
  `action` varchar(100) NOT NULL COMMENT 'Action effectuée',
  `entite` varchar(50) DEFAULT NULL COMMENT 'Entité concernée (sujet, version, etc.)',
  `entite_id` int(11) DEFAULT NULL COMMENT 'ID de l''entité',
  `details` json DEFAULT NULL COMMENT 'Détails de l''action',
  `adresse_ip` varchar(45) DEFAULT NULL COMMENT 'Adresse IP utilisateur',
  `user_agent` text COMMENT 'User Agent navigateur',
  `date_action` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Date action'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Logs système';

-- --------------------------------------------------------

--
-- Structure de la table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL COMMENT 'Identifiant notification',
  `utilisateur_id` int(11) NOT NULL COMMENT 'Utilisateur destinataire',
  `titre` varchar(200) NOT NULL COMMENT 'Titre notification',
  `message` text NOT NULL COMMENT 'Message détaillé',
  `type` enum('info','success','warning','danger','email','sms') DEFAULT 'info' COMMENT 'Type notification',
  `priorite` enum('basse','normale','haute','urgente') DEFAULT 'normale',
  `est_lu` tinyint(1) DEFAULT '0' COMMENT 'Lue par utilisateur?',
  `est_envoye_email` tinyint(1) DEFAULT '0' COMMENT 'Email envoyé?',
  `est_envoye_sms` tinyint(1) DEFAULT '0' COMMENT 'SMS envoyé?',
  `lien` varchar(255) DEFAULT NULL COMMENT 'Lien de redirection',
  `icone` varchar(50) DEFAULT NULL COMMENT 'Icône FontAwesome',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Date création',
  `date_lecture` datetime DEFAULT NULL COMMENT 'Date lecture',
  `metadonnees` json DEFAULT NULL COMMENT 'Données supplémentaires'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notifications utilisateurs';

--
-- Déchargement des données de la table `notifications`
--

INSERT INTO `notifications` (`id`, `utilisateur_id`, `titre`, `message`, `type`, `priorite`, `est_lu`, `est_envoye_email`, `est_envoye_sms`, `lien`, `icone`, `date_creation`, `date_lecture`, `metadonnees`) VALUES
(1, 6, 'Nouvelle version soumise', 'Marie a soumis Introduction - Taux: 5.97%', 'info', 'normale', 0, 0, 0, '/directeur/corriger/1', NULL, '2026-05-27 01:26:22', NULL, NULL),
(2, 6, 'Nouvelle version soumise', 'Marie a soumis Chapitre 1 - Taux: 3.63%', 'info', 'normale', 0, 0, 0, '/directeur/corriger/2', NULL, '2026-05-27 01:27:19', NULL, NULL),
(3, 6, 'Version finale soumise - À valider', 'Marie MULUMBA - Taux: 25.29%', 'info', 'normale', 0, 0, 0, '/directeur/valider_final/3', NULL, '2026-05-27 17:40:52', NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL COMMENT 'Identifiant unique du rôle',
  `nom` varchar(50) NOT NULL COMMENT 'Nom du rôle (etudiant, directeur, doyen)',
  `description` text COMMENT 'Description détaillée du rôle',
  `permissions` json DEFAULT NULL COMMENT 'Permissions spécifiques (format JSON)',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
  `date_modification` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Date de dernière modification'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table des rôles utilisateurs';

--
-- Déchargement des données de la table `roles`
--

INSERT INTO `roles` (`id`, `nom`, `description`, `permissions`, `date_creation`, `date_modification`) VALUES
(1, 'etudiant', 'Étudiant finaliste (L3 ou M2) soumettant un mémoire/thèse', '{\"voir_dashboard\": true, \"soumettre_sujet\": true, \"soumettre_version\": true}', '2026-05-27 00:30:45', NULL),
(2, 'directeur', 'Directeur encadrant les étudiants', '{\"valider_final\": true, \"corriger_travaux\": true, \"voir_statistiques\": true}', '2026-05-27 00:30:45', NULL),
(3, 'doyen', 'Doyen de faculté supervisant le processus (un doyen par faculté)', '{\"voir_faculte\": true, \"valider_sujets\": true, \"exporter_rapports\": true, \"attribuer_directeurs\": true}', '2026-05-27 00:30:45', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `suivi_delais`
--

CREATE TABLE `suivi_delais` (
  `id` int(11) NOT NULL COMMENT 'Identifiant suivi',
  `sujet_id` int(11) NOT NULL COMMENT 'Sujet concerné',
  `etape` varchar(100) NOT NULL COMMENT 'Étape du processus',
  `type_delai` enum('soumission','correction','validation','finalisation') NOT NULL,
  `delai_jours` int(11) NOT NULL COMMENT 'Délai en jours',
  `date_debut` datetime NOT NULL COMMENT 'Date début',
  `date_fin_prevue` datetime NOT NULL COMMENT 'Date fin prévue',
  `date_fin_reelle` datetime DEFAULT NULL COMMENT 'Date fin réelle',
  `est_en_retard` tinyint(1) DEFAULT '0' COMMENT 'En retard?',
  `jours_retard` int(11) DEFAULT '0' COMMENT 'Nombre jours retard',
  `notification_24h_envoyee` tinyint(1) DEFAULT '0' COMMENT 'Rappel 24h avant?',
  `notification_depassement_envoyee` tinyint(1) DEFAULT '0' COMMENT 'Rappel dépassement?',
  `notification_7j_envoyee` tinyint(1) DEFAULT '0' COMMENT 'Rappel 7 jours retard?',
  `escalade_doyen` tinyint(1) DEFAULT '0' COMMENT 'Escaladé au doyen?'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Suivi des délais';

-- --------------------------------------------------------

--
-- Structure de la table `sujets`
--

CREATE TABLE `sujets` (
  `id` int(11) NOT NULL COMMENT 'Identifiant sujet',
  `titre` varchar(255) NOT NULL COMMENT 'Titre du mémoire/thèse',
  `description` text COMMENT 'Description détaillée',
  `mots_cles` text COMMENT 'Mots-clés séparés par des virgules',
  `domaine_id` int(11) NOT NULL COMMENT 'Domaine concerné',
  `etudiant_id` int(11) NOT NULL COMMENT 'Étudiant auteur',
  `directeur_id` int(11) DEFAULT NULL COMMENT 'Directeur attribué',
  `co_directeur_id` int(11) DEFAULT NULL COMMENT 'Co-directeur (optionnel)',
  `fichier_concept` varchar(255) DEFAULT NULL COMMENT 'Chemin fichier concept paper',
  `statut` enum('en_attente','approuve','rejete','en_cours','finalise','soutenu') DEFAULT 'en_attente' COMMENT 'Statut du sujet',
  `motif_rejet` text COMMENT 'Motif si rejeté',
  `date_soumission` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Date soumission',
  `date_validation` datetime DEFAULT NULL COMMENT 'Date validation par doyen',
  `date_attribution` datetime DEFAULT NULL COMMENT 'Date attribution directeur',
  `date_finalisation` datetime DEFAULT NULL COMMENT 'Date finalisation mémoire',
  `annee_academique` varchar(20) DEFAULT NULL COMMENT 'Année académique',
  `niveau_etude` varchar(10) DEFAULT NULL COMMENT 'Niveau d''étude (L3, M1, M2)',
  `notes_internes` text COMMENT 'Notes internes (doyen/directeur)',
  `chapitre_courant` int(11) DEFAULT '1' COMMENT 'Chapitre actuel à travailler (1=Ch1, 2=Ch2, ... 5=Conclusion)',
  `chapitre_max` int(11) DEFAULT '5' COMMENT 'Nombre total de chapitres prévus',
  `chapitre_1_titre` varchar(200) DEFAULT 'Introduction générale' COMMENT 'Titre du chapitre 1',
  `chapitre_2_titre` varchar(200) DEFAULT 'Revue de littérature' COMMENT 'Titre du chapitre 2',
  `chapitre_3_titre` varchar(200) DEFAULT 'Méthodologie' COMMENT 'Titre du chapitre 3',
  `chapitre_4_titre` varchar(200) DEFAULT 'Résultats et analyses' COMMENT 'Titre du chapitre 4',
  `chapitre_5_titre` varchar(200) DEFAULT 'Discussion et recommandations' COMMENT 'Titre du chapitre 5',
  `chapitre_1_valide` tinyint(1) DEFAULT '0' COMMENT 'Chapitre 1 validé par directeur',
  `chapitre_2_valide` tinyint(1) DEFAULT '0' COMMENT 'Chapitre 2 validé par directeur',
  `chapitre_3_valide` tinyint(1) DEFAULT '0' COMMENT 'Chapitre 3 validé par directeur',
  `chapitre_4_valide` tinyint(1) DEFAULT '0' COMMENT 'Chapitre 4 validé par directeur',
  `chapitre_5_valide` tinyint(1) DEFAULT '0' COMMENT 'Chapitre 5 validé par directeur',
  `structure_chapitres` json DEFAULT NULL COMMENT 'Structure complète des chapitres (format JSON)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Sujets de mémoire/thèse avec suivi séquentiel des chapitres';

--
-- Déchargement des données de la table `sujets`
--

INSERT INTO `sujets` (`id`, `titre`, `description`, `mots_cles`, `domaine_id`, `etudiant_id`, `directeur_id`, `co_directeur_id`, `fichier_concept`, `statut`, `motif_rejet`, `date_soumission`, `date_validation`, `date_attribution`, `date_finalisation`, `annee_academique`, `niveau_etude`, `notes_internes`, `chapitre_courant`, `chapitre_max`, `chapitre_1_titre`, `chapitre_2_titre`, `chapitre_3_titre`, `chapitre_4_titre`, `chapitre_5_titre`, `chapitre_1_valide`, `chapitre_2_valide`, `chapitre_3_valide`, `chapitre_4_valide`, `chapitre_5_valide`, `structure_chapitres`) VALUES
(1, 'Impact des réseaux sociaux sur la cohésion sociale en milieu universitaire', 'Cette recherche examine l\'influence des réseaux sociaux sur les relations interpersonnelles et la cohésion sociale parmi les étudiants de l\'UAAC. L\'étude utilise une approche mixte.', NULL, 1, 11, 6, NULL, NULL, 'en_cours', NULL, '2026-05-27 00:30:45', '2026-05-27 00:56:28', '2026-05-27 00:56:28', NULL, '2026/2027', 'L3', NULL, 3, 5, 'Introduction générale', 'Revue de littérature', 'Méthodologie', 'Résultats et analyses', 'Discussion et recommandations', 1, 0, 0, 0, 0, NULL),
(2, 'Optimisation de la chaîne logistique dans les entreprises congolaises', 'Cette recherche propose un modèle d\'optimisation de la chaîne logistique adapté au contexte congolais, avec une étude de cas dans trois entreprises de Kinshasa.', NULL, 2, 12, NULL, NULL, NULL, 'en_attente', NULL, '2026-05-27 00:30:45', NULL, NULL, NULL, '2026/2027', 'M2', NULL, 1, 5, 'Introduction générale', 'Revue de littérature', 'Méthodologie', 'Résultats et analyses', 'Discussion et recommandations', 0, 0, 0, 0, 0, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

CREATE TABLE `utilisateurs` (
  `id` int(11) NOT NULL COMMENT 'Identifiant unique utilisateur',
  `matricule` varchar(50) NOT NULL COMMENT 'Matricule universitaire',
  `nom` varchar(100) NOT NULL COMMENT 'Nom de famille',
  `prenom` varchar(100) NOT NULL COMMENT 'Prénom(s)',
  `email` varchar(100) NOT NULL COMMENT 'Email institutionnel',
  `mot_de_passe` varchar(255) NOT NULL COMMENT 'Mot de passe hashé (SHA256)',
  `role_id` int(11) NOT NULL COMMENT 'ID du rôle (FK)',
  `telephone` varchar(20) DEFAULT NULL COMMENT 'Numéro de téléphone',
  `domaine_id` int(11) DEFAULT NULL COMMENT 'Domaine d''étude (pour étudiants)',
  `domaine_responsable_id` int(11) DEFAULT NULL COMMENT 'Domaine dont le doyen est responsable (UNIQUEMENT pour doyens)',
  `annee_academique` varchar(20) DEFAULT NULL COMMENT 'Année académique (L3, M2)',
  `photo_profil` varchar(255) DEFAULT NULL COMMENT 'Chemin photo de profil',
  `est_actif` tinyint(1) DEFAULT '1' COMMENT 'Compte actif ou désactivé',
  `premiere_connexion` tinyint(1) DEFAULT '1' COMMENT 'Première connexion (force changement mot de passe)',
  `date_derniere_connexion` datetime DEFAULT NULL COMMENT 'Date dernière connexion',
  `date_inscription` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Date d''inscription',
  `preferences` json DEFAULT NULL COMMENT 'Préférences utilisateur (thème, notifications, etc.)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table des utilisateurs du système';

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id`, `matricule`, `nom`, `prenom`, `email`, `mot_de_passe`, `role_id`, `telephone`, `domaine_id`, `domaine_responsable_id`, `annee_academique`, `photo_profil`, `est_actif`, `premiere_connexion`, `date_derniere_connexion`, `date_inscription`, `preferences`) VALUES
(1, 'DOYEN_SHS', 'MAMBU', 'Antoine', 'doyen_shs@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 1, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(2, 'DOYEN_SAE', 'KALONJI', 'Béatrice', 'doyen_sae@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 2, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(3, 'DOYEN_SEG', 'MUKENDI', 'Joseph', 'doyen_seg@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 3, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(4, 'DOYEN_ST', 'NZUZI', 'Rachel', 'doyen_st@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 4, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(5, 'DOYEN_SPE', 'LUFUNGA', 'Christian', 'doyen_spe@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 5, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(6, 'DIR_SHS', 'TSHIBANGU', 'Paul', 'directeur_shs@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 1, NULL, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(7, 'DIR_SAE', 'MUMBALA', 'Claire', 'directeur_sae@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 2, NULL, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(8, 'DIR_SEG', 'KASONGO', 'Pierre', 'directeur_seg@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 3, NULL, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(9, 'DIR_ST', 'LUMUMBA', 'Grace', 'directeur_st@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 4, NULL, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(10, 'DIR_SPE', 'KABILA', 'Fabrice', 'directeur_spe@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 5, NULL, NULL, NULL, 1, 0, NULL, '2026-05-27 00:30:45', NULL),
(11, 'ETU_SHS001', 'MULUMBA', 'Marie', 'marie.mulumba@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 1, NULL, 'L3', NULL, 1, 1, NULL, '2026-05-27 00:30:45', NULL),
(12, 'ETU_SAE001', 'KASONGO', 'David', 'david.kasongo@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 2, NULL, 'M2', NULL, 1, 1, NULL, '2026-05-27 00:30:45', NULL),
(13, 'ETU_SEG001', 'MBAYO', 'Joseph', 'joseph.mbayo@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 3, NULL, 'L3', NULL, 1, 1, NULL, '2026-05-27 00:30:45', NULL),
(14, 'ETU_ST001', 'NGOMA', 'Rachel', 'rachel.ngoma@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 4, NULL, 'M2', NULL, 1, 1, NULL, '2026-05-27 00:30:45', NULL),
(15, 'ETU_SPE001', 'LUFUNGA', 'Christian', 'christian.lufunga@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 5, NULL, 'L3', NULL, 1, 1, NULL, '2026-05-27 00:30:45', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `verifications_plagiat`
--

CREATE TABLE `verifications_plagiat` (
  `id` int(11) NOT NULL COMMENT 'Identifiant vérification',
  `version_travail_id` int(11) NOT NULL COMMENT 'Version vérifiée',
  `methode` varchar(50) NOT NULL COMMENT 'Méthode utilisée',
  `score_similarite` float NOT NULL COMMENT 'Score similarité (%)',
  `score_genai` float DEFAULT NULL COMMENT 'Score GenAI (0-1)',
  `sources` json DEFAULT NULL COMMENT 'Sources trouvées',
  `rapport_chemin` varchar(255) DEFAULT NULL COMMENT 'Chemin rapport complet',
  `temps_traitement` float DEFAULT NULL COMMENT 'Temps traitement (secondes)',
  `est_conforme` tinyint(1) DEFAULT NULL COMMENT 'Conforme au seuil?',
  `date_verification` datetime DEFAULT CURRENT_TIMESTAMP,
  `metadonnees` json DEFAULT NULL COMMENT 'Métadonnées vérification'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Résultats vérifications plagiat';

-- --------------------------------------------------------

--
-- Structure de la table `versions_travail`
--

CREATE TABLE `versions_travail` (
  `id` int(11) NOT NULL COMMENT 'Identifiant version',
  `sujet_id` int(11) NOT NULL COMMENT 'Sujet associé',
  `numero_version` int(11) NOT NULL COMMENT 'Numéro de version (1,2,3...)',
  `chapitre` varchar(50) DEFAULT NULL COMMENT 'Numéro/nom du chapitre',
  `titre_chapitre` varchar(200) DEFAULT NULL COMMENT 'Titre du chapitre',
  `contenu` longtext COMMENT 'Contenu texte du chapitre',
  `fichier_chemin` varchar(255) DEFAULT NULL COMMENT 'Chemin fichier uploadé',
  `commentaire_directeur` text COMMENT 'Commentaires du directeur',
  `statut` enum('brouillon','soumis','corrige','valide','approuve') DEFAULT 'brouillon' COMMENT 'Statut version',
  `taux_similarite` float DEFAULT '0' COMMENT 'Taux de similarité (%)',
  `rapport_similarite` varchar(255) DEFAULT NULL COMMENT 'Chemin rapport similarité',
  `score_genai` float DEFAULT '0' COMMENT 'Score détection IA (0-1)',
  `date_soumission` datetime DEFAULT NULL COMMENT 'Date soumission',
  `date_correction` datetime DEFAULT NULL COMMENT 'Date correction par directeur',
  `date_validation` datetime DEFAULT NULL COMMENT 'Date validation',
  `est_version_finale` tinyint(1) DEFAULT '0' COMMENT 'Version finale?',
  `version_precedente_id` int(11) DEFAULT NULL COMMENT 'Version précédente (pour historique)',
  `metadonnees` json DEFAULT NULL COMMENT 'Métadonnées supplémentaires'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Versions des travaux';

--
-- Déchargement des données de la table `versions_travail`
--

INSERT INTO `versions_travail` (`id`, `sujet_id`, `numero_version`, `chapitre`, `titre_chapitre`, `contenu`, `fichier_chemin`, `commentaire_directeur`, `statut`, `taux_similarite`, `rapport_similarite`, `score_genai`, `date_soumission`, `date_correction`, `date_validation`, `est_version_finale`, `version_precedente_id`, `metadonnees`) VALUES
(1, 1, 1, '1', 'Introduction générale', '', 'uploads/travaux/version_1_ETU_SHS001_1779834378_CHAPITRE_IIILevi.pdf', 'Va faire ceci', 'corrige', 5.97, NULL, 0.190824, '2026-05-27 01:26:20', '2026-05-27 17:33:30', NULL, 0, NULL, NULL),
(2, 1, 2, '2', 'Revue de littérature', '', 'uploads/travaux/version_1_ETU_SHS001_1779834435_IntroKalyoto.pdf', 'Version acceptable. Vous pouvez procéder au chapitre suivant.', 'valide', 3.63, NULL, 0.190154, '2026-05-27 01:27:17', NULL, '2026-05-27 09:56:49', 0, NULL, NULL),
(3, 1, 3, 'Manuscrit complet', 'Version finale', NULL, 'uploads/final/final_1_ETU_SHS001_1779892850.pdf', NULL, 'soumis', 25.29, 'uploads/rapports\\rapport_similarite_final_1_ETU_SHS001_1779892850_20260527_174050.pdf', 0.0998098, '2026-05-27 17:40:50', NULL, NULL, 1, NULL, NULL);

--
-- Déclencheurs `versions_travail`
--
DELIMITER $$
CREATE TRIGGER `after_version_validee` AFTER UPDATE ON `versions_travail` FOR EACH ROW BEGIN
    DECLARE v_numero_chapitre INT;
    
    IF NEW.statut = 'valide' AND OLD.statut != 'valide' THEN
                IF NEW.chapitre REGEXP '^[0-9]+$' THEN
            SET v_numero_chapitre = CAST(NEW.chapitre AS UNSIGNED);
        ELSE
            SET v_numero_chapitre = 1;
        END IF;
        
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
        
                CALL deverrouiller_chapitre_suivant(NEW.sujet_id, v_numero_chapitre);
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_alertes_par_faculte`
-- (Voir ci-dessous la vue réelle)
--
CREATE TABLE `vue_alertes_par_faculte` (
`domaine_id` int(11)
,`domaine_code` varchar(20)
,`sujet_id` int(11)
,`sujet_titre` varchar(255)
,`etudiant_nom` varchar(201)
,`directeur_nom` varchar(201)
,`etape` varchar(100)
,`jours_retard` int(11)
,`date_fin_prevue` datetime
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_progression_etudiants`
-- (Voir ci-dessous la vue réelle)
--
CREATE TABLE `vue_progression_etudiants` (
`sujet_id` int(11)
,`titre` varchar(255)
,`etudiant_nom` varchar(201)
,`chapitre_courant` int(11)
,`chapitre_max` int(11)
,`chapitre_1_valide` tinyint(1)
,`chapitre_2_valide` tinyint(1)
,`chapitre_3_valide` tinyint(1)
,`chapitre_4_valide` tinyint(1)
,`chapitre_5_valide` tinyint(1)
,`pourcentage_completion` decimal(13,2)
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_stats_par_faculte`
-- (Voir ci-dessous la vue réelle)
--
CREATE TABLE `vue_stats_par_faculte` (
`domaine_id` int(11)
,`domaine_code` varchar(20)
,`domaine_nom` varchar(100)
,`total_sujets` bigint(21)
,`en_attente` decimal(23,0)
,`approuves` decimal(23,0)
,`en_cours` decimal(23,0)
,`finalises` decimal(23,0)
,`rejetes` decimal(23,0)
,`directeurs_actifs` bigint(21)
,`etudiants_actifs` bigint(21)
);

-- --------------------------------------------------------

--
-- Structure de la vue `vue_alertes_par_faculte`
--
DROP TABLE IF EXISTS `vue_alertes_par_faculte`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_alertes_par_faculte`  AS  select `d`.`id` AS `domaine_id`,`d`.`code` AS `domaine_code`,`s`.`id` AS `sujet_id`,`s`.`titre` AS `sujet_titre`,concat(`e`.`prenom`,' ',`e`.`nom`) AS `etudiant_nom`,concat(`dr`.`prenom`,' ',`dr`.`nom`) AS `directeur_nom`,`sd`.`etape` AS `etape`,`sd`.`jours_retard` AS `jours_retard`,`sd`.`date_fin_prevue` AS `date_fin_prevue` from ((((`suivi_delais` `sd` join `sujets` `s` on((`sd`.`sujet_id` = `s`.`id`))) join `domaines` `d` on((`s`.`domaine_id` = `d`.`id`))) join `utilisateurs` `e` on((`s`.`etudiant_id` = `e`.`id`))) join `utilisateurs` `dr` on((`s`.`directeur_id` = `dr`.`id`))) where ((`sd`.`est_en_retard` = TRUE) and isnull(`sd`.`date_fin_reelle`)) ;

-- --------------------------------------------------------

--
-- Structure de la vue `vue_progression_etudiants`
--
DROP TABLE IF EXISTS `vue_progression_etudiants`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_progression_etudiants`  AS  select `s`.`id` AS `sujet_id`,`s`.`titre` AS `titre`,concat(`e`.`prenom`,' ',`e`.`nom`) AS `etudiant_nom`,`s`.`chapitre_courant` AS `chapitre_courant`,`s`.`chapitre_max` AS `chapitre_max`,`s`.`chapitre_1_valide` AS `chapitre_1_valide`,`s`.`chapitre_2_valide` AS `chapitre_2_valide`,`s`.`chapitre_3_valide` AS `chapitre_3_valide`,`s`.`chapitre_4_valide` AS `chapitre_4_valide`,`s`.`chapitre_5_valide` AS `chapitre_5_valide`,round(((((((`s`.`chapitre_1_valide` + `s`.`chapitre_2_valide`) + `s`.`chapitre_3_valide`) + `s`.`chapitre_4_valide`) + `s`.`chapitre_5_valide`) / `s`.`chapitre_max`) * 100),2) AS `pourcentage_completion` from (`sujets` `s` join `utilisateurs` `e` on((`s`.`etudiant_id` = `e`.`id`))) ;

-- --------------------------------------------------------

--
-- Structure de la vue `vue_stats_par_faculte`
--
DROP TABLE IF EXISTS `vue_stats_par_faculte`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_stats_par_faculte`  AS  select `d`.`id` AS `domaine_id`,`d`.`code` AS `domaine_code`,`d`.`nom` AS `domaine_nom`,count(distinct `s`.`id`) AS `total_sujets`,sum((case when (`s`.`statut` = 'en_attente') then 1 else 0 end)) AS `en_attente`,sum((case when (`s`.`statut` = 'approuve') then 1 else 0 end)) AS `approuves`,sum((case when (`s`.`statut` = 'en_cours') then 1 else 0 end)) AS `en_cours`,sum((case when (`s`.`statut` = 'finalise') then 1 else 0 end)) AS `finalises`,sum((case when (`s`.`statut` = 'rejete') then 1 else 0 end)) AS `rejetes`,count(distinct `s`.`directeur_id`) AS `directeurs_actifs`,count(distinct `s`.`etudiant_id`) AS `etudiants_actifs` from (`domaines` `d` left join `sujets` `s` on((`d`.`id` = `s`.`domaine_id`))) where ((year(`s`.`date_soumission`) = year(curdate())) or isnull(`s`.`date_soumission`)) group by `d`.`id` ;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `configuration`
--
ALTER TABLE `configuration`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `cle` (`cle`),
  ADD KEY `idx_cle` (`cle`);

--
-- Index pour la table `domaines`
--
ALTER TABLE `domaines`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD KEY `doyen_id` (`doyen_id`);

--
-- Index pour la table `feedback_processus`
--
ALTER TABLE `feedback_processus`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_version` (`version_travail_id`),
  ADD KEY `idx_emetteur` (`emetteur_id`),
  ADD KEY `idx_destinataire` (`destinataire_id`);

--
-- Index pour la table `historique_connexions`
--
ALTER TABLE `historique_connexions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_utilisateur` (`utilisateur_id`),
  ADD KEY `idx_date` (`date_connexion`);

--
-- Index pour la table `logs_systeme`
--
ALTER TABLE `logs_systeme`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_utilisateur` (`utilisateur_id`),
  ADD KEY `idx_action` (`action`),
  ADD KEY `idx_date` (`date_action`);

--
-- Index pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_utilisateur` (`utilisateur_id`),
  ADD KEY `idx_non_lu` (`utilisateur_id`,`est_lu`);

--
-- Index pour la table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nom` (`nom`);

--
-- Index pour la table `suivi_delais`
--
ALTER TABLE `suivi_delais`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sujet` (`sujet_id`),
  ADD KEY `idx_retard` (`est_en_retard`);

--
-- Index pour la table `sujets`
--
ALTER TABLE `sujets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_etudiant` (`etudiant_id`),
  ADD KEY `idx_directeur` (`directeur_id`),
  ADD KEY `idx_statut` (`statut`),
  ADD KEY `idx_domaine` (`domaine_id`),
  ADD KEY `idx_chapitre_courant` (`chapitre_courant`),
  ADD KEY `co_directeur_id` (`co_directeur_id`),
  ADD KEY `idx_sujets_domaine_statut` (`domaine_id`,`statut`),
  ADD KEY `idx_sujets_domaine_date` (`domaine_id`,`date_soumission`),
  ADD KEY `idx_sujets_chapitre_courant` (`chapitre_courant`),
  ADD KEY `idx_sujets_chapitre_valide` (`chapitre_1_valide`,`chapitre_2_valide`,`chapitre_3_valide`,`chapitre_4_valide`,`chapitre_5_valide`);

--
-- Index pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `matricule` (`matricule`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `domaine_responsable_id` (`domaine_responsable_id`),
  ADD KEY `idx_email` (`email`),
  ADD KEY `idx_matricule` (`matricule`),
  ADD KEY `idx_role` (`role_id`),
  ADD KEY `idx_utilisateurs_domaine_role` (`domaine_id`,`role_id`);

--
-- Index pour la table `verifications_plagiat`
--
ALTER TABLE `verifications_plagiat`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_version` (`version_travail_id`);

--
-- Index pour la table `versions_travail`
--
ALTER TABLE `versions_travail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sujet` (`sujet_id`),
  ADD KEY `idx_statut` (`statut`),
  ADD KEY `idx_chapitre` (`chapitre`),
  ADD KEY `version_precedente_id` (`version_precedente_id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `configuration`
--
ALTER TABLE `configuration`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
--
-- AUTO_INCREMENT pour la table `domaines`
--
ALTER TABLE `domaines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant domaine', AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT pour la table `feedback_processus`
--
ALTER TABLE `feedback_processus`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant feedback';
--
-- AUTO_INCREMENT pour la table `historique_connexions`
--
ALTER TABLE `historique_connexions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `logs_systeme`
--
ALTER TABLE `logs_systeme`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant log';
--
-- AUTO_INCREMENT pour la table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant notification', AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT pour la table `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique du rôle', AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT pour la table `suivi_delais`
--
ALTER TABLE `suivi_delais`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant suivi';
--
-- AUTO_INCREMENT pour la table `sujets`
--
ALTER TABLE `sujets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant sujet', AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique utilisateur', AUTO_INCREMENT=16;
--
-- AUTO_INCREMENT pour la table `verifications_plagiat`
--
ALTER TABLE `verifications_plagiat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant vérification';
--
-- AUTO_INCREMENT pour la table `versions_travail`
--
ALTER TABLE `versions_travail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant version', AUTO_INCREMENT=4;
--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `domaines`
--
ALTER TABLE `domaines`
  ADD CONSTRAINT `domaines_ibfk_1` FOREIGN KEY (`doyen_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `feedback_processus`
--
ALTER TABLE `feedback_processus`
  ADD CONSTRAINT `feedback_processus_ibfk_1` FOREIGN KEY (`version_travail_id`) REFERENCES `versions_travail` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `feedback_processus_ibfk_2` FOREIGN KEY (`emetteur_id`) REFERENCES `utilisateurs` (`id`),
  ADD CONSTRAINT `feedback_processus_ibfk_3` FOREIGN KEY (`destinataire_id`) REFERENCES `utilisateurs` (`id`);

--
-- Contraintes pour la table `historique_connexions`
--
ALTER TABLE `historique_connexions`
  ADD CONSTRAINT `historique_connexions_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `logs_systeme`
--
ALTER TABLE `logs_systeme`
  ADD CONSTRAINT `logs_systeme_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `suivi_delais`
--
ALTER TABLE `suivi_delais`
  ADD CONSTRAINT `suivi_delais_ibfk_1` FOREIGN KEY (`sujet_id`) REFERENCES `sujets` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `sujets`
--
ALTER TABLE `sujets`
  ADD CONSTRAINT `sujets_ibfk_1` FOREIGN KEY (`domaine_id`) REFERENCES `domaines` (`id`),
  ADD CONSTRAINT `sujets_ibfk_2` FOREIGN KEY (`etudiant_id`) REFERENCES `utilisateurs` (`id`),
  ADD CONSTRAINT `sujets_ibfk_3` FOREIGN KEY (`directeur_id`) REFERENCES `utilisateurs` (`id`),
  ADD CONSTRAINT `sujets_ibfk_4` FOREIGN KEY (`co_directeur_id`) REFERENCES `utilisateurs` (`id`);

--
-- Contraintes pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD CONSTRAINT `utilisateurs_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  ADD CONSTRAINT `utilisateurs_ibfk_2` FOREIGN KEY (`domaine_id`) REFERENCES `domaines` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `utilisateurs_ibfk_3` FOREIGN KEY (`domaine_responsable_id`) REFERENCES `domaines` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `verifications_plagiat`
--
ALTER TABLE `verifications_plagiat`
  ADD CONSTRAINT `verifications_plagiat_ibfk_1` FOREIGN KEY (`version_travail_id`) REFERENCES `versions_travail` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `versions_travail`
--
ALTER TABLE `versions_travail`
  ADD CONSTRAINT `versions_travail_ibfk_1` FOREIGN KEY (`sujet_id`) REFERENCES `sujets` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `versions_travail_ibfk_2` FOREIGN KEY (`version_precedente_id`) REFERENCES `versions_travail` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
