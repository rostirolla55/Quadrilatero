// ====================================================================
// BLOCCO UNO (REVISIONATO) - CONFIGURAZIONE E UTILITY
// ====================================================================

// 1. IMPORTAZIONI FIREBASE (Standard 11.6.1)
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const APP_VERSION = '1.3.00 - Integrata logica Firebase e Cronologia';

// 2. GESTIONE LINGUA
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'Quadrilatero_lastLang';
// Recupero l'ultima lingua o default 'it'
let currentLang = localStorage.getItem(LAST_LANG_KEY) || 'it';

// 3. CONFIGURAZIONE FIREBASE (Usa costanti globali fornite dall'ambiente)
const app_id = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};

// Inizializzazione Servizi
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Stato Utente
let currentUser = null;
let isAuthReady = false;

// 4. COORDINATE POI (Mantenute dal tuo originale)
// ===========================================
// DATI: Punti di Interesse GPS (DA COMPILARE)
// ===========================================
// Attenzione le coordinate sono della zona QUADDRILATERO
// in C:\Users\User\Documents\salvataggi_github\POIA_LOCATIONS_Quadrilatero_js.txt
const notificationSound = new Audio('assets/audio/drin.mp3');
const POIS_LOCATIONS = [
    { id: 'manifattura', lat: 44.498910, lon: 11.342241, distanceThreshold: 50 },
    { id: 'pittoricarracci', lat: 44.50085, lon: 11.33610, distanceThreshold: 50 },
    { id: 'cavaticcio', lat: 44.50018, lon: 11.33807, distanceThreshold: 50 },
    { id: 'bsmariamaggiore', lat: 44.49806368372069, lon: 11.34192628931731, distanceThreshold: 50 },
    { id: 'chiesasancarlo', lat: 44.50100929028893, lon: 11.3409277679376, distanceThreshold: 50 },
    // ** MARKER: START NEW POIS **
    // Lapide_Grazia.jpg
    { id: 'graziaxx', lat: 44.5006638888889, lon: 11.3407694444444, distanceThreshold: 50 },
    // Pugliole.jpg
    { id: 'pugliole', lat: 44.5001944444444, lon: 11.3399861111111, distanceThreshold: 50 },
    // Casa_Carracci_Portone.jpg
    { id: 'carracci', lat: 44.4999972222222, lon: 11.3403888888889, distanceThreshold: 50 },
    // ViaGalliera79.jpg 44.501514, 11.343557
    { id: 'chiesasbene', lat: 44.501514, lon: 11.343557, distanceThreshold: 120 },
    // Piazzetta Pioggia da Galliera 44.498910, 11.342241
    { id: 'chiesapioggia', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    // Paesaggio con San Bartolomeo Alfonso Lombardi -  44.498910, 11.342241
    { id: 'pioggia1', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    // Scultura San Bartolomeo - 44.498910, 11.342241
    { id: 'pioggia2', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    // Opera di Agostino Carracci - 44.498910, 11.342241
    { id: 'pioggia3', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    // Tanari_11.jpg
    { id: 'lastre', lat: 44.49925278, lon: 11.34074444, distanceThreshold: 50 }
];

// ===========================================
// FUNZIONI UTILITY (CON AGGIUNTE PER FIREBASE)
// ===========================================

/**
 * Ottiene l'ID della pagina corrente per caricamento JSON e Cronologia
 */
const getCurrentPageId = () => {
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1);
    if (fileName === '' || fileName.startsWith('index')) {
        return 'home';
    }
    return fileName.replace(/-[a-z]{2}\.html/i, '').replace('.html', '').toLowerCase();
};

/**
 * Funzione per riprodurre il suono
 * Nota: I browser moderni bloccano l'audio se l'utente non ha interagito 
 * almeno una volta con la pagina (un click ovunque).
 */
function playNotification() {
    notificationSound.play().catch(error => {
        console.warn("Riproduzione audio bloccata dal browser. L'utente deve interagire con la pagina prima.", error);
    });

    // Feedback visivo o vibrazione per dispositivi mobili
    if ("vibrate" in navigator) {
        navigator.vibrate([300, 100, 300]);
    }
}



/**
 * Carica il contenuto di un file in modo asincrono (Tuo codice originale)
 */
async function fetchFileContent(filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error(`Errore HTTP: ${response.status}`);
        return await response.text();
    } catch (error) {
        console.error(`ERRORE: Caricamento fallito per ${filePath}`, error);
        return `[ERRORE: Contenuto non disponibile]`;
    }
}

// Espongo le funzioni al window per usarle in altri file non-module se necessario
window.getCurrentPageId = getCurrentPageId;
window.fetchFileContent = fetchFileContent;


// ===========================================
// FUNZIONI AUDIO (Corrette per argomenti locali)
// ===========================================

const toggleAudioPlayback = function (audioPlayer, playButton) {
    const currentPlayText = playButton.dataset.playText || "Ascolta";
    const currentPauseText = playButton.dataset.pauseText || "Pausa";

    if (audioPlayer.paused) {
        audioPlayer.play();
        playButton.textContent = currentPauseText;
        playButton.classList.replace('play-style', 'pause-style');
    } else {
        audioPlayer.pause();
        playButton.textContent = currentPlayText;
        playButton.classList.replace('pause-style', 'play-style');
    }
};

const handleAudioEnded = function (audioPlayer, playButton) {
    const currentPlayText = playButton.dataset.playText || "Ascolta";
    audioPlayer.currentTime = 0;
    playButton.textContent = currentPlayText;
    playButton.classList.replace('pause-style', 'play-style');
};

/**
 * BLOCCO DUE - GESTIONE PUNTI DI INTERESSE (POI)
 * Gestisce il calcolo delle distanze e la generazione del menu dinamico.
 */

const formatDistance = (distance) => {
    if (!Number.isFinite(distance)) return '–';
    if (distance < 0) distance = Math.abs(distance);
    if (distance < 1000) {
        return `${Math.round(distance)} m`;
    }
    return `${parseFloat((distance / 1000).toFixed(1))} km`;
};

/**
 * Aggiorna il menu dei POI vicini basandosi sulla posizione utente.
 * @param {Array} locations - Array di oggetti POI dal database.
 * @param {number} userLat - Latitudine utente.
 * @param {number} userLon - Longitudine utente.
 * @param {string} userLang - Lingua corrente (it, en, es, fr).
 * @param {Object} allPageData - Oggetto contenente i testi tradotti di tutte le pagine.
 */
function updatePoiMenu(locations, userLat, userLon, userLang, allPageData) {
    const nearbyLocations = [];
    const nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    if (!locations || typeof calculateDistance !== 'function') {
        console.warn("Dati POI mancanti o funzione calculateDistance non definita.");
        return;
    }

    // 1. Calcola la distanza e filtra in base alla soglia specifica del POI
    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);

        // Soglia dinamica: usa quella del POI o un default di 50m
        const threshold = location.distanceThreshold || 50;

        if (distance <= threshold) {
            nearbyLocations.push({
                ...location,
                distance: distance
            });
        }
    });

    // 2. Ordina per distanza crescente e rimuovi eventuali duplicati ID
    nearbyLocations.sort((a, b) => a.distance - b.distance);
    const uniquePois = [...new Map(nearbyLocations.map(item => [item['id'], item])).values()];

    // 3. Genera l'HTML del menu
    let menuHtml = '';

    if (uniquePois.length > 0) {
        let listItems = '';

        uniquePois.forEach(poi => {
            const poiContent = allPageData ? allPageData[poi.id] : null;

            // Recupera il titolo tradotto, pulito da spazi
            const displayTitle = (poiContent && poiContent.pageTitle)
                ? poiContent.pageTitle.trim()
                : `[Titolo: ${poi.id}]`;

            // Costruzione URL (es: museo-en.html o museo-it.html)
            const langSuffix = userLang === 'it' ? '-it' : `-${userLang}`;
            const href = `${poi.id}${langSuffix}.html`;

            listItems += `<li><a href="${href}" class="poi-link-item">${displayTitle} <span class="poi-distance">(${poi.distance.toFixed(0)}m)</span></a></li>`;
        });

        menuHtml = `<ul class="poi-links">${listItems}</ul>`;

    } else {
        // Fallback: Nessun POI trovato
        let maxThreshold = locations.reduce((max, loc) => Math.max(max, loc.distanceThreshold || 50), 0);
        let noPoiMessage;

        switch (userLang) {
            case 'es': noPoiMessage = `No se encontraron puntos de interés dentro de ${maxThreshold}m. <br><br> Pulse de nuevo el botón para cerrar.`; break;
            case 'en': noPoiMessage = `No Points of Interest found within ${maxThreshold}m. <br><br> Press the button again to close.`; break;
            case 'fr': noPoiMessage = `Aucun point d'intérêt trouvé à moins de ${maxThreshold}m. <br><br> Appuyez à nouveau pour fermer.`; break;
            case 'it':
            default: noPoiMessage = `Nessun Punto di Interesse trovato entro ${maxThreshold}m.<br><br> Premere di nuovo il bottone per chiudere.`; break;
        }

        menuHtml = `<div class="no-poi-alert" style="color:#e53e3e; padding: 20px; text-align: center; font-weight: 500;">${noPoiMessage}</div>`;
    }

    // 4. Iniezione nel DOM
    if (nearbyMenuPlaceholder) {
        nearbyMenuPlaceholder.innerHTML = menuHtml;
    }
}
// BLOCCO DUE - FINE 
// BLOCCO TRE - INIZIO 
/**
 * BLOCCO TRE - CARICAMENTO DINAMICO DEI CONTENUTI E TRADUZIONI
 * Gestisce l'iniezione dei testi, dei frammenti HTML esterni e degli asset multimediali.
 */

