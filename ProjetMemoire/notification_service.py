# notification_service.py
"""
Service de notifications pour le système UAAC
Gère les notifications par email, SMS et in-app
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import threading
from queue import Queue

class NotificationService:
    """Service centralisé pour toutes les notifications"""
    
    def __init__(self, app=None):
        """
        Initialise le service de notifications
        Args:
            app: Instance Flask (pour accéder à la configuration)
        """
        self.app = app
        self.email_queue = Queue()
        self.sms_queue = Queue()
        self._start_workers()
    
    def _start_workers(self):
        """Démarre les workers asynchrones pour l'envoi de notifications"""
        def email_worker():
            while True:
                try:
                    email_data = self.email_queue.get(timeout=1)
                    self._send_email_sync(email_data)
                except:
                    pass
        
        def sms_worker():
            while True:
                try:
                    sms_data = self.sms_queue.get(timeout=1)
                    self._send_sms_sync(sms_data)
                except:
                    pass
        
        thread = threading.Thread(target=email_worker, daemon=True)
        thread.start()
        
        thread = threading.Thread(target=sms_worker, daemon=True)
        thread.start()
    
    def create_notification(self, user_id, titre, message, type_notif='info', lien=None):
        """
        Crée une notification dans la base de données
        Args:
            user_id: ID de l'utilisateur destinataire
            titre: Titre de la notification
            message: Message de la notification
            type_notif: Type (info, success, warning, danger)
            lien: Lien de redirection (optionnel)
        """
        try:
            from app import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO notifications (utilisateur_id, titre, message, type, lien, date_creation)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (user_id, titre, message, type_notif, lien))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Si email configuré, envoyer aussi par email
            if self.app and self.app.config.get('MAIL_USERNAME'):
                self.send_email_by_id(user_id, titre, message)
                
        except Exception as e:
            print(f"Erreur création notification: {e}")
    
    def send_email(self, to_email, subject, html_content):
        """
        Envoie un email (asynchrone)
        Args:
            to_email: Email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
        """
        email_data = {
            'to': to_email,
            'subject': subject,
            'html': html_content
        }
        self.email_queue.put(email_data)
    
    def send_email_by_id(self, user_id, subject, html_content):
        """
        Envoie un email à un utilisateur par son ID
        Args:
            user_id: ID de l'utilisateur
            subject: Sujet de l'email
            html_content: Contenu HTML
        """
        try:
            from app import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT email FROM utilisateurs WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and user['email']:
                self.send_email(user['email'], subject, html_content)
        except Exception as e:
            print(f"Erreur envoi email par ID: {e}")
    
    def _send_email_sync(self, email_data):
        """
        Envoie un email de manière synchrone
        Args:
            email_data: Dictionnaire avec les données de l'email
        """
        if not self.app:
            return
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_data['subject']
            msg['From'] = self.app.config.get('MAIL_USERNAME', 'notifications@uaconline.edu.cd')
            msg['To'] = email_data['to']
            
            # Version texte (fallback)
            text_part = MIMEText(self._html_to_text(email_data['html']), 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Version HTML
            html_part = MIMEText(email_data['html'], 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connexion SMTP
            server = smtplib.SMTP(
                self.app.config.get('MAIL_SERVER', 'smtp.gmail.com'),
                self.app.config.get('MAIL_PORT', 587)
            )
            server.starttls()
            
            if self.app.config.get('MAIL_USERNAME') and self.app.config.get('MAIL_PASSWORD'):
                server.login(
                    self.app.config['MAIL_USERNAME'],
                    self.app.config['MAIL_PASSWORD']
                )
            
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email envoyé à {email_data['to']}")
            
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
    
    def _send_sms_sync(self, sms_data):
        """
        Envoie un SMS (à implémenter avec Twilio ou autre)
        """
        # Implémentation avec Twilio si nécessaire
        pass
    
    def _html_to_text(self, html):
        """Convertit HTML en texte brut simple"""
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def mark_as_read(self, notification_id, user_id):
        """
        Marque une notification comme lue
        Args:
            notification_id: ID de la notification
            user_id: ID de l'utilisateur
        """
        try:
            from app import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notifications 
                SET est_lu = 1, date_lecture = NOW()
                WHERE id = %s AND utilisateur_id = %s
            """, (notification_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur marquage notification: {e}")
            return False
    
    def get_unread_count(self, user_id):
        """
        Récupère le nombre de notifications non lues
        Args:
            user_id: ID de l'utilisateur
        Returns:
            Nombre de notifications non lues
        """
        try:
            from app import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT COUNT(*) as count FROM notifications 
                WHERE utilisateur_id = %s AND est_lu = 0
            """, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Erreur comptage notifications: {e}")
            return 0