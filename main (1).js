// ===========================================
// CONFIGURAZIONE E COSTANTI GLOBALI
// ===========================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
import { getDatabase, ref, set } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-database.js";

const APP_VERSION = '1.3.2 - Fix percorsi immagini dettaglio, caricamento menu e rimozione doppio DOMContentLoaded';
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
    { id: 'navHome', key: 'navHome', base: 'index', poiId: 'home' },
    { id: 'navManifattura', key: 'navManifattura', base: 'manifattura', poiId: 'manifattura' },
    { id: 'navPittoricarracci', key: 'navPittoricarracci', base: 'pittoricarracci', poiId: 'pittoricarracci' },
    { id: 'navCavaticcio', key: 'navCavaticcio', base: 'cavaticcio', poiId: 'cavaticcio' },
    { id: 'navBsmariamaggiore', key: 'navBsmariamaggiore', base: 'bsmariamaggiore', poiId: 'bsmariamaggiore' },
    { id: 'navGraziaxx', key: 'navGraziaxx', base: 'graziaxx', poiId: 'graziaxx' },
    { id: 'navPugliole', key: 'navPugliole', base: 'pugliole', poiId: 'pugliole' },
    { id: 'navCarracci', key: 'navCarracci', base: 'carracci', poiId: 'carracci' },
    { id: 'navIntervista_ludovico', key: 'navIntervista_ludovico', base: 'intervista_ludovico', poiId: 'intervista_ludovico' },
    { id: 'navLastre', key: 'navLastre', base: 'lastre', poiId: 'lastre' },
    { id: 'navChiesasbene', key: 'navChiesasbene', base: 'chiesasbene', poiId: 'chiesasbene' },
    { id: 'navSantuariopioggia', key: 'navSantuariopioggia', base: 'santuariopioggia', poiId: 'santuariopioggia' },
    { id: 'navEdicola_votiva', key: 'navEdicola_votiva', base: 'edicola_votiva', poiId: 'edicola_votiva' },
    { id: 'navPioggia1', key: 'navPioggia1', base: 'pioggia1', poiId: 'pioggia1' },
    { id: 'navPioggia2', key: 'navPioggia2', base: 'pioggia2', poiId: 'pioggia2' },
    { id: 'navPioggia3', key: 'navPioggia3', base: 'pioggia3', poiId: 'pioggia3' },
    { id: 'navChiesasancarlo', key: 'navChiesasancarlo', base: 'chiesasancarlo', poiId: 'chiesasancarlo' },
    { id: 'navPsontuoso', key: 'navPsontuoso', base: 'psontuoso', poiId: 'psontuoso' },
    { id: 'navArco170madonnagrassa', key: 'navArco170madonnagrassa', base: 'arco170_madonna_grassa', poiId: 'arco170_madonna_grassa' },
    { id: 'navArco125_francesi', key: 'navArco125_francesi', base: 'arco125_francesi', poiId: 'arco125_francesi' },
    { id: 'navArco126_beccari', key: 'navArco126_beccari', base: 'arco126_beccari', poiId: 'arco126_beccari' },
    { id: 'navArco3fornasari', key: 'navArco3fornasari', base: 'arco3_fornasari', poiId: 'arco3_fornasari' },
    { id: 'navStabilevandini', key: 'navStabilevandini', base: 'stabile_legno_vandini', poiId: 'stabile_legno_vandini' }
];

