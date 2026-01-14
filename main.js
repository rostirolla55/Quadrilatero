// ====================================================================
// BLOCCO UNO (REVISIONATO) - CONFIGURAZIONE E UTILITY
// ====================================================================

// 1. IMPORTAZIONI FIREBASE (Standard 11.6.1)
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp, query, orderBy } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const APP_VERSION = '1.3.00 - Integrata logica Firebase e Cronologia';

// 2. GESTIONE LINGUA
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'Quadrilatero_lastLang';
let currentLang = localStorage.getItem(LAST_LANG_KEY) || 'it';

// 3. CONFIGURAZIONE FIREBASE & VARIABILI GLOBALI
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};

// Dichiarazione globale dei servizi (accessibili da tutto il file)
let app, auth, db;
let currentUser = null;
let isAuthReady = false;

// 4. COORDINATE POI (Originali)
const notificationSound = new Audio('assets/audio/drin.mp3');
const POIS_LOCATIONS = [
    { id: 'manifattura', lat: 44.498910, lon: 11.342241, distanceThreshold: 50 },
    { id: 'pittoricarracci', lat: 44.50085, lon: 11.33610, distanceThreshold: 50 },
    { id: 'cavaticcio', lat: 44.50018, lon: 11.33807, distanceThreshold: 50 },
    { id: 'bsmariamaggiore', lat: 44.49806368372069, lon: 11.34192628931731, distanceThreshold: 50 },
    { id: 'chiesasancarlo', lat: 44.50100929028893, lon: 11.3409277679376, distanceThreshold: 50 },
    { id: 'graziaxx', lat: 44.5006638888889, lon: 11.3407694444444, distanceThreshold: 50 },
    { id: 'pugliole', lat: 44.5001944444444, lon: 11.3399861111111, distanceThreshold: 50 },
    { id: 'carracci', lat: 44.4999972222222, lon: 11.3403888888889, distanceThreshold: 50 },
    { id: 'chiesasbene', lat: 44.501514, lon: 11.343557, distanceThreshold: 120 },
    { id: 'chiesapioggia', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    { id: 'pioggia1', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    { id: 'pioggia2', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    { id: 'pioggia3', lat: 44.498910, lon: 11.342241, distanceThreshold: 120 },
    { id: 'lastre', lat: 44.49925278, lon: 11.34074444, distanceThreshold: 50 }
];

// 5. INIZIALIZZAZIONE APP & FIREBASE
async function startApp() {
    try {
        // Inizializzazione Servizi (Assegnazione alle variabili globali)
        app = initializeApp(firebaseConfig);
        auth = getAuth(app);
        db = getFirestore(app);

        // Autenticazione (Fondamentale per i permessi Firestore)
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
            await signInWithCustomToken(auth, __initial_auth_token);
        } else {
            await signInAnonymously(auth);
        }

        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUser = user;
                isAuthReady = true;
                console.log("Firebase Pronto - UID:", user.uid);
                // Innesca il caricamento della cronologia o altre funzioni real-time qui
                if (window.inizializzaLogicaFirebase) window.inizializzaLogicaFirebase();
            }
        });

    } catch (e) {
        console.error("Errore inizializzazione Firebase:", e);
    }

    // Logica di avvio interfaccia
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) loadingScreen.style.display = 'none';

    // Chiamata alla tua funzione di setup mappa (assicurati che esista nel resto del file)
    if (typeof setupMap === 'function') setupMap();
}

// Avvio
startApp();

// ===========================================
// FUNZIONI UTILITY (Originali + Export)
// ===========================================

const getCurrentPageId = () => {
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1);
    if (fileName === '' || fileName.startsWith('index')) return 'home';
    return fileName.replace(/-[a-z]{2}\.html/i, '').replace('.html', '').toLowerCase();
};

function playNotification() {
    notificationSound.play().catch(error => {
        console.warn("Audio bloccato: richiede interazione utente.", error);
    });
    if ("vibrate" in navigator) navigator.vibrate([300, 100, 300]);
}

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

// Esposizione globale
window.getCurrentPageId = getCurrentPageId;
window.fetchFileContent = fetchFileContent;
window.toggleAudioPlayback = toggleAudioPlayback;
window.handleAudioEnded = handleAudioEnded;
window.playNotification = playNotification;

