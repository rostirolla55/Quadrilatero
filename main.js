// ===========================================
// CONFIGURAZIONE E COSTANTI GLOBALI
// ===========================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, onSnapshot, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const APP_VERSION = '1.2.18 - Full Restore + Firebase Features';
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'Quadrilatero_lastLang';
let currentLang = 'it';

// Variabili per elementi DOM globali
let nearbyPoiButton;
let nearbyMenuPlaceholder;

// Variabili Firebase (fornite dall'ambiente)
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
let db, auth;
let currentUserId = null;
let isAuthReady = false;

// ===========================================
// DATI: Punti di Interesse GPS (POI)
// ===========================================
const POIS_LOCATIONS = [
    { id: 'manifattura', lat: 44.498910, lon: 11.342241, distanceThreshold: 50 },
    { id: 'pittoricarracci', lat: 44.50085, lon: 11.33610, distanceThreshold: 50 },
    { id: 'cavaticcio', lat: 44.50018, lon: 11.33807, distanceThreshold: 50 },
    { id: 'bsmariamaggiore', lat: 44.49806368372069, lon: 11.34192628931731, distanceThreshold: 50 },
    // ** MARKER: START NEW POIS **
    // Lapide_Grazia.jpg
    { id: 'graziaxx', lat: 44.5006638888889, lon: 11.3407694444444, distanceThreshold: 50 },
    // Pugliole.jpg
    { id: 'pugliole', lat: 44.5001944444444, lon: 11.3399861111111, distanceThreshold: 50 },
    // Casa_Carracci_Portone.jpg
    { id: 'carracci', lat: 44.4999972222222, lon: 11.3403888888889, distanceThreshold: 50 },
    // ViaSanCarlo45_f.jpg
    { id: 'lastre', lat: 44.49925278, lon: 11.34074444, distanceThreshold: 50 },
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
// FUNZIONI DI SUPPORTO (Utility)
// ===========================================

const getCurrentPageId = () => {
    const urlPath = window.location.pathname;
    const fileName = urlPath.substring(urlPath.lastIndexOf('/') + 1);
    if (fileName === '' || fileName.startsWith('index')) return 'home';
    const id = fileName.replace(/-[a-z]{2}\.html/i, '').replace('.html', '');
    return id.toLowerCase();
};

const updateTextContent = (id, value) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value || '';
};

const updateHTMLContent = (id, htmlContent) => {
    const element = document.getElementById(id);
    if (element) element.innerHTML = htmlContent || '';
};

function isFilePath(value) {
    if (typeof value !== 'string') return false;
    const trimmed = value.trim();
    return trimmed.endsWith('.html') || trimmed.endsWith('.txt');
}

async function fetchFileContent(filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error(`Errore caricamento: ${response.status}`);
        return await response.text();
    } catch (error) {
        console.error(`Impossibile caricare frammento: ${filePath}`, error);
        return `[Contenuto non disponibile]`;
    }
}

// ===========================================
// LOGICA FIREBASE: DRIN E CRONOLOGIA
// ===========================================

function setupDrinListener() {
    if (!db) return;
    const drinDocRef = doc(db, 'artifacts', appId, 'public', 'data', 'commands', 'drin');
    onSnapshot(drinDocRef, (snapshot) => {
        if (snapshot.exists()) {
            console.log("🔔 Segnale DRIN intercettato!");
            const audio = new Audio('Assets/Audio/drin.mp3');
            audio.play().catch(e => console.warn("Riproduzione Drin impedita dal browser"));
        }
    }, (error) => console.error("Errore Drin Listener:", error));
}

async function logAccess(pageId, lang) {
    if (!db || !currentUserId) return;
    try {
        const logsCol = collection(db, 'artifacts', appId, 'public', 'data', 'access_logs');
        await addDoc(logsCol, {
            pageId: pageId,
            lang: lang,
            userId: currentUserId,
            timestamp: serverTimestamp(),
            userAgent: navigator.userAgent
        });
        console.log("📝 Accesso loggato correttamente.");
    } catch (error) {
        console.error("Errore registrazione cronologia:", error);
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
        playButton.classList.remove('play-style');
        playButton.classList.add('pause-style');
    } else {
        audioPlayer.pause();
        playButton.textContent = currentPlayText;
        playButton.classList.remove('pause-style');
        playButton.classList.add('play-style');
    }
};