// ===========================================
// CONFIGURAZIONE TITOLI CATEGORIE MULTILINGUA
// ===========================================
const CATEGORIE_TITOLI = {
    'chiesa': { it: '⛪ Chiese & Luoghi di Culto', en: '⛪ Churches & Places of Worship', es: '⛪ Iglesias y Culto', fr: '⛪ Églises et Lieux de Culte' },
    'edificio': { it: '🏛️ Architettura & Palazzi', en: '🏛️ Architecture & Buildings', es: '🏛️ Arquitectura y Edificios', fr: '🏛️ Architecture et Bâtiments' },
    'portici': { it: '🏛️ Portici & Archi Storici', en: '🏛️ Porticoes & Historic Arches', es: '🏛️ Pórticos y Arcos Históricos', fr: '🏛️ Portiques et Arches Historiques' },
    'mpatind': { it: '🏭 Museo Patrimonio Industriale', en: '🏭 Museum of Industrial Heritage', es: '🏭 Museo del Patrimonio Industrial', fr: '🏭 Musée du Patrimoine Industriel' },
    'itinerari': { it: '🥾 Itinerari & Percorsi', en: '🥾 Routes & Walking Tours', es: '🥾 Itinerarios y Rutas', fr: '🥾 Itinéraires et Parcours' },
    'arte': { it: '🎨 Opere d’Arte & Quadri', en: '🎨 Artworks & Paintings', es: '🎨 Obras de Arte', fr: '🎨 Œuvres d’Art' },
    'statua': { it: '🗿 Sculture e Monumenti', en: '🗿 Sculptures & Monuments', es: '🗿 Esculturas y Monumentos', fr: '🗿 Sculptures et Monuments' },
    'esterno': { it: '🌳 Esterni e Luoghi', en: '🌳 Outdoors & Places', es: '🌳 Exteriores y Lugares', fr: '🌳 Extérieurs et Lieux' },
    'altro': { it: '📍 Altri Punti di Interesse', en: '📍 Other Points of Interest', es: '📍 Otros Puntos de Interés', fr: '📍 Autres Points d’Intérêt' }
};

// ===========================================
// DATI: POI GPS
// ===========================================
const POIS_LOCATIONS = [
    { id: 'manifattura', lat: 44.4989321, lon: 11.336618, distanceThreshold: 50, categoria: 'edificio', ordine_cammino: 1502 },
    { id: 'pittoricarracci', lat: 44.49909, lon: 11.340316, distanceThreshold: 50, categoria: 'arte', ordine_cammino: 601 },
    { id: 'cavaticcio', lat: 44.500207, lon: 11.338076, distanceThreshold: 50, categoria: 'edificio', ordine_cammino: 1503 },
    { id: 'bsmariamaggiore', lat: 44.498118, lon: 11.341923, distanceThreshold: 50, categoria: 'chiesa', ordine_cammino: 801 },
    { id: 'graziaxx', lat: 44.500594, lon: 11.340758, distanceThreshold: 50, categoria: 'esterno', ordine_cammino: 901 },
    { id: 'pugliole', lat: 44.500071, lon: 11.339805, distanceThreshold: 50, categoria: 'esterno', ordine_cammino: 902 },
    { id: 'carracci', lat: 44.499912, lon: 11.34041, distanceThreshold: 50, categoria: 'edificio', ordine_cammino: 1504 },
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
    { id: 'arco125_francesi', lat: 44.48983889, lon: 11.32184722, distanceThreshold: 15, categoria: 'portici', ordine_cammino: 125 },
    { id: 'arco126_beccari', lat: 44.48983895, lon: 11.32184732, distanceThreshold: 15, categoria: 'portici', ordine_cammino: 126 },
    { id: 'arco3_fornasari', lat: 44.490633, lon: 11.329205, distanceThreshold: 15, categoria: 'portici', ordine_cammino: 3 },
    { id: 'stabile_legno_vandini', lat: 44.502054, lon: 11.338546, distanceThreshold: 120, categoria: 'edificio', ordine_cammino: 1501 }
];

// ===========================================
// UTILITY
// ===========================================
const getCurrentLanguage = () => {
    const urlLang = location.pathname.match(/-([a-z]{2})\.html/i);
    if (urlLang && LANGUAGES.includes(urlLang[1].toLowerCase())) {
        return urlLang[1].toLowerCase();
    }
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    if (savedLang && LANGUAGES.includes(savedLang.toLowerCase())) {
        return savedLang.toLowerCase();
    }
    return currentLang || 'it';
};

