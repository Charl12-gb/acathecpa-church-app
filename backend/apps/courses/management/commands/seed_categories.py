"""
Seed the initial list of course categories.

Mirrors the historical list that used to live in the front-end
(`front/src/services/utils.ts`). After this runs, the database becomes the
source of truth and categories are managed from the admin UI.

Usage::

    python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.courses.models import Category

CATEGORIES = [
    # Catégories spécifiques aux serviteurs de Dieu
    "Développement Personnel",
    "Leadership Chrétien",
    "Théologie & Doctrine",
    "Exégèse & Herméneutique",
    "Homilétique & Prédication",
    "Pastorale & Conseil",
    "Mission & Évangélisation",
    "Adoration & Louange",
    "Gestion du Ministère",
    "Finances & Dîme",
    "Droit Canonique & Éthique",
    "Histoire de l'Église",
    "Apologétique",
    "Relations Interpersonnelles",
    "Communication & Médias",
    "Compétences Numériques",
    "Santé Mentale & Bien-être",
    "Action Sociale & Diaconie",
    "Famille & Mariage",
    "Ministère des Enfants & Jeunesse",
    "Discipolat",
    "Langues Bibliques",
    "Liturgie & Célébration",
    "Gestion de Projet (Ministériel)",
    "Innovation & Vision",
    "Planification Stratégique pour l'Église",
    "Gestion des Conflits",
    "Encouragement & Motivation",
    "Discipline Ecclésiastique",
    "Intercession & Prière",
    "Prophétie & Discernement Spirituel",
    "Conduite de Petits Groupes",
    "Fondements de la Foi",
    "Théologie Systématique",
    "Théologie Pratique",
    "Missiologie Contextuelle",
    "Leadership Serviteur",
    "Gestion du Temps & Productivité",
    "Mentorat & Coaching Spirituel",
    "Organisation d'Événements (Chrétiens)",
    "Sécurité & Protection (Église/Communauté)",
    "Art & Créativité dans le Culte",
    "Interprétation des Songes & Visions",
    "Libération & Guérison",
    "Rédaction de Sermons & Études Bibliques",
    "Gestion de Crise (Pastorale)",
    "Implémentation de Programmes Communautaires",
    "Cultiver une Vie de Sainteté",
    "Ministère auprès des Personnes Âgées",
    "Accompagnement du Deuil",
    "Stratégies de Croissance de l'Église",
    "Impact Social Chrétien",
    "Théologie de la Prospérité (Analyse Critique)",
    "Gouvernance d'Église",
    # Catégories plus générales
    "Développement Logiciel",
    "Science des Données",
    "Intelligence Artificielle",
    "Cybersécurité",
    "Marketing Digital",
    "Vente & Négociation",
    "Gestion de Projet (Général)",
    "Ressources Humaines",
    "Comptabilité & Fiscalité",
    "Entrepreneuriat",
    "Design Graphique",
    "Montage Vidéo",
    "Photographie",
    "Musique",
    "Écriture & Rédaction",
    "Langues Étrangères",
    "Bien-être & Sport",
    "Cuisine & Gastronomie",
    "Artisanat & Bricolage",
    "Éducation & Pédagogie",
    "Environnement & Durabilité",
    "Droit & Législation (Général)",
    "Recherche Scientifique",
    "Relations Publiques",
    "Logistique & Chaîne d'Approvisionnement",
    "Service Client",
    "Développement Durable",
    "Innovation & Créativité",
    "Finances Personnelles",
    "Investissement",
    "Immobilier",
    "Commerce International",
    "Psychologie",
    "Sociologie",
    "Histoire Générale",
    "Philosophie",
    "Technologie Blockchain",
    "Robotique",
    "Impression 3D",
    "Réalité Virtuelle & Augmentée",
    "Développement Mobile",
    "Sécurité au Travail",
    "Gestion de Qualité",
    "Audit",
    "Branding Personnel",
    "Rédaction de Contenu",
    "SEO & SEM",
    "Publicité en Ligne",
    "Analytique Web",
    "Gestion de Communauté",
    "Création de Podcasts",
    "Animation",
    "Développement de Jeux Vidéo",
    "Maintenance Informatique",
    "Réseaux Informatiques",
    "Cloud Computing",
    "Big Data",
    "Ethique des Affaires",
    "Planification Urbaine",
    "Agriculture & Agroalimentaire",
    "Tourisme & Hôtellerie",
    "Mode & Textile",
    "Journalisme",
    "Traduction & Interprétation",
]


class Command(BaseCommand):
    help = "Seed the initial list of course categories."

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        for name in CATEGORIES:
            _, was_created = Category.objects.get_or_create(name=name)
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding done. Categories created: {created} | "
                f"total in DB: {Category.objects.count()}"
            )
        )