const handleAudioEnded = function (audioPlayer, playButton) {
    const currentPlayText = playButton.dataset.playText || "Ascolta";
    audioPlayer.currentTime = 0;
    playButton.textContent = currentPlayText;
    playButton.classList.remove('pause-style');
    playButton.classList.add('play-style');
};

// ===========================================
// LOGICA GEOLOCALIZZAZIONE E POI
// ===========================================

const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3;
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
};

function updatePoiMenu(locations, userLat, userLon, userLang, allPageData) {
    const nearbyLocations = [];
    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);
        if (distance <= location.distanceThreshold) {
            nearbyLocations.push({ ...location, distance: distance });
        }
    });

    nearbyLocations.sort((a, b) => a.distance - b.distance);
    const uniquePois = [...new Map(nearbyLocations.map(item => [item['id'], item])).values()];

    let menuHtml = '';
    if (uniquePois.length > 0) {
        let listItems = '';
        uniquePois.forEach(poi => {
            const poiContent = allPageData ? allPageData[poi.id] : null;
            const displayTitle = (poiContent && poiContent.pageTitle) ? poiContent.pageTitle.trim() : `POI: ${poi.id}`;
            const langSuffix = userLang === 'it' ? '-it' : `-${userLang}`;
            listItems += `<li><a href="${poi.id}${langSuffix}.html">${displayTitle} <span class="poi-distance">(${poi.distance.toFixed(0)}m)</span></a></li>`;
        });
        menuHtml = `<ul class="poi-links">${listItems}</ul>`;
    } else {
        const noPoiMessages = {
            it: "Nessun Punto di Interesse trovato nelle vicinanze.<br><br>Premere il bottone verde per chiudere.",
            en: "No Points of Interest found nearby.<br><br>Press the green button to close.",
            es: "No se encontraron puntos de interés cercanos.<br><br>Pulse el botón verde para cerrar.",
            fr: "Aucun point d'intérêt trouvé à proximité.<br><br>Appuyez sur le bouton vert pour fermer."
        };
        menuHtml = `<div style="color:red; padding: 20px; text-align: center; font-weight: bold;">${noPoiMessages[userLang] || noPoiMessages.it}</div>`;
    }

    if (nearbyMenuPlaceholder) nearbyMenuPlaceholder.innerHTML = menuHtml;
}

const checkProximity = (position, allPageData) => {
    if (!position || !position.coords) return;
    const userLat = position.coords.latitude;
    const userLon = position.coords.longitude;

    if (nearbyPoiButton) {
        nearbyPoiButton.style.display = 'block';
        updatePoiMenu(POIS_LOCATIONS, userLat, userLon, currentLang, allPageData);
    }
};

const startGeolocation = (allPageData) => {
    const debugPosition = { coords: { latitude: 44.498910, longitude: 11.342241 } };

    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (position) => checkProximity(position, allPageData),
            (error) => {
                console.warn("GPS fallito o negato, uso posizione simulata.");
                if (nearbyPoiButton) nearbyPoiButton.style.display = 'block';
                checkProximity(debugPosition, allPageData);
            },
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
        );
    } else {
        checkProximity(debugPosition, allPageData);
    }
};

// ===========================================
// CARICAMENTO CONTENUTI DINAMICI
// ===========================================