const getCurrentPageId = () => {
    const urlPath = window.location.pathname;
    let fileName = urlPath.substring(urlPath.lastIndexOf('/') + 1);
    if (!fileName) return 'home';

    let cleanName = fileName.replace('.html', '').toLowerCase();

    // Rimuove suffissi lingua con trattino (es. arco125-it)
    LANGUAGES.forEach(lang => {
        if (cleanName.endsWith(`-${lang}`)) {
            cleanName = cleanName.substring(0, cleanName.length - (lang.length + 1));
        }
    });

    // Rimuove prefissi lingua con underscore (retrocompatibilità)
    LANGUAGES.forEach(lang => {
        if (cleanName.startsWith(`${lang}_`)) {
            cleanName = cleanName.substring(lang.length + 1);
        }
    });

    if (cleanName === 'index' || cleanName === 'home' || cleanName === '') {
        return 'home';
    }

    return cleanName;
};

window.getSimboloCategoria = function (categoria) {
    if (!categoria || categoria === "" || categoria === "undefined") {
        return '📍';
    }
    const catClean = categoria.toString().toLowerCase().trim();
    const simboli = {
        'edificio': '🏛️',
        'esterno': '🌳',
        'chiesa': '⛪',
        'quadro': '🎨',
        'statua': '🗿',
        'arte': '🎨',
        'monumento': '🏛️',
        'portici': '🏛️',
        'mpatind': '🏭',
        'itinerari': '🥾'
    };
    return simboli[catClean] || '📍';
};