async function loadContent(lang) {
    document.documentElement.lang = lang;

    try {
        const pageId = getCurrentPageId();
        // Carica il dizionario delle traduzioni per la lingua selezionata
        const response = await fetch(`data/translations/${lang}/texts.json`);

        if (!response.ok) {
            console.error(`File di traduzione non trovato per la lingua: ${lang}. Fallback su 'it'.`);
            if (lang !== 'it') {
                loadContent('it');
                return;
            }
            throw new Error(`Impossibile caricare i dati per ${lang}.`);
        }

        const data = await response.json();
        const pageData = data[pageId];

        // Se la pagina specifica non esiste nel JSON, mostra un errore amichevole
        if (!pageData) {
            console.warn(`Dati non trovati per la chiave pagina: ${pageId} in lingua: ${lang}.`);
            updateTextContent('pageTitle', `[Errore Contenuto: ${pageId}]`);
            document.body.classList.add('content-loaded');
            return;
        }

        // ====================================================================
        // LOGICA CARICAMENTO ASINCRONO FRAMMENTI (FILE .txt o .html esterni)
        // ====================================================================
        const fragmentPromises = [];
        const textKeysToUpdate = ['mainText', 'mainText1', 'mainText2', 'mainText3', 'mainText4', 'mainText5'];

        for (const key of textKeysToUpdate) {
            const value = pageData[key];

            // isFilePath deve essere una funzione che controlla se la stringa termina con .txt o .html
            if (value && isFilePath(value)) {
                const fullPath = "text_files/" + value;
                console.log(`Caricamento frammento esterno per ${key}: ${fullPath}`);

                // fetchFileContent deve gestire il recupero del testo grezzo dal file
                const promise = fetchFileContent(fullPath).then(content => ({ key, content }));
                fragmentPromises.push(promise);
            } else if (value !== undefined) {
                // Se è testo normale già presente nel JSON, lo risolviamo subito
                fragmentPromises.push(Promise.resolve({ key, content: value }));
            }
        }

        // Attende la risoluzione di tutte le fetch dei file esterni
        const fragmentResults = await Promise.all(fragmentPromises);

        // Sovrascrive i puntatori ai file con il contenuto reale scaricato
        fragmentResults.forEach(item => {
            pageData[item.key] = item.content;
        });
        // ====================================================================

        // AGGIORNAMENTO MENU DI NAVIGAZIONE
        const navBarMain = document.getElementById('navBarMain');
        if (data.nav && navBarMain) {
            const langSuffix = lang === 'it' ? '-it' : `-${lang}`;

            const navLinksData = [
                { id: 'navHome', key: 'navHome', base: 'index' },
                { id: 'navCarracci', key: 'navCarracci', base: 'carracci' },
                { id: 'navLastre', key: 'navLastre', base: 'lastre' },
                { id: 'navPugliole', key: 'navPugliole', base: 'pugliole' },
                { id: 'navGraziaxx', key: 'navGraziaxx', base: 'graziaxx' },
                { id: 'navChiesaSBene', key: 'navChiesaSBene', base: 'chiesasbene' },
                { id: 'navPioggia1', key: 'navPioggia1', base: 'pioggia1' },
                { id: 'navPioggia2', key: 'navPioggia2', base: 'pioggia2' },
                { id: 'navPioggia3', key: 'navPioggia3', base: 'pioggia3' },
                { id: 'navManifattura', key: 'navManifattura', base: 'manifattura' },
                { id: 'navPittoriCarracci', key: 'navPittoriCarracci', base: 'pittoricarracci' },
                { id: 'navbsmariamaggiore', key: 'navbsmariamaggiore', base: 'bsmariamaggiore' },
                { id: 'navchiesasancarlo', key: 'navchiesasancarlo', base: 'chiesasancarlo' },
                // ** MARKER: START NEW NAV LINKS **
                { id: 'navCavaticcio', key: 'navCavaticcio', base: 'cavaticcio' }
            ];

            navLinksData.forEach(link => {
                const el = document.getElementById(link.id);
                if (el) {
                    el.href = `${link.base}${langSuffix}.html`;
                    if (data.nav[link.key]) el.textContent = data.nav[link.key];
                }
            });
        }

        // AGGIORNAMENTO ELEMENTI TESTATA
        updateTextContent('pageTitle', pageData.pageTitle);
        updateHTMLContent('headerTitle', pageData.pageTitle);

        const headerImage = document.getElementById('headImage');
        if (headerImage && pageData.headImage) {
            headerImage.src = `public/images/${pageData.headImage}`;
            headerImage.alt = pageData.pageTitle || "Header";
        }

        // AGGIORNAMENTO CORPO DEL TESTO (Main Text 0-5)
        updateHTMLContent('mainText', pageData.mainText || '');
        for (let i = 1; i <= 5; i++) {
            updateHTMLContent(`mainText${i}`, pageData[`mainText${i}`] || '');
        }

        // AGGIORNAMENTO INFO FOOTER
        if (pageData.sourceText) updateTextContent('infoSource', `Fonte: ${pageData.sourceText}`);
        if (pageData.creationDate) updateTextContent('infoCreatedDate', `Data: ${pageData.creationDate}`);
        if (pageData.lastUpdate) updateTextContent('infoUpdatedDate', `Aggiornamento: ${pageData.lastUpdate}`);

        // GESTIONE AUDIO
        const audioPlayer = document.getElementById('audioPlayer');
        const playBtn = document.getElementById('playAudio');

        if (audioPlayer && playBtn && pageData.audioSource) {
            audioPlayer.src = `Assets/Audio/${pageData.audioSource}`;
            audioPlayer.load();
            playBtn.textContent = pageData.playAudioButton;
            playBtn.dataset.playText = pageData.playAudioButton;
            playBtn.dataset.pauseText = pageData.pauseAudioButton;
            playBtn.style.display = 'inline-block';
        } else if (playBtn) {
            playBtn.style.display = 'none';
        }

        // AGGIORNAMENTO IMMAGINI DINAMICHE
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

        // AVVIO GEOLOCALIZZAZIONE (Passando l'intero oggetto traduzioni per i menu POI)
        if (typeof startGeolocation === 'function') {
            startGeolocation(data);
        }

        // Rende visibile il contenuto (rimuovendo eventuali loader o skeleton)
        document.body.classList.add('content-loaded');
        console.log(`✅ Pagina "${pageId}" caricata in lingua: ${lang}`);

    } catch (error) {
        console.error('Errore critico durante loadContent:', error);
        document.body.classList.add('content-loaded');
    }
}// BLOCCO TRE - FINE 
// BLOCCO QUATTRO - INIZIO 
/**
 * BLOCCO QUATTRO - UTILITY GPS, CALCOLO DISTANZE E GESTIONE PROSSIMITÀ
 * Include la gestione della cronologia e le notifiche di prossimità (campanello).
 */

