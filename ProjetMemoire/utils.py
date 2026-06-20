# utils.py
"""
Fonctions utilitaires pour le système UAC
"""

import os
import re
from werkzeug.utils import secure_filename

class Utils:
    """Classe utilitaire avec fonctions statiques"""
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """
        Vérifie si le fichier a une extension autorisée
        Args:
            filename: Nom du fichier
            allowed_extensions: Set des extensions autorisées
        Returns:
            True si autorisé, False sinon
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def sanitize_filename(filename):
        """
        Nettoie un nom de fichier
        Args:
            filename: Nom de fichier original
        Returns:
            Nom de fichier nettoyé
        """
        return secure_filename(filename)
    
    @staticmethod
    def truncate_text(text, max_length=200):
        """
        Tronque un texte à une longueur maximale
        Args:
            text: Texte à tronquer
            max_length: Longueur maximale
        Returns:
            Texte tronqué avec "..."
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def extract_file_extension(filename):
        """
        Extrait l'extension d'un fichier
        Args:
            filename: Nom du fichier
        Returns:
            Extension en minuscules
        """
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    @staticmethod
    def format_date(date_obj, format_str='%d/%m/%Y'):
        """
        Formate une date
        Args:
            date_obj: Objet datetime
            format_str: Format de sortie
        Returns:
            Date formatée ou chaîne vide
        """
        if date_obj:
            return date_obj.strftime(format_str)
        return ''