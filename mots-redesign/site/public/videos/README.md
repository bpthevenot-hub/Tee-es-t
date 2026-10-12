# Vidéo du portail d'introduction

Déposer ici le fichier **`intro-medecins.mp4`** : il sera automatiquement lu en
fond du portail d'introduction (composant `components/IntroPortail.tsx`).
Sans fichier, le portail affiche sa scène animée intégrée — le site
fonctionne donc dès maintenant.

## Spécifications recommandées

- MP4 (H.264 + AAC), **1920×1080**, 10 à 25 secondes, pensé pour la boucle.
- **Muet** (le lecteur force `muted` — indispensable à l'autoplay).
- Poids cible **≤ 8 Mo** (compresser : `ffmpeg -i source.mp4 -vf scale=1920:-2 -c:v libx264 -crf 28 -an intro-medecins.mp4`).
- Image plutôt **sombre / désaturée** : le texte blanc se superpose (le
  lecteur applique déjà une opacité de 40 % + un voile marine).

## Contenu — à l'image des médecins français

Ambiance suggérée : mains de soignants, couloirs d'hôpital au petit matin,
cabinet de médecine générale, blouse enfilée, regard fatigué puis apaisé —
sobre et digne, jamais misérabiliste.

⚠️ **Droits obligatoires** : uniquement une vidéo dont l'association (ou toi)
détient les droits — génération IA maison (CLI `grok-video` sur le Mac),
tournage original, ou banque d'images sous licence. Pas d'extraits de
reportages, de JT ou de contenus tiers sans licence.

Une fois le fichier déposé : commit + push → Vercel redéploie, le portail
bascule automatiquement de la scène animée à la vidéo.
