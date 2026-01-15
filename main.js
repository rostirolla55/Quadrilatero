// ====================================================================
// BLOCCO UNO (REVISIONATO) - CONFIGURAZIONE, FIREBASE E UTILITY
// ====================================================================

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, collection, addDoc, serverTimestamp, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// 1. CONFIGURAZIONE CORE
const APP_VERSION = '1.3.00 - Quadrilatero';

// Lettura sicura della configurazione (Risolve l'errore invalid-api-key)
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'quadrilatero-bologna';

// Stato globale
let currentUser = null;
let isAuthReady = false;
let currentLang = localStorage.getItem('Quadrilatero_lastLang') || 'it';

// 2. COORDINATE PUNTI DI INTERESSE (POI)
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

// 3. LOGICA DI AVVIO FIREBASE
async function startAppServices() {
    try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
            await signInWithCustomToken(auth, __initial_auth_token);
        } else {
            await signInAnonymously(auth);
        }

        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUser = user;
                isAuthReady = true;
                const status = document.getElementById('status-label');
                if (status) status.innerText = "Sistema connesso";
                initHistoryListener();
            }
        });
    } catch (e) {
        console.error("Errore inizializzazione Firebase:", e);
    }
}

// 4. FUNZIONI UTILITY
const getCurrentPageId = () => {
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1);
    if (fileName === '' || fileName.startsWith('index')) return 'home';
    return fileName.replace(/-[a-z]{2}\.html/i, '').replace('.html', '').toLowerCase();
};

function playNotification() {
    notificationSound.play().catch(() => console.warn("Audio richiede interazione"));
    if ("vibrate" in navigator) navigator.vibrate([300, 100, 300]);
}

// 5. GESTIONE CRONOLOGIA (Regole 1 e 2)
function initHistoryListener() {
    const historyRef = collection(db, 'artifacts', appId, 'public', 'data', 'access_history');
    onSnapshot(historyRef, (snapshot) => {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        let entries = [];
        snapshot.forEach(doc => entries.push({ id: doc.id, ...doc.data() }));
        entries.sort((a, b) => (b.timestamp?.seconds || 0) - (a.timestamp?.seconds || 0));
        historyList.innerHTML = entries.slice(0, 8).map(entry => `
            <li style="padding: 10px; border-bottom: 1px solid #eee; font-size: 0.85em;">
                <strong style="color: #e53e3e;">🔔 ${entry.pageName}</strong><br>
                <small style="color: #666;">${entry.timestamp ? new Date(entry.timestamp.seconds * 1000).toLocaleString('it-IT') : 'Adesso'}</small>
            </li>
        `).join('') || '<li style="padding:10px; color:#999; text-align:center;">Nessun DRIN.</li>';
    });
}

// 6. FUNZIONE DRIN
async function handleDrin() {
    const feedback = document.getElementById('drin-feedback');
    if (!currentUser) return;
    try {
        const historyRef = collection(db, 'artifacts', appId, 'public', 'data', 'access_history');
        const pageTitle = document.getElementById('pageTitle')?.innerText || document.title;
        await addDoc(historyRef, {
            userId: currentUser.uid,
            pageName: pageTitle,
            timestamp: serverTimestamp()
        });
        if (feedback) {
            feedback.style.color = "green";
            feedback.innerText = "✅ Registrato!";
            setTimeout(() => { if(feedback) feedback.innerText = ""; }, 3000);
        }
        playNotification();
    } catch (error) { console.error("Errore DRIN:", error); }
}

// Esposizione globale e avvio
window.handleDrin = handleDrin;
window.getCurrentPageId = getCurrentPageId;
startAppServices();

/**
 * BLOCCO DUE - GESTIONE PUNTI DI INTERESSE (POI) E SEGNALI
 * Integra il calcolo delle distanze e la gestione dinamica dell'interfaccia.
 */

import { collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

/**
 * Calcola la distanza tra due punti (Formula di Haversine)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Raggio della Terra in metri
    const phi1 = lat1 * Math.PI / 180;
    const phi2 = lat2 * Math.PI / 180;
    const deltaPhi = (lat2 - lat1) * Math.PI / 180;
    const deltaLambda = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
              Math.cos(phi1) * Math.cos(phi2) *
              Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distanza in metri
}

const formatDistance = (distance) => {
    if (!Number.isFinite(distance)) return '–';
    distance = Math.abs(distance);
    if (distance < 1000) return `${Math.round(distance)} m`;
    return `${parseFloat((distance / 1000).toFixed(1))} km`;
};

/**
 * Invia il segnale "Drin" a Firestore (RULE 1 applicata)
 */
async function sendDrinSignal(poi, userId) {
    if (typeof db === 'undefined' || !userId) return;

    try {
        // Percorso obbligatorio per dati pubblici: /artifacts/{appId}/public/data/{collection}
        const signalsRef = collection(db, 'artifacts', appId, 'public', 'data', 'signals');

        await addDoc(signalsRef, {
            poiId: poi.id,
            poiTitle: poi.title || poi.id,
            userId: userId,
            timestamp: serverTimestamp(),
            type: 'drin'
        });

        console.log(`Segnale registrato nel cloud per: ${poi.id}`);
    } catch (error) {
        console.error("Errore nell'invio del segnale:", error);
    }
}

/**
 * Funzione coordinatrice per l'azione della campanella
 */
async function handleDrinAction(locations, userLat, userLon, user) {
    if (!locations || !userLat || !userLon) {
        console.warn("Dati posizione mancanti per il Drin");
        return;
    }

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
        await sendDrinSignal(closestPoi, user.uid);
        // Richiama la funzione audio definita nel Blocco Uno
        if (typeof window.playNotification === 'function') window.playNotification();
        
        return { success: true, poi: closestPoi };
    } else {
        console.log("Sei fuori portata per suonare questo campanello.");
        return { success: false, reason: 'too_far' };
    }
}

/**
 * Aggiorna il menu dei POI vicini nell'interfaccia
 */
function updatePoiMenu(locations, userLat, userLon, userLang, allPageData) {
    const nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');
    if (!nearbyMenuPlaceholder) return;

    const nearbyLocations = [];

    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);
        const threshold = location.distanceThreshold || 100; // Soglia leggermente più ampia per il menu

        if (distance <= threshold) {
            nearbyLocations.push({ ...location, distance });
        }
    });

    nearbyLocations.sort((a, b) => a.distance - b.distance);
    
    // Rimuove duplicati per ID
    const uniquePois = Array.from(new Map(nearbyLocations.map(item => [item.id, item])).values());

    if (uniquePois.length > 0) {
        let listHtml = '<ul class="poi-links" style="list-style:none; padding:0; margin:0;">';
        uniquePois.forEach(poi => {
            const poiContent = allPageData ? allPageData[poi.id] : null;
            const displayTitle = (poiContent && poiContent.pageTitle) ? poiContent.pageTitle : poi.id;
            const langSuffix = userLang === 'it' ? '-it' : `-${userLang}`;
            const href = `${poi.id}${langSuffix}.html`;

            listHtml += `
                <li style="margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                    <a href="${href}" style="text-decoration:none; color:#2d3748; display:flex; justify-content:space-between; align-items:center;">
                        <span>📍 ${displayTitle}</span>
                        <span style="font-size:0.8em; color:#718096; background:#edf2f7; padding:2px 6px; rounded:4px;">
                            ${formatDistance(poi.distance)}
                        </span>
                    </a>
                </li>`;
        });
        listHtml += '</ul>';
        nearbyMenuPlaceholder.innerHTML = listHtml;
    } else {
        const messages = {
            it: "Nessun luogo d'interesse nelle immediate vicinanze.",
            en: "No points of interest nearby.",
            es: "No hay puntos de interés cerca.",
            fr: "Aucun point d'intérêt à proximité."
        };
        const msg = messages[userLang] || messages.it;
        nearbyMenuPlaceholder.innerHTML = `<div style="text-align:center; color:#a0aec0; padding:20px;">${msg}</div>`;
    }
}

// Esposizione per l'utilizzo globale
window.calculateDistance = calculateDistance;
window.handleDrinAction = handleDrinAction;
window.updatePoiMenu = updatePoiMenu;


// ### Cosa ho aggiunto per far funzionare il tuo codice:
// 1.  **Formula di Haversine**: Ho aggiunto la funzione `calculateDistance` completa, altrimenti il menu e il Drin non avrebbero potuto calcolare i metri di distanza.
// 2.  **Integrazione tra blocchi**: Ho collegato `handleDrinAction` alla funzione `playNotification` del Blocco Uno per garantire il feedback sonoro.
// 3.  **Gestione Titoli Fallback**: Se `allPageData` è vuoto, il menu usa l'ID del POI come titolo per evitare link vuoti.
// 4.  **Stile Inline**: Ho aggiunto un minimo di stile CSS inline nel menu per assicurarmi che sia leggibile anche senza un foglio di stile esterno caricato.