async function loadContent(lang) {
    document.documentElement.lang = lang;
    const pageId = getCurrentPageId();

    try {
        const response = await fetch(`data/translations/${lang}/texts.json`);
        if (!response.ok) {
            if (lang !== 'it') return loadContent('it');
            throw new Error("Impossibile caricare JSON traduzioni.");
        }

        const data = await response.json();
        const pageData = data[pageId];

        if (!pageData) {
            updateTextContent('pageTitle', `Contenuto non trovato per: ${pageId}`);
            document.body.classList.add('content-loaded');
            return;
        }

        // --- Gestione Navigazione ---
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
                // ** MARKER: START NEW NAV LINKS **
                { id: 'navCavaticcio', key: 'navCavaticcio', base: 'cavaticcio' }
            ];

            navLinks.forEach(link => {
                const el = document.getElementById(link.id);
                if (el) {
                    el.href = `${link.base}${langSuffix}.html`;
                    el.textContent = data.nav[link.key] || link.id;
                }
            });
        }

        // --- Gestione Testi e Frammenti Esterni ---
        const textKeys = ['mainText', 'mainText1', 'mainText2', 'mainText3', 'mainText4', 'mainText5'];
        const fragmentPromises = [];

        textKeys.forEach(key => {
            const value = pageData[key];
            if (isFilePath(value)) {
                fragmentPromises.push(
                    fetchFileContent("text_files/" + value).then(content => ({ key, content }))
                );
            } else if (value !== undefined) {
                fragmentPromises.push(Promise.resolve({ key, content: value }));
            }
        });

        const fragments = await Promise.all(fragmentPromises);
        fragments.forEach(item => { pageData[item.key] = item.content; });

        // --- Aggiornamento UI ---
        updateTextContent('pageTitle', pageData.pageTitle);
        updateHTMLContent('headerTitle', pageData.pageTitle);

        const headImg = document.getElementById('headImage');
        if (headImg && pageData.headImage) headImg.src = `public/images/${pageData.headImage}`;

        textKeys.forEach(key => updateHTMLContent(key, pageData[key]));

        updateTextContent('infoSource', pageData.sourceText ? `Fonte: ${pageData.sourceText}` : '');
        updateTextContent('infoCreatedDate', pageData.creationDate ? `Data: ${pageData.creationDate}` : '');

        // --- Gestione Audio ---
        const audioPlayer = document.getElementById('audioPlayer');
        const playButton = document.getElementById('playAudio');
        if (audioPlayer && playButton && pageData.audioSource) {
            playButton.textContent = pageData.playAudioButton || "Ascolta";
            playButton.dataset.playText = pageData.playAudioButton;
            playButton.dataset.pauseText = pageData.pauseAudioButton;
            audioPlayer.src = `Assets/Audio/${pageData.audioSource}`;
            audioPlayer.load();
            playButton.style.display = 'block';
        } else if (playButton) {
            playButton.style.display = 'none';
        }

        // --- Gestione Immagini Secondarie (1-5) ---
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

        startGeolocation(data);
        document.body.classList.add('content-loaded');

        if (isAuthReady) logAccess(pageId, lang);

    } catch (error) {
        console.error("Errore critico loadContent:", error);
        document.body.classList.add('content-loaded');
    }
}

// ===========================================
// FUNZIONI LINGUA E BANDIERE
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
        document.location.href = `${fileBase}-${newLang}.html`;
    }
}

// ===========================================
// ASSEGNAZIONE EVENT LISTENER
// ===========================================

function initEventListeners() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navBarMain = document.getElementById('navBarMain');
    const body = document.body;

    // --- Menu Hamburger Principale ---
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

    // --- Menu POI (Pulsante Verde) ---
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

    // --- Audio ---
    const localAudioPlayer = document.getElementById('audioPlayer');
    const localPlayButton = document.getElementById('playAudio');
    if (localAudioPlayer && localPlayButton && !localPlayButton.dataset.listenerAttached) {
        localPlayButton.addEventListener('click', () => toggleAudioPlayback(localAudioPlayer, localPlayButton));
        localAudioPlayer.addEventListener('ended', () => handleAudioEnded(localAudioPlayer, localPlayButton));
        localPlayButton.dataset.listenerAttached = 'true';
    }

    // --- Selettore Lingua ---
    document.querySelectorAll('.language-selector button').forEach(button => {
        button.addEventListener('click', handleLanguageChange);
    });
}

// ===========================================
// INITIALIZATION ON DOM LOAD
// ===========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log(`%c Quadrilatero App v${APP_VERSION} `, 'background: #222; color: #bada55');

    nearbyPoiButton = document.getElementById('nearbyPoiButton');
    nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    // Determinazione Lingua Corrente
    let finalLang = 'it';
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    if (savedLang && LANGUAGES.includes(savedLang)) finalLang = savedLang;

    const urlMatch = document.location.pathname.match(/-([a-z]{2})\.html/);
    if (urlMatch && LANGUAGES.includes(urlMatch[1])) {
        finalLang = urlMatch[1];
    }

    currentLang = finalLang;
    localStorage.setItem(LAST_LANG_KEY, currentLang);

    updateLanguageSelectorActiveState(currentLang);
    initEventListeners();
    loadContent(currentLang);

    // --- Inizializzazione Firebase ---
    if (firebaseConfig.apiKey) {
        const app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        auth = getAuth(app);

        const initAuth = async () => {
            if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
                await signInWithCustomToken(auth, __initial_auth_token);
            } else {
                await signInAnonymously(auth);
            }
        };

        onAuthStateChanged(auth, (user) => {
            if (user) {
                currentUserId = user.uid;
                isAuthReady = true;
                setupDrinListener();
                logAccess(getCurrentPageId(), currentLang);
            }
        });

        initAuth().catch(err => console.error("Errore inizializzazione Auth:", err));
    }
});