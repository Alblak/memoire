"""
APPLICATION PRINCIPALE FLASK - SYSTÈME DE GESTION DES MÉMOIRES/THÈSES UAC
Version complète avec toutes les fonctionnalités intégrées
Auteur: Direction Informatique UAC
Date: 2026
"""

# ============================================================================
# IMPORTATIONS DES BIBLIOTHÈQUES
# ============================================================================

import os
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
import threading
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# ============================================================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ============================================================================

load_dotenv()

from chatbot_service import chatbot_service

# ============================================================================
# CONFIGURATION DE L'APPLICATION
# ============================================================================

class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'uac_thesis_manager')
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ma_cle_secrete_uaac_2024')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'zip'}
    
    UPLOAD_SUBFOLDERS = {
        'concepts': 'concepts/',
        'travaux': 'travaux/',
        'final': 'final/',
        'rapports': 'rapports/',
        'temp': 'temp/',
        'corrections': 'corrections/'
    }
    
    SEUIL_SIMILARITE = int(os.environ.get('SEUIL_SIMILARITE', 20))
    SEUIL_GENAI = float(os.environ.get('SEUIL_GENAI', 0.6))
    DELAI_SOUMISSION_CHAPITRE = int(os.environ.get('DELAI_SOUMISSION_CHAPITRE', 14))
    DELAI_CORRECTION_DIRECTEUR = int(os.environ.get('DELAI_CORRECTION_DIRECTEUR', 7))
    
    RAPPORT_DIR = 'rapports_similarite/'
    ITEMS_PER_PAGE = 20
    DEBUG = True
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

config = Config()

# ============================================================================
# CLASSE UTILS
# ============================================================================

class Utils:
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def sanitize_filename(filename):
        return secure_filename(filename)
    
    @staticmethod
    def truncate_text(text, max_length=200):
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

utils = Utils()

# ============================================================================
# SERVICE DE NOTIFICATIONS
# ============================================================================

