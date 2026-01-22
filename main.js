/**
 * main.js - Quartiere Porto
 * Handles multi-language content loading, GPS proximity for POIs, 
 * and asynchronous fragment fetching.
 */

// ====================================================================
// DICHIARAZIONE VARIABILI GLOBALI (NECESSARIE)
// ====================================================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const APP_VERSION = '1.2.22 - Final POI Fix';

const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'Quartiere Porto_lastLang'; 
let currentLang = 'it';
let nearbyPoiButton, nearbyMenuPlaceholder;

// Variabili Firebase
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
let db, auth;
let currentUserId = null;
let isAuthReady = false;

// Variabile globale per tracciare la posizione e il POI attivo
window.lastKnownPosition = null;
let currentPoiId = null;

// ===========================================
// FUNZIONI UTILITY GENERALI
// ===========================================

const getCurrentPageId = () => {
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1);
    if (fileName === '' || fileName.startsWith('index')) {
        return 'home';
    }
    return fileName.replace(/-[a-z]{2}\.html/i, '').replace('.html', '').toLowerCase();
};

const updateTextContent = (id, value) => {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value || '';
    }
};

const updateHTMLContent = (id, htmlContent) => {
    const element = document.getElementById(id);
    if (element) {
        element.innerHTML = htmlContent || '';
    }
};

function isFilePath(value) {
    if (typeof value !== 'string') return false;
    return /\.(html|txt)$/i.test(value.trim());
}

async function fetchFileContent(filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`Errore HTTP: ${response.status} per ${filePath}`);
        }
        return await response.text();
    } catch (error) {
        console.error(`ERRORE: Impossibile caricare il frammento ${filePath}`, error);
        return `[ERRORE: Caricamento fallito per ${filePath}. ${error.message}]`;
    }
}

// ===========================================
// FUNZIONI AUDIO
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

// ===========================================
// FUNZIONI POI E GEOLOCALIZZAZIONE
// ===========================================

/**
 * Calcola la distanza tra due punti (Formula di Haversine)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Raggio della Terra in metri
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distanza in metri
}

function getPoisLocations() {
    return (window.APP_DATA && window.APP_DATA.poisLocations) ? window.APP_DATA.poisLocations : [];
}

/**
 * Avvia il tracciamento GPS.
 */
function startGeolocation(allData) {
    if ("geolocation" in navigator) {
        console.log("[GPS] Avvio tracciamento posizione...");
        
        navigator.geolocation.watchPosition(
            (position) => {
                // Salviamo la posizione globalmente per il menu POI
                window.lastKnownPosition = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                checkProximity(position, allData);
            },
            (error) => {
                console.error("[GPS] Errore Geolocation:", error.message);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    } else {
        console.error("[GPS] Geolocation non supportata dal browser.");
    }
}

async function checkProximity(position, allData) {
    const { latitude, longitude } = position.coords;
    const pois = getPoisLocations();

    for (const poi of pois) {
        const distance = calculateDistance(latitude, longitude, poi.lat, poi.lon);

        if (distance <= (poi.radius || 50) && currentPoiId !== poi.id) {
            console.log(`[GPS] Entrato nel raggio del POI: ${poi.id} (${distance.toFixed(0)}m)`);
            currentPoiId = poi.id;
            
            // Nota: Se hai una funzione updateUI definita altrove, chiamala qui
            // updateUI(poi.id, allData);
        }
    }
}

/**
 * Aggiorna l'HTML del menu POI verde
 */
function updatePoiMenu(locations, userLat, userLon, userLang, allPageData) {
    if (!locations || !Array.isArray(locations)) {
        console.warn("POI Locations data not available yet.");
        return;
    }

    const nearbyLocations = [];
    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);
        if (distance <= (location.distanceThreshold || 500)) { // Raggio di visibilità nel menu
            nearbyLocations.push({ ...location, distance: distance });
        }
    });

    nearbyLocations.sort((a, b) => a.distance - b.distance);
    const uniquePois = [...new Map(nearbyLocations.map(item => [item['id'], item])).values()];

    let menuHtml = '';
    if (uniquePois.length > 0) {
        let listItems = '';
        uniquePois.forEach(poi => {
            // Cerchiamo il titolo nelle traduzioni o usiamo ID
            const displayTitle = (allPageData && allPageData.nav && allPageData.nav[poi.id]) 
                                 ? allPageData.nav[poi.id] 
                                 : poi.id;

            const langSuffix = userLang === 'it' ? '-it' : `-${userLang}`;
            const href = `${poi.id}${langSuffix}.html`;
            listItems += `<li><a href="${href}">${displayTitle} <span class="poi-distance">(${poi.distance.toFixed(0)}m)</span></a></li>`;
        });
        menuHtml = `<ul class="poi-links">${listItems}</ul>`;
    } else {
        let maxThreshold = locations.reduce((max, loc) => Math.max(max, loc.distanceThreshold || 50), 0);
        let noPoiMessage;
        switch (userLang) {
            case 'es': noPoiMessage = `No si trovano puntos de interés dentro de ${maxThreshold}m. <br><br> Pulse de nuevo para cerrar.`; break;
            case 'en': noPoiMessage = `No Points of Interest found within ${maxThreshold}m. <br><br> Press the green button again to close.`; break;
            case 'fr': noPoiMessage = `Aucun point d'intérêt trouvé dans i ${maxThreshold}m. <br><br> Appuyez à nouveau pour fermer.`; break;
            case 'it':
            default: noPoiMessage = `Nessun Punto di Interesse trovato entro ${maxThreshold}m.<br><br> Premere di nuovo il bottone verde per chiudere.`; break;
        }
        menuHtml = `<div style="color:#fff; padding: 20px; text-align: center;">${noPoiMessage}</div>`;
    }

    if (nearbyMenuPlaceholder) {
        nearbyMenuPlaceholder.innerHTML = menuHtml;
    }
}

