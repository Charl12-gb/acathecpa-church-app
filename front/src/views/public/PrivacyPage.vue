<template>
  <LegalLayout title="Politique de confidentialité">
    <p>
      Cette page explique quelles données {{ org.legalName || org.name }} collecte sur la plateforme, pourquoi,
      combien de temps elles sont gardées et comment exercer vos droits.
    </p>

    <h2>1. Responsable du traitement</h2>
    <p>
      {{ org.legalName || org.name }}<template v-if="org.address">, {{ org.address }}</template>.
      Pour toute question sur vos données : {{ org.privacyEmail }}.
    </p>

    <h2>2. Données collectées</h2>
    <ul>
      <li><strong>Compte</strong> : nom, adresse email, mot de passe (enregistré chiffré, jamais lisible), et si vous les indiquez : téléphone, pays, date de naissance.</li>
      <li><strong>Parcours de formation</strong> : cours suivis, leçons terminées, réponses et résultats aux quiz, certificats obtenus.</li>
      <li><strong>Paiements</strong> : montant, formation ou contenu acheté, date, statut et référence de la transaction. Vos coordonnées bancaires ou Mobile Money sont traitées par le prestataire de paiement et ne sont pas conservées par {{ org.name }}.</li>
      <li><strong>Sessions en direct</strong> : heures d'arrivée et de départ, pour le suivi de présence par le formateur.</li>
      <li><strong>Formateurs</strong> : spécialité, biographie et compétences, affichées publiquement sur leurs cours.</li>
      <li><strong>Messages de contact</strong> : nom, email, sujet et message.</li>
      <li><strong>Sécurité</strong> : adresse IP lors des tentatives de connexion et d'envoi du formulaire de contact, pour limiter les abus.</li>
    </ul>

    <h2>3. Pourquoi ces données</h2>
    <ul>
      <li>Fournir le service : accès aux formations, suivi de progression, correction des quiz, délivrance des certificats.</li>
      <li>Gérer les paiements et en garder la trace comptable.</li>
      <li>Permettre au formateur de suivre ses étudiants (progression, résultats, présence aux sessions).</li>
      <li>Vous écrire : confirmation de compte, réinitialisation du mot de passe, sessions en direct programmées, réponses à vos messages.</li>
      <li>Protéger la plateforme contre la fraude et les attaques.</li>
    </ul>

    <h2>4. Qui peut voir vos données</h2>
    <ul>
      <li><strong>Vos formateurs</strong> voient votre nom, votre email, votre progression et vos résultats dans leurs cours.</li>
      <li><strong>L'équipe d'administration</strong> accède aux comptes pour la gestion de la plateforme ; ses actions sensibles sont journalisées.</li>
      <li><strong>Le public</strong> peut vérifier un certificat à partir de son code (nom du titulaire, formation, date).</li>
      <li><strong>L'annuaire Alumni</strong> affiche le nom, le pays et les formations certifiées des anciens étudiants. Vous pouvez vous en retirer à tout moment depuis votre profil (« Afficher mon profil dans l'annuaire des Alumni »).</li>
      <li><strong>Prestataires techniques</strong> : hébergement, envoi d'emails, paiement, visioconférence. Ils n'utilisent vos données que pour rendre ce service.</li>
    </ul>
    <p>Vos données ne sont ni vendues ni utilisées à des fins publicitaires.</p>

    <h2>5. Durée de conservation</h2>
    <ul>
      <li>Compte et parcours : tant que le compte est ouvert, puis supprimés à sa fermeture définitive.</li>
      <li>Certificats : conservés tant que la vérification publique doit rester possible, sauf demande de suppression.</li>
      <li>Paiements : pendant la durée imposée par les obligations comptables et fiscales.</li>
      <li>Messages de contact : un an après le dernier échange.</li>
      <li>Données de sécurité (tentatives de connexion) : quelques heures au plus.</li>
    </ul>

    <h2>6. Vos droits</h2>
    <p>
      Vous pouvez accéder à vos données, les corriger (la plupart depuis votre profil), demander leur suppression,
      vous opposer à un traitement ou en demander une copie. Écrivez à {{ org.privacyEmail }} ; une réponse vous est
      apportée dans un délai d'un mois. Vous pouvez aussi saisir l'autorité de protection des données personnelles de votre pays.
    </p>

    <h2>7. Stockage dans votre navigateur</h2>
    <p>
      La plateforme garde dans votre navigateur le jeton de connexion et votre profil, pour vous éviter de vous reconnecter
      à chaque visite. Elle n'utilise pas de cookies publicitaires ni de mesure d'audience tierce. Se déconnecter efface ces informations.
    </p>

    <h2>8. Sécurité</h2>
    <p>
      Mots de passe chiffrés, accès limité selon les rôles, nombre de tentatives de connexion limité, journal des actions
      d'administration. Aucun système n'étant infaillible, signalez-nous toute anomalie.
    </p>

    <h2>9. Évolution de cette politique</h2>
    <p>La date de mise à jour figure en haut de la page. En cas de changement important, vous êtes prévenu par email.</p>
  </LegalLayout>
</template>

<script setup lang="ts">
import LegalLayout from '../../components/LegalLayout.vue';
import { ORGANISATION as org } from '../../config';
</script>