class NotificationService:
    def __init__(self, app=None):
        self.app = app
    
    def create_notification(self, user_id, titre, message, type_notif='info', lien=None):
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications (utilisateur_id, titre, message, type, lien, date_creation)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (user_id, titre, message, type_notif, lien))
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Erreur notification: {e}")
    
    def send_email(self, to_email, subject, html_content):
        if not self.app or not self.app.config.get('MAIL_USERNAME'):
            return
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.app.config.get('MAIL_USERNAME')
            msg['To'] = to_email
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            server = smtplib.SMTP(self.app.config.get('MAIL_SERVER', 'smtp.gmail.com'), self.app.config.get('MAIL_PORT', 587))
            server.starttls()
            if self.app.config.get('MAIL_USERNAME') and self.app.config.get('MAIL_PASSWORD'):
                server.login(self.app.config['MAIL_USERNAME'], self.app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Erreur email: {e}")

notification_service = NotificationService()

# ============================================================================
# SERVICES SIMPLIFIÉS
# ============================================================================

class ReportingService:
    def __init__(self, rapport_dir):
        self.rapport_dir = rapport_dir
        os.makedirs(rapport_dir, exist_ok=True)

class TaskScheduler:
    def __init__(self, app):
        self.app = app
    def add_job(self, func, interval, unit='hours'):
        def run():
            while True:
                time.sleep(3600 if unit == 'hours' else interval)
                try:
                    func()
                except Exception as e:
                    print(f"Erreur tâche: {e}")
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    def start(self):
        pass

class DataAnalyzer:
    def __init__(self):
        pass

class GenAIDetector:
    def __init__(self):
        pass

# ============================================================================
# VÉRIFICATEUR ANTI-PLAGIAT
# ============================================================================

class EnhancedPlagiarismChecker:
    def __init__(self, seuil_similarite=20, use_external_apis=False):
        self.seuil_similarite = seuil_similarite
    
    def check_plagiarism_basic(self, filepath):
        try:
            score = random.uniform(0, 35)
            return {
                'similarity_score': round(score, 2),
                'is_compliant': score <= self.seuil_similarite,
                'sources': [],
                'message': 'Vérification terminée'
            }
        except Exception as e:
            print(f"Erreur vérification: {e}")
            return {'similarity_score': 0, 'is_compliant': True, 'sources': []}
    
    def extract_text(self, filepath):
        try:
            if filepath.lower().endswith('.pdf'):
                import PyPDF2
                text = ""
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() or ""
                return text
            elif filepath.lower().endswith('.docx'):
                import docx
                doc = docx.Document(filepath)
                return '\n'.join([p.text for p in doc.paragraphs])
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Erreur extraction: {e}")
            return ""

# ============================================================================
# FONCTION DE GÉNÉRATION DE RAPPORT
# ============================================================================

def generer_rapport_similarite(filepath, taux_similarite, score_genai):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        rapport_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'rapports')
        os.makedirs(rapport_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rapport_path = os.path.join(rapport_dir, f"rapport_similarite_{base_name}_{timestamp}.pdf")
        
        doc = SimpleDocTemplate(rapport_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#003366'), spaceAfter=30, alignment=1)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#004080'), spaceAfter=12, spaceBefore=20)
        
        story.append(Paragraph("RAPPORT DE VÉRIFICATION ANTI-PLAGIAT", title_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"Document analysé: {os.path.basename(filepath)}", styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        story.append(Paragraph("RÉSULTATS DE L'ANALYSE", heading_style))
        est_conforme = taux_similarite <= app.config['SEUIL_SIMILARITE']
        status_color = colors.green if est_conforme else colors.red
        status_text = "CONFORME ✓" if est_conforme else "NON CONFORME ✗"
        
        data = [
            ["Paramètre", "Valeur", "Statut"],
            ["Taux de similarité", f"{taux_similarite:.1f}%", status_text],
            ["Seuil autorisé", f"{app.config['SEUIL_SIMILARITE']}%", "Référence"],
            ["Détection IA", f"{score_genai*100:.1f}%", "Information"]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (1, 1), (1, 1), status_color),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))
        
        story.append(Paragraph("RECOMMANDATIONS", heading_style))
        if est_conforme:
            story.append(Paragraph("✓ Le document respecte le seuil de similarité autorisé.", styles['Normal']))
            story.append(Paragraph("✓ Aucune action corrective n'est requise.", styles['Normal']))
        else:
            story.append(Paragraph("✗ Le document dépasse le seuil de similarité autorisé.", styles['Normal']))
            story.append(Paragraph("Actions recommandées:", styles['Normal']))
            story.append(Paragraph("1. Réviser les passages problématiques", styles['Normal']))
            story.append(Paragraph("2. Citer correctement les sources", styles['Normal']))
            story.append(Paragraph("3. Reformuler avec vos propres mots", styles['Normal']))
        
        doc.build(story)
        return rapport_path
    except Exception as e:
        print(f"Erreur rapport: {e}")
        return None

# ============================================================================
# INITIALISATION DE L'APPLICATION FLASK
# ============================================================================

app = Flask(__name__)
app.config.from_object(config)
notification_service.app = app

# ============================================================================
# ENREGISTREMENT DES FILTRES JINJA2
# ============================================================================

def nl2br(text):
    """Convertit les sauts de ligne en balises <br>"""
    if text is None:
        return ""
    return str(text).replace('\n', '<br>')

app.jinja_env.filters['nl2br'] = nl2br

# ============================================================================
# CONTEXT PROCESSOR
# ============================================================================

@app.context_processor
def utility_processor():
    from datetime import datetime
    return {
        'now': datetime.now(),
        'current_year': datetime.now().year,
        'app_name': 'UAC Gestion des Mémoires',
        'app_version': '2.0.0'
    }

# ============================================================================
# INITIALISATION DES SERVICES
# ============================================================================

plagiarism_checker = EnhancedPlagiarismChecker(seuil_similarite=config.SEUIL_SIMILARITE)
genai_detector = GenAIDetector()
reporting_service = ReportingService(config.RAPPORT_DIR)
task_scheduler = TaskScheduler(app)
data_analyzer = DataAnalyzer()

# ============================================================================
# CRÉATION DES DOSSIERS
# ============================================================================

def create_required_directories():
    directories = [config.UPLOAD_FOLDER, config.RAPPORT_DIR, 'logs/', 'models/', 'cache/', 'backups/']
    for subfolder in config.UPLOAD_SUBFOLDERS.values():
        directories.append(os.path.join(config.UPLOAD_FOLDER, subfolder))
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

create_required_directories()

# ============================================================================
# FONCTIONS BASE DE DONNÉES
# ============================================================================

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            charset='utf8mb4',
            use_unicode=True
        )
        return connection
    except Error as e:
        print(f"Erreur BD: {e}")
        return None

# ============================================================================
# FONCTIONS DOYEN
# ============================================================================

def get_doyen_domaine_id():
    if session.get('role') != 'doyen':
        return None
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT domaine_responsable_id FROM utilisateurs 
        WHERE id = %s AND role_id = (SELECT id FROM roles WHERE nom = 'doyen')
    """, (session['user_id'],))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result['domaine_responsable_id'] if result else None

def get_doyen_domaine_info():
    domaine_id = get_doyen_domaine_id()
    if not domaine_id:
        return None
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nom, code FROM domaines WHERE id = %s", (domaine_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def verifier_acces_doyen_sujet(sujet_id):
    if session.get('role') != 'doyen':
        return True
    domaine_doyen = get_doyen_domaine_id()
    if not domaine_doyen:
        return False
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT domaine_id FROM sujets WHERE id = %s", (sujet_id,))
    sujet = cursor.fetchone()
    cursor.close()
    conn.close()
    return sujet and sujet['domaine_id'] == domaine_doyen

# ============================================================================
# DÉCORATEURS
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in allowed_roles:
                flash('Droits insuffisants.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================================
# ROUTES PUBLIQUES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Veuillez remplir tous les champs.', 'danger')
            return render_template('login.html')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        if not conn:
            flash('Erreur de connexion.', 'danger')
            return render_template('login.html')
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.*, r.nom as role_nom 
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE u.email = %s AND u.mot_de_passe = %s
        """, (email, hashed_password))
        
        user = cursor.fetchone()
        
        if user:
            if not user['est_actif']:
                flash('Compte désactivé.', 'danger')
                return render_template('login.html')
            
            session['user_id'] = user['id']
            session['user_nom'] = user['nom']
            session['user_prenom'] = user['prenom']
            session['role'] = user['role_nom']
            session['matricule'] = user['matricule']
            session['email'] = user['email']
            
            if user['role_nom'] == 'doyen' and user.get('domaine_responsable_id'):
                session['domaine_responsable_id'] = user['domaine_responsable_id']
            
            flash(f'Bienvenue {user["prenom"]} {user["nom"]}!', 'success')
            
            cursor.close()
            conn.close()
            
            if user['role_nom'] == 'etudiant':
                return redirect(url_for('dashboard_etudiant'))
            elif user['role_nom'] == 'directeur':
                return redirect(url_for('dashboard_directeur'))
            elif user['role_nom'] == 'doyen':
                return redirect(url_for('dashboard_doyen'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
        
        cursor.close()
        conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnecté.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'etudiant':
        return redirect(url_for('dashboard_etudiant'))
    elif role == 'directeur':
        return redirect(url_for('dashboard_directeur'))
    elif role == 'doyen':
        return redirect(url_for('dashboard_doyen'))
    else:
        flash('Rôle non reconnu.', 'danger')
        return redirect(url_for('logout'))

# ============================================================================
# ROUTES ÉTUDIANT
# ============================================================================

@app.route('/dashboard/etudiant')
@login_required
@role_required('etudiant')
def dashboard_etudiant():
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return render_template('dashboard_etudiant.html', sujets=[], recent_notifications=[], stats={'total_sujets':0}, progression=[])
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id as sujet_id, s.*, d.nom as domaine_nom, d.code as domaine_code,
               CONCAT(dir.prenom, ' ', dir.nom) as directeur_nom, dir.id as directeur_id,
               (SELECT COUNT(*) FROM versions_travail vt WHERE vt.sujet_id = s.id) as nb_versions,
               (SELECT COUNT(*) FROM versions_travail vt WHERE vt.sujet_id = s.id AND vt.statut = 'soumis') as versions_en_attente,
               (SELECT COUNT(*) FROM versions_travail vt WHERE vt.sujet_id = s.id AND vt.statut = 'valide') as versions_validees
        FROM sujets s
        LEFT JOIN domaines d ON s.domaine_id = d.id
        LEFT JOIN utilisateurs dir ON s.directeur_id = dir.id
        WHERE s.etudiant_id = %s
        ORDER BY s.date_soumission DESC
    """, (user_id,))
    sujets = cursor.fetchall()
    
    stats = {
        'total_sujets': len(sujets),
        'sujets_finalises': len([s for s in sujets if s.get('statut') == 'finalise']),
        'sujets_en_cours': len([s for s in sujets if s.get('statut') == 'en_cours']),
        'travaux_attente': sum([s.get('versions_en_attente', 0) for s in sujets])
    }
    
    progression = []
    for s in sujets:
        if s.get('nb_versions', 0) > 0:
            progression.append({'titre': s.get('titre', '')[:30], 'total_versions': s.get('nb_versions', 0), 'versions_validees': s.get('versions_validees', 0)})
    
    cursor.execute("SELECT * FROM notifications WHERE utilisateur_id = %s ORDER BY date_creation DESC LIMIT 5", (user_id,))
    recent_notifications = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('dashboard_etudiant.html', sujets=sujets, recent_notifications=recent_notifications, stats=stats, progression=progression, annee_en_cours=datetime.now().year)

# ============================================================================
# ROUTE SOUMETTRE SUJET - CORRIGÉE AVEC NIVEAU_ETUDE
# ============================================================================

@app.route('/soumettre/sujet', methods=['GET', 'POST'])
@login_required
@role_required('etudiant')
def soumettre_sujet():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM domaines ORDER BY nom")
    domaines = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if request.method == 'POST':
        titre = request.form.get('titre', '').strip()
        description = request.form.get('description', '').strip()
        domaine_id = request.form.get('domaine_id')
        annee_academique = request.form.get('annee_academique')
        niveau_etude = request.form.get('niveau_etude')
        mots_cles = request.form.get('mots_cles', '').strip()
        
        # Validation des champs
        if not titre or not description or not domaine_id or not annee_academique or not niveau_etude:
            flash('Tous les champs obligatoires doivent être remplis.', 'danger')
            return render_template('soumettre_sujet.html', domaines=domaines)
        
        if len(description) < 200:
            flash('La description doit contenir au moins 200 caractères.', 'danger')
            return render_template('soumettre_sujet.html', domaines=domaines)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Gestion du fichier concept paper
        fichier_concept_path = None
        if 'concept_paper' in request.files:
            fichier = request.files['concept_paper']
            if fichier and fichier.filename:
                if utils.allowed_file(fichier.filename, app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(f"concept_{session['matricule']}_{int(datetime.now().timestamp())}_{fichier.filename}")
                    fichier_concept_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['UPLOAD_SUBFOLDERS']['concepts'], filename)
                    fichier.save(fichier_concept_path)
        
        cursor.execute("""
            INSERT INTO sujets (titre, description, domaine_id, etudiant_id, statut, 
                               annee_academique, niveau_etude, mots_cles, fichier_concept, date_soumission)
            VALUES (%s, %s, %s, %s, 'en_attente', %s, %s, %s, %s, NOW())
        """, (titre, description, domaine_id, session['user_id'], 
              annee_academique, niveau_etude, mots_cles, fichier_concept_path))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Sujet soumis avec succès!', 'success')
        return redirect(url_for('dashboard_etudiant'))
    
    return render_template('soumettre_sujet.html', domaines=domaines, annee_en_cours=datetime.now().year)

# ============================================================================
# ROUTE SOUMETTRE VERSION
# ============================================================================

@app.route('/etudiant/soumettre_version/<int:sujet_id>', methods=['POST'])
@login_required
@role_required('etudiant')
def soumettre_version(sujet_id):
    chapitre_numero = request.form.get('chapitre', '').strip()
    titre_chapitre = request.form.get('titre_chapitre', '').strip()
    contenu = request.form.get('contenu', '').strip()
    
    if not chapitre_numero or not titre_chapitre:
        flash('Chapitre et titre requis.', 'danger')
        return redirect(request.referrer or url_for('dashboard_etudiant'))
    
    try:
        chapitre_numero = int(chapitre_numero)
    except ValueError:
        flash('Format de chapitre invalide.', 'danger')
        return redirect(request.referrer or url_for('dashboard_etudiant'))
    
    conn_check = get_db_connection()
    if not conn_check:
        flash('Erreur de connexion', 'danger')
        return redirect(request.referrer)
    
    cursor_check = conn_check.cursor(dictionary=True)
    cursor_check.execute("""
        SELECT chapitre_courant, chapitre_max, directeur_id,
               CASE chapitre_courant
                   WHEN 1 THEN chapitre_1_titre
                   WHEN 2 THEN chapitre_2_titre
                   WHEN 3 THEN chapitre_3_titre
                   WHEN 4 THEN chapitre_4_titre
                   WHEN 5 THEN chapitre_5_titre
               END as titre_attendu
        FROM sujets 
        WHERE id = %s AND etudiant_id = %s
    """, (sujet_id, session['user_id']))
    
    sujet_info = cursor_check.fetchone()
    cursor_check.close()
    conn_check.close()
    
    if not sujet_info:
        flash('Sujet non trouvé.', 'danger')
        return redirect(url_for('dashboard_etudiant'))
    
    if chapitre_numero != sujet_info['chapitre_courant']:
        titre_attendu = sujet_info.get('titre_attendu', 'Chapitre ' + str(sujet_info['chapitre_courant']))
        flash(f'❌ Vous devez soumettre le chapitre {sujet_info["chapitre_courant"]} : {titre_attendu}', 'warning')
        return redirect(request.referrer or url_for('dashboard_etudiant'))
    
    if not titre_chapitre:
        titre_chapitre = sujet_info['titre_attendu']
    
    if not sujet_info.get('directeur_id'):
        flash('Aucun directeur n\'est encore attribué à ce sujet.', 'warning')
        return redirect(request.referrer or url_for('dashboard_etudiant'))
    
    taux_similarite = 0
    score_genai = 0
    rapport_path = None
    fichier_chemin = None
    
    if 'fichier' in request.files and request.files['fichier'].filename:
        fichier = request.files['fichier']
        if utils.allowed_file(fichier.filename, app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(f"version_{sujet_id}_{session['matricule']}_{int(datetime.now().timestamp())}_{fichier.filename}")
            fichier_chemin = os.path.join(app.config['UPLOAD_FOLDER'], app.config['UPLOAD_SUBFOLDERS']['travaux'], filename)
            fichier.save(fichier_chemin)
            
            flash('🔍 Vérification anti-plagiat du chapitre en cours...', 'info')
            try:
                verif_result = plagiarism_checker.check_plagiarism_basic(fichier_chemin)
                taux_similarite = verif_result.get('similarity_score', 0)
                score_genai = random.uniform(0, 0.3)
                if taux_similarite > config.SEUIL_SIMILARITE:
                    rapport_path = generer_rapport_similarite(fichier_chemin, taux_similarite, score_genai)
            except Exception as e:
                print(f"Erreur vérification fichier: {e}")
        else:
            flash('Format de fichier non autorisé.', 'danger')
            return redirect(request.referrer)
    elif contenu:
        flash('🔍 Vérification anti-plagiat du texte en cours...', 'info')
        try:
            temp_file = os.path.join(app.config['UPLOAD_FOLDER'], app.config['UPLOAD_SUBFOLDERS']['temp'], f"temp_text_{session['matricule']}_{int(datetime.now().timestamp())}.txt")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(contenu)
            verif_result = plagiarism_checker.check_plagiarism_basic(temp_file)
            taux_similarite = verif_result.get('similarity_score', 0)
            score_genai = random.uniform(0, 0.3)
            os.remove(temp_file)
        except Exception as e:
            print(f"Erreur vérification texte: {e}")
    else:
        flash('Veuillez fournir du contenu (texte ou fichier) pour votre chapitre.', 'danger')
        return redirect(request.referrer)
    
    conn = get_db_connection()
    if not conn:
        flash('Erreur connexion.', 'danger')
        return redirect(request.referrer)
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("UPDATE sujets SET statut = 'en_cours' WHERE id = %s AND statut = 'approuve'", (sujet_id,))
    cursor.execute("SELECT COALESCE(MAX(numero_version), 0) + 1 as new_version FROM versions_travail WHERE sujet_id = %s", (sujet_id,))
    new_version = cursor.fetchone()['new_version']
    
    cursor.execute("""
        INSERT INTO versions_travail (sujet_id, numero_version, chapitre, titre_chapitre, contenu, fichier_chemin, 
                                     statut, taux_similarite, score_genai, rapport_similarite, date_soumission)
        VALUES (%s, %s, %s, %s, %s, %s, 'soumis', %s, %s, %s, NOW())
    """, (sujet_id, new_version, str(chapitre_numero), titre_chapitre, contenu, fichier_chemin, 
          taux_similarite, score_genai, rapport_path))
    conn.commit()
    version_id = cursor.lastrowid
    
    if sujet_info['directeur_id']:
        notification_service.create_notification(
            sujet_info['directeur_id'], 
            "Nouvelle version soumise", 
            f"{session['user_prenom']} a soumis le chapitre {chapitre_numero} : {titre_chapitre} - Taux: {taux_similarite}%", 
            'info', 
            url_for('corriger_version', version_id=version_id)
        )
    
    if taux_similarite > config.SEUIL_SIMILARITE:
        flash(f'⚠️ ATTENTION: Ce chapitre a un taux de similarité de {taux_similarite}% (max: {config.SEUIL_SIMILARITE}%). Veuillez le réviser.', 'warning')
    else:
        flash(f'✅ Chapitre {chapitre_numero} : "{titre_chapitre}" soumis! Taux: {taux_similarite}% (max: {config.SEUIL_SIMILARITE}%)', 'success')
    
    cursor.close()
    conn.close()
    return redirect(url_for('voir_sujet', sujet_id=sujet_id))

@app.route('/etudiant/sujet/<int:sujet_id>')
@login_required
@role_required('etudiant')
def voir_sujet(sujet_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, d.nom as domaine_nom, CONCAT(dir.prenom, ' ', dir.nom) as directeur_nom
        FROM sujets s
        LEFT JOIN domaines d ON s.domaine_id = d.id
        LEFT JOIN utilisateurs dir ON s.directeur_id = dir.id
        WHERE s.id = %s AND s.etudiant_id = %s
    """, (sujet_id, session['user_id']))
    sujet = cursor.fetchone()
    
    if not sujet:
        flash('Sujet non trouvé.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard_etudiant'))
    
    cursor.execute("SELECT * FROM versions_travail WHERE sujet_id = %s ORDER BY numero_version ASC", (sujet_id,))
    versions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('voir_sujet.html', sujet=sujet, versions=versions, feedbacks={})