// Stato locale per la cronologia dei luoghi visitati
const visitedPois = new Set();

/**
 * Calcola la distanza tra due punti geografici (Formula di Haversine)
 * @returns {number} Distanza in metri
 */
const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3; // Raggio della terra in metri
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
};

/**
 * Gestisce la logica di notifica (Campanello) e aggiornamento cronologia
 */
const triggerPoiNotification = (poiId, poiName) => {
    if (!visitedPois.has(poiId)) {
        visitedPois.add(poiId);

        // Effetto "Campanello": Feedback visivo/logico
        console.warn(`🔔 NOTIFICA: Sei vicino a "${poiName}"!`);

        // Qui potresti attivare una classe CSS per far lampeggiare il tasto POI
        if (nearbyPoiButton) {
            nearbyPoiButton.classList.add('notification-ring');
            setTimeout(() => nearbyPoiButton.classList.remove('notification-ring'), 3000);
        }

        // Salvataggio in cronologia locale (opzionale: localStorage)
        saveToHistory(poiId, poiName);
    }
};

const saveToHistory = (id, name) => {
    const history = JSON.parse(localStorage.getItem('trekking_history') || '[]');
    if (!history.find(item => item.id === id)) {
        history.push({ id, name, timestamp: new Date().toISOString() });
        localStorage.setItem('trekking_history', JSON.stringify(history));
    }
};

