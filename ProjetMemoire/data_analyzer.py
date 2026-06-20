# data_analyzer.py - Version ultra complète
"""
Analyseur de données pour statistiques avancées avec visualisations
"""

import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import statistics
import math

class DataAnalyzer:
    """Classe pour l'analyse avancée des données du système"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300
    
    def _is_cache_valid(self, key):
        if key not in self.cache:
            return False
        return (datetime.now() - self.cache[key]['timestamp']).seconds < self.cache_duration
    
    def _get_cached(self, key):
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _set_cache(self, key, data):
        self.cache[key] = {'data': data, 'timestamp': datetime.now()}
    
    def analyze(self, data, analysis_type='general'):
        """
        Point d'entrée principal pour l'analyse
        Args:
            data: Données à analyser (dict ou list)
            analysis_type: Type d'analyse ('general', 'etudiant', 'directeur', 'plagiat')
        Returns:
            Dict contenant les résultats de l'analyse
        """
        cache_key = f"{analysis_type}_{hash(str(data))}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if analysis_type == 'general':
            result = self._analyze_general(data)
        elif analysis_type == 'etudiant':
            result = self._analyze_etudiant(data)
        elif analysis_type == 'directeur':
            result = self._analyze_directeur(data)
        elif analysis_type == 'plagiat':
            result = self._analyze_plagiat(data)
        else:
            result = self._analyze_custom(data, analysis_type)
        
        self._set_cache(cache_key, result)
        return result
    
    def _analyze_general(self, data):
        """Analyse générale du système"""
        sujets = data.get('sujets', [])
        utilisateurs = data.get('utilisateurs', [])
        versions = data.get('versions', [])
        
        # Distribution par statut
        statut_counts = Counter(s.get('statut', 'inconnu') for s in sujets)
        
        # Distribution par domaine
        domaine_counts = Counter(s.get('domaine_id') for s in sujets if s.get('domaine_id'))
        
        # Calcul des délais moyens
        delais = []
        for s in sujets:
            if s.get('date_soumission') and s.get('date_finalisation'):
                delai = (s['date_finalisation'] - s['date_soumission']).days
                delais.append(delai)
        
        delai_moyen = statistics.mean(delais) if delais else 0
        
        return {
            'total_sujets': len(sujets),
            'total_etudiants': len([u for u in utilisateurs if u.get('role_id') == 1]),
            'total_directeurs': len([u for u in utilisateurs if u.get('role_id') == 2]),
            'total_versions': len(versions),
            'statut_repartition': dict(statut_counts),
            'domaine_repartition': dict(domaine_counts),
            'delai_moyen_finalisation': round(delai_moyen, 1),
            'taux_completion_global': self._calculate_global_completion_rate(sujets),
            'sujets_par_mois': self._group_by_month(sujets, 'date_soumission')
        }
    
    def _analyze_etudiant(self, data):
        """Analyse spécifique pour un étudiant"""
        etudiant_id = data.get('etudiant_id')
        sujets = data.get('sujets', [])
        versions = data.get('versions', [])
        feedbacks = data.get('feedbacks', [])
        
        sujets_etudiant = [s for s in sujets if s.get('etudiant_id') == etudiant_id]
        versions_etudiant = [v for v in versions if v.get('sujet_id') in [s['id'] for s in sujets_etudiant]]
        
        if not sujets_etudiant:
            return {'error': 'Aucun sujet trouvé pour cet étudiant'}
        
        return {
            'total_sujets': len(sujets_etudiant),
            'total_versions': len(versions_etudiant),
            'versions_validees': len([v for v in versions_etudiant if v.get('statut') == 'valide']),
            'taux_reussite': self._calculate_success_rate(sujets_etudiant),
            'progression_par_sujet': self._calculate_progression_by_subject(sujets_etudiant, versions_etudiant),
            'temps_moyen_correction': self._calculate_avg_correction_time(feedbacks, etudiant_id),
            'derniere_activite': self._get_last_activity(versions_etudiant),
            'performance_over_time': self._group_by_month(versions_etudiant, 'date_soumission')
        }
    
    def _analyze_directeur(self, data):
        """Analyse spécifique pour un directeur"""
        directeur_id = data.get('directeur_id')
        sujets = data.get('sujets', [])
        versions = data.get('versions', [])
        feedbacks = data.get('feedbacks', [])
        
        sujets_directeur = [s for s in sujets if s.get('directeur_id') == directeur_id]
        versions_directeur = [v for v in versions if v.get('sujet_id') in [s['id'] for s in sujets_directeur]]
        feedbacks_directeur = [f for f in feedbacks if f.get('destinataire_id') == directeur_id]
        
        # Calcul du temps de réponse moyen
        temps_reponse = []
        for f in feedbacks_directeur:
            if f.get('date_envoi') and f.get('date_lecture'):
                delta = (f['date_lecture'] - f['date_envoi']).total_seconds() / 3600
                temps_reponse.append(delta)
        
        return {
            'total_encadres': len(sujets_directeur),
            'finalises': len([s for s in sujets_directeur if s.get('statut') == 'finalise']),
            'en_cours': len([s for s in sujets_directeur if s.get('statut') == 'en_cours']),
            'versions_en_attente': len([v for v in versions_directeur if v.get('statut') == 'soumis']),
            'temps_reponse_moyen': round(statistics.mean(temps_reponse), 1) if temps_reponse else 0,
            'charge_travail': len([s for s in sujets_directeur if s.get('statut') in ['approuve', 'en_cours']]),
            'performance_par_etudiant': self._calculate_student_performance(sujets_directeur, versions_directeur),
            'evolution_mensuelle': self._group_by_month(sujets_directeur, 'date_attribution')
        }
    
    def _analyze_plagiat(self, data):
        """Analyse des tendances de plagiat"""
        versions = data.get('versions', [])
        versions_avec_score = [v for v in versions if v.get('taux_similarite', 0) > 0]
        
        if not versions_avec_score:
            return {'taux_moyen': 0, 'conformes': 0, 'non_conformes': 0}
        
        scores = [v['taux_similarite'] for v in versions_avec_score]
        seuil = data.get('seuil', 20)
        
        return {
            'taux_moyen': round(statistics.mean(scores), 2),
            'taux_median': round(statistics.median(scores), 2),
            'taux_max': round(max(scores), 2),
            'taux_min': round(min(scores), 2),
            'conformes': len([s for s in scores if s <= seuil]),
            'non_conformes': len([s for s in scores if s > seuil]),
            'taux_conformite': round((len([s for s in scores if s <= seuil]) / len(scores) * 100), 2),
            'distribution': self._calculate_distribution(scores, [0, 10, 20, 30, 40, 50, 100]),
            'evolution': self._group_by_month(versions_avec_score, 'date_verification')
        }
    
    def _calculate_global_completion_rate(self, sujets):
        """Calcule le taux de complétion global"""
        total = len(sujets)
        finalises = len([s for s in sujets if s.get('statut') == 'finalise'])
        return round((finalises / total * 100), 2) if total > 0 else 0
    
    def _calculate_success_rate(self, sujets):
        """Calcule le taux de succès d'un étudiant"""
        total = len(sujets)
        valides = len([s for s in sujets if s.get('statut') == 'finalise'])
        return round((valides / total * 100), 2) if total > 0 else 0
    
    def _calculate_progression_by_subject(self, sujets, versions):
        """Calcule la progression par sujet"""
        progression = []
        for sujet in sujets:
            versions_sujet = [v for v in versions if v.get('sujet_id') == sujet['id']]
            total_versions = len(versions_sujet)
            validees = len([v for v in versions_sujet if v.get('statut') == 'valide'])
            progression.append({
                'sujet_id': sujet['id'],
                'titre': sujet['titre'][:50] + '...' if len(sujet.get('titre', '')) > 50 else sujet.get('titre', ''),
                'avancement': round((validees / max(total_versions, 1) * 100), 2),
                'total_versions': total_versions,
                'validees': validees
            })
        return progression
    
    def _calculate_avg_correction_time(self, feedbacks, etudiant_id):
        """Calcule le temps moyen de correction"""
        temps = []
        for f in feedbacks:
            if f.get('emetteur_id') == etudiant_id and f.get('date_envoi') and f.get('date_lecture'):
                delta = (f['date_lecture'] - f['date_envoi']).total_seconds() / 3600
                temps.append(delta)
        return round(statistics.mean(temps), 1) if temps else 0
    
    def _get_last_activity(self, versions):
        """Récupère la date de dernière activité"""
        if not versions:
            return None
        dernieres_dates = [v.get('date_soumission') for v in versions if v.get('date_soumission')]
        if not dernieres_dates:
            return None
        return max(dernieres_dates).strftime('%d/%m/%Y')
    
    def _calculate_student_performance(self, sujets, versions):
        """Calcule la performance par étudiant pour un directeur"""
        performance = []
        etudiants_ids = set(s.get('etudiant_id') for s in sujets if s.get('etudiant_id'))
        
        for etudiant_id in etudiants_ids:
            sujets_etudiant = [s for s in sujets if s.get('etudiant_id') == etudiant_id]
            versions_etudiant = [v for v in versions if v.get('sujet_id') in [s['id'] for s in sujets_etudiant]]
            
            performance.append({
                'etudiant_id': etudiant_id,
                'total_sujets': len(sujets_etudiant),
                'versions_soumises': len(versions_etudiant),
                'taux_avancement': self._calculate_success_rate(sujets_etudiant)
            })
        
        return performance
    
    def _group_by_month(self, items, date_field):
        """Groupe des éléments par mois"""
        grouped = defaultdict(int)
        for item in items:
            date = item.get(date_field)
            if date:
                mois = date.strftime('%Y-%m')
                grouped[mois] += 1
        return dict(sorted(grouped.items()))
    
    def _calculate_distribution(self, values, bins):
        """Calcule la distribution des valeurs dans des intervalles"""
        distribution = []
        for i in range(len(bins) - 1):
            count = len([v for v in values if bins[i] <= v < bins[i+1]])
            distribution.append({
                'min': bins[i],
                'max': bins[i+1],
                'count': count,
                'percentage': round((count / len(values) * 100), 2) if values else 0
            })
        return distribution
    
    def _analyze_custom(self, data, analysis_type):
        """Analyse personnalisée selon le type"""
        # À implémenter selon les besoins spécifiques
        return {'type': analysis_type, 'result': 'Analyse personnalisée à implémenter'}