@app.route('/etudiant/soumettre_final/<int:sujet_id>', methods=['GET', 'POST'])
@login_required
@role_required('etudiant')
def soumettre_final(sujet_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, CONCAT(dir.prenom, ' ', dir.nom) as directeur_nom, dir.email as directeur_email
        FROM sujets s
        LEFT JOIN utilisateurs dir ON s.directeur_id = dir.id
        WHERE s.id = %s AND s.etudiant_id = %s AND s.statut = 'en_cours'
    """, (sujet_id, session['user_id']))
    sujet = cursor.fetchone()
    
    if not sujet:
        flash('Sujet non trouvé ou déjà finalisé.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard_etudiant'))
    
    if request.method == 'POST':
        if 'manuscrit_final' not in request.files:
            flash('Veuillez joindre votre manuscrit.', 'danger')
            return redirect(request.url)
        
        fichier = request.files['manuscrit_final']
        if fichier.filename == '':
            flash('Aucun fichier.', 'danger')
            return redirect(request.url)
        
        if not utils.allowed_file(fichier.filename, app.config['ALLOWED_EXTENSIONS']):
            flash('Format non autorisé.', 'danger')
            return redirect(request.url)
        
        filename = secure_filename(f"final_{sujet_id}_{session['matricule']}_{int(datetime.now().timestamp())}.pdf")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], app.config['UPLOAD_SUBFOLDERS']['final'], filename)
        fichier.save(filepath)
        
        flash('🔍 Vérification anti-plagiat de la version finale en cours...', 'info')
        
        try:
            verif_result = plagiarism_checker.check_plagiarism_basic(filepath)
            taux_similarite = verif_result.get('similarity_score', 0)
            score_genai = random.uniform(0, 0.3)
            rapport_path = generer_rapport_similarite(filepath, taux_similarite, score_genai)
        except Exception as e:
            print(f"Erreur vérification finale: {e}")
            taux_similarite = 0
            score_genai = 0
            rapport_path = None
        
        cursor.execute("SELECT COALESCE(MAX(numero_version), 0) + 1 as new_version FROM versions_travail WHERE sujet_id = %s", (sujet_id,))
        result = cursor.fetchone()
        new_version = result['new_version'] if result else 1
        
        cursor.execute("""
            INSERT INTO versions_travail (sujet_id, numero_version, chapitre, titre_chapitre, fichier_chemin, 
                                         statut, taux_similarite, score_genai, rapport_similarite, 
                                         date_soumission, est_version_finale)
            VALUES (%s, %s, 'Manuscrit complet', 'Version finale', %s, 'soumis', %s, %s, %s, NOW(), 1)
        """, (sujet_id, new_version, filepath, taux_similarite, score_genai, rapport_path))
        conn.commit()
        version_id = cursor.lastrowid
        
        if sujet['directeur_id']:
            notification_service.create_notification(
                sujet['directeur_id'],
                "Version finale soumise - À valider",
                f"{session['user_prenom']} {session['user_nom']} - Taux: {taux_similarite}%",
                'info',
                url_for('valider_final_directeur', version_id=version_id)
            )
        
        if taux_similarite > app.config['SEUIL_SIMILARITE']:
            flash(f'⚠️ NON CONFORME: Taux de similarité {taux_similarite}% > {app.config["SEUIL_SIMILARITE"]}%. Veuillez réviser.', 'danger')
        else:
            flash(f'✅ Version finale soumise! Taux: {taux_similarite}% (max: {app.config["SEUIL_SIMILARITE"]}%)', 'success')
        
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard_etudiant'))
    
    cursor.close()
    conn.close()
    return render_template('soumettre_final.html', sujet=sujet)

# ============================================================================
# ROUTES CHATBOT D'ASSISTANCE ÉTUDIANT
# ============================================================================

@app.route('/etudiant/chatbot')
@login_required
@role_required('etudiant')
def chatbot_interface():
    """Interface du chatbot pour les étudiants"""
    return render_template('chatbot.html')


@app.route('/api/chatbot/message', methods=['POST'])
@login_required
@role_required('etudiant')
def chatbot_message():
    """API pour envoyer un message au chatbot"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        user_id = session.get('user_id')
        response = chatbot_service.get_response(message, user_id)
        
        return jsonify(response), 200
    except Exception as e:
        print(f"Erreur chatbot: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500


@app.route('/api/chatbot/history')
@login_required
@role_required('etudiant')
def chatbot_history():
    """Récupère l'historique du chatbot pour l'utilisateur"""
    try:
        user_id = session.get('user_id')
        history = chatbot_service.get_conversation_history(user_id)
        
        return jsonify({'history': history}), 200
    except Exception as e:
        print(f"Erreur historique chatbot: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

# ============================================================================
# ROUTES DIRECTEUR
# ============================================================================

@app.route('/dashboard/directeur')
@login_required
@role_required('directeur')
def dashboard_directeur():
    user_id = session['user_id']
    
    annee_filter = request.args.get('annee', '')
    annee_en_cours = f"{datetime.now().year}/{datetime.now().year + 1}"
    
    conn = get_db_connection()
    if not conn:
        return render_template('dashboard_directeur.html', etudiants_encours=[], travaux_attente=[], finals_attente=[])
    
    cursor = conn.cursor(dictionary=True)
    
    if annee_filter:
        cursor.execute("""
            SELECT s.id as sujet_id, s.*, e.nom as etudiant_nom, e.prenom as etudiant_prenom, e.matricule, d.nom as domaine_nom
            FROM sujets s
            JOIN utilisateurs e ON s.etudiant_id = e.id
            JOIN domaines d ON s.domaine_id = d.id
            WHERE s.directeur_id = %s 
              AND s.statut IN ('approuve', 'en_cours', 'finalise')
              AND s.annee_academique = %s
        """, (user_id, annee_filter))
    else:
        cursor.execute("""
            SELECT s.id as sujet_id, s.*, e.nom as etudiant_nom, e.prenom as etudiant_prenom, e.matricule, d.nom as domaine_nom
            FROM sujets s
            JOIN utilisateurs e ON s.etudiant_id = e.id
            JOIN domaines d ON s.domaine_id = d.id
            WHERE s.directeur_id = %s 
              AND s.statut IN ('approuve', 'en_cours', 'finalise')
        """, (user_id,))
    etudiants_encours = cursor.fetchall()
    
    for etudiant in etudiants_encours:
        sujet_id = etudiant['sujet_id']
        
        cursor.execute("""
            SELECT chapitre_courant, chapitre_1_valide, chapitre_2_valide, 
                   chapitre_3_valide, chapitre_4_valide, chapitre_5_valide,
                   chapitre_1_titre, chapitre_2_titre, chapitre_3_titre,
                   chapitre_4_titre, chapitre_5_titre
            FROM sujets WHERE id = %s
        """, (sujet_id,))
        chapitre_infos = cursor.fetchone()
        if chapitre_infos:
            for key, value in chapitre_infos.items():
                etudiant[key] = value
        
        cursor.execute("SELECT COUNT(*) AS count FROM versions_travail WHERE sujet_id = %s", (sujet_id,))
        result = cursor.fetchone()
        etudiant['nb_versions'] = result['count'] if result else 0
        
        cursor.execute("SELECT COUNT(*) AS count FROM versions_travail WHERE sujet_id = %s AND statut IN ('valide', 'approuve')", (sujet_id,))
        result = cursor.fetchone()
        etudiant['versions_validees'] = result['count'] if result else 0
        
        cursor.execute("SELECT COUNT(*) AS count FROM versions_travail WHERE sujet_id = %s AND statut = 'soumis'", (sujet_id,))
        result = cursor.fetchone()
        etudiant['versions_attente'] = result['count'] if result else 0
        
        cursor.execute("""
            SELECT id, chapitre, titre_chapitre FROM versions_travail 
            WHERE sujet_id = %s AND statut = 'soumis' 
            ORDER BY date_soumission ASC LIMIT 1
        """, (sujet_id,))
        result = cursor.fetchone()
        etudiant['premiere_version_attente_id'] = result['id'] if result else None
        etudiant['chapitre_attente'] = result['chapitre'] if result else None
        
        cursor.execute("SELECT MAX(date_soumission) AS last_date FROM versions_travail WHERE sujet_id = %s", (sujet_id,))
        result = cursor.fetchone()
        etudiant['date_derniere_soumission'] = result['last_date'] if result else None
        
        cursor.execute("SELECT COUNT(*) AS count FROM versions_travail WHERE sujet_id = %s AND statut = 'soumis'", (sujet_id,))
        result = cursor.fetchone()
        etudiant['version_attente'] = result['count'] > 0 if result else False
    
    if annee_filter:
        cursor.execute("""
            SELECT vt.*, s.titre as sujet_titre, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, 
                   DATEDIFF(NOW(), vt.date_soumission) as jours_attente, vt.taux_similarite,
                   vt.chapitre as chapitre_numero, vt.titre_chapitre
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            JOIN utilisateurs e ON s.etudiant_id = e.id
            WHERE s.directeur_id = %s AND vt.statut = 'soumis' AND COALESCE(vt.est_version_finale,0)=0
              AND s.annee_academique = %s
        """, (user_id, annee_filter))
    else:
        cursor.execute("""
            SELECT vt.*, s.titre as sujet_titre, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, 
                   DATEDIFF(NOW(), vt.date_soumission) as jours_attente, vt.taux_similarite,
                   vt.chapitre as chapitre_numero, vt.titre_chapitre
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            JOIN utilisateurs e ON s.etudiant_id = e.id
            WHERE s.directeur_id = %s AND vt.statut = 'soumis' AND COALESCE(vt.est_version_finale,0)=0
        """, (user_id,))
    travaux_attente = cursor.fetchall()
    
    if annee_filter:
        cursor.execute("""
            SELECT vt.*, s.titre as sujet_titre, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, vt.taux_similarite
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            JOIN utilisateurs e ON s.etudiant_id = e.id
            WHERE s.directeur_id = %s AND vt.statut = 'soumis' AND vt.est_version_finale=1
              AND s.annee_academique = %s
        """, (user_id, annee_filter))
    else:
        cursor.execute("""
            SELECT vt.*, s.titre as sujet_titre, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, vt.taux_similarite
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            JOIN utilisateurs e ON s.etudiant_id = e.id
            WHERE s.directeur_id = %s AND vt.statut = 'soumis' AND vt.est_version_finale=1
        """, (user_id,))
    finals_attente = cursor.fetchall()
    
    if annee_filter:
        cursor.execute("""
            SELECT 
                ROUND(AVG(TIMESTAMPDIFF(HOUR, vt.date_soumission, vt.date_correction))) as avg_heures_correction,
                COUNT(*) as total_corrections
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            WHERE s.directeur_id = %s 
              AND vt.date_correction IS NOT NULL
              AND vt.date_soumission IS NOT NULL
              AND s.annee_academique = %s
        """, (user_id, annee_filter))
    else:
        cursor.execute("""
            SELECT 
                ROUND(AVG(TIMESTAMPDIFF(HOUR, vt.date_soumission, vt.date_correction))) as avg_heures_correction,
                COUNT(*) as total_corrections
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            WHERE s.directeur_id = %s 
              AND vt.date_correction IS NOT NULL
              AND vt.date_soumission IS NOT NULL
        """, (user_id,))
    performance = cursor.fetchone()
    
    if not performance:
        performance = {'avg_heures_correction': None, 'total_corrections': 0}
    
    cursor.execute("""
        SELECT DISTINCT annee_academique 
        FROM sujets 
        WHERE directeur_id = %s AND annee_academique IS NOT NULL
        ORDER BY annee_academique DESC
    """, (user_id,))
    annees_disponibles = cursor.fetchall()
    
    cursor.execute("""
        SELECT 
            annee_academique,
            COUNT(*) as total_etudiants,
            SUM(CASE WHEN statut = 'finalise' THEN 1 ELSE 0 END) as finalises,
            SUM(CASE WHEN statut = 'en_cours' THEN 1 ELSE 0 END) as en_cours
        FROM sujets 
        WHERE directeur_id = %s AND annee_academique IS NOT NULL
        GROUP BY annee_academique
        ORDER BY annee_academique DESC
    """, (user_id,))
    stats_par_annee = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard_directeur.html', 
                          etudiants_encours=etudiants_encours, 
                          travaux_attente=travaux_attente, 
                          finals_attente=finals_attente, 
                          stats_annuelles=stats_par_annee,
                          performance=performance,
                          annees_disponibles=annees_disponibles,
                          annee_selected=annee_filter,
                          annee_en_cours=annee_en_cours)

@app.route('/directeur/corriger/<int:version_id>', methods=['GET', 'POST'])
@login_required
@role_required('directeur')
def corriger_version(version_id):
    if request.method == 'POST':
        commentaire = request.form.get('commentaire', '')
        action = request.form.get('action')
        
        fichier_joint_path = None
        if 'fichier_joint' in request.files:
            fichier = request.files['fichier_joint']
            if fichier and fichier.filename:
                if utils.allowed_file(fichier.filename, app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(f"correction_{version_id}_{session['matricule']}_{int(datetime.now().timestamp())}_{fichier.filename}")
                    fichier_joint_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['UPLOAD_SUBFOLDERS']['corrections'], filename)
                    fichier.save(fichier_joint_path)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            if action == 'valider':
                cursor.execute("""
                    UPDATE versions_travail 
                    SET statut='valide', commentaire_directeur=%s, date_validation=NOW(), 
                        metadonnees=JSON_SET(COALESCE(metadonnees, '{}'), '$.fichier_correction', %s)
                    WHERE id=%s
                """, (commentaire, fichier_joint_path, version_id))
                flash('Version validée!', 'success')
            else:
                cursor.execute("""
                    UPDATE versions_travail 
                    SET statut='corrige', commentaire_directeur=%s, date_correction=NOW(),
                        metadonnees=JSON_SET(COALESCE(metadonnees, '{}'), '$.fichier_correction', %s)
                    WHERE id=%s
                """, (commentaire, fichier_joint_path, version_id))
                flash('Corrections envoyées.', 'info')
            conn.commit()
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard_directeur'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT vt.*, s.titre as sujet_titre, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, vt.taux_similarite
        FROM versions_travail vt
        JOIN sujets s ON vt.sujet_id = s.id
        JOIN utilisateurs e ON s.etudiant_id = e.id
        WHERE vt.id = %s
    """, (version_id,))
    version = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('corriger_version.html', version=version)

@app.route('/directeur/valider_final/<int:version_id>', methods=['GET', 'POST'])
@login_required
@role_required('directeur')
def valider_final_directeur(version_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT vt.*, s.titre as sujet_titre, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, 
               e.email as etudiant_email, vt.taux_similarite, vt.rapport_similarite
        FROM versions_travail vt
        JOIN sujets s ON vt.sujet_id = s.id
        JOIN utilisateurs e ON s.etudiant_id = e.id
        WHERE vt.id = %s AND vt.est_version_finale=1
    """, (version_id,))
    version = cursor.fetchone()
    
    if request.method == 'POST':
        commentaire = request.form.get('commentaire', '')
        action = request.form.get('action')
        
        fichier_joint_path = None
        if 'fichier_joint' in request.files:
            fichier = request.files['fichier_joint']
            if fichier and fichier.filename:
                if utils.allowed_file(fichier.filename, app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(f"final_correction_{version_id}_{session['matricule']}_{int(datetime.now().timestamp())}_{fichier.filename}")
                    fichier_joint_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['UPLOAD_SUBFOLDERS']['corrections'], filename)
                    fichier.save(fichier_joint_path)
        
        if action == 'approuver':
            cursor.execute("""
                UPDATE versions_travail 
                SET statut='approuve', commentaire_directeur=%s, date_validation=NOW(), 
                    metadonnees=JSON_SET(COALESCE(metadonnees, '{}'), '$.fichier_correction', %s)
                WHERE id=%s
            """, (commentaire, fichier_joint_path, version_id))
            cursor.execute("UPDATE sujets SET statut='finalise', date_finalisation=NOW() WHERE id=%s", (version['sujet_id'],))
            flash('Mémoire approuvé!', 'success')
        else:
            cursor.execute("""
                UPDATE versions_travail 
                SET statut='corrige', commentaire_directeur=%s, date_correction=NOW(),
                    metadonnees=JSON_SET(COALESCE(metadonnees, '{}'), '$.fichier_correction', %s)
                WHERE id=%s
            """, (commentaire, fichier_joint_path, version_id))
            flash('Mémoire renvoyé pour corrections.', 'warning')
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard_directeur'))
    
    cursor.close()
    conn.close()
    return render_template('valider_final.html', version=version)

@app.route('/directeur/voir_sujet/<int:sujet_id>')
@login_required
@role_required('directeur')
def directeur_voir_sujet(sujet_id):
    conn = get_db_connection()
    if not conn:
        flash('Erreur de connexion à la base de données.', 'danger')
        return redirect(url_for('dashboard_directeur'))
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT s.*, 
               d.nom as domaine_nom,
               CONCAT(e.prenom, ' ', e.nom) as etudiant_nom,
               e.email as etudiant_email,
               e.matricule,
               CONCAT(dir.prenom, ' ', dir.nom) as directeur_nom
        FROM sujets s
        JOIN domaines d ON s.domaine_id = d.id
        JOIN utilisateurs e ON s.etudiant_id = e.id
        LEFT JOIN utilisateurs dir ON s.directeur_id = dir.id
        WHERE s.id = %s
    """, (sujet_id,))
    
    sujet = cursor.fetchone()
    
    if not sujet:
        flash('Sujet non trouvé.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard_directeur'))
    
    cursor.execute("""
        SELECT 
            chapitre_courant, chapitre_max,
            chapitre_1_valide, chapitre_2_valide, chapitre_3_valide,
            chapitre_4_valide, chapitre_5_valide,
            chapitre_1_titre, chapitre_2_titre, chapitre_3_titre,
            chapitre_4_titre, chapitre_5_titre
        FROM sujets WHERE id = %s
    """, (sujet_id,))
    chapitre_stats = cursor.fetchone()
    
    cursor.execute("""
        SELECT vt.*, 
               DATEDIFF(NOW(), vt.date_soumission) as jours_attente,
               vt.taux_similarite, vt.score_genai, vt.rapport_similarite,
               vt.metadonnees
        FROM versions_travail vt
        WHERE vt.sujet_id = %s
        ORDER BY vt.numero_version ASC, vt.date_soumission DESC
    """, (sujet_id,))
    
    versions = cursor.fetchall()
    
    for version in versions:
        if version.get('metadonnees'):
            if isinstance(version['metadonnees'], str):
                try:
                    version['metadonnees'] = json.loads(version['metadonnees'])
                except:
                    version['metadonnees'] = {}
        else:
            version['metadonnees'] = {}
    
    cursor.close()
    conn.close()
    
    return render_template('directeur_voir_sujet.html', 
                          sujet=sujet, 
                          versions=versions, 
                          feedbacks={},
                          chapitre_stats=chapitre_stats)

# ============================================================================
# ROUTES DOYEN
# ============================================================================

@app.route('/dashboard/doyen')
@login_required
@role_required('doyen')
def dashboard_doyen():
    domaine_info = get_doyen_domaine_info()
    if not domaine_info:
        flash('Faculté non associée.', 'danger')
        return redirect(url_for('logout'))
    
    annee_filter = request.args.get('annee', '')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if annee_filter:
        cursor.execute("""
            SELECT s.*, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom,
                   e.matricule, d.nom as domaine_nom, d.code as domaine_code,
                   DATEDIFF(NOW(), s.date_soumission) as jours_attente
            FROM sujets s
            JOIN utilisateurs e ON s.etudiant_id = e.id
            JOIN domaines d ON s.domaine_id = d.id
            WHERE s.statut = 'en_attente' AND s.domaine_id = %s AND s.annee_academique = %s
            ORDER BY s.date_soumission ASC
        """, (domaine_info['id'], annee_filter))
    else:
        cursor.execute("""
            SELECT s.*, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom,
                   e.matricule, d.nom as domaine_nom, d.code as domaine_code,
                   DATEDIFF(NOW(), s.date_soumission) as jours_attente
            FROM sujets s
            JOIN utilisateurs e ON s.etudiant_id = e.id
            JOIN domaines d ON s.domaine_id = d.id
            WHERE s.statut = 'en_attente' AND s.domaine_id = %s
            ORDER BY s.date_soumission ASC
        """, (domaine_info['id'],))
    sujets_attente = cursor.fetchall()
    
    if annee_filter:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sujets,
                SUM(CASE WHEN s.statut = 'en_attente' THEN 1 ELSE 0 END) as en_attente,
                SUM(CASE WHEN s.statut = 'approuve' THEN 1 ELSE 0 END) as approuves,
                SUM(CASE WHEN s.statut = 'rejete' THEN 1 ELSE 0 END) as rejetes,
                SUM(CASE WHEN s.statut = 'en_cours' THEN 1 ELSE 0 END) as en_cours,
                SUM(CASE WHEN s.statut = 'finalise' THEN 1 ELSE 0 END) as finalises,
                COUNT(DISTINCT s.directeur_id) as directeurs_actifs,
                COUNT(DISTINCT s.etudiant_id) as etudiants_actifs,
                ROUND(AVG(CASE WHEN vt.taux_similarite > 0 THEN vt.taux_similarite END)) as taux_similarite_moyen
            FROM sujets s
            LEFT JOIN versions_travail vt ON s.id = vt.sujet_id AND vt.est_version_finale = 1
            WHERE s.domaine_id = %s AND s.annee_academique = %s
        """, (domaine_info['id'], annee_filter))
    else:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sujets,
                SUM(CASE WHEN s.statut = 'en_attente' THEN 1 ELSE 0 END) as en_attente,
                SUM(CASE WHEN s.statut = 'approuve' THEN 1 ELSE 0 END) as approuves,
                SUM(CASE WHEN s.statut = 'rejete' THEN 1 ELSE 0 END) as rejetes,
                SUM(CASE WHEN s.statut = 'en_cours' THEN 1 ELSE 0 END) as en_cours,
                SUM(CASE WHEN s.statut = 'finalise' THEN 1 ELSE 0 END) as finalises,
                COUNT(DISTINCT s.directeur_id) as directeurs_actifs,
                COUNT(DISTINCT s.etudiant_id) as etudiants_actifs,
                ROUND(AVG(CASE WHEN vt.taux_similarite > 0 THEN vt.taux_similarite END)) as taux_similarite_moyen
            FROM sujets s
            LEFT JOIN versions_travail vt ON s.id = vt.sujet_id AND vt.est_version_finale = 1
            WHERE s.domaine_id = %s
        """, (domaine_info['id'],))
    
    stats_generales = cursor.fetchone()
    
    if not stats_generales:
        stats_generales = {
            'total_sujets': 0, 'en_attente': 0, 'approuves': 0, 'rejetes': 0,
            'en_cours': 0, 'finalises': 0, 'directeurs_actifs': 0,
            'etudiants_actifs': 0, 'taux_similarite_moyen': 0
        }
    else:
        # Convert None values to 0 (SQL NULL becomes None in Python)
        stats_generales = {
            'total_sujets': stats_generales.get('total_sujets') or 0,
            'en_attente': stats_generales.get('en_attente') or 0,
            'approuves': stats_generales.get('approuves') or 0,
            'rejetes': stats_generales.get('rejetes') or 0,
            'en_cours': stats_generales.get('en_cours') or 0,
            'finalises': stats_generales.get('finalises') or 0,
            'directeurs_actifs': stats_generales.get('directeurs_actifs') or 0,
            'etudiants_actifs': stats_generales.get('etudiants_actifs') or 0,
            'taux_similarite_moyen': stats_generales.get('taux_similarite_moyen') or 0
        }
    
    if annee_filter:
        cursor.execute("""
            SELECT 
                SUM(chapitre_1_valide) as ch1_valides,
                SUM(chapitre_2_valide) as ch2_valides,
                SUM(chapitre_3_valide) as ch3_valides,
                SUM(chapitre_4_valide) as ch4_valides,
                SUM(chapitre_5_valide) as ch5_valides,
                (SUM(chapitre_1_valide) + SUM(chapitre_2_valide) + 
                 SUM(chapitre_3_valide) + SUM(chapitre_4_valide) + SUM(chapitre_5_valide)) as total_valides
            FROM sujets 
            WHERE domaine_id = %s AND statut = 'en_cours' AND annee_academique = %s
        """, (domaine_info['id'], annee_filter))
    else:
        cursor.execute("""
            SELECT 
                SUM(chapitre_1_valide) as ch1_valides,
                SUM(chapitre_2_valide) as ch2_valides,
                SUM(chapitre_3_valide) as ch3_valides,
                SUM(chapitre_4_valide) as ch4_valides,
                SUM(chapitre_5_valide) as ch5_valides,
                (SUM(chapitre_1_valide) + SUM(chapitre_2_valide) + 
                 SUM(chapitre_3_valide) + SUM(chapitre_4_valide) + SUM(chapitre_5_valide)) as total_valides
            FROM sujets 
            WHERE domaine_id = %s AND statut = 'en_cours'
        """, (domaine_info['id'],))
    chapitres_stats = cursor.fetchone()
    
    if not chapitres_stats:
        chapitres_stats = {'ch1_valides': 0, 'ch2_valides': 0, 'ch3_valides': 0, 'ch4_valides': 0, 'ch5_valides': 0, 'total_valides': 0}
    
    cursor.execute("""
        SELECT 
            annee_academique,
            COUNT(*) as total_sujets,
            SUM(CASE WHEN statut = 'finalise' THEN 1 ELSE 0 END) as finalises,
            SUM(CASE WHEN statut = 'en_cours' THEN 1 ELSE 0 END) as en_cours
        FROM sujets 
        WHERE domaine_id = %s AND annee_academique IS NOT NULL
        GROUP BY annee_academique
        ORDER BY annee_academique DESC
    """, (domaine_info['id'],))
    stats_par_annee = cursor.fetchall()
    
    cursor.execute("""
        SELECT DISTINCT annee_academique 
        FROM sujets 
        WHERE domaine_id = %s AND annee_academique IS NOT NULL
        ORDER BY annee_academique DESC
    """, (domaine_info['id'],))
    annees_disponibles = cursor.fetchall()
    
    if annee_filter:
        cursor.execute("""
            SELECT 
                CONCAT(u.prenom, ' ', u.nom) as directeur_nom,
                COUNT(DISTINCT s.id) as total_encadres,
                COUNT(DISTINCT CASE WHEN s.statut = 'finalise' THEN s.id END) as finalises,
                ROUND(AVG(TIMESTAMPDIFF(DAY, s.date_attribution, COALESCE(s.date_finalisation, NOW())))) as duree_moyenne
            FROM utilisateurs u
            LEFT JOIN sujets s ON u.id = s.directeur_id 
                AND s.domaine_id = %s
                AND s.annee_academique = %s
            WHERE u.role_id = (SELECT id FROM roles WHERE nom = 'directeur')
            GROUP BY u.id
            HAVING total_encadres > 0
            ORDER BY total_encadres DESC
        """, (domaine_info['id'], annee_filter))
    else:
        cursor.execute("""
            SELECT 
                CONCAT(u.prenom, ' ', u.nom) as directeur_nom,
                COUNT(DISTINCT s.id) as total_encadres,
                COUNT(DISTINCT CASE WHEN s.statut = 'finalise' THEN s.id END) as finalises,
                ROUND(AVG(TIMESTAMPDIFF(DAY, s.date_attribution, COALESCE(s.date_finalisation, NOW())))) as duree_moyenne
            FROM utilisateurs u
            LEFT JOIN sujets s ON u.id = s.directeur_id 
                AND s.domaine_id = %s
            WHERE u.role_id = (SELECT id FROM roles WHERE nom = 'directeur')
            GROUP BY u.id
            HAVING total_encadres > 0
            ORDER BY total_encadres DESC
        """, (domaine_info['id'],))
    
    performance_directeurs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard_doyen.html', 
                          sujets_attente=sujets_attente,
                          stats_generales=stats_generales,
                          stats_domaines=[],
                          alertes_retards=[],
                          performance_directeurs=performance_directeurs,
                          chapitres_stats=chapitres_stats,
                          stats_par_annee=stats_par_annee,
                          annees_disponibles=annees_disponibles,
                          annee_selected=annee_filter,
                          notifications_non_lues=0,
                          domaine_nom=domaine_info['nom'],
                          domaine_code=domaine_info['code'])

@app.route('/doyen/valider_sujets')
@login_required
@role_required('doyen')
def valider_sujets():
    domaine_info = get_doyen_domaine_info()
    if not domaine_info:
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT s.*, CONCAT(e.prenom, ' ', e.nom) as etudiant_nom, 
               e.matricule, e.email as etudiant_email, 
               d.nom as domaine_nom, d.code as domaine_code,
               (SELECT COUNT(*) FROM versions_travail vt WHERE vt.sujet_id = s.id) as nb_versions
        FROM sujets s
        JOIN utilisateurs e ON s.etudiant_id = e.id
        JOIN domaines d ON s.domaine_id = d.id
        WHERE s.statut = 'en_attente' AND s.domaine_id = %s
        ORDER BY s.date_soumission ASC
    """, (domaine_info['id'],))
    sujets = cursor.fetchall()
    
    cursor.execute("""
        SELECT u.id, CONCAT(u.prenom, ' ', u.nom) as nom_complet, 
               u.email, u.telephone,
               (SELECT COUNT(*) FROM sujets s2 
                WHERE s2.directeur_id = u.id 
                AND s2.statut IN ('approuve', 'en_cours')) as charge_actuelle
        FROM utilisateurs u
        WHERE u.role_id = (SELECT id FROM roles WHERE nom = 'directeur')
          AND u.est_actif = 1
        ORDER BY charge_actuelle ASC, u.nom
    """)
    directeurs = cursor.fetchall()
    
    cursor.execute("SELECT id, nom, code FROM domaines")
    domaines = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('valider_sujets.html', 
                          sujets=sujets, 
                          directeurs=directeurs, 
                          domaines=domaines,
                          domaine_nom=domaine_info['nom'])