/**
 * Controlla la vicinanza dell'utente ai punti di interesse definiti
 */
const checkProximity = (position, allPageData) => {
    if (!position || !position.coords) {
        console.error("DEBUG CRITICO: Oggetto posizione non valido.");
        return;
    }

    const userLat = position.coords.latitude;
    const userLon = position.coords.longitude;
    const userLang = typeof currentLang !== 'undefined' ? currentLang : 'it';

    console.warn(`[POI DEBUG] Posizione: Lat=${userLat.toFixed(6)}, Lon=${userLon.toFixed(6)}`);

    // Logica del campanello: se siamo entro 50 metri da un POI, attiviamo la notifica
    if (typeof POIS_LOCATIONS !== 'undefined') {
        POIS_LOCATIONS.forEach(poi => {
            const dist = calculateDistance(userLat, userLon, poi.lat, poi.lon);
            if (dist < 50) { // Raggio di 50 metri
                triggerPoiNotification(poi.id, poi.id);
            }
            // Esempio: Se siamo a meno di 50 metri e non abbiamo ancora suonato per questo POI
            if (dist < 50 && !poi.notified) {

                // --- QUI RICHIAMI LA FUNZIONE ---
                playNotification();

                console.log("Notifica attivata per: " + poi.name);
                poi.notified = true; // Impedisce al drin di ripetersi ogni secondo
            }
        });
    }

    // Aggiorna l'interfaccia del menu POI
    if (nearbyPoiButton) {
        nearbyPoiButton.style.display = 'block';
        if (typeof updatePoiMenu === 'function') {
            updatePoiMenu(POIS_LOCATIONS, userLat, userLon, userLang, allPageData);
        }
    }
};