// ===========================================
// CONFIGURAZIONE GOOGLE MAPS PER POI CORRENTE
// ===========================================
function setupGoogleMapsButton(lang) {
    const pageId = getCurrentPageId();
    const gmapsBtn = document.getElementById('gmapsLink');
    if (!gmapsBtn) return;

    const basePoiId = pageId.replace(/_dett(?:aglio|agli|_.*)?$/i, '').toLowerCase();
    const currentPoi = POIS_LOCATIONS.find(p => p.id.toLowerCase() === pageId.toLowerCase())
                    || POIS_LOCATIONS.find(p => p.id.toLowerCase() === basePoiId);

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
// CARICAMENTO CONTENUTI (DETTAGLIO & PRINCIPALE)
// ===========================================
async function loadContent(forcedLang) {
    const lang = forcedLang || getCurrentLanguage();
    currentLang = lang;
    const pageId = getCurrentPageId();

    // Rileva se si tratta di una pagina di dettaglio (_dettaglio, _dettagli o _dett_)
    const isDetail = /_dett(?:aglio|agli|_)/i.test(pageId) || /_dett(?:aglio|agli|_)/i.test(window.location.pathname);
    const basePoiId = pageId.replace(/_dett(?:aglio|agli|_.*)?$/i, '').toLowerCase();

    const response = await fetch(`data/translations/${lang}/texts.json`);
    const data = await response.json();
    window.allData = data;

    // Aggiorna menu di navigazione, geolocalizzazione e pulsante Google Maps
    if (data.navigation) {
        updateNavigation(data.navigation, lang);
    }
    setupGoogleMapsButton(lang);
    startGeolocation(data);

    // Priorità all'oggetto specifico della pagina (es. chiesasancarlo_dett_chiesa),
    // con fallback sulla scheda base solo se non esiste un blocco dedicato
    const pageData = data[pageId] || data[basePoiId];

    if (!pageData) {
        console.error(`Dati non trovati in texts.json per pageId="${pageId}" o basePoiId="${basePoiId}"`);
        return;
    }

    const updateHTML = (id, content) => {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = content || '';
        }
    };

    // Helper per aggiornare le immagini gestendo sia nomi semplici sia percorsi relativi completi
    const updateImage = (id, src) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (src && src.trim() !== '') {
            let cleanSrc = src.trim();
            let fullSrc;
            if (cleanSrc.startsWith('Assets/') || cleanSrc.startsWith('http://') || cleanSrc.startsWith('https://')) {
                fullSrc = cleanSrc;
            } else if (cleanSrc.includes('/')) {
                // Es. "chiesasancarlo/foto.jpg" o "chiesasancarlo_dett_chiesa/dettaglio/foto.jpg"
                fullSrc = `Assets/images/${cleanSrc}`;
            } else {
                // Solo nome file (es. "foto.jpg"): ricostruisce la sottocartella del POI
                fullSrc = isDetail
                    ? `Assets/images/${pageId}/dettaglio/${cleanSrc}`
                    : `Assets/images/${pageId}/${cleanSrc}`;
            }
            el.src = fullSrc;
            el.style.display = '';
        } else {
            el.style.display = 'none';
        }
    };

    const isFilePath = (str) => typeof str === 'string' && str.trim().endsWith('.html');

    const fetchFileContent = async (path) => {
        try {
            const res = await fetch(path);
            return res.ok ? await res.text() : '';
        } catch (e) {
            console.warn(`Impossibile caricare il frammento: ${path}`, e);
            return '';
        }
    };

    // 1. Immagine di testata
    if (pageData.headImage) {
        updateImage('headImage', pageData.headImage);
    }

    // 2. Titoli e sottotitoli (se presenti nel template)
    if (pageData.pageTitle || pageData.title) {
        updateHTML('pageTitle', pageData.pageTitle || pageData.title);
    }
    if (pageData.subtitle) {
        updateHTML('pageSubtitle', pageData.subtitle);
    }

    // 3. Caricamento Testi e Immagini
    if (isDetail) {
        // --- SCHEDA DI DETTAGLIO ---
        const dettKeys = ['dettText1', 'dettText2', 'dettText3', 'dettText4', 'dettText5'];
        for (const key of dettKeys) {
            let content = pageData[key];
            if (isFilePath(content)) {
                const filePath = content.startsWith('text_files/')
                    ? content
                    : `text_files/${content}`;
                content = await fetchFileContent(filePath);
            }
            if (content && typeof content === 'string') {
                content = content.replace(/<img[^>]*>/gi, '');
            }
            updateHTML(key, content);
        }

        const dettImgKeys = ['imageDett1', 'imageDett2', 'imageDett3', 'imageDett4', 'imageDett5'];
        for (const key of dettImgKeys) {
            updateImage(key, pageData[key]);
        }
    } else {
        // --- SCHEDA PRINCIPALE POI ---
        const textKeys = ['mainText', 'mainText1', 'mainText2', 'mainText3', 'mainText4', 'mainText5'];
        for (const key of textKeys) {
            let content = pageData[key];
            if (isFilePath(content)) {
                const filePath = content.startsWith('text_files/')
                    ? content
                    : `text_files/${content}`;
                content = await fetchFileContent(filePath);
            }
            updateHTML(key, content);
        }

        const imgKeys = ['imageSource1', 'imageSource2', 'imageSource3', 'imageSource4', 'imageSource5'];
        for (const key of imgKeys) {
            updateImage(key, pageData[key]);
        }
    }

    // 4. Tabella delle Fonti (caricamento dinamico HTML) e Metadati
    const infoSourceEl = document.getElementById('infoSource');
    if (infoSourceEl) {
        const customSourceFile = pageData.infoSource || (isFilePath(pageData.sourceText) ? pageData.sourceText : null);
        const sourceFilePath = customSourceFile
            ? (customSourceFile.startsWith('text_files/') ? customSourceFile : `text_files/${customSourceFile}`)
            : `text_files/${lang}_${pageId}_infoSource.html`;

        try {
            const resSource = await fetch(sourceFilePath);
            if (resSource.ok) {
                infoSourceEl.innerHTML = await resSource.text();
            } else if (pageData.sourceText && !isFilePath(pageData.sourceText) && pageData.sourceText.trim() !== '') {
                infoSourceEl.innerHTML = `Fonte: ${pageData.sourceText}`;
            } else {
                infoSourceEl.innerHTML = '';
            }
        } catch (err) {
            infoSourceEl.innerHTML = (pageData.sourceText && !isFilePath(pageData.sourceText))
                ? `Fonte: ${pageData.sourceText}`
                : '';
        }
    }

    if (pageData.creationDate) updateHTML('infoCreatedDate', `Data Creazione: ${pageData.creationDate}`);
    if (pageData.lastUpdate) updateHTML('infoUpdatedDate', `Ultimo Aggiornamento: ${pageData.lastUpdate}`);

    // 5. Player Audio
    const audioPlayer = document.getElementById('audioPlayer');
    if (audioPlayer && pageData.audioSource) {
        audioPlayer.src = pageData.audioSource.startsWith('Assets/')
            ? pageData.audioSource
            : `Assets/audio/${pageData.audioSource}`;
    }
}