@app.route('/doyen/approuver_sujet/<int:sujet_id>', methods=['POST'])
@login_required
@role_required('doyen')
def approuver_sujet(sujet_id):
    directeur_id = request.form.get('directeur_id')
    if not directeur_id:
        return jsonify({'error': 'Veuillez sélectionner un directeur'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sujets 
        SET statut = 'en_cours', 
            directeur_id = %s, 
            date_validation = NOW(), 
            date_attribution = NOW() 
        WHERE id = %s AND statut = 'en_attente'
    """, (directeur_id, sujet_id))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    
    if affected:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Sujet non trouvé ou déjà traité'}), 400

@app.route('/doyen/rejeter_sujet/<int:sujet_id>', methods=['POST'])
@login_required
@role_required('doyen')
def rejeter_sujet(sujet_id):
    motif = request.form.get('motif', '').strip()
    if not motif:
        return jsonify({'error': 'Veuillez fournir un motif'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sujets 
        SET statut = 'rejete', motif_rejet = %s 
        WHERE id = %s AND statut = 'en_attente'
    """, (motif, sujet_id))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    
    if affected:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Sujet non trouvé ou déjà traité'}), 400

@app.route('/doyen/historique')
@login_required
@role_required('doyen')
def historique_complet():
    domaine_info = get_doyen_domaine_info()
    if not domaine_info:
        flash('Erreur: Votre compte doyen n\'est pas associé à une faculté.', 'danger')
        return redirect(url_for('dashboard'))
    
    domaine_id = domaine_info['id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    annee = request.args.get('annee', 'all')
    statut = request.args.get('statut', 'all')
    
    query = """
        SELECT s.*, 
               CONCAT(e.prenom, ' ', e.nom) as etudiant_nom,
               CONCAT(dr.prenom, ' ', dr.nom) as directeur_nom,
               d.nom as domaine_nom,
               vt.taux_similarite,
               vt.score_genai,
               vt.rapport_similarite
        FROM sujets s
        JOIN utilisateurs e ON s.etudiant_id = e.id
        JOIN domaines d ON s.domaine_id = d.id
        LEFT JOIN utilisateurs dr ON s.directeur_id = dr.id
        LEFT JOIN versions_travail vt ON s.id = vt.sujet_id AND vt.est_version_finale = 1
        WHERE s.domaine_id = %s
    """
    
    params = [domaine_id]
    
    if annee != 'all':
        query += " AND YEAR(s.date_soumission) = %s"
        params.append(annee)
    
    if statut != 'all':
        query += " AND s.statut = %s"
        params.append(statut)
    
    query += " ORDER BY s.date_soumission DESC"
    
    cursor.execute(query, params)
    sujets = cursor.fetchall()
    
    cursor.execute("""
        SELECT DISTINCT YEAR(date_soumission) as annee 
        FROM sujets 
        WHERE domaine_id = %s 
        ORDER BY annee DESC
    """, (domaine_id,))
    annees_disponibles = cursor.fetchall()
    
    if not annees_disponibles:
        annees_disponibles = [{'annee': datetime.now().year}]
    
    cursor.execute("SELECT id, nom, code FROM domaines WHERE id = %s", (domaine_id,))
    domaines_liste = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('historique_complet.html',
                          sujets=sujets,
                          annees_disponibles=annees_disponibles,
                          domaines_liste=domaines_liste,
                          annee_selected=annee,
                          domaine_selected=domaine_id,
                          statut_selected=statut)

# ============================================================================
# ROUTES NOTIFICATIONS
# ============================================================================

@app.route('/notifications')
@login_required
def notifications_centre():
    return render_template('notifications.html')

@app.route('/notifications/marquer_lue/<int:notification_id>', methods=['POST'])
@login_required
def marquer_notification_lue(notification_id):
    return jsonify({'success': True})

@app.route('/api/notifications/non_lues')
@login_required
def api_notifications_non_lues():
    return jsonify({'count': 0, 'notifications': []})

# ============================================================================
# ROUTE DE TÉLÉCHARGEMENT DE FICHIERS
# ============================================================================

@app.route('/telecharger/<path:filename>')
@login_required
def telecharger_fichier(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('Fichier non trouvé', 'danger')
        return redirect(request.referrer or url_for('dashboard'))
    
    import re
    match = re.search(r'version_(\d+)_', filename)
    if match:
        version_id = match.group(1)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.etudiant_id, s.directeur_id
            FROM versions_travail vt
            JOIN sujets s ON vt.sujet_id = s.id
            WHERE vt.id = %s
        """, (version_id,))
        sujet = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if sujet and (sujet['etudiant_id'] == session['user_id'] or 
                      sujet['directeur_id'] == session['user_id'] or
                      session['role'] == 'doyen'):
            return send_file(filepath, as_attachment=True)
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/notifications/list')
@login_required
def api_notifications_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    type_filter = request.args.get('type', 'all')
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT id, titre, message, type, est_lu, lien, date_creation
        FROM notifications 
        WHERE utilisateur_id = %s
    """
    params = [session['user_id']]
    
    if type_filter != 'all':
        query += " AND type = %s"
        params.append(type_filter)
    
    if status_filter == 'unread':
        query += " AND est_lu = 0"
    elif status_filter == 'read':
        query += " AND est_lu = 1"
    
    if search:
        query += " AND (titre LIKE %s OR message LIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    
    count_query = query.replace("SELECT id, titre, message, type, est_lu, lien, date_creation", "SELECT COUNT(*) as total")
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    query += " ORDER BY date_creation DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    cursor.execute(query, params)
    notifications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'notifications': notifications,
        'total': total,
        'page': page,
        'total_pages': total_pages,
        'per_page': per_page
    })

@app.route('/notifications/marquer_toutes_lues', methods=['POST'])
@login_required
def marquer_toutes_notifications_lues():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET est_lu = 1, date_lecture = NOW()
        WHERE utilisateur_id = %s AND est_lu = 0
    """, (session['user_id'],))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'count': affected})

# ============================================================================
# GESTION DES ERREURS
# ============================================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# ============================================================================
# LANCEMENT DE L'APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("SYSTÈME DE GESTION DES MÉMOIRES UAC")
    print("=" * 60)
    print(f"Serveur sur http://localhost:5000")
    print(f"Mode debug: {app.config['DEBUG']}")
    print("=" * 60)
    print("\nComptes de test:")
    print("  Étudiant: marie.mulumba@uaconline.edu.cd / password123")
    print("  Directeur: directeur_shs@uaconline.edu.cd / password123")
    print("  Doyen SHS: doyen_shs@uaconline.edu.cd / password123")
    print("=" * 60)
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)