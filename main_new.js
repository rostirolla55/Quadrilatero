// ===========================================
// CONFIGURAZIONE E COSTANTI GLOBALI
// ===========================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
import { getDatabase, ref, set } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-database.js";

const APP_VERSION = '1.3.0 - Nuova versione dei menu e della geolocalizzazione';
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'Quadrilatero_lastLang';
let currentLang = 'it';
console.log(`Version : ${APP_VERSION}`);

window.navTitles = {};
window.allData = {};

// Elementi DOM Globali
let nearbyPoiButton;
let nearbyMenuPlaceholder;

// Configurazione Firebase
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {
    apiKey: "AIzaSyBDl1XOHCkARszY5g2A_j4XamL38qsmqOY",
    authDomain: "sito-turistico-quadrilatero.firebaseapp.com",
    databaseURL: "https://sito-turistico-quadrilatero-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "sito-turistico-quadrilatero",
    storageBucket: "sito-turistico-quadrilatero.firebasestorage.app",
    messagingSenderId: "217504750698",
    appId: "1:217504750698:web:e02c49cb43d57f2a307e13"
};

let db, auth, rtdb, currentUserId = null, isAuthReady = false;

const navLinksData = [
    { id: 'navHome', key: 'navHome', base: 'index', poiId: 'home', ordine_cammino: 0 },
    { id: 'navManifattura', key: 'navManifattura', base: 'manifattura', poiId: 'manifattura', ordine_cammino: 502 },
    { id: 'navPittoricarracci', key: 'navPittoricarracci', base: 'pittoricarracci', poiId: 'pittoricarracci', ordine_cammino: 601 },
    { id: 'navCavaticcio', key: 'navCavaticcio', base: 'cavaticcio', poiId: 'cavaticcio', ordine_cammino: 503 },
    { id: 'navBsmariamaggiore', key: 'navBsmariamaggiore', base: 'bsmariamaggiore', poiId: 'bsmariamaggiore', ordine_cammino: 801 },
    { id: 'navGraziaxx', key: 'navGraziaxx', base: 'graziaxx', poiId: 'graziaxx', ordine_cammino: 901 },
    { id: 'navPugliole', key: 'navPugliole', base: 'pugliole', poiId: 'pugliole', ordine_cammino: 902 },
    { id: 'navCarracci', key: 'navCarracci', base: 'carracci', poiId: 'carracci', ordine_cammino: 504 },
    { id: 'navIntervista_ludovico', key: 'navIntervista_ludovico', base: 'intervista_ludovico', poiId: 'intervista_ludovico', ordine_cammino: 602 },
    { id: 'navLastre', key: 'navLastre', base: 'lastre', poiId: 'lastre', ordine_cammino: 903 },
    { id: 'navChiesasbene', key: 'navChiesasbene', base: 'chiesasbene', poiId: 'chiesasbene', ordine_cammino: 802 },
    { id: 'navSantuariopioggia', key: 'navSantuariopioggia', base: 'santuariopioggia', poiId: 'santuariopioggia', ordine_cammino: 803 },
    { id: 'navEdicola_votiva', key: 'navEdicola_votiva', base: 'edicola_votiva', poiId: 'edicola_votiva', ordine_cammino: 904 },
    { id: 'navPioggia1', key: 'navPioggia1', base: 'pioggia1', poiId: 'pioggia1', ordine_cammino: 603 },
    { id: 'navPioggia2', key: 'navPioggia2', base: 'pioggia2', poiId: 'pioggia2', ordine_cammino: 701 },
    { id: 'navPioggia3', key: 'navPioggia3', base: 'pioggia3', poiId: 'pioggia3', ordine_cammino: 604 },
    { id: 'navChiesasancarlo', key: 'navChiesasancarlo', base: 'chiesasancarlo', poiId: 'chiesasancarlo', ordine_cammino: 804 },
    { id: 'navPsontuoso', key: 'navPsontuoso', base: 'psontuoso', poiId: 'psontuoso', ordine_cammino: 1 },
    { id: 'navArco170_madonna_grassa', key: 'navArco170_madonna_grassa', base: 'arco170_madonna_grassa', poiId: 'arco170_madonna_grassa', ordine_cammino: 170 },
    { id: 'navArco3_fornasari', key: 'navArco3_fornasari', base: 'arco3_fornasari', poiId: 'arco3_fornasari', ordine_cammino: 3 },
    { id: 'navStabilevandini', key: 'navStabilevandini', base: 'stabile_legno_vandini', poiId: 'stabile_legno_vandini', ordine_cammino: 501 }
];