/**
 * BLOCCO DUE - GESTIONE PUNTI DI INTERESSE (POI) E SEGNALI
 * Gestisce il calcolo delle distanze, il menu dinamico e l'invio dei segnali a Firestore.
 */

// Importa le funzioni di Firestore (da aggiungere agli import iniziali se non presenti)
// import { collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";

const formatDistance = (distance) => {
    if (!Number.isFinite(distance)) return '–';
    if (distance < 0) distance = Math.abs(distance);
    if (distance < 1000) {
        return `${Math.round(distance)} m`;
    }
    return `${parseFloat((distance / 1000).toFixed(1))} km`;
};

/**
 * Gestisce l'invio del segnale "Drin" a Firestore.
 * @param {Object} poi - Il punto di interesse più vicino.
 * @param {string} userId - L'ID dell'utente autenticato.
 */
async function sendDrinSignal(poi, userId) {
    if (typeof db === 'undefined' || !userId) return;

    try {
        // RULE 1: Percorso obbligatorio per dati pubblici
        const signalsRef = collection(db, 'artifacts', appId, 'public', 'data', 'signals');

        await addDoc(signalsRef, {
            poiId: poi.id,
            poiTitle: poi.title || poi.id,
            userId: userId,
            timestamp: new Date().toISOString(), // In alternativa serverTimestamp() se importato
            type: 'drin'
        });

        console.log(`Segnale inviato per: ${poi.id}`);
    } catch (error) {
        console.error("Errore nell'invio del segnale:", error);
    }
}

/**
 * Funzione principale attivata dal tasto "Drin" (Campanella).
 * Coordina il controllo posizione, l'invio dati e il feedback UI.
 */
async function handleDrinAction(locations, userLat, userLon, user) {
    if (!locations || !userLat || !userLon) return;

    // Trova il POI più vicino entro la soglia
    let closestPoi = null;
    let minDistance = Infinity;

    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);
        const threshold = location.distanceThreshold || 50;

        if (distance <= threshold && distance < minDistance) {
            minDistance = distance;
            closestPoi = location;
        }
    });

    if (closestPoi && user) {
        // Se siamo vicino a un POI, invia il segnale al database
        await sendDrinSignal(closestPoi, user.uid);

        // Esegui qui il feedback visivo (animazione campanella, suoneria, etc.)
        // es: triggerVisualDrin(closestPoi);
    } else {
        // Feedback: "Troppo lontano per suonare"
        console.log("Nessun POI abbastanza vicino per inviare il segnale.");
    }
}

/**
 * Aggiorna il menu dei POI vicini basandosi sulla posizione utente.
 */
function updatePoiMenu(locations, userLat, userLon, userLang, allPageData) {
    const nearbyLocations = [];
    const nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    if (!locations || typeof calculateDistance !== 'function') {
        console.warn("Dati POI mancanti o funzione calculateDistance non definita.");
        return;
    }

    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);
        const threshold = location.distanceThreshold || 50;

        if (distance <= threshold) {
            nearbyLocations.push({
                ...location,
                distance: distance
            });
        }
    });

    nearbyLocations.sort((a, b) => a.distance - b.distance);
    const uniquePois = [...new Map(nearbyLocations.map(item => [item['id'], item])).values()];

    let menuHtml = '';

    if (uniquePois.length > 0) {
        let listItems = '';

        uniquePois.forEach(poi => {
            const poiContent = allPageData ? allPageData[poi.id] : null;
            const displayTitle = (poiContent && poiContent.pageTitle)
                ? poiContent.pageTitle.trim()
                : `[Titolo: ${poi.id}]`;

            const langSuffix = userLang === 'it' ? '-it' : `-${userLang}`;
            const href = `${poi.id}${langSuffix}.html`;

            listItems += `<li><a href="${href}" class="poi-link-item">${displayTitle} <span class="poi-distance">(${poi.distance.toFixed(0)}m)</span></a></li>`;
        });

        menuHtml = `<ul class="poi-links">${listItems}</ul>`;

    } else {
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

    if (nearbyMenuPlaceholder) {
        nearbyMenuPlaceholder.innerHTML = menuHtml;
    }
}
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

/**
 * Gestisce l'invio del segnale Drin a Firestore se l'utente è vicino a un POI.
 */
