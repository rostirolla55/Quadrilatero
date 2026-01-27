/**
 * QUARTIERE PORTO - MASTER ENGINE (Versione Integrale)
 * --------------------------------------------------
 * Questo file gestisce l'intero ciclo di vita dell'applicazione:
 * 1. Configurazione Firebase e Autenticazione (Regola 3)
 * 2. Gestione Stato Multilingua (IT, EN, FR, ES)
 * 3. Motore di Geolocalizzazione e calcolo distanze in tempo reale
 * 4. Database POI interno (Hardcoded per massima stabilità)
 * 5. Rendering Dinamico della UI e gestione eventi DOM
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, getDoc, collection, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// --- 1. CONFIGURAZIONE E COSTANTI ---
const APP_ID = typeof __app_id !== 'undefined' ? __app_id : 'quartiere-porto-dev';
const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');

// Configurazione Lingue
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const DEFAULT_LANG = 'it';
const STORAGE_KEY_LANG = 'porto_pref_lang';

// Database Interno POI (Ripristinato per evitare errori di caricamento asincrono)
const POI_DATA = [
    { id: 'index', lat: 44.5020, lon: 11.3360, category: 'center' },
    { id: 'storia', lat: 44.5035, lon: 11.3375, category: 'culture' },
    { id: 'luoghi', lat: 44.5010, lon: 11.3340, category: 'monument' },
    { id: 'itinerari', lat: 44.5050, lon: 11.3400, category: 'walk' },
    { id: 'contatti', lat: 44.5000, lon: 11.3300, category: 'service' }
];

// --- 2. STATO DELL'APPLICAZIONE ---
let state = {
    user: null,
    currentLang: DEFAULT_LANG,
    userLocation: null,
    translations: null,
    isInitialized: false
};

// --- 3. INIZIALIZZAZIONE FIREBASE (Regola 3) ---
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

async function performAuth() {
    try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
            await signInWithCustomToken(auth, __initial_auth_token);
        } else {
            await signInAnonymously(auth);
        }
    } catch (error) {
        console.error("Auth Failure:", error);
    }
}

// --- 4. MOTORE GEOGRAFICO ---

/**
 * Calcola la distanza tra due coordinate usando la formula dell'Haversine
 */
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Raggio Terra in metri
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function initGps() {
    if ("geolocation" in navigator) {
        navigator.geolocation.watchPosition(
            (pos) => {
                state.userLocation = {
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                };
                if (document.getElementById('nearbyMenuPlaceholder')?.classList.contains('poi-active')) {
                    renderPoiList();
                }
            },
            (err) => console.warn("GPS Access Denied:", err.message),
            { enableHighAccuracy: true }
        );
    }
}

// --- 5. GESTIONE CONTENUTI E TRADUZIONI ---

async function fetchTranslations(lang) {
    // In questa fase integriamo i testi direttamente o via fetch locale
    // Per domani, prevediamo un caricamento atomico
    try {
        const response = await fetch(`data/translations/${lang}.json`);
        if (!response.ok) throw new Error("Missing translation file");
        return await response.json();
    } catch (e) {
        // Fallback strutturato
        return {
            nav: { index: "Home", storia: "Storia", luoghi: "Luoghi", itinerari: "Itinerari", contatti: "Contatti" },
            ui: { nearby: "Nelle vicinanze", loading: "Caricamento...", noGps: "Segnale GPS assente" }
        };
    }
}

// --- 6. RENDERING UI E GESTIONE EVENTI ---

function renderNavigation() {
    const navContainer = document.getElementById('navLinks');
    if (!navContainer || !state.translations) return;

    navContainer.innerHTML = '';
    Object.entries(state.translations.nav).forEach(([id, label]) => {
        const li = document.createElement('li');
        const suffix = state.currentLang === 'it' ? '' : `-${state.currentLang}`;
        li.innerHTML = `<a href="${id}${suffix}.html" class="nav-item">${label}</a>`;
        navContainer.appendChild(li);
    });
}

function renderPoiList() {
    const container = document.getElementById('nearbyMenuPlaceholder');
    if (!container) return;

    if (!state.userLocation) {
        container.innerHTML = `<div class="poi-msg">${state.translations.ui.noGps}</div>`;
        return;
    }

    const nearby = POI_DATA.map(poi => ({
        ...poi,
        dist: getDistance(state.userLocation.lat, state.userLocation.lon, poi.lat, poi.lon)
    })).sort((a, b) => a.dist - b.dist);

    let html = `<div class="poi-header">${state.translations.ui.nearby}</div><ul class="poi-list">`;
    nearby.forEach(poi => {
        const suffix = state.currentLang === 'it' ? '' : `-${state.currentLang}`;
        const name = state.translations.nav[poi.id] || poi.id;
        html += `
            <li>
                <a href="${poi.id}${suffix}.html">
                    <span class="name">${name}</span>
                    <span class="dist">${Math.round(poi.dist)}m</span>
                </a>
            </li>`;
    });
    html += `</ul>`;
    container.innerHTML = html;
}

function setupEventListeners() {
    const poiBtn = document.getElementById('nearbyPoiButton');
    const poiMenu = document.getElementById('nearbyMenuPlaceholder');
    const langSel = document.getElementById('langSelector');

    if (poiBtn && poiMenu) {
        poiBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            poiMenu.classList.toggle('poi-active');
            if (poiMenu.classList.contains('poi-active')) renderPoiList();
        });
    }

    if (langSel) {
        langSel.value = state.currentLang;
        langSel.addEventListener('change', (e) => {
            const newLang = e.target.value;
            localStorage.setItem(STORAGE_KEY_LANG, newLang);
            const path = window.location.pathname;
            const page = path.split('/').pop().replace(/-[a-z]{2}\.html/, '').replace('.html', '') || 'index';
            const suffix = newLang === 'it' ? '' : `-${newLang}`;
            window.location.href = `${page}${suffix}.html`;
        });
    }

    document.addEventListener('click', () => poiMenu?.classList.remove('poi-active'));
}

// --- 7. BOOTSTRAP SEQUENZIALE ---

async function bootstrap() {
    console.log("Bootstrap sequence started...");
    
    // 1. Auth (Mandatorio per Firestore)
    await performAuth();

    // 2. Determinazione Lingua
    const path = window.location.pathname;
    const match = path.match(/-([a-z]{2})\.html/);
    state.currentLang = match ? match[1] : (localStorage.getItem(STORAGE_KEY_LANG) || DEFAULT_LANG);

    // 3. Caricamento Dati
    state.translations = await fetchTranslations(state.currentLang);

    // 4. Inizializzazione UI e GPS
    renderNavigation();
    setupEventListeners();
    initGps();

    // 5. Cleanup Loading
    const loader = document.getElementById('loadingOverlay');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => loader.style.display = 'none', 500);
    }

    state.isInitialized = true;
    console.log("App Ready. Language:", state.currentLang);
}

// Avvio al caricamento del DOM
document.addEventListener('DOMContentLoaded', bootstrap);

// Listener per stato Auth
onAuthStateChanged(auth, (user) => {
    state.user = user;
    if (user) console.log("Firebase Session Active:", user.uid);
});