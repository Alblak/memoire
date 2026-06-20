"""
SERVICE DE CHATBOT D'ASSISTANCE POUR LES ÉTUDIANTS
Gère les réponses aux questions sur :
- Informations administratives
- Conseils méthodologiques
- Assistance à la rédaction
- Recherche documentaire
"""

from datetime import datetime
import os
import re
import unicodedata
from typing import Dict, List, Tuple

import requests

class ChatbotService:
    """Service intelligent de chatbot pour l'assistance étudiante"""
    
    def __init__(self):
        # Base de connaissances
        self.knowledge_base = self._initialize_knowledge_base()
        # Historique des conversations
        self.conversations = {}
        # Intelligence artificielle (OpenAI) facultative
        self.openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        self.ai_model = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')
        self.ai_enabled = bool(self.openai_api_key)
    
    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize('NFD', text)
        return ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn').lower()
    
    def _initialize_knowledge_base(self) -> Dict:
        """Initialise la base de connaissances du chatbot"""
        return {
            'administrative': {
                'keywords': ['seuil', 'plagiat', 'similarité', 'délai', 'soumission', 'date', 'deadline', 'administratif', 'calendrier', 'année académique', 'inscription', 'justificatif', 'diplôme', 'frais'],
                'responses': {
                    'seuil_plagiat': "Le seuil de similarité autorisé est de **20%**. Si votre travail dépasse ce seuil, vous devrez le réviser et le soumettre à nouveau.",
                    'dossier_administratif': "Vous devez fournir:\n- Attestation d'inscription\n- Accord du directeur\n- Relevé de notes\n- Pièce d'identité\n- Justificatif de paiement des frais",
                    'delai_soumission': "Les délais de soumission sont:\n- **Chapitres**: max 14 jours entre les soumissions\n- **Validation directeur**: 7 jours\n- **Soutenance**: max 90 jours après validation",
                    'contact_admin': "Pour toute question administrative, contactez:\n📧 admin@uaconline.edu.cd\n📞 +243 (autre numéro)\n🏢 Bureau Administration, niveau 2",
                }
            },
            'methodologique': {
                'keywords': ['structure', 'plan', 'introduction', 'conclusion', 'chapitre', 'méthodologie', 'résultats', 'analyse', 'organisation', 'approche', 'méthode'],
                'responses': {
                    'structure_memoire': """**Structure recommandée d'un mémoire:**

1. **Introduction** (5-10 pages)
   - Contexte et problématique
   - Questions de recherche
   - Objectifs
   - Pertinence de l'étude

2. **Revue de littérature** (15-20 pages)
   - État de l'art
   - Cadre théorique
   - Lacunes identifiées

3. **Méthodologie** (10-15 pages)
   - Approche de recherche
   - Population/Échantillon
   - Outils et techniques
   - Considérations éthiques

4. **Résultats/Analyse** (20-30 pages)
   - Présentation des données
   - Analyse détaillée
   - Interprétation

5. **Conclusion** (5-10 pages)
   - Synthèse des trouvailles
   - Implications
   - Limitations
   - Perspectives futures""",
                    
                    'definition_methodologie': """**Définition de la méthodologie :**

La méthodologie est la partie du mémoire qui décrit comment vous allez répondre à votre question de recherche.
Elle explique:
- le type d'étude choisi,
- les sources et l'échantillon,
- les outils et techniques de collecte,
- les méthodes d'analyse,
- les raisons de ces choix et les limites associés.

Son rôle est de montrer que votre démarche est rigoureuse, cohérente et adaptée à la problématique.""",
                    
                    'choix_methodologie': """**Quelle méthodologie choisir ?**

🔹 **Quantitative**
- Utilise des chiffres, des enquêtes, des scores, des tableaux.
- Utile pour mesurer des phénomènes, comparer des groupes ou tester des hypothèses.
- Exemple : questionnaire, statistiques, tests de corrélation.

🔹 **Qualitative**
- Utilise des entretiens, observations, analyses de discours.
- Utile pour comprendre des comportements, des opinions et des significations.
- Exemple : entretien semi-directif, étude de cas, analyse de contenu.

🔹 **Mixte**
- Combine les deux approches.
- Utile lorsque vous voulez à la fois mesurer et comprendre.
- Exemple : questionnaire + entretiens, données quantitatives et analyse de texte.

**Comment choisir ?**
1. Regardez votre problème de recherche.
2. Si vous devez mesurer des tendances, optez pour du quantitatif.
3. Si vous devez comprendre des trajectoires ou des perceptions, optez pour du qualitatif.
4. Si vous avez besoin des deux, choisissez une approche mixte.

✅ L’important est de justifier **pourquoi** cette méthode est la plus adaptée à votre sujet.""",
                    
                    'conseils_redaction': """**Conseils pour bien structurer votre écrit:**

✅ Un paragraphe = une idée principale
✅ Utilisez des transitions entre paragraphes
✅ Citez vos sources régulièrement
✅ Relisez votre texte plusieurs fois
✅ Demandez feedback à votre directeur""",
                }
            },
            'redaction': {
                'keywords': ['citation', 'référence', 'bibliographie', 'grammaire', 'orthographe', 'style', 'écriture', 'formule', 'expression', 'vocabulaire', 'plagiat', 'paraphrase'],
                'responses': {
                    'citation_apa': """**Format APA pour les citations:**

📚 Livre: Auteur, A. A. (2020). *Titre du livre*. Éditeur.

📰 Article: Auteur, A. A. (2020). Titre de l'article. *Titre du Journal*, 12(3), 45-67.

🌐 Site web: Auteur. (2020). Titre. Récupéré de http://www.exemple.com

Insérez des citations directes entre guillemets avec page!""",
                    
                    'eviter_plagiat': """**Comment éviter le plagiat:**

1. ✏️ **Paraphrase**: Reformulez avec vos mots
2. 📝 **Citations directes**: Utilisez guillemets + source
3. 🔍 **Vérification**: Utilisez l'outil anti-plagiat
4. 📚 **Attribution**: Toujours mentionner l'auteur original
5. 🎯 **Votre analyse**: Ajoutez votre critique/interprétation

**Formules utiles:**
- \"Selon [Auteur] (année)...\"
- \"La recherche indique que...\"
- \"En interprétant ces données...\" """,
                    
                    'grammaire_francaise': """**Erreurs courantes à éviter:**

❌ \"Le rapport qu'il a communiqué\" (mauvais accord)
✅ \"Les rapports qu'ils ont communiqués\" (bon accord)

❌ \"Données qui montre\" (sujet-verbe désaccord)
✅ \"Données qui montrent\" (accord correct)

❌ \"A cause de ce problème\" (3 mots)
✅ \"À cause de ce problème\" (accent grave)

💡 Utilisez un correcteur (Antidote, Reverso) et faites relire!""",
                }
            },
            'documentaire': {
                'keywords': ['source', 'article', 'journal', 'base de données', 'bibliothèque', 'recherche documentaire', 'document', 'ressource', 'book', 'publication'],
                'responses': {
                    'sources_academiques': """**Ressources pour rechercher des sources:**

🔗 **Accès libre:**
- Google Scholar (scholar.google.com)
- ResearchGate (researchgate.net)
- SSRN (ssrn.com)
- arXiv (arxiv.org)

🏫 **Via l'université (demander accès):**
- JSTOR
- ProQuest
- ScienceDirect
- Web of Science

📚 **Catalogues:**
- Opac UAC (bibliothèque)
- Worldcat (worldcat.org)""",
                    
                    'evaluer_source': """**Critères pour évaluer une source académique:**

✅ **CREDIBLE** = Évaluation par les pairs
✅ **ACTUELLE** = Publiée récemment (< 10 ans généralement)
✅ **PERTINENTE** = Liée à votre sujet
✅ **AUTORISÉE** = Auteur avec expertise
✅ **OBJECTIVE** = Pas de biais apparent

❌ Évitez les blogs, Wikipédia, sources anonymes""",
                    
                    'organiser_biblio': """**Comment organiser votre bibliographie:**

1. 📋 Collectez les sources progressivement
2. 🏷️ Utilisez Zotero ou Mendeley (gratuit!)
3. 📝 Notez: auteur, année, titre, éditeur, URL
4. 📊 Groupez par thème
5. 📄 Générez la liste au format APA

**Outils recommandés:**
- Zotero (open source)
- Mendeley (gratuit)
- BibTeX (pour LaTeX)""",
                }
            }
        }
    
    def get_category_keyword(self, message: str) -> Tuple[str, float]:
        """
        Détermine la catégorie du message basée sur les mots-clés
        Retourne (catégorie, confidence_score)
        """
        message_lower = self._normalize_text(message)
        scores = {}
        
        for category, data in self.knowledge_base.items():
            score = 0
            keywords = data.get('keywords', [])
            
            for keyword in keywords:
                keyword_norm = self._normalize_text(keyword)
                # Compte les occurrences du mot-clé
                if keyword_norm in message_lower:
                    score += 1
            
            if score > 0:
                scores[category] = score
        
        if not scores:
            return 'general', 0.3
        
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 5, 1.0)  # Normaliser
        
        return best_category, confidence
    
    def get_response(self, message: str, user_id: str = None) -> Dict:
        """
        Génère une réponse intelligente basée sur le message utilisateur
        """
        # Détecter la catégorie
        category, confidence = self.get_category_keyword(message)
        
        # Chercher la meilleure correspondance
        best_response = self._find_best_response(message, category)
        source = 'knowledge_base'
        
        # Si aucune bonne correspondance trouvée, on tente une réponse IA si possible
        if not best_response and self.ai_enabled:
            best_response = self._generate_ai_response(message, category)
            source = 'openai'
        
        # Si toujours aucune réponse, fallback classique
        if not best_response:
            best_response = self._get_fallback_response(message, category)
            if source == 'knowledge_base':
                source = 'fallback'
        
        response = {
            'text': best_response,
            'category': category,
            'confidence': confidence,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'suggestions': self._get_suggestions(category)
        }
        
        # Sauvegarder dans l'historique
        if user_id:
            self._save_conversation(user_id, message, best_response, category, source)
        
        return response
    
    def _find_best_response(self, message: str, category: str) -> str:
        """Trouve la meilleure réponse prédéfinie"""
        if category not in self.knowledge_base:
            return ''

        message_lower = self._normalize_text(message)
        responses = self.knowledge_base[category].get('responses', {})
        
        # Correspondance simple : chercher le mot-clé le plus spécifique
        keywords_to_response = {
            'seuil': 'seuil_plagiat',
            'plagiat': 'seuil_plagiat',
            'similarite': 'seuil_plagiat',
            'administratif': 'dossier_administratif',
            'dossier': 'dossier_administratif',
            'justificatif': 'dossier_administratif',
            'delai': 'delai_soumission',
            'soumission': 'delai_soumission',
            'deadline': 'delai_soumission',
            'structure': 'structure_memoire',
            'plan': 'structure_memoire',
            'chapitre': 'structure_memoire',
            'introduction': 'structure_memoire',
            'methodologie': 'choix_methodologie',
            'methodogie': 'choix_methodologie',
            'methodologique': 'choix_methodologie',
            'approche': 'choix_methodologie',
            'quantitative': 'choix_methodologie',
            'qualitative': 'choix_methodologie',
            'mixte': 'choix_methodologie',
            'outil': 'organiser_biblio',
            'outils': 'organiser_biblio',
            'citation': 'citation_apa',
            'apa': 'citation_apa',
            'reference': 'citation_apa',
            'eviter': 'eviter_plagiat',
            'paraphrase': 'eviter_plagiat',
            'formule': 'eviter_plagiat',
            'grammaire': 'grammaire_francaise',
            'orthographe': 'grammaire_francaise',
            'accord': 'grammaire_francaise',
            'source': 'sources_academiques',
            'article': 'sources_academiques',
            'base de donnees': 'sources_academiques',
            'evaluer': 'evaluer_source',
            'credibilite': 'evaluer_source',
            'pertinent': 'evaluer_source',
            'bibliographie': 'organiser_biblio',
            'zotero': 'organiser_biblio',
            'mendeley': 'organiser_biblio',
            'rediger': 'conseils_redaction',
        }
        
        # Vérifier d'abord les questions spécifiques
        if 'quelle méthodologie choisir' in message_lower or 'quelle methode choisir' in message_lower or 'méthodologie choisir' in message_lower or 'methode choisir' in message_lower:
            return responses.get('choix_methodologie', '')
        if 'c\'est quoi la méthodologie' in message_lower or 'qu\'est-ce que la méthodologie' in message_lower or 'definition de la méthodologie' in message_lower or 'c est quoi la méthodologie' in message_lower:
            return responses.get('definition_methodologie', '')

        for keyword, response_key in keywords_to_response.items():
            if keyword in message_lower:
                return responses.get(response_key, '')
        
        # Si pas trouvé
        return ''

    def _generate_ai_response(self, message: str, category: str) -> str:
        """Génère une réponse via l'API OpenAI si la clé est configurée."""
        if not self.ai_enabled:
            return ''

        system_prompt = (
            "Vous êtes un assistant pédagogique pour des étudiants de mémoire. "
            "Répondez en français de manière claire et structurée, en respectant la catégorie indiquée. "
            "Si la question porte sur la méthodologie, expliquez la définition ou le choix entre quantitative, qualitative et mixte selon le contexte."
        )

        try:
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': self.ai_model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': 300,
                'temperature': 0.7,
                'top_p': 0.9
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                print(f"Erreur OpenAI {response.status_code}: {response.text}")
                return ''
        except Exception as e:
            print(f"Erreur génération IA: {e}")
            return ''
    
    def _get_fallback_response(self, message: str, category: str) -> str:
        """Retourne une réponse par défaut générique"""
        fallbacks = {
            'administrative': "Je n'ai pas trouvé de réponse spécifique. Contactez admin@uaconline.edu.cd pour plus d'informations administratives.",
            'methodologique': "Pour des conseils méthodologiques plus détaillés, veuillez consulter votre directeur ou les guides disponibles dans le dossier 'Ressources'.",
            'redaction': "Pour des questions spécifiques d'écriture, consultez un correcteur (Antidote) ou demandez conseil à votre directeur.",
            'documentaire': "Consultez les ressources numériques de l'université ou contactez la bibliothèque pour une aide à la recherche documentaire.",
            'general': "Désolé, je n'ai pas bien compris votre question. Pouvez-vous reformuler ou choisir parmi les catégories proposées?"
        }
        
        return fallbacks.get(category, fallbacks['general'])
    
    def _get_suggestions(self, category: str) -> List[str]:
        """Retourne des suggestions de questions pour la catégorie"""
        suggestions_map = {
            'administrative': [
                "Quel est le seuil de plagiat?",
                "Quels sont les délais de soumission?",
                "Quels documents dois-je fournir?",
                "Comment contacter l'administration?"
            ],
            'methodologique': [
                "Comment structurer mon mémoire?",
                "Quelle méthodologie choisir?",
                "Comment organiser mes chapitres?",
                "Conseils de rédaction"
            ],
            'redaction': [
                "Comment citer une source (APA)?",
                "Comment éviter le plagiat?",
                "Erreurs de grammaire courantes",
                "Format de bibliographie"
            ],
            'documentaire': [
                "Où trouver des sources académiques?",
                "Comment évaluer une source?",
                "Comment organiser ma bibliographie?",
                "Quels outils utiliser?"
            ]
        }
        
        return suggestions_map.get(category, [
            "Avez-vous d'autres questions?",
            "Comment puis-je vous aider davantage?"
        ])
    
    def _save_conversation(self, user_id: str, message: str, response: str, category: str, source: str):
        """Enregistre la conversation pour améliorer le chatbot"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': response,
            'category': category,
            'source': source
        })
        
        # Garder les 50 derniers messages
        if len(self.conversations[user_id]) > 50:
            self.conversations[user_id] = self.conversations[user_id][-50:]
    
    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Retourne l'historique de conversation de l'utilisateur"""
        return self.conversations.get(user_id, [])


# Instance globale du service
chatbot_service = ChatbotService()