async function handleDrinClick() {
    // Verifichiamo di avere posizione e dati necessari
    if (typeof userLat === 'undefined' || typeof userLon === 'undefined' || !locations) {
        console.warn("Posizione non disponibile o POI non caricati.");
        return;
    }

    // Cerchiamo il POI più vicino entro la sua soglia (utilizza la logica del Blocco 2)
    let closestPoi = null;
    let minDistance = Infinity;

    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);
        const threshold = location.distanceThreshold || 50;

        if (distance <= threshold && distance < minDistance) {
            minDistance = distance;
            closestPoi = location;
        }
    });

    if (closestPoi) {
        // Se siamo vicino a un POI, inviamo il segnale a Firestore
        // Nota: Assicurati che 'auth' e 'db' siano inizializzati globalmente
        const user = typeof auth !== 'undefined' ? auth.currentUser : null;
        const uid = user ? user.uid : "anonymous";

        try {
            const signalsRef = collection(db, 'artifacts', appId, 'public', 'data', 'signals');
            await addDoc(signalsRef, {
                poiId: closestPoi.id,
                userId: uid,
                timestamp: new Date().toISOString(),
                type: 'drin'
            });

            // Feedback visivo: animazione campanella
            const drinBtn = document.getElementById('drinButton');
            if (drinBtn) {
                drinBtn.classList.add('drin-animation');
                setTimeout(() => drinBtn.classList.remove('drin-animation'), 1000);
            }
            
            console.log("Drin inviato con successo per:", closestPoi.id);
        } catch (e) {
            console.error("Errore invio segnale:", e);
        }
    } else {
        console.log("Troppo lontano dai punti di interesse per suonare.");
        // Opzionale: mostra un piccolo messaggio UI all'utente
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
            if (typeof nearbyMenuPlaceholder !== 'undefined' && nearbyMenuPlaceholder) {
                nearbyMenuPlaceholder.classList.remove('poi-active');
            }
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
    if (typeof nearbyPoiButton !== 'undefined' && nearbyPoiButton && !nearbyPoiButton.dataset.listenerAttached) {
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

    // --- NUOVO: Gestione Pulsante Drin (Campanella) ---
    const drinButton = document.getElementById('drinButton');
    if (drinButton && !drinButton.dataset.listenerAttached) {
        drinButton.addEventListener('click', handleDrinClick);
        drinButton.dataset.listenerAttached = 'true';
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

// ===========================================
// BLOCCO SETTE - PUNTO DI INGRESSO (DOM LOADED)
// ===========================================

document.addEventListener('DOMContentLoaded', async () => {
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

    try {
        await loadContent(currentLang);
    } catch (err) {
        console.warn("Errore durante il caricamento dei contenuti:", err);
    }

    // 4. ATTIVAZIONE GEOLOCALIZZAZIONE
    updateNearbyMenu(currentLang);

    // 5. ANALYTICS (Safe call)
    if (typeof gtag === 'function') {
        gtag('event', 'page_view', {
            'page_title': document.title,
            'page_path': window.location.pathname,
            'lingua_pagina': currentLang
        });
    }

    // 6. FIREBASE - GESTIONE ERRORI PER EVITARE BLOCCHI
    // Se la configurazione è mancante o errata, l'app continuerà a funzionare
    if (typeof initializeApp !== 'undefined' && typeof firebaseConfig !== 'undefined') {
        try {
            // Controlliamo che la configurazione abbia almeno una chiave API valida
            if (!firebaseConfig.apiKey || firebaseConfig.apiKey.includes("AIza")) {
                const app = initializeApp(firebaseConfig);
                db = getFirestore(app);
                auth = getAuth(app);

                signInAnonymously(auth).then(() => {
                    console.log("Firebase: Autenticazione anonima completata.");
                }).catch(err => {
                    console.error("Firebase Auth Error (Sign-in):", err.message);
                });
            } else {
                console.warn("Firebase: API Key non valida o mancante nella configurazione.");
            }
        } catch (err) {
            console.error("Firebase Init Error:", err.message);
            // Non rilanciamo l'errore, così l'app non si blocca
        }
    } else {
        console.info("Firebase: Librerie non caricate o configurazione assente.");
    }

    // 7. RIMOZIONE SCHERMATA CARICAMENTO (Fallback di sicurezza)
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
        console.info("Applicazione pronta.");
    }
});