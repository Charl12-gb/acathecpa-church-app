<template>
  <LegalLayout title="Conditions générales d'utilisation">
    <p>
      Les présentes conditions encadrent l'utilisation de la plateforme {{ org.name }}, ses formations en ligne,
      ses articles, ses podcasts et ses sessions en direct. En créant un compte, vous les acceptez.
    </p>

    <h2>1. Éditeur de la plateforme</h2>
    <p>
      La plateforme est éditée par {{ org.legalName || org.name }}<template v-if="org.registration">, {{ org.registration }}</template><template v-if="org.address">, {{ org.address }}</template>.
      Contact : {{ org.email }}<template v-if="org.phone">, {{ org.phone }}</template>.
      <template v-if="org.host"> Hébergement : {{ org.host }}.</template>
    </p>

    <h2>2. Compte utilisateur</h2>
    <ul>
      <li>L'inscription est ouverte à toute personne qui fournit des informations exactes. Une adresse email valide est nécessaire ; un lien de confirmation y est envoyé.</li>
      <li>Vous êtes responsable de la confidentialité de votre mot de passe et des actions faites depuis votre compte. Signalez sans délai tout usage frauduleux.</li>
      <li>Les comptes formateurs et administrateurs sont créés par l'équipe de {{ org.name }}.</li>
      <li>Vous pouvez demander la fermeture de votre compte à tout moment (voir la politique de confidentialité).</li>
    </ul>

    <h2>3. Formations et contenus</h2>
    <ul>
      <li>Une formation gratuite est accessible dès l'inscription au cours. Une formation ou un contenu premium payant est accessible une fois le paiement confirmé.</li>
      <li>Les prix sont indiqués en francs CFA (XOF), toutes taxes comprises le cas échéant.</li>
      <li>L'accès à une formation achetée reste ouvert tant que la formation existe sur la plateforme, même si elle est retirée du catalogue.</li>
      <li>Les contenus (textes, vidéos, quiz, supports) sont protégés par le droit d'auteur. Ils sont réservés à votre usage personnel : leur copie, revente ou diffusion est interdite.</li>
    </ul>

    <h2>4. Évaluations et certificats</h2>
    <ul>
      <li>Les quiz sont corrigés automatiquement ; leur nombre de tentatives peut être limité par le formateur.</li>
      <li>Un certificat est délivré lorsque toutes les leçons sont terminées, les quiz réussis et, le cas échéant, le nombre de points requis atteint.</li>
      <li>Chaque certificat porte un code de vérification. Toute personne disposant de ce code peut vérifier son authenticité sur la plateforme (nom du titulaire, formation, date).</li>
      <li>Un certificat obtenu par fraude peut être retiré.</li>
    </ul>

    <h2>5. Sessions en direct</h2>
    <p>
      Les sessions en direct sont réservées aux personnes inscrites au cours concerné. Elles se déroulent sur un service
      de visioconférence tiers. Un comportement respectueux est attendu ; l'enregistrement par les participants est interdit sans accord du formateur.
    </p>

    <h2>6. Règles de conduite</h2>
    <p>Il est interdit d'utiliser la plateforme pour :</p>
    <ul>
      <li>partager son compte ou tenter d'accéder au compte d'un autre utilisateur ;</li>
      <li>contourner les mesures d'accès aux contenus payants ou aux évaluations ;</li>
      <li>publier ou transmettre des propos illicites, injurieux ou discriminatoires.</li>
    </ul>
    <p>En cas de manquement, {{ org.name }} peut suspendre ou fermer le compte concerné.</p>

    <h2>7. Responsabilité</h2>
    <p>
      {{ org.name }} veille au bon fonctionnement de la plateforme mais ne peut garantir une disponibilité continue.
      Les formations ont une visée pédagogique et ne remplacent pas un conseil professionnel personnalisé.
    </p>

    <h2>8. Données personnelles</h2>
    <p>
      Le traitement de vos données est décrit dans la
      <RouterLink to="/confidentialite">politique de confidentialité</RouterLink>.
    </p>

    <h2>9. Modification des conditions</h2>
    <p>
      Ces conditions peuvent évoluer. La date de mise à jour figure en haut de cette page ; en cas de changement important,
      les utilisateurs sont prévenus par email.
    </p>

    <h2>10. Contact</h2>
    <p>Pour toute question : {{ org.email }}<template v-if="org.phone"> ou {{ org.phone }}</template>, ou via le <RouterLink to="/contact">formulaire de contact</RouterLink>.</p>
  </LegalLayout>
</template>

<script setup lang="ts">
import LegalLayout from '../../components/LegalLayout.vue';
import { ORGANISATION as org } from '../../config';
</script>
