# Module de vérification de similarité - plagiarism_checker.py
import re
import os
import hashlib
from datetime import datetime
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Téléchargement des ressources NLTK nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class PlagiarismChecker:
    """Classe principale pour la vérification de similarité et de plagiat"""
    
    def __init__(self, seuil_similarite=20):
        """
        Initialise le vérificateur de plagiat
        Args:
            seuil_similarite: Seuil maximum de similarité accepté (en pourcentage)
        """
        self.seuil_similarite = seuil_similarite
        self.stop_words = set(stopwords.words('french'))
        
        # Base de données de documents de référence (simulation)
        self.reference_documents = []
        self.reference_titles = []
        
    def extraire_texte_fichier(self, chemin_fichier):
        """
        Extrait le texte d'un fichier (PDF, DOCX, TXT)
        Args:
            chemin_fichier: Chemin vers le fichier à analyser
        Returns:
            Texte extrait du fichier
        """
        texte = ""
        
        try:
            # Vérifier l'extension du fichier
            extension = os.path.splitext(chemin_fichier)[1].lower()
            
            if extension == '.pdf':
                # Extraction depuis PDF
                with open(chemin_fichier, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        texte += page.extract_text()
                        
            elif extension == '.docx':
                # Extraction depuis DOCX
                doc = docx.Document(chemin_fichier)
                for paragraph in doc.paragraphs:
                    texte += paragraph.text + "\n"
                    
            elif extension == '.txt':
                # Extraction depuis TXT
                with open(chemin_fichier, 'r', encoding='utf-8') as file:
                    texte = file.read()
                    
            else:
                raise ValueError(f"Format de fichier non supporté: {extension}")
                
        except Exception as e:
            print(f"Erreur lors de l'extraction du texte: {e}")
            texte = ""
            
        return texte
    
    def preprocesser_texte(self, texte):
        """
        Prétraite le texte pour l'analyse de similarité
        Args:
            texte: Texte brut à prétraiter
        Returns:
            Texte prétraité
        """
        # Mise en minuscules
        texte = texte.lower()
        
        # Suppression des caractères spéciaux et chiffres
        texte = re.sub(r'[^a-zàâçéèêëîïôûùüÿñ\s]', '', texte)
        
        # Tokenisation
        tokens = word_tokenize(texte, language='french')
        
        # Suppression des stop words
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Suppression des tokens trop courts
        tokens = [token for token in tokens if len(token) > 2]
        
        return ' '.join(tokens)
    
    def calculer_similarite_tfidf(self, texte1, texte2):
        """
        Calcule la similarité entre deux textes en utilisant TF-IDF
        Args:
            texte1: Premier texte
            texte2: Deuxième texte
        Returns:
            Score de similarité (0-100)
        """
        if not texte1 or not texte2:
            return 0
            
        try:
            # Prétraitement des textes
            texte1_pretraite = self.preprocesser_texte(texte1)
            texte2_pretraite = self.preprocesser_texte(texte2)
            
            # Création du vectoriseur TF-IDF
            vectorizer = TfidfVectorizer()
            
            # Calcul de la matrice TF-IDF
            tfidf_matrix = vectorizer.fit_transform([texte1_pretraite, texte2_pretraite])
            
            # Calcul de la similarité cosinus
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            # Conversion en pourcentage
            score = round(similarity[0][0] * 100, 2)
            
            return score
            
        except Exception as e:
            print(f"Erreur lors du calcul de similarité: {e}")
            return 0
    
    def calculer_similarite_ngram(self, texte1, texte2, n=3):
        """
        Calcule la similarité basée sur les n-grammes
        Args:
            texte1: Premier texte
            texte2: Deuxième texte
            n: Taille des n-grammes
        Returns:
            Score de similarité (0-100)
        """
        def obtenir_ngrams(texte, n):
            """Extrait les n-grammes d'un texte"""
            texte = self.preprocesser_texte(texte)
            ngrams = zip(*[texte[i:] for i in range(n)])
            return [' '.join(ngram) for ngram in ngrams]
        
        ngrams1 = obtenir_ngrams(texte1, n)
        ngrams2 = obtenir_ngrams(texte2, n)
        
        if not ngrams1 or not ngrams2:
            return 0
            
        # Calcul de l'intersection des n-grammes
        set1 = set(ngrams1)
        set2 = set(ngrams2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        similarity = len(intersection) / len(union) if union else 0
        
        return round(similarity * 100, 2)
    
    def verifier_similarite_document(self, chemin_fichier):
        """
        Vérifie la similarité d'un document par rapport à une base de référence
        Args:
            chemin_fichier: Chemin du fichier à vérifier
        Returns:
            Dict contenant les résultats de vérification
        """
        # Extraction du texte du document
        texte_document = self.extraire_texte_fichier(chemin_fichier)
        
        if not texte_document:
            return {
                'taux_similarite': 0,
                'est_conforme': False,
                'erreur': "Impossible d'extraire le texte du document"
            }
        
        # Calcul des scores avec différentes méthodes
        scores = []
        
        # Simuler des documents de référence (à remplacer par la vraie base)
        for ref_doc in self.reference_documents:
            score_tfidf = self.calculer_similarite_tfidf(texte_document, ref_doc)
            score_ngram = self.calculer_similarite_ngram(texte_document, ref_doc)
            score_moyen = (score_tfidf + score_ngram) / 2
            scores.append(score_moyen)
        
        # Taux de similarité maximum trouvé
        taux_similarite = max(scores) if scores else 0
        
        # Vérification de la conformité
        est_conforme = taux_similarite <= self.seuil_similarite
        
        return {
            'taux_similarite': taux_similarite,
            'est_conforme': est_conforme,
            'seuil_applique': self.seuil_similarite,
            'erreur': None
        }
    
    def verifier_genai(self, texte):
        """
        Vérifie la probabilité que le texte soit généré par une IA (GenAI)
        Utilise des heuristiques statistiques
        Args:
            texte: Texte à analyser
        Returns:
            Score de probabilité GenAI (0-100)
        """
        if not texte:
            return 0
            
        texte_pretraite = self.preprocesser_texte(texte)
        
        # Caractéristiques suspectes pour du contenu GenAI
        score_genai = 0
        
        # 1. Longueur moyenne des phrases
        phrases = re.split(r'[.!?]+', texte)
        longueur_moyenne = sum(len(p.split()) for p in phrases) / len(phrases) if phrases else 0
        
        # Les textes GenAI ont souvent des phrases de longueur uniforme
        if 15 <= longueur_moyenne <= 25:
            score_genai += 20
        
        # 2. Richesse lexicale (ratio de mots uniques)
        mots = texte_pretraite.split()
        mots_uniques = set(mots)
        richesse_lexicale = len(mots_uniques) / len(mots) if mots else 0
        
        # Les textes GenAI ont souvent une richesse lexicale moyenne
        if 0.4 <= richesse_lexicale <= 0.6:
            score_genai += 15
            
        # 3. Répétition de séquences
        sequences = []
        for i in range(len(mots) - 2):
            seq = ' '.join(mots[i:i+3])
            sequences.append(seq)
        
        repetitions = len(sequences) - len(set(sequences))
        taux_repetition = repetitions / len(sequences) if sequences else 0
        
        # Les textes GenAI ont moins de répétitions
        if taux_repetition < 0.1:
            score_genai += 15
        
        # 4. Complexité des phrases (signes de ponctuation)
        ponctuation_count = len(re.findall(r'[,;:()"\'-]', texte))
        phrase_count = len(phrases)
        ponctuation_par_phrase = ponctuation_count / phrase_count if phrase_count > 0 else 0
        
        if 2 <= ponctuation_par_phrase <= 5:
            score_genai += 20
            
        # 5. Distribution des classes grammaticales (simplifiée)
        mots_style_formel = re.findall(r'\b(cependant|néanmoins|par conséquent|en outre|de plus|ainsi)\b', texte.lower())
        style_formel_count = len(mots_style_formel) / len(phrases) if phrases else 0
        
        if 0.1 <= style_formel_count <= 0.3:
            score_genai += 30
            
        return min(score_genai, 100)
    
    def generer_rapport_similarite(self, nom_fichier, resultats):
        """
        Génère un rapport PDF détaillé de la vérification
        Args:
            nom_fichier: Nom original du fichier vérifié
            resultats: Résultats de la vérification
        Returns:
            Chemin du rapport généré
        """
        # Création du dossier rapports s'il n'existe pas
        rapport_dir = "rapports_similarite"
        if not os.path.exists(rapport_dir):
            os.makedirs(rapport_dir)
        
        # Nom du rapport avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rapport_path = os.path.join(rapport_dir, f"rapport_{timestamp}.pdf")
        
        # Création du document PDF
        doc = SimpleDocTemplate(rapport_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Style personnalisé
        styles.add(ParagraphStyle(name='CustomTitle', fontSize=16, textColor=colors.HexColor('#003366'), spaceAfter=30))
        styles.add(ParagraphStyle(name='CustomHeading', fontSize=12, textColor=colors.HexColor('#004080'), spaceAfter=12))
        styles.add(ParagraphStyle(name='CustomBody', fontSize=10, spaceAfter=6))
        
        # Contenu du rapport
        story = []
        
        # Titre
        story.append(Paragraph("RAPPORT DE VÉRIFICATION DE SIMILARITÉ", styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Informations générales
        story.append(Paragraph(f"Document analysé: {nom_fichier}", styles['CustomBody']))
        story.append(Paragraph(f"Date d'analyse: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}", styles['CustomBody']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Résultats
        story.append(Paragraph("Résultats de l'analyse:", styles['CustomHeading']))
        
        # Tableau des scores
        data = [
            ["Paramètre", "Valeur", "Statut"],
            ["Taux de similarité", f"{resultats['taux_similarite']:.2f}%", 
             "✓ Conforme" if resultats['est_conforme'] else "✗ Non conforme"],
            ["Seuil appliqué", f"{resultats['seuil_applique']}%", "Valeur de référence"],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Détection GenAI
        if 'score_genai' in resultats:
            story.append(Paragraph("Analyse de contenu généré par IA:", styles['CustomHeading']))
            story.append(Paragraph(f"Probabilité de contenu GenAI: {resultats['score_genai']:.2f}%", styles['CustomBody']))
            
            if resultats['score_genai'] > 30:
                story.append(Paragraph("⚠️ ATTENTION: Ce texte présente des caractéristiques pouvant indiquer une génération par IA", 
                                     ParagraphStyle('Warning', parent=styles['CustomBody'], textColor=colors.red)))
        story.append(Spacer(1, 0.2 * inch))
        
        # Recommandations
        story.append(Paragraph("Recommandations:", styles['CustomHeading']))
        
        if resultats['est_conforme']:
            story.append(Paragraph("✓ Le document respecte le seuil de similarité autorisé.", styles['CustomBody']))
            story.append(Paragraph("✓ Aucune action corrective n'est nécessaire.", styles['CustomBody']))
        else:
            story.append(Paragraph("✗ Le document dépasse le seuil de similarité autorisé.", 
                                 ParagraphStyle('Error', parent=styles['CustomBody'], textColor=colors.red)))
            story.append(Paragraph("Actions requises:", styles['CustomBody']))
            story.append(Paragraph("1. Réviser les parties problématiques du document", styles['CustomBody']))
            story.append(Paragraph("2. Citer correctement les sources utilisées", styles['CustomBody']))
            story.append(Paragraph("3. Reformuler les passages trop similaires", styles['CustomBody']))
            story.append(Paragraph("4. Soumettre à nouveau le document après corrections", styles['CustomBody']))
        
        # Génération du PDF
        doc.build(story)
        
        return rapport_path
    
    def ajouter_document_reference(self, chemin_fichier, titre):
        """
        Ajoute un document à la base de référence
        Args:
            chemin_fichier: Chemin du document de référence
            titre: Titre du document
        """
        texte = self.extraire_texte_fichier(chemin_fichier)
        if texte:
            self.reference_documents.append(texte)
            self.reference_titles.append(titre)
            return True
        return False