/**
 * Avvia il monitoraggio GPS continuo
 */
const startGeolocation = (allPageData) => {
    // Posizione di test (es. Bologna, Chiesa della Pioggia)
    const debugPosition = {
        coords: {
            latitude: 44.498910,
            longitude: 11.342241
        }
    };

    if (navigator.geolocation) {
        console.info("Avvio monitoraggio GPS...");

        navigator.geolocation.watchPosition(
            (position) => {
                const FORCE_DEBUG = false; // Impostare a true per simulare la posizione in ufficio
                const posToUse = FORCE_DEBUG ? debugPosition : position;
                checkProximity(posToUse, allPageData);
            },
            (error) => {
                console.warn(`GPS REALE FALLITO (${error.code}): ${error.message}. Uso simulazione.`);
                if (nearbyPoiButton) nearbyPoiButton.style.display = 'block';
                checkProximity(debugPosition, allPageData);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        console.error("Geolocalizzazione non supportata. Modalità simulazione attiva.");
        if (nearbyPoiButton) nearbyPoiButton.style.display = 'block';
        checkProximity(debugPosition, allPageData);
    }
};
// BLOCCO QUATTRO - FINE
// 
// ===========================================
// BLOCCO CINQUE - FUNZIONI LINGUA E UI
// ===========================================

function updateLanguageSelectorActiveState(lang) {
    document.querySelectorAll('.language-selector button').forEach(button => {
        if (button.getAttribute('data-lang') === lang) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

function handleLanguageChange(event) {
    const newLang = event.currentTarget.getAttribute('data-lang');
    if (newLang && LANGUAGES.includes(newLang) && newLang !== currentLang) {
        localStorage.setItem(LAST_LANG_KEY, newLang);

        let fileBase = getCurrentPageId();
        if (fileBase === 'home') fileBase = 'index';

        // Reindirizzamento al file corrispondente (es: index-en.html)
        const newPath = `${fileBase}-${newLang}.html`;
        document.location.href = newPath;
    }
}

function initEventListeners(lang) {
    const menuToggle = document.querySelector('.menu-toggle');
    const navBarMain = document.getElementById('navBarMain');
    const body = document.body;

    // Hamburger Menu Principale
    if (menuToggle && navBarMain && !menuToggle.dataset.listenerAttached) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            navBarMain.classList.toggle('active');
            body.classList.toggle('menu-open');
            if (nearbyMenuPlaceholder) nearbyMenuPlaceholder.classList.remove('poi-active');
        });

        navBarMain.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                menuToggle.classList.remove('active');
                navBarMain.classList.remove('active');
                body.classList.remove('menu-open');
            }
        });
        menuToggle.dataset.listenerAttached = 'true';
    }

    // Menu POI Vicini (Pulsante Verde)
    if (nearbyPoiButton && nearbyMenuPlaceholder && !nearbyPoiButton.dataset.listenerAttached) {
        nearbyPoiButton.addEventListener('click', () => {
            nearbyMenuPlaceholder.classList.toggle('poi-active');
            if (menuToggle && navBarMain) {
                menuToggle.classList.remove('active');
                navBarMain.classList.remove('active');
            }
            body.classList.toggle('menu-open', nearbyMenuPlaceholder.classList.contains('poi-active'));
        });

        nearbyMenuPlaceholder.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                nearbyMenuPlaceholder.classList.remove('poi-active');
                body.classList.remove('menu-open');
            }
        });
        nearbyPoiButton.dataset.listenerAttached = 'true';
    }

    // Audio Player
    const localAudioPlayer = document.getElementById('audioPlayer');
    const localPlayButton = document.getElementById('playAudio');
    if (localAudioPlayer && localPlayButton && !localPlayButton.dataset.listenerAttached) {
        localPlayButton.addEventListener('click', () => toggleAudioPlayback(localAudioPlayer, localPlayButton));
        localAudioPlayer.addEventListener('ended', () => handleAudioEnded(localAudioPlayer, localPlayButton));
        localPlayButton.dataset.listenerAttached = 'true';
    }

    // Selettore Lingua
    document.querySelectorAll('.language-selector button').forEach(button => {
        button.addEventListener('click', handleLanguageChange);
    });
}