// BLOCCO TRE - INIZIO 
/**
 * BLOCCO TRE - CARICAMENTO DINAMICO DEI CONTENUTI E TRADUZIONI
 * Gestisce l'iniezione dei testi, dei frammenti HTML esterni e degli asset multimediali.
 */

// --- FUNZIONI DI SUPPORTO (Helper) ---

/**
 * Determina se una stringa è un percorso a un file esterno
 */
const isFilePath = (str) => {
    if (typeof str !== 'string') return false;
    return str.endsWith('.txt') || str.endsWith('.html');
};

/**
 * Recupera il contenuto testuale di un file esterno con gestione errori
 */
async function fetchFileContent(path) {
    try {
        const response = await fetch(path);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.text();
    } catch (error) {
        console.error(`Errore nel recupero del file ${path}:`, error);
        return `[Errore nel caricamento del frammento: ${path}]`;
    }
}

/**
 * Estrae l'ID della pagina corrente dall'URL (es: index-it.html -> index)
 */
function getCurrentPageId() {
    const path = window.location.pathname;
    const page = path.split("/").pop() || 'index.html';
    // Rimuove l'estensione e il suffisso lingua (es: -it, -en)
    return page.replace(/-(it|en|es|fr)\.html$/, '').replace(/\.html$/, '');
}

/**
 * Aggiorna in modo sicuro il contenuto testuale di un elemento
 */
function updateTextContent(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text || '';
}

/**
 * Aggiorna in modo sicuro il contenuto HTML di un elemento
 */
function updateHTMLContent(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html || '';
}

// --- FUNZIONE PRINCIPALE DI CARICAMENTO ---

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

            if (value && isFilePath(value)) {
                const fullPath = "text_files/" + value;
                console.log(`Caricamento frammento esterno per ${key}: ${fullPath}`);

                const promise = fetchFileContent(fullPath).then(content => ({ key, content }));
                fragmentPromises.push(promise);
            } else if (value !== undefined) {
                fragmentPromises.push(Promise.resolve({ key, content: value }));
            }
        }

        const fragmentResults = await Promise.all(fragmentPromises);

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
        if (typeof window.startGeolocation === 'function') {
            window.startGeolocation(data);
        }

        document.body.classList.add('content-loaded');
        console.log(`✅ Pagina "${pageId}" caricata in lingua: ${lang}`);

    } catch (error) {
        console.error('Errore critico durante loadContent:', error);
        document.body.classList.add('content-loaded');
    }
}

// Esposizione globale
window.loadContent = loadContent;
window.getCurrentPageId = getCurrentPageId;
// BLOCCO TRE - FINE 
// BLOCCO QUATTRO - INIZIO 
/**
 * BLOCCO QUATTRO - UTILITY GPS, CALCOLO DISTANZE E GESTIONE PROSSIMITÀ
 * Gestisce la logica di posizione, notifiche sonore e cronologia.
 * Nota: POIS_LOCATIONS è importato dal Blocco Uno.
 */

// Stato locale per la sessione corrente
const visitedPois = new Set();
const nearbyPoiButton = document.getElementById('nearbyPoiButton');

/**
 * Riproduce un feedback sonoro (Campanello) sintetizzato
 */
const playNotification = () => {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); 
        oscillator.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.5);

        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.5);
    } catch (e) {
        console.warn("Audio Context non supportato o bloccato dal browser.");
    }
};

/**
 * Calcola la distanza tra due punti (Haversine)
 * @returns {number} Distanza in metri
 */
const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3; 
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
};

/**
 * Gestisce la notifica visiva e il salvataggio in cronologia
 */
const triggerPoiNotification = (poiId, poiName) => {
    if (!visitedPois.has(poiId)) {
        visitedPois.add(poiId);

        console.warn(`🔔 PROSSIMITÀ: ${poiName}`);

        if (nearbyPoiButton) {
            nearbyPoiButton.classList.add('notification-ring');
            setTimeout(() => nearbyPoiButton.classList.remove('notification-ring'), 3000);
        }

        saveToHistory(poiId, poiName);
    }
};

/**
 * Salva il passaggio nel localStorage
 */
const saveToHistory = (id, name) => {
    try {
        const history = JSON.parse(localStorage.getItem('trekking_history') || '[]');
        if (!history.find(item => item.id === id)) {
            history.push({ id, name, timestamp: new Date().toISOString() });
            localStorage.setItem('trekking_history', JSON.stringify(history));
        }
    } catch (e) {
        console.error("Errore localStorage:", e);
    }
};