// ===========================================
// CARICAMENTO CONTENUTI (loadContent)
// ===========================================

async function loadContent(lang) {
    document.documentElement.lang = lang;
    try {
        const pageId = getCurrentPageId();
        const response = await fetch(`data/translations/${lang}/texts.json`);

        if (!response.ok) {
            if (lang !== 'it') { loadContent('it'); return; }
            throw new Error(`Data load failed for ${lang}`);
        }

        const data = await response.json();
        const pageData = data[pageId];

        if (!pageData) {
            updateTextContent('pageTitle', `[ERRORE] Dati mancanti (${pageId}/${lang})`);
            document.body.classList.add('content-loaded');
            return;
        }

        // Caricamento Asincrono Frammenti
        const fragmentPromises = [];
        const textKeys = ['mainText', 'mainText1', 'mainText2', 'mainText3', 'mainText4', 'mainText5'];

        for (const key of textKeys) {
            const value = pageData[key];
            if (value && isFilePath(value)) {
                const fullPath = "text_files/" + value;
                fragmentPromises.push(fetchFileContent(fullPath).then(content => ({ key, content })));
            } else if (value !== undefined) {
                fragmentPromises.push(Promise.resolve({ key, content: value }));
            }
        }

        const fragmentResults = await Promise.all(fragmentPromises);
        fragmentResults.forEach(item => { pageData[item.key] = item.content; });

        // Aggiornamento Navigazione
        const navBarMain = document.getElementById('navBarMain');
        if (data.nav && navBarMain) {
            const langSuffix = lang === 'it' ? '-it' : `-${lang}`;
            const navLinks = (window.APP_DATA && window.APP_DATA.navigation) ? window.APP_DATA.navigation : [];
            navLinks.forEach(link => {
                const el = document.getElementById(link.id);
                if (el) {
                    el.href = `${link.base}${langSuffix}.html`;
                    el.textContent = data.nav[link.key] || el.textContent;
                }
            });
        }

        // Update UI
        updateTextContent('pageTitle', pageData.pageTitle);
        updateHTMLContent('headerTitle', pageData.pageTitle);
        
        const headImg = document.getElementById('headImage');
        if (headImg && pageData.headImage) {
            headImg.src = `public/images/${pageData.headImage}`;
            headImg.alt = pageData.pageTitle;
        }

        textKeys.forEach(key => updateHTMLContent(key, pageData[key] || ''));
        
        updateTextContent('infoSource', pageData.sourceText ? `Fonte: ${pageData.sourceText}` : '');
        updateTextContent('infoCreatedDate', pageData.creationDate ? `Data Creazione: ${pageData.creationDate}` : '');
        updateTextContent('infoUpdatedDate', pageData.lastUpdate ? `Ultimo Aggiornamento: ${pageData.lastUpdate}` : '');

        // Audio
        const player = document.getElementById('audioPlayer');
        const btn = document.getElementById('playAudio');
        if (player && btn && pageData.audioSource) {
            btn.textContent = pageData.playAudioButton;
            btn.dataset.playText = pageData.playAudioButton;
            btn.dataset.pauseText = pageData.pauseAudioButton;
            player.src = `Assets/Audio/${pageData.audioSource}`;
            player.load();
            btn.style.display = 'block';
        } else if (btn) {
            btn.style.display = 'none';
        }

        // Images
        for (let i = 1; i <= 5; i++) {
            const img = document.getElementById(`pageImage${i}`);
            const src = pageData[`imageSource${i}`];
            if (img) {
                img.src = src ? `Assets/images/${src}` : '';
                img.style.display = src ? 'block' : 'none';
            }
        }

        // Salviamo i dati globalmente per il menu POI
        window.ALL_PAGE_DATA = data;
        
        // AVVIO GEOLOCALIZZAZIONE (Dopo il caricamento dati)
        startGeolocation(data);
        
        document.body.classList.add('content-loaded');
    } catch (error) {
        console.error('Critical load error:', error);
        document.body.classList.add('content-loaded');
    }
}