// ===========================================
// BLOCCO SEI - LOGICA NAVIGAZIONE DINAMICA (POI VICINI)
// ===========================================

async function updateNearbyMenu(lang) {
    if (!nearbyMenuPlaceholder) return;

    try {
        const coords = await getCurrentLocation();
        const nearbyPOIs = getNearbyPOIs(coords.latitude, coords.longitude, POI_DATA);

        if (nearbyPOIs.length > 0) {
            let html = `<ul class="nearby-list">`;
            nearbyPOIs.forEach(poi => {
                // Genera link tipo "nomepoi-it.html"
                const poiLink = `${poi.id}-${lang}.html`;
                html += `<li><a href="${poiLink}">${poi.label[lang] || poi.label['it']} (${poi.distance.toFixed(0)}m)</a></li>`;
            });
            html += `</ul>`;
            nearbyMenuPlaceholder.innerHTML = html;
            if (nearbyPoiButton) nearbyPoiButton.style.display = 'flex';
        } else {
            nearbyMenuPlaceholder.innerHTML = `<p>Nessun punto di interesse nelle immediate vicinanze.</p>`;
        }
    } catch (error) {
        console.warn("Impossibile aggiornare menu vicini:", error);
        nearbyMenuPlaceholder.innerHTML = `<p>Attiva la posizione per vedere i punti vicini.</p>`;
    }
}