/**
 * Cuore della logica GPS: confronta posizione utente con POI
 */
const checkProximity = (position, allPageData) => {
    if (!position || !position.coords) return;

    const userLat = position.coords.latitude;
    const userLon = position.coords.longitude;
    const userLang = typeof currentLang !== 'undefined' ? currentLang : (document.documentElement.lang || 'it');

    // Verifica la presenza dei dati dal Blocco Uno
    if (typeof POIS_LOCATIONS !== 'undefined' && Array.isArray(POIS_LOCATIONS)) {
        POIS_LOCATIONS.forEach(poi => {
            const dist = calculateDistance(userLat, userLon, poi.lat, poi.lon);
            
            // Soglia di prossimità: 50 metri
            if (dist < 50) {
                triggerPoiNotification(poi.id, poi.name || poi.id);
                
                if (!poi.notified) {
                    playNotification();
                    poi.notified = true; 
                }
            } else if (dist > 100) {
                // Reset per permettere una nuova notifica se l'utente torna indietro
                poi.notified = false;
            }
        });
    }

    // Aggiornamento UI
    if (nearbyPoiButton) {
        nearbyPoiButton.style.display = 'block';
        if (typeof window.updatePoiMenu === 'function') {
            window.updatePoiMenu(POIS_LOCATIONS, userLat, userLon, userLang, allPageData);
        }
    }
};

/**
 * Inizializza il monitoraggio della posizione
 */
const startGeolocation = (allPageData) => {
    const debugPosition = {
        coords: { latitude: 44.498910, longitude: 11.342241 } // Punto di test
    };

    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (position) => {
                // Cambiare in true per testare la logica stando fermi in ufficio
                const USE_DEBUG = false; 
                checkProximity(USE_DEBUG ? debugPosition : position, allPageData);
            },
            (error) => {
                console.warn("GPS non disponibile, avvio simulazione.");
                checkProximity(debugPosition, allPageData);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        checkProximity(debugPosition, allPageData);
    }
};

// Esportazione per gli altri blocchi
window.startGeolocation = startGeolocation;
// BLOCCO QUATTRO - FINE
// 
/**
 * BLOCCO CINQUE - FUNZIONI LINGUA, UI E SEGNALI (DRIN)
 * Gestisce il cambio lingua, i menu a comparsa e l'invio segnali a Firestore.
 */

// --- GESTIONE LINGUA ---

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
    // Verifica variabili globali dal Blocco Uno
    if (newLang && typeof LANGUAGES !== 'undefined' && LANGUAGES.includes(newLang) && newLang !== currentLang) {
        localStorage.setItem(typeof LAST_LANG_KEY !== 'undefined' ? LAST_LANG_KEY : 'selected_lang', newLang);

        let fileBase = typeof getCurrentPageId === 'function' ? getCurrentPageId() : 'index';
        if (fileBase === 'home') fileBase = 'index';

        // Reindirizzamento: es. index-en.html
        const newPath = `${fileBase}-${newLang}.html`;
        document.location.href = newPath;
    }
}

// --- GESTIONE DRIN (SEGNALI PROSSIMITÀ) ---

/**
 * Invia un segnale 'drin' a Firestore se l'utente è vicino a un POI
 */
async function handleDrinClick() {
    // Recupero coordinate globali aggiornate dal Blocco Quattro
    const uLat = window.userLat; 
    const uLon = window.userLon;

    if (!uLat || !uLon || typeof POIS_LOCATIONS === 'undefined') {
        console.warn("Posizione non rilevata o dati POI mancanti.");
        return;
    }

    let closestPoi = null;
    let minDistance = Infinity;

    POIS_LOCATIONS.forEach(location => {
        // calculateDistance è definita nel Blocco Quattro
        const distance = typeof calculateDistance === 'function' 
            ? calculateDistance(uLat, uLon, location.lat, location.lon) 
            : 999;
        
        const threshold = location.distanceThreshold || 50;

        if (distance <= threshold && distance < minDistance) {
            minDistance = distance;
            closestPoi = location;
        }
    });

    if (closestPoi) {
        const user = typeof auth !== 'undefined' ? auth.currentUser : null;
        const uid = user ? user.uid : "anonymous";
        const aId = typeof appId !== 'undefined' ? appId : 'default-app';

        try {
            // Importante: Rispettiamo la RULE 1 dei percorsi Firestore
            const signalsRef = collection(db, 'artifacts', aId, 'public', 'data', 'signals');
            await addDoc(signalsRef, {
                poiId: closestPoi.id,
                userId: uid,
                timestamp: new Date().toISOString(),
                type: 'drin'
            });

            // Feedback visivo
            const drinBtn = document.getElementById('drinButton');
            if (drinBtn) {
                drinBtn.classList.add('drin-animation');
                setTimeout(() => drinBtn.classList.remove('drin-animation'), 1000);
            }
            
            console.log("Drin inviato per:", closestPoi.id);
        } catch (e) {
            console.error("Errore invio segnale Firestore:", e);
        }
    } else {
        console.log("Troppo lontano dai POI per suonare.");
    }
}