// ===========================================
// CONFIGURAZIONE TITOLI CATEGORIE MULTILINGUA
// ===========================================
const CATEGORIE_TITOLI = {
    'chiesa':    { it: '⛪ Chiese & Luoghi di Culto', en: '⛪ Churches & Places of Worship', es: '⛪ Iglesias y Culto', fr: '⛪ Églises et Lieux de Culte' },
    'edificio':  { it: '🏛️ Architettura & Palazzi', en: '🏛️ Architecture & Buildings', es: '🏛️ Arquitectura y Edificios', fr: '🏛️ Architecture et Bâtiments' },
    'portici':   { it: '🏛️ Portici & Archi Storici', en: '🏛️ Porticoes & Historic Arches', es: '🏛️ Pórticos y Arcos Históricos', fr: '🏛️ Portiques et Arches Historiques' },
    'mpatind':   { it: '🏭 Museo Patrimonio Industriale', en: '🏭 Museum of Industrial Heritage', es: '🏭 Museo del Patrimonio Industrial', fr: '🏭 Musée du Patrimoine Industriel' },
    'itinerari': { it: '🥾 Itinerari & Percorsi', en: '🥾 Routes & Walking Tours', es: '🥾 Itinerarios y Rutas', fr: '🥾 Itinéraires et Parcours' },
    'arte':      { it: '🎨 Opere d’Arte & Quadri', en: '🎨 Artworks & Paintings', es: '🎨 Obras de Arte', fr: '🎨 Œuvres d’Art' },
    'statua':    { it: '🗿 Sculture e Monumenti', en: '🗿 Sculptures & Monuments', es: '🗿 Esculturas y Monumentos', fr: '🗿 Sculptures et Monuments' },
    'esterno':   { it: '🌳 Esterni e Luoghi', en: '🌳 Outdoors & Places', es: '🌳 Exteriores y Lugares', fr: '🌳 Extérieurs et Lieux' },
    'altro':     { it: '📍 Altri Punti di Interesse', en: '📍 Other Points of Interest', es: '📍 Otros Puntos de Interés', fr: '📍 Autres Points d’Intérêt' }
};

// ===========================================
// DATI: POI GPS
// ===========================================
const POIS_LOCATIONS = [
    { id: 'manifattura', lat: 44.4989321, lon: 11.336618, distanceThreshold: 50, categoria: 'edificio', ordine_cammino: 502 },
    { id: 'pittoricarracci', lat: 44.49909, lon: 11.340316, distanceThreshold: 50, categoria: 'arte', ordine_cammino: 601 },
    { id: 'cavaticcio', lat: 44.500207, lon: 11.338076, distanceThreshold: 50, categoria: 'edificio', ordine_cammino: 503 },
    { id: 'bsmariamaggiore', lat: 44.498118, lon: 11.341923, distanceThreshold: 50, categoria: 'chiesa', ordine_cammino: 801 },
    { id: 'graziaxx', lat: 44.500594, lon: 11.340758, distanceThreshold: 50, categoria: 'esterno', ordine_cammino: 901 },
    { id: 'pugliole', lat: 44.500071, lon: 11.339805, distanceThreshold: 50, categoria: 'esterno', ordine_cammino: 902 },
    { id: 'carracci', lat: 44.499912, lon: 11.34041, distanceThreshold: 50, categoria: 'edificio', ordine_cammino: 504 },
    { id: 'intervista_ludovico', lat: 44.499993, lon: 11.340385, distanceThreshold: 50, categoria: 'arte', ordine_cammino: 602 },
    { id: 'lastre', lat: 44.499312, lon: 11.340714, distanceThreshold: 50, categoria: 'esterno', ordine_cammino: 903 },
    { id: 'chiesasbene', lat: 44.5019, lon: 11.343843, distanceThreshold: 120, categoria: 'chiesa', ordine_cammino: 802 },
    { id: 'santuariopioggia', lat: 44.498891, lon: 11.342148, distanceThreshold: 120, categoria: 'chiesa', ordine_cammino: 803 },
    { id: 'edicola_votiva', lat: 44.499125, lon: 11.341781, distanceThreshold: 120, categoria: 'esterno', ordine_cammino: 904 },
    { id: 'pioggia1', lat: 44.498921, lon: 11.341923, distanceThreshold: 120, categoria: 'arte', ordine_cammino: 603 },
    { id: 'pioggia2', lat: 44.499023, lon: 11.34176, distanceThreshold: 120, categoria: 'statua', ordine_cammino: 701 },
    { id: 'pioggia3', lat: 44.499023, lon: 11.34176, distanceThreshold: 120, categoria: 'arte', ordine_cammino: 604 },
    { id: 'chiesasancarlo', lat: 44.501295, lon: 11.34085, distanceThreshold: 120, categoria: 'chiesa', ordine_cammino: 804 },
    { id: 'psontuoso', lat: 44.49046395468894, lon: 11.329397374392755, distanceThreshold: 15, categoria: 'portici', ordine_cammino: 1 },
    { id: 'arco170_madonna_grassa', lat: 44.48938722340913, lon: 11.319113695503352, distanceThreshold: 15, categoria: 'portici', ordine_cammino: 170 },
    { id: 'arco3_fornasari', lat: 44.490633, lon: 11.329205, distanceThreshold: 15, categoria: 'portici', ordine_cammino: 3 },
    { id: 'stabile_legno_vandini', lat: 44.502054, lon: 11.338546, distanceThreshold: 120, categoria: 'edificio', ordine_cammino: 501 }
];