function updateNavigation(navData, lang) {
    if (!navData) return;
    const navContent = document.querySelector('#navBarMain .nav-bar-content');
    if (!navContent) return;

    const langSuffix = lang === 'it' ? '-it' : `-${lang}`;

    // 1. Inserimento voce fissa Home / Benvenuto in alto
    let menuHtml = `<ul class="menu-principale">
        <li class="menu-item-home">
            <a href="index${langSuffix}.html">📍 ${navData['navHome'] || 'Benvenuto'}</a>
        </li>`;

    // 2. Raggruppamento dei POI per categoria
    const poiPerCategoria = {};

    navLinksData.forEach(item => {
        if (item.base === 'index') return; // Salta la Home

        const targetPoiId = (item.poiId || item.base).toLowerCase();
        const poiInfo = POIS_LOCATIONS.find(p => p.id.toLowerCase() === targetPoiId);
        const catKey = poiInfo ? (poiInfo.categoria || 'altro') : 'altro';

        // Lettura ordine_cammino con fallback a 999 se omesso
        const ordineCammino = item.ordine_cammino !== undefined
            ? item.ordine_cammino
            : (poiInfo && poiInfo.ordine_cammino !== undefined ? poiInfo.ordine_cammino : 999);

        const titoloTradotto = navData[item.key] ||
            (window.allData[item.base] && window.allData[item.base].pageTitle) ||
            item.base;

        const simbolo = window.getSimboloCategoria(catKey);

        if (!poiPerCategoria[catKey]) {
            poiPerCategoria[catKey] = [];
        }

        poiPerCategoria[catKey].push({
            href: `${item.base}${langSuffix}.html`,
            titolo: titoloTradotto,
            simbolo: simbolo,
            ordine_cammino: ordineCammino
        });
    });

    // 3. Costruzione sottomenu e ordinamento per ordine_cammino (con parità alfabetica multilingua)
    Object.keys(poiPerCategoria).forEach(catKey => {
        poiPerCategoria[catKey].sort((a, b) => {
            if (a.ordine_cammino !== b.ordine_cammino) {
                return a.ordine_cammino - b.ordine_cammino;
            }
            return a.titolo.localeCompare(b.titolo, lang, { sensitivity: 'base' });
        });

        const titoloCategoria = (CATEGORIE_TITOLI[catKey] && CATEGORIE_TITOLI[catKey][lang])
            || (CATEGORIE_TITOLI['altro'][lang] || 'ALTRO');

        menuHtml += `
            <li class="menu-categoria-group">
                <details class="category-accordion">
                    <summary class="category-header">${titoloCategoria} (${poiPerCategoria[catKey].length})</summary>
                    <ul class="submenu-poi">`;

        poiPerCategoria[catKey].forEach(poi => {
            menuHtml += `
                        <li>
                            <a href="${poi.href}"><span class="menu-icon">${poi.simbolo}</span> ${poi.titolo}</a>
                        </li>`;
        });

        menuHtml += `
                    </ul>
                </details>
            </li>`;
    });

    menuHtml += `</ul>`;
    navContent.innerHTML = menuHtml;
}