// --- INIZIALIZZAZIONE UI ---

function initEventListeners(lang) {
    const menuToggle = document.querySelector('.menu-toggle');
    const navBarMain = document.getElementById('navBarMain');
    const nearbyPoiButton = document.getElementById('nearbyPoiButton');
    const nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');
    const body = document.body;

    // 1. Hamburger Menu Principale
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

    // 2. Menu POI Vicini (Pulsante Verde)
    if (nearbyPoiButton && nearbyMenuPlaceholder && !nearbyPoiButton.dataset.listenerAttached) {
        nearbyPoiButton.addEventListener('click', () => {
            nearbyMenuPlaceholder.classList.toggle('poi-active');
            if (menuToggle) {
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

    // 3. Pulsante Drin (Campanella)
    const drinButton = document.getElementById('drinButton');
    if (drinButton && !drinButton.dataset.listenerAttached) {
        drinButton.addEventListener('click', handleDrinClick);
        drinButton.dataset.listenerAttached = 'true';
    }

    // 4. Audio Player (Logica dal Blocco 3)
    const localAudioPlayer = document.getElementById('audioPlayer');
    const localPlayButton = document.getElementById('playAudio');
    if (localAudioPlayer && localPlayButton && !localPlayButton.dataset.listenerAttached) {
        localPlayButton.addEventListener('click', () => {
            if (typeof toggleAudioPlayback === 'function') {
                toggleAudioPlayback(localAudioPlayer, localPlayButton);
            }
        });
        localAudioPlayer.addEventListener('ended', () => {
            if (typeof handleAudioEnded === 'function') {
                handleAudioEnded(localAudioPlayer, localPlayButton);
            }
        });
        localPlayButton.dataset.listenerAttached = 'true';
    }

    // 5. Selettore Lingua
    document.querySelectorAll('.language-selector button').forEach(button => {
        button.addEventListener('click', handleLanguageChange);
    });

    // Aggiorna lo stato visivo dei bottoni lingua all'avvio
    updateLanguageSelectorActiveState(lang);
}

// Esponiamo le funzioni per l'avvio globale
window.initEventListeners = initEventListeners;

// BLOCCO CINQUE - FINE
/**
 * BLOCCO SEI E SETTE - NAVIGAZIONE DINAMICA E BOOTSTRAP
 * Gestisce il menu contestuale dei POI e l'avvio globale dell'app.
 */

// ===========================================
// LOGICA NAVIGAZIONE DINAMICA (POI VICINI)
// ===========================================

/**
 * Aggiorna il menu a comparsa con i link ai POI fisicamente vicini
 */
async function updateNearbyMenu(lang) {
    if (!nearbyMenuPlaceholder) return;

    try {
        // getCurrentLocation() e getNearbyPOIs() definiti nel Blocco Quattro
        const coords = await getCurrentLocation();
        const nearbyPOIs = getNearbyPOIs(coords.latitude, coords.longitude, typeof POI_DATA !== 'undefined' ? POI_DATA : {});

        if (nearbyPOIs.length > 0) {
            let html = `<ul class="nearby-list" style="list-style:none; padding:1rem; margin:0;">`;
            nearbyPOIs.forEach(poi => {
                // Genera link relativo: nomepoi-it.html
                const poiLink = `${poi.id}-${lang}.html`;
                const label = (poi.label && poi.label[lang]) ? poi.label[lang] : (poi.id.toUpperCase());
                
                html += `
                <li style="margin-bottom:0.8rem; border-bottom:1px solid #eee; padding-bottom:0.5rem;">
                    <a href="${poiLink}" style="text-decoration:none; color:inherit; display:block;">
                        <div style="font-weight:bold;">${label}</div>
                        <div style="font-size:0.8rem; color:#666;">Distante ${poi.distance.toFixed(0)}m</div>
                    </a>
                </li>`;
            });
            html += `</ul>`;
            
            nearbyMenuPlaceholder.innerHTML = html;
            if (nearbyPoiButton) nearbyPoiButton.style.display = 'flex';
        } else {
            const msg = lang === 'it' ? "Nessun punto nelle vicinanze" : "No points nearby";
            nearbyMenuPlaceholder.innerHTML = `<p style="padding:1rem; text-align:center; color:#666;">${msg}</p>`;
        }
    } catch (error) {
        console.warn("Impossibile aggiornare menu vicini:", error);
        const errorMsg = lang === 'it' ? "Attiva la posizione per vedere i punti vicini." : "Enable GPS to see nearby places.";
        nearbyMenuPlaceholder.innerHTML = `<p style="padding:1rem; text-align:center; color:#888; font-size:0.9rem;">${errorMsg}</p>`;
    }
}

// ===========================================
// PUNTO DI INGRESSO (DOM CONTENT LOADED)
// ===========================================

document.addEventListener('DOMContentLoaded', async () => {
    console.info(`🌍 Versione in esecuzione: ${typeof APP_VERSION !== 'undefined' ? APP_VERSION : '1.0.0'}`);

    // 1. ASSEGNAZIONE RIFERIMENTI UI GLOBALI
    window.nearbyPoiButton = document.getElementById('nearbyPoiButton');
    window.nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    // 2. DETERMINAZIONE LINGUA CORRENTE
    let finalLang = 'it';
    const savedLang = localStorage.getItem(typeof LAST_LANG_KEY !== 'undefined' ? LAST_LANG_KEY : 'selected_lang');
    if (savedLang && typeof LANGUAGES !== 'undefined' && LANGUAGES.includes(savedLang)) {
        finalLang = savedLang;
    }

    // Check da URL (priorità sul salvataggio locale se presente)
    const urlPath = document.location.pathname;
    const langMatch = urlPath.match(/-([a-z]{2})\.html/);
    if (langMatch && typeof LANGUAGES !== 'undefined' && LANGUAGES.includes(langMatch[1])) {
        finalLang = langMatch[1];
        localStorage.setItem(typeof LAST_LANG_KEY !== 'undefined' ? LAST_LANG_KEY : 'selected_lang', finalLang);
    }

    window.currentLang = finalLang;
    document.documentElement.lang = currentLang;

    // 3. INIZIALIZZAZIONE UI E LINGUA
    if (typeof updateLanguageSelectorActiveState === 'function') {
        updateLanguageSelectorActiveState(currentLang);
    }
    if (typeof initEventListeners === 'function') {
        initEventListeners(currentLang);
    }

    // 4. CARICAMENTO CONTENUTI (Blocco Due)
    try {
        if (typeof loadContent === 'function') {
            await loadContent(currentLang);
        }
    } catch (err) {
        console.error("Errore critico caricamento contenuti:", err);
    }

    // 5. ATTIVAZIONE FIREBASE (Con gestione errori sicura)
    if (typeof initializeApp !== 'undefined' && typeof __firebase_config !== 'undefined') {
        try {
            const firebaseConfig = JSON.parse(__firebase_config);
            const app = initializeApp(firebaseConfig);
            window.db = getFirestore(app);
            window.auth = getAuth(app);

            // Regola 3: Autenticazione prima di qualsiasi query
            const initAuth = async () => {
                try {
                    if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
                        await signInWithCustomToken(auth, __initial_auth_token);
                    } else {
                        await signInAnonymously(auth);
                    }
                    console.log("Firebase: Autenticazione completata.");
                } catch (authErr) {
                    console.error("Firebase Auth Error:", authErr.message);
                }
            };
            await initAuth();
        } catch (initErr) {
            console.error("Firebase Initialization Failed:", initErr.message);
        }
    }

    // 6. AVVIO GEOLOCALIZZAZIONE E MENU VICINI
    // Eseguiamo un primo aggiornamento manuale
    updateNearbyMenu(currentLang);
    
    // Attiviamo il monitoraggio continuo (Blocco Quattro)
    if (typeof startProximityTracking === 'function') {
        startProximityTracking();
    }

    // 7. ANALYTICS
    if (typeof gtag === 'function') {
        gtag('event', 'page_view', {
            'page_title': document.title,
            'page_path': window.location.pathname,
            'lingua_pagina': currentLang
        });
    }

    // 8. RIMOZIONE LOADING SCREEN
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            console.info("🚀 Applicazione pronta.");
        }, 500);
    }
});