// ===========================================
// CONFIGURAZIONE GOOGLE MAPS PER POI CORRENTE
// ===========================================
function setupGoogleMapsButton(lang) {
    const pageId = getCurrentPageId();
    const gmapsBtn = document.getElementById('gmapsLink');
    if (!gmapsBtn) return;

    const currentPoi = POIS_LOCATIONS.find(p => p.id.toLowerCase() === pageId.toLowerCase());

    if (currentPoi && currentPoi.lat && currentPoi.lon) {
        const gmapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${currentPoi.lat},${currentPoi.lon}&travelmode=walking`;
        gmapsBtn.href = gmapsUrl;

        const labels = {
            'it': '🧭 Portami qui',
            'en': '🧭 Navigate here',
            'fr': '🧭 Y aller',
            'es': '🧭 Llevarme aquí'
        };

        const btnText = gmapsBtn.querySelector('.gmaps-btn');
        if (btnText) {
            btnText.textContent = labels[lang] || labels['it'];
        }

        gmapsBtn.style.display = 'inline-flex';
    } else {
        gmapsBtn.style.display = 'none';
    }
}

// ===========================================
// UTILITY
// ===========================================
const getCurrentPageId = () => {
    const urlPath = window.location.pathname;
    let fileName = urlPath.substring(urlPath.lastIndexOf('/') + 1);
    if (!fileName || fileName.startsWith('index')) return 'home';
    return fileName.split('-')[0].replace('.html', '').toLowerCase();
};

const updateText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val || ''; };
const updateHTML = (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val || ''; };
const isFilePath = (val) => typeof val === 'string' && (val.endsWith('.html') || val.endsWith('.txt'));

async function fetchFileContent(path) {
    try {
        const res = await fetch(path);
        if (!res.ok) return `[Errore caricamento: ${path}]`;
        return await res.text();
    } catch (e) { return `[Contenuto non disponibile]`; }
}

// ===========================================
// LOGICA FIREBASE
// ===========================================
function setupDrinListener() {
    if (!db) return;
    const drinDocRef = doc(db, 'artifacts', appId, 'public', 'data', 'commands', 'drin');
    onSnapshot(drinDocRef, (snap) => {
        if (snap.exists()) {
            const audio = new Audio('Assets/Audio/drin.mp3');
            audio.play().catch(() => { });
        }
    });
}

async function logAccess(pageId, lang) {
    if (!db || !currentUserId) return;
    try {
        const logsCol = collection(db, 'artifacts', appId, 'public', 'data', 'access_logs');
        await addDoc(logsCol, { pageId, lang, userId: currentUserId, timestamp: serverTimestamp() });
    } catch (e) { console.error("Log error:", e); }
}

// ===========================================
// CARICAMENTO CONTENUTI
// ===========================================
async function loadContent(lang) {
    document.documentElement.lang = lang;
    const pageId = getCurrentPageId();

    try {
        const response = await fetch(`data/translations/${lang}/texts.json`);
        const data = await response.json();
        window.allData = data;
        const pageData = data[pageId];

        if (!pageData) {
            updateText('pageTitle', "Contenuto non trovato");
            document.body.classList.add('content-loaded');
            return;
        }

        updateText('pageTitle', pageData.pageTitle);
        updateHTML('headerTitle', pageData.pageTitle);

        const headImg = document.getElementById('headImage');
        if (headImg && pageData.headImage) {
            headImg.src = `public/images/${pageData.headImage}`;
            headImg.style.display = 'block';
        }

        const textKeys = ['mainText', 'mainText1', 'mainText2', 'mainText3', 'mainText4', 'mainText5'];
        for (const key of textKeys) {
            let content = pageData[key];
            if (isFilePath(content)) {
                content = await fetchFileContent(`text_files/${content}`);
            }
            updateHTML(key, content);
        }

        for (let i = 1; i <= 5; i++) {
            const imgEl = document.getElementById(`pageImage${i}`);
            const src = pageData[`imageSource${i}`];
            if (imgEl) {
                if (src) {
                    imgEl.src = `Assets/images/${src}`;
                    imgEl.style.display = 'block