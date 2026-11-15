// ===========================================
// CONFIGURAZIONE E COSTANTI GLOBALI
// ===========================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
import { getDatabase, ref, set } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-database.js";

const APP_VERSION = '1.3.1 - Nuova versione dei menu e della geolocalizzazione - controllo categorie e ordine_cammino';
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
// CARICAMENTO CONTENUTI (DETTAGLIO & PRINCIPALE)
// ===========================================  
async function loadContent(lang) {
    document.documentElement.lang = lang;
    const pageId = getCurrentPageId();

    // Rileva se si tratta di una pagina di dettaglio (_dettaglio o _dettagli)
    const isDetail = window.location.pathname.includes('_dettagli');
    const basePoiId = pageId.replace(/_dettaglio?$/i, '').toLowerCase(); 
    try {
        const response = await fetch(`data/translations/${lang}/texts.json`);
        const data = await response.json();
        window.allData = data;
        const pageData = data[basePoiId] || data[pageId];

        if (!pageData) {
            updateText('pageTitle', "Contenuto non trovato");
            document.body.classList.add('content-loaded');
            return;
        }

        // 1. Titoli della pagina  
        updateText('pageTitle', pageData.pageTitle);
        updateHTML('headerTitle', pageData.headerTitle || pageData.pageTitle);

        // 2. Gestione Immagine di Testata (headImage) con fall-back sicuro per evitare 404
        const headImg = document.getElementById('headImage');
        if (headImg) {
            if (pageData.headImage && pageData.headImage.trim() !== "") {
                const headSrc = pageData.headImage.startsWith('public/') || pageData.headImage.startsWith('Assets/')
                    ? pageData.headImage
                    : `public/images/${pageData.headImage}`;

                headImg.src = headSrc;
                headImg.style.display = 'block';
                headImg.onerror = () => { headImg.style.display = 'none'; };
            } else {
                headImg.style.display = 'none';
            }
        }

        // 3. Caricamento Testi e Immagini
        if (isDetail) {
            // Imposta il link del pulsante "Torna alla scheda principale" alla pagina madre
            const backBtnList = document.querySelectorAll('.btn-back, #btnBackToPoi');
            backBtnList.forEach(btn => {
                btn.href = `${basePoiId}-${lang}.html`;
            });
            // --- SCHEDA DI DETTAGLIO ---
            // Carica dettText1..5 rimuovendo eventuali tag <img> orfani scritti da LibreOffice nei frammenti
            const dettKeys = ['dettText1', 'dettText2', 'dettText3', 'dettText4', 'dettText5'];
            for (const key of dettKeys) {
                let content = pageData[key];
                if (isFilePath(content)) {
                    content = await fetchFileContent(`text_files/${content}`);
                }

                if (content && typeof content === 'string') {
                    content = content.replace(/<img[^>]*>/gi, '');
                }

                updateHTML(key, content);
            }

            // Carica le immagini specifiche per il dettaglio (imageDett1..5)
            for (let i = 1; i <= 5; i++) {
                const imgEl = document.getElementById(`imageDett${i}`);
                const src = pageData[`imageDett${i}`];
                if (imgEl) {
                    if (src && src.trim() !== "") {
                        imgEl.src = `Assets/images/${src}`;
                        imgEl.style.display = 'block';
                    } else {
                        imgEl.style.display = 'none';
                    }
                }
            }
        } else {
            // --- SCHEDA PRINCIPALE POI ---
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
                    if (src && src.trim() !== "") {
                        imgEl.src = `Assets/images/${src}`;
                        imgEl.style.display = 'block';
                    } else {
                        imgEl.style.display = 'none';
                    }
                }
            }
        }

        // 4. Metadati e Player Audio (se presente)
        if (pageData.sourceText) updateHTML('infoSource', `Fonte: ${pageData.sourceText}`);
        if (pageData.creationDate) updateHTML('infoCreatedDate', `Data Creazione: ${pageData.creationDate}`);
        if (pageData.lastUpdate) updateHTML('infoUpdatedDate', `Ultimo Aggiornamento: ${pageData.lastUpdate}`);

        const audioPlayer = document.getElementById('audioPlayer');
        const playBtn = document.getElementById('playAudio');
        if (audioPlayer && playBtn) {
            if (pageData && pageData.audioSource) {
                audioPlayer.src = `Assets/Audio/${pageData.audioSource}`;
                playBtn.textContent = pageData.playAudioButton || "Ascolta";
                playBtn.dataset.playText = pageData.playAudioButton || "Ascolta";
                playBtn.dataset.pauseText = pageData.pauseAudioButton || "Pausa";
                playBtn.style.display = 'inline-block';
            } else {
                playBtn.style.display = 'none';
                audioPlayer.removeAttribute('src');
            }
        }

        updateNavigation(data.nav, lang);
        setupGoogleMapsButton(lang);
        startGeolocation(data);

        if (audioPlayer) {
            audioPlayer.onplay = () => {
                const pageId = getCurrentPageId();
                const pageTitle = document.getElementById('pageTitle')?.textContent || pageId;
                registraAscoltoAudio(pageId, pageTitle);
            };
        }

        document.body.classList.add('content-loaded');
        if (isAuthReady) logAccess(pageId, lang);

    } catch (e) {
        console.error("Errore caricamento:", e);
        document.body.classList.add('content-loaded');
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
        const ordineCammino = item.ordine_cammino !== undefined ? item.ordine_cammino : (poiInfo && poiInfo.ordine_cammino !== undefined ? poiInfo.ordine_cammino : 999);

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
            // In caso di pari ordine_cammino, ordina alfabeticamente in base alla lingua
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

function startGeolocation(allData) {
    if (!navigator.geolocation) return;

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
        // Se arriviamo da un QR Code, salviamo il token del PC
        const oldToken = localStorage.getItem('site_pair_token');
        localStorage.setItem('site_pair_token', tokenFromUrl);

        // Se c'era un token locale con ascolti precedenti, uniamo i dati su Firebase
        if (oldToken && oldToken !== tokenFromUrl && rtdb) {
            unisciAscoltiPrecedenti(oldToken, tokenFromUrl);
        }
        return tokenFromUrl;
    }

    // Se non c'è token nell'URL nè in locale, ne generiamo uno unico per lo smartphone
    let localToken = localStorage.getItem('site_pair_token');
    if (!localToken) {
        localToken = 'session_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
        localStorage.setItem('site_pair_token', localToken);
    }
    return localToken;
}