// ===========================================
// GEOLOCALIZZAZIONE
// ===========================================
const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
};

let geoWatchStarted = false;
function startGeolocation(allData) {
    if (!navigator.geolocation || geoWatchStarted) return;
    geoWatchStarted = true;

    const geoOptions = { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 };

    navigator.geolocation.watchPosition((pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        if (nearbyPoiButton) {
            nearbyPoiButton.style.display = 'block';
        }

        let menuHtml = '<ul class="poi-links">';
        let found = false;

        POIS_LOCATIONS.forEach(poi => {
            const dist = calculateDistance(lat, lon, poi.lat, poi.lon);
            if (dist <= poi.distanceThreshold) {
                const title = (allData[poi.id] && allData[poi.id].pageTitle) ? allData[poi.id].pageTitle : poi.id;
                const simbolo = (typeof window.getSimboloCategoria === 'function') ? window.getSimboloCategoria(poi.categoria) : '📍';
                const suffix = currentLang === 'it' ? '-it' : `-${currentLang}`;
                menuHtml += `<li>
                    <a href="${poi.id}${suffix}.html">
                        <span>${simbolo}</span> ${title} (${dist.toFixed(0)}m)
                    </a>
                </li>`;
                found = true;
            }
        });

        menuHtml += '</ul>';
        if (!found) {
            let noPoiMessage;
            switch (currentLang) {
                case 'es': noPoiMessage = `No se encontraron puntos de interés dentro 50 m. <br><br> Pulse de nuevo el botón verde para cerrar el menú.`; break;
                case 'en': noPoiMessage = `No Points of Interest found within 50 m. <br><br> Press the green button again to close the menu.`; break;
                case 'fr': noPoiMessage = `Aucun point d'interet trouve dans les environs 50 m. <br><br> Appuyez à nouveau sur le bouton vert pour fermer le menu.`; break;
                case 'it':
                default: noPoiMessage = `Nessun Punto di Interesse trovato entro 50 m.<br><br> Premere di nuovo il bottone verde per chiudere la lista.`; break;
            }
            menuHtml = `<div style="color:red; padding: 20px; text-align: center; font-size: 1em;">${noPoiMessage}</div>`;
        }
        if (nearbyMenuPlaceholder) nearbyMenuPlaceholder.innerHTML = menuHtml;

    }, (err) => {
        console.warn("Geolocation error:", err.message);
    }, geoOptions);
}

// ===========================================
// SINCRONIZZAZIONE ASCOLTI (CRONOLOGIA SMARTPHONE)
// ===========================================
function gestisciSincronizzazioneToken() {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('pair');

    if (tokenFromUrl) {
        const oldToken = localStorage.getItem('site_pair_token');
        localStorage.setItem('site_pair_token', tokenFromUrl);

        if (oldToken && oldToken !== tokenFromUrl && rtdb) {
            unisciAscoltiPrecedenti(oldToken, tokenFromUrl);
        }
        return tokenFromUrl;
    }

    let localToken = localStorage.getItem('site_pair_token');
    if (!localToken) {
        localToken = 'session_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
        localStorage.setItem('site_pair_token', localToken);
    }
    return localToken;
}

function unisciAscoltiPrecedenti(oldToken, newToken) {
    if (!rtdb) return;
    const oldRef = ref(rtdb, `cronologia/${oldToken}`);

    import("https://www.gstatic.com/firebasejs/11.6.1/firebase-database.js").then(({ get }) => {
        get(oldRef).then((snapshot) => {
            if (snapshot.exists()) {
                const data = snapshot.val();
                Object.keys(data).forEach(pageId => {
                    set(ref(rtdb, `cronologia/${newToken}/${pageId}`), data[pageId]);
                });
            }
        }).catch(err => console.error("Errore unione ascolti:", err));
    });
}

gestisciSincronizzazioneToken();

function registraAscoltoAudio(pageId, pageTitle) {
    const token = gestisciSincronizzazioneToken();
    if (!token || !rtdb) return;

    const timestamp = new Date().toISOString();
    const currentUrl = window.location.href;

    set(ref(rtdb, `cronologia/${token}/${pageId}`), {
        pageId: pageId,
        title: pageTitle,
        url: currentUrl,
        timestamp: timestamp
    }).catch(err => console.error("Errore salvataggio ascolto:", err));
}

// ===========================================
// INIZIALIZZAZIONE EVENTI
// ===========================================
function initEvents() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('navBarMain');

    const closeMainMenu = () => {
        if (toggle && nav) {
            toggle.classList.remove('active');
            nav.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    };

    const closePoiMenu = () => {
        if (nearbyMenuPlaceholder) {
            nearbyMenuPlaceholder.classList.remove('poi-active');
            document.body.classList.remove('menu-open');
        }
    };

    if (toggle && nav) {
        toggle.onclick = (e) => {
            e.stopPropagation();
            closePoiMenu();
            toggle.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        };
    }

    if (nearbyPoiButton && nearbyMenuPlaceholder) {
        nearbyPoiButton.onclick = (e) => {
            e.stopPropagation();
            closeMainMenu();
            nearbyMenuPlaceholder.classList.toggle('poi-active');
            document.body.classList.toggle('menu-open');
        };
    }

    // Gestione Pulsante Audio
    const playBtn = document.getElementById('playAudio');
    const player = document.getElementById('audioPlayer');
    if (playBtn && player) {
        playBtn.onclick = () => {
            if (player.paused) {
                player.play();
                playBtn.textContent = playBtn.dataset.pauseText;
                playBtn.classList.replace('play-style', 'pause-style');

                const pageId = getCurrentPageId();
                const pageTitle = document.getElementById('pageTitle')?.textContent || pageId;
                registraAscoltoAudio(pageId, pageTitle);
            } else {
                player.pause();
                playBtn.textContent = playBtn.dataset.playText;
                playBtn.classList.replace('pause-style', 'play-style');
            }
        };
        player.onended = () => {
            playBtn.textContent = playBtn.dataset.playText;
            playBtn.classList.replace('pause-style', 'play-style');
        };
    }

    // Selettore Lingue
    document.querySelectorAll('.language-selector button, .language-selector img, .language-selector a').forEach(el => {
        el.onclick = (e) => {
            const target = e.target.closest('[data-lang]');
            const lang = target ? target.dataset.lang : null;

            if (!lang) return;

            e.preventDefault();
            e.stopPropagation();

            localStorage.setItem(LAST_LANG_KEY, lang);
            const pageId = getCurrentPageId();
            const base = (pageId === 'home' || pageId === 'index') ? 'index' : pageId;

            window.location.href = `${base}-${lang}.html`;
        };
    });
}

// Esposizione globale per eventuali chiamate dai template HTML
window.loadContent = loadContent;

// ===========================================
// INIZIALIZZAZIONE ALL'AVVIO (UNICA)
// ===========================================
document.addEventListener('DOMContentLoaded', () => {
    currentLang = getCurrentLanguage();

    nearbyPoiButton = document.getElementById('nearbyPoiButton');
    nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    initEvents();
    loadContent(currentLang);

    if (firebaseConfig.apiKey) {
        try {
            const app = initializeApp(firebaseConfig);
            db = getFirestore(app);
            auth = getAuth(app);
            rtdb = getDatabase(app);

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
        } catch (e) {
            console.error("Errore inizializzazione Firebase:", e);
        }
    }
});
