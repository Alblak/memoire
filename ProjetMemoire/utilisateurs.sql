-- phpMyAdmin SQL Dump
-- version 4.7.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le :  ven. 15 mai 2026 à 13:20
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
(1, 'DOYEN_SHS', 'MAMBU', 'Antoine', 'doyen_shs@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 1, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(2, 'DOYEN_SAE', 'KALONJI', 'Béatrice', 'doyen_sae@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 2, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(3, 'DOYEN_SEG', 'MUKENDI', 'Joseph', 'doyen_seg@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 3, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(4, 'DOYEN_ST', 'NZUZI', 'Rachel', 'doyen_st@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 4, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(5, 'DOYEN_SPE', 'LUFUNGA', 'Christian', 'doyen_spe@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 3, NULL, NULL, 5, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(6, 'DIR_SHS', 'TSHIBANGU', 'Paul', 'directeur_shs@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 1, NULL, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(7, 'DIR_SAE', 'MUMBALA', 'Claire', 'directeur_sae@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 2, NULL, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(8, 'DIR_SEG', 'KASONGO', 'Pierre', 'directeur_seg@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 3, NULL, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(9, 'DIR_ST', 'LUMUMBA', 'Grace', 'directeur_st@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 4, NULL, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(10, 'DIR_SPE', 'KABILA', 'Fabrice', 'directeur_spe@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 2, NULL, 5, NULL, NULL, NULL, 1, 0, NULL, '2026-05-15 11:21:26', NULL),
(11, 'ETU_SHS001', 'MULUMBA', 'Marie', 'marie.mulumba@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 1, NULL, 'L3', NULL, 1, 1, NULL, '2026-05-15 11:21:26', NULL),
(12, 'ETU_SAE001', 'KASONGO', 'David', 'david.kasongo@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 2, NULL, 'M2', NULL, 1, 1, NULL, '2026-05-15 11:21:26', NULL),
(13, 'ETU_SEG001', 'MBAYO', 'Joseph', 'joseph.mbayo@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 3, NULL, 'L3', NULL, 1, 1, NULL, '2026-05-15 11:21:26', NULL),
(14, 'ETU_ST001', 'NGOMA', 'Rachel', 'rachel.ngoma@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 4, NULL, 'M2', NULL, 1, 1, NULL, '2026-05-15 11:21:26', NULL),
(15, 'ETU_SPE001', 'LUFUNGA', 'Christian', 'christian.lufunga@uaconline.edu.cd', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1, NULL, 5, NULL, 'L3', NULL, 1, 1, NULL, '2026-05-15 11:21:26', NULL);

--
-- Index pour les tables déchargées
--

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
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique utilisateur', AUTO_INCREMENT=16;
--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD CONSTRAINT `utilisateurs_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  ADD CONSTRAINT `utilisateurs_ibfk_2` FOREIGN KEY (`domaine_id`) REFERENCES `domaines` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `utilisateurs_ibfk_3` FOREIGN KEY (`domaine_responsable_id`) REFERENCES `domaines` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
