/* Service worker du carnet de projets.
 *
 * Rôle : garder une copie locale de l'application pour qu'elle démarre sans
 * réseau (utile pour la liste de courses dans un magasin mal couvert).
 *
 * Important : les échanges avec Firestore ne sont JAMAIS mis en cache ici.
 * C'est Firestore lui-même qui gère les données hors ligne, avec sa propre
 * base locale, et qui renvoie les modifications au serveur au retour du réseau.
 *
 * Pour forcer la mise à jour de tous les appareils après un changement,
 * il suffit d'incrémenter VERSION ci-dessous.
 */
const VERSION = 'v2';
const CACHE = 'carnet-' + VERSION;

const A_PRECHARGER = [
  './',
  './index.html',
  './firebase-config.js',
  './manifest.json',
  './icones/icon-192.png',
  './icones/icon-512.png',
  './icones/apple-touch-icon.png',
  './icones/favicon-32.png'
];

// Domaines dont les réponses ne doivent jamais être servies depuis le cache
const TOUJOURS_RESEAU = [
  'firestore.googleapis.com',
  'firebaseinstallations.googleapis.com',
  'firebaseremoteconfig.googleapis.com',
  'identitytoolkit.googleapis.com'
];

// Ressources externes utiles hors ligne (SDK Firebase, polices)
const EXTERNES_CACHABLES = [
  'www.gstatic.com',
  'fonts.googleapis.com',
  'fonts.gstatic.com'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // Volontairement fichier par fichier : cache.addAll() est atomique, donc un
    // seul fichier manquant (une icône renommée, par exemple) ferait échouer tout
    // le préchargement et l'application ne démarrerait plus hors ligne.
    await Promise.all(A_PRECHARGER.map(async u => {
      try{
        await cache.add(new Request(u, { cache: 'reload' }));
      }catch(err){
        console.warn('Fichier non préchargé :', u, err);
      }
    }));
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const noms = await caches.keys();
    await Promise.all(noms.filter(n => n !== CACHE).map(n => caches.delete(n)));
    await self.clients.claim();
  })());
});

// L'application demande l'activation immédiate quand l'utilisateur accepte la mise à jour
self.addEventListener('message', e => {
  if (e.data === 'ACTIVER_MAINTENANT') self.skipWaiting();
});

async function reseauPuisCache(req) {
  const cache = await caches.open(CACHE);
  try {
    const rep = await fetch(req);
    if (rep && rep.ok) cache.put(req, rep.clone());
    return rep;
  } catch (err) {
    const enCache = await cache.match(req) || await cache.match('./index.html');
    if (enCache) return enCache;
    throw err;
  }
}

async function cachePuisReseau(req) {
  const cache = await caches.open(CACHE);
  const enCache = await cache.match(req);
  // On rafraîchit en arrière-plan sans bloquer l'affichage
  const maj = fetch(req).then(rep => {
    if (rep && (rep.ok || rep.type === 'opaque')) cache.put(req, rep.clone());
    return rep;
  }).catch(() => null);
  return enCache || maj.then(r => r || Promise.reject(new Error('indisponible')));
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (TOUJOURS_RESEAU.some(h => url.hostname.includes(h))) return;   // laissé à Firestore

  // Navigation : on privilégie le réseau pour récupérer les nouveautés,
  // avec repli sur la copie locale si on est hors ligne.
  if (req.mode === 'navigate') { e.respondWith(reseauPuisCache(req)); return; }

  if (url.origin === self.location.origin || EXTERNES_CACHABLES.some(h => url.hostname === h)) {
    e.respondWith(cachePuisReseau(req));
  }
});