// Funzione per trasferire gli ascolti fatti "offline/prima del QR code" al token del PC
function unisciAscoltiPrecedenti(oldToken, newToken) {
    if (!rtdb) return;
    const oldRef = ref(rtdb, `cronologia/${oldToken}`);

    // Leggiamo i dati del vecchio token e li copiamo sul nuovo token
    import("https://www.gstatic.com/firebasejs/11.6.1/firebase-database.js").then(({ get, child }) => {
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

// Salva subito il token all'avvio
gestisciSincronizzazioneToken();

// Registrazione dell'ascolto audio su Realtime Database
function registraAscoltoAudio(pageId, pageTitle) {
    // Garantisce che ci sia sempre un token valido prima di inviare
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

                // Invio ascolto a Firebase Realtime Database
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

document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    const urlLang = location.pathname.match(/-([a-z]{2})\.html/);
    currentLang = (urlLang && urlLang[1]) || savedLang || 'it';

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


// ===========================================  
// ESPOSIZIONE GLOBALE ED AUTO-START DETTAGLI
// ===========================================  
// ===========================================  
// ESPOSIZIONE GLOBALE PER I TEMPLATE HTML
// ===========================================  
window.loadContent = loadContent;

// ===========================================  
// INIZIALIZZAZIONE ALL'AVVIO
// ===========================================  
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    const urlLang = location.pathname.match(/-([a-z]{2})\.html/);
    currentLang = (urlLang && urlLang[1]) || savedLang || 'it';

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
        'portici': '🏛️'
    };
    return simboli[catClean] || '📍';
};

window.POIS_LOCATIONS = POIS_LOCATIONS;
if (!window.navTitles) window.navTitles = {};