// ===========================================
// BLOCCO SETTE - PUNTO DI INGRESSO (DOM LOADED)
// ===========================================

document.addEventListener('DOMContentLoaded', () => {
    console.info(`🌍 Versione in esecuzione: ${APP_VERSION}`);

    // 1. ASSEGNAZIONE VARIABILI GLOBALI
    nearbyPoiButton = document.getElementById('nearbyPoiButton');
    nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    // 2. DETERMINAZIONE LINGUA CORRENTE
    let finalLang = 'it';
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    if (savedLang && LANGUAGES.includes(savedLang)) finalLang = savedLang;

    const urlPath = document.location.pathname;
    const langMatch = urlPath.match(/-([a-z]{2})\.html/);
    if (langMatch && LANGUAGES.includes(langMatch[1])) {
        finalLang = langMatch[1];
        localStorage.setItem(LAST_LANG_KEY, finalLang);
    }

    currentLang = finalLang;
    document.documentElement.lang = currentLang;

    // 3. INIZIALIZZAZIONE UI E CONTENUTI
    updateLanguageSelectorActiveState(currentLang);
    initEventListeners(currentLang);
    loadContent(currentLang);

    // 4. ATTIVAZIONE GEOLOCALIZZAZIONE (Novità Blocco 6)
    updateNearbyMenu(currentLang);

    // 5. ANALYTICS
    if (typeof gtag === 'function') {
        gtag('event', 'page_view', {
            'page_title': document.title,
            'page_path': window.location.pathname,
            'lingua_pagina': currentLang
        });
    }


    // 6. FIREBASE (Opzionale)
    if (typeof initializeApp !== 'undefined' && typeof firebaseConfig !== 'undefined') {
        const app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        auth = getAuth(app);

        signInAnonymously(auth).then(() => {
            console.log("Firebase: Autenticazione anonima completata.");
        }).catch(err => console.error("Firebase Auth Error:", err));
    }
    console.log("App pronta: Inizializzazione dati e GPS...");
});