// ===========================================
// LINGUA E EVENTI
// ===========================================

function updateLanguageSelectorActiveState(lang) {
    document.querySelectorAll('.language-selector button').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });
}

function handleLanguageChange(event) {
    const newLang = event.currentTarget.getAttribute('data-lang');
    if (newLang && LANGUAGES.includes(newLang) && newLang !== currentLang) {
        localStorage.setItem(LAST_LANG_KEY, newLang);
        let fileBase = getCurrentPageId();
        if (fileBase === 'home') fileBase = 'index';
        document.location.href = `${fileBase}-${newLang}.html`;
    }
}

function initEventListeners() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navBarMain = document.getElementById('navBarMain');
    const body = document.body;

    // Gestione Menu Principale (Hamburger)
    if (menuToggle && navBarMain) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            navBarMain.classList.toggle('active');
            body.classList.toggle('menu-open');
            if (nearbyMenuPlaceholder) nearbyMenuPlaceholder.classList.remove('poi-active');
        });
    }

    // Gestione Menu POI (Dinamico)
    if (nearbyPoiButton && nearbyMenuPlaceholder) {
        nearbyPoiButton.addEventListener('click', () => {
            const isOpening = !nearbyMenuPlaceholder.classList.contains('poi-active');
            
            if (isOpening) {
                console.log("[POI] Apertura menu: calcolo distanze...");
                
                if (window.lastKnownPosition) {
                    updatePoiMenu(
                        getPoisLocations(), 
                        window.lastKnownPosition.lat, 
                        window.lastKnownPosition.lon, 
                        currentLang, 
                        window.ALL_PAGE_DATA
                    );
                } else {
                    nearbyMenuPlaceholder.innerHTML = `<div style="color:orange; padding:20px; text-align:center;">Attivazione GPS in corso...</div>`;
                }
            }

            nearbyMenuPlaceholder.classList.toggle('poi-active');
            if (menuToggle) {
                menuToggle.classList.remove('active');
                navBarMain.classList.remove('active');
            }
            body.classList.toggle('menu-open', nearbyMenuPlaceholder.classList.contains('poi-active'));
        });
    }

    // Gestione Audio
    const audioPlayer = document.getElementById('audioPlayer');
    const playBtn = document.getElementById('playAudio');
    if (audioPlayer && playBtn) {
        playBtn.addEventListener('click', () => toggleAudioPlayback(audioPlayer, playBtn));
        audioPlayer.addEventListener('ended', () => handleAudioEnded(audioPlayer, playBtn));
    }

    // Gestione Lingua
    document.querySelectorAll('.language-selector button').forEach(btn => {
        btn.addEventListener('click', handleLanguageChange);
    });
}

// ===========================================
// INIT
// ===========================================

document.addEventListener('DOMContentLoaded', () => {
    console.info(`🌍 Versione: ${APP_VERSION}`);
    
    nearbyPoiButton = document.getElementById('nearbyPoiButton');
    nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    let finalLang = 'it';
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    if (savedLang && LANGUAGES.includes(savedLang)) finalLang = savedLang;
    
    const langMatch = window.location.pathname.match(/-([a-z]{2})\.html/);
    if (langMatch && LANGUAGES.includes(langMatch[1])) finalLang = langMatch[1];

    currentLang = finalLang;
    updateLanguageSelectorActiveState(currentLang);
    
    initEventListeners();
    loadContent(currentLang);

    // Firebase Init
    if (typeof firebaseConfig.apiKey !== 'undefined') {
        const app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        auth = getAuth(app);
        
        const initAuth = async () => {
            try {
                if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
                    await signInWithCustomToken(auth, __initial_auth_token);
                } else {
                    await signInAnonymously(auth);
                }
                onAuthStateChanged(auth, (user) => {
                    currentUserId = user ? user.uid : null;
                    isAuthReady = true;
                });
            } catch (e) { console.error("Auth error", e); }
        };
        initAuth();
    }
});