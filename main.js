// ===========================================
// CONFIGURAZIONE E COSTANTI GLOBALI
// ===========================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const APP_VERSION = '1.2.30 - Full Restoration 2026 versione rettificata';
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'Quadrilatero_lastLang';
let currentLang = 'it';
console.log(`Version : ${APP_VERSION}`);
// Elementi DOM Globali
let nearbyPoiButton;
let nearbyMenuPlaceholder;

// Configurazione Firebase
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
let db, auth, currentUserId = null, isAuthReady = false;

// ===========================================
// DATI: POI GPS (Tutti i 13 punti originali)
// ===========================================
// FIX: Controllo che window.APP_DATA e navLinksData esistano per evitare TypeError
// const navLinksData_futuro = (window.APP_DATA && window.APP_DATA.navLinksData) ? window.APP_DATA.navLinksData : [];

const POIS_LOCATIONS = [
    { id: 'manifattura', lat: 44.49891, lon: 11.342241, distanceThreshold: 50 },
    { id: 'pittoricarracci', lat: 44.50085, lon: 11.3361, distanceThreshold: 50 },
    { id: 'cavaticcio', lat: 44.50018, lon: 11.33807, distanceThreshold: 50 },
    { id: 'bsmariamaggiore', lat: 44.49806368372069, lon: 11.34192628931731, distanceThreshold: 50 },
    { id: 'graziaxx', lat: 44.5006638888889, lon: 11.3407694444444, distanceThreshold: 50 },
    { id: 'pugliole', lat: 44.5001944444444, lon: 11.3399861111111, distanceThreshold: 50 },
    { id: 'carracci', lat: 44.4999972222222, lon: 11.3403888888889, distanceThreshold: 50 },
    { id: 'lastre', lat: 44.49925278, lon: 11.34074444, distanceThreshold: 50 },
    { id: 'chiesasbene', lat: 44.501514, lon: 11.343557, distanceThreshold: 120 },
    { id: 'santuariopioggia', lat: 44.49891, lon: 11.342241, distanceThreshold: 120 },
    { id: 'pioggia1', lat: 44.49891, lon: 11.342241, distanceThreshold: 120 },
    { id: 'pioggia2', lat: 44.49891, lon: 11.342241, distanceThreshold: 120 },
    { id: 'pioggia3', lat: 44.49891, lon: 11.342241, distanceThreshold: 120 }
];

// ===========================================
// UTILITY E SUPPORTO
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
// CARICAMENTO CONTENUTI (LA PARTE MANCANTE)
// ===========================================

async function loadContent(lang) {
    document.documentElement.lang = lang;
    const pageId = getCurrentPageId();

    try {
        const response = await fetch(`data/translations/${lang}/texts.json`);
        const data = await response.json();
        const pageData = data[pageId];

        if (!pageData) {
            updateText('pageTitle', "Contenuto non trovato");
            document.body.classList.add('content-loaded');
            return;
        }

        // 1. Titoli e Header
        updateText('pageTitle', pageData.pageTitle);
        updateHTML('headerTitle', pageData.pageTitle);

        // 2. Immagine di Testata
        const headImg = document.getElementById('headImage');
        if (headImg && pageData.headImage) {
            headImg.src = `public/images/${pageData.headImage}`;
            headImg.style.display = 'block';
        }

        // 3. Testi Principali (Gestione file .txt)
        const textKeys = ['mainText', 'mainText1', 'mainText2', 'mainText3', 'mainText4', 'mainText5'];
        for (const key of textKeys) {
            let content = pageData[key];
            if (isFilePath(content)) {
                content = await fetchFileContent(`text_files/${content}`);
            }
            updateHTML(key, content);
        }

        // 4. Immagini Secondarie (1-5)
        for (let i = 1; i <= 5; i++) {
            const imgEl = document.getElementById(`pageImage${i}`);
            const src = pageData[`imageSource${i}`];
            if (imgEl) {
                if (src) {
                    imgEl.src = `Assets/images/${src}`;
                    imgEl.style.display = 'block';
                } else {
                    imgEl.style.display = 'none';
                }
            }
        }

        // 5. Metadati
        updateText('infoSource', pageData.sourceText ? `Fonte: ${pageData.sourceText}` : '');
        updateText('infoCreatedDate', pageData.creationDate ? `Data: ${pageData.creationDate}` : '');

        // 6. Audio
        const audioPlayer = document.getElementById('audioPlayer');
        const playBtn = document.getElementById('playAudio');
        if (audioPlayer && playBtn && pageData.audioSource) {
            audioPlayer.src = `Assets/Audio/${pageData.audioSource}`;
            playBtn.textContent = pageData.playAudioButton || "Play";
            playBtn.dataset.playText = pageData.playAudioButton;
            playBtn.dataset.pauseText = pageData.pauseAudioButton;
            playBtn.style.display = 'block';
        }

        // 7. Navigazione
        updateNavigation(data.nav, lang);

        startGeolocation(data);
        document.body.classList.add('content-loaded');
        if (isAuthReady) logAccess(pageId, lang);

    } catch (e) {
        console.error("Errore caricamento:", e);
        document.body.classList.add('content-loaded');
    }
}

function updateNavigation(navData, lang) {
    if (!navData) return;
    const langSuffix = lang === 'it' ? '-it' : `-${lang}`;

    // FIX: Controllo che window.APP_DATA e navLinksData esistano per evitare TypeError
//    const navLinksData_futuro = (window.APP_DATA && window.APP_DATA.navLinksData) ? window.APP_DATA.navLinksData : [];

    const navLinksData = [
        { id: 'navHome', key: 'navHome', base: 'index' },
        { id: 'navManifattura', key: 'navManifattura', base: 'manifattura' },
        { id: 'navPittoriCarracci', key: 'navPittoriCarracci', base: 'pittoricarracci' },
        { id: 'navCavaticcio', key: 'navCavaticcio', base: 'cavaticcio' },
        { id: 'navbsmariamaggiore', key: 'navbsmariamaggiore', base: 'bsmariamaggiore' },
        { id: 'navGraziaxx', key: 'navGraziaxx', base: 'graziaxx' },
        { id: 'navPugliole', key: 'navPugliole', base: 'pugliole' },
        { id: 'navCarracci', key: 'navCarracci', base: 'carracci' },
        { id: 'navLastre', key: 'navLastre', base: 'lastre' },
        { id: 'navChiesaSBene', key: 'navChiesaSBene', base: 'chiesasbene' },
        { id: 'navSantuarioPioggia', key: 'navSantuarioPioggia', base: 'santuariopioggia' },
        { id: 'navPioggia1', key: 'navPioggia1', base: 'pioggia1' },
        { id: 'navPioggia2', key: 'navPioggia2', base: 'pioggia2' },
        { id: 'navPioggia3', key: 'navPioggia3', base: 'pioggia3' }
    ];
    links.forEach(l => {
        const el = document.getElementById(l.id);
        if (el) {
            el.href = `${l.base}${langSuffix}.html`;
            el.textContent = navData[l.key] || l.id;
        }
    });
}

// ===========================================
// GEOLOCALIZZAZIONE E AUDIO
// ===========================================

const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
};

function startGeolocation(allData) {
    if (!navigator.geolocation) return;
    navigator.geolocation.watchPosition((pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        if (nearbyPoiButton) nearbyPoiButton.style.display = 'block';

        let menuHtml = '<ul class="poi-links">';
        let found = false;
        POIS_LOCATIONS.forEach(poi => {
            const dist = calculateDistance(lat, lon, poi.lat, poi.lon);
            if (dist <= poi.distanceThreshold) {
                const title = allData[poi.id]?.pageTitle || poi.id;
                const suffix = currentLang === 'it' ? '-it' : `-${currentLang}`;
                menuHtml += `<li><a href="${poi.id}${suffix}.html">${title} (${dist.toFixed(0)}m)</a></li>`;
                found = true;
            }
        });
        menuHtml += '</ul>';
        if (!found) menuHtml = '<div style="padding:20px;text-align:center;">Nessun punto vicino</div>';
        if (nearbyMenuPlaceholder) nearbyMenuPlaceholder.innerHTML = menuHtml;
    });
}

// ===========================================
// EVENTI E INIZIALIZZAZIONE
// ===========================================

function initEvents() {
    // Menu principale
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('navBarMain');
    if (toggle && nav) {
        toggle.onclick = () => {
            toggle.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        };
    }

    // Menu POI
    if (nearbyPoiButton && nearbyMenuPlaceholder) {
        nearbyPoiButton.onclick = () => {
            nearbyMenuPlaceholder.classList.toggle('poi-active');
            document.body.classList.toggle('menu-open');
        };
    }

    // Audio
    const playBtn = document.getElementById('playAudio');
    const player = document.getElementById('audioPlayer');
    if (playBtn && player) {
        playBtn.onclick = () => {
            if (player.paused) {
                player.play();
                playBtn.textContent = playBtn.dataset.pauseText;
            } else {
                player.pause();
                playBtn.textContent = playBtn.dataset.playText;
            }
        };
        player.onended = () => { playBtn.textContent = playBtn.dataset.playText; };
    }

    // Lingue
    document.querySelectorAll('.language-selector button').forEach(btn => {
        btn.onclick = () => {
            const lang = btn.dataset.lang;
            localStorage.setItem(LAST_LANG_KEY, lang);
            const base = getCurrentPageId() === 'home' ? 'index' : getCurrentPageId();
            location.href = `${base}-${lang}.html`;
        };
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    const urlLang = location.pathname.match(/-([a-z]{2})\.html/);
    currentLang = (urlLang && urlLang[1]) || savedLang || 'it';
    nearbyPoiButton = document.getElementById('nearbyPoiButton');
    nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    initEvents();
    loadContent(currentLang);

    if (firebaseConfig.apiKey) {
        const app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        auth = getAuth(app);

        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUserId = user.uid;
                isAuthReady = true;
                setupDrinListener();
                logAccess(getCurrentPageId(), currentLang);
            } else {
                signInAnonymously(auth);
            }
        });
    }
});