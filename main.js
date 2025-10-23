// ====================================================================
// DICHIARAZIONE VARIABILI GLOBALI (NECESSARIE)
// ====================================================================
const LANGUAGES = ['it', 'en', 'fr', 'es'];
const LAST_LANG_KEY = 'porticiSanLuca_lastLang'; // Chiave per salvare l'ultima lingua in localStorage (Coerente con index.html)
let currentLang = 'it';
let nearbyPoiButton, nearbyMenuPlaceholder;

// ===========================================
// DATI: Punti di Interesse GPS (DA COMPILARE)
// ===========================================
// Attenzione le coordinate sono della zona PORTORENO
// in C:\Users\User\Documents\salvataggi_github\ARCO_LOCATIONS_PORTICISANLUCA_js.txt
const POIS_LOCATIONS = [
    // Lapide_Grazia.jpg
    { id: 'graziaxx', lat: 44.5006638888889, lon: 11.3407694444444, distanceThreshold: 5 },
    // Pugliole_1.jpg
    { id: 'Pugliole', lat: 44.4990527777778, lon: 11.3394472222222, distanceThreshold: 5 },
    // Pugliole.jpg
    { id: 'pugliole', lat: 44.5001944444444, lon: 11.3399861111111, distanceThreshold: 5 },
    // viaPolese_f.jpg
    { id: 'carracci', lat: 44.5000722222222, lon: 11.3404333333333, distanceThreshold: 5 },
    // ViaSanCarlo45_f.jpg
    { id: 'carracci', lat: 44.5005194444444, lon: 11.3407111111111, distanceThreshold: 5 },
    // ViaSanCarlo45_f.jpg
    { id: 'lastre', lat: 44.49925278, lon: 11.34074444, distanceThreshold: 10 },
    // ViaSanCarlo42Dett_f.jpg
    { id: 'lastre', lat: 44.5004194444444, lon: 11.3406333333333, distanceThreshold: 10 },
    // ViaSanCarlo42_f.jpg
    { id: 'lastre', lat: 44.5004361111111, lon: 11.3406416666667, distanceThreshold: 10 },
    // Tanari_11.jpg
    { id: 'lastre', lat: 44.4992472222222, lon: 11.3407194444444, distanceThreshold: 10 },
    // Tanari_11.jpg
    { id: 'lastre', lat: 44.49925278, lon: 11.34074444, distanceThreshold: 10 }
];


// ===========================================
// FUNZIONI UTILITY GENERALI (Lingua e DOM)
// ===========================================

const getCurrentPageId = () => {
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1);

    // Correzione: La base 'index' deve essere gestita come 'home' per il JSON
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


// ===========================================
// FUNZIONI POI (PULSANTE VERDE)
// ===========================================

const formatDistance = (distance) => {
    if (distance < 1000) {
        return `${Math.round(distance)}m`;
    }
    return `${(distance / 1000).toFixed(1)}km`;
};

function updatePoiMenu(locations, userLat, userLon, userLang) {
    const nearbyLocations = [];
    const minProximity = 50; // 50 metri

    // 1. Calcola la distanza e filtra
    locations.forEach(location => {
        const distance = calculateDistance(userLat, userLon, location.lat, location.lon);

        if (distance <= minProximity) {
            nearbyLocations.push({
                ...location,
                distance: distance
            });
        }
    });

    // 2. Ordina e Rimuovi duplicati (basati sull'ID)
    nearbyLocations.sort((a, b) => a.distance - b.distance);
    const uniquePois = [...new Map(nearbyLocations.map(item => [item['id'], item])).values()];

    // 3. Genera l'HTML del menu
    let menuHtml = '';

    if (uniquePois.length > 0) {
        const langSuffix = userLang === 'it' ? '' : `-${userLang}`;

        menuHtml += '<ul class="poi-links">';
        uniquePois.forEach(poi => {
            const distanceText = formatDistance(poi.distance);
            const fileBaseName = poi.id.toLowerCase();

            // La pagina IT non ha suffisso nel nome del file, ma la base del link DEVE essere coerente
            const poiLink = `${fileBaseName}${(userLang === 'it' ? '-it' : langSuffix)}.html`; // Correzione per URL coerenti

            const displayTitle = poi.id.replace(/_/g, ' ').replace(/([a-z])(\d)/i, '$1 $2');

            menuHtml += `<li><a href="${poiLink}">${displayTitle} (${distanceText})</a></li>`;
        });
        menuHtml += '</ul>';

    } else {
        // Nessun POI trovato: mostra un messaggio informativo
        let noPoiMessage;
        switch (userLang) {
            case 'en': noPoiMessage = `No Points of Interest found within ${minProximity}m.`; break;
            case 'es': noPoiMessage = `No se encontraron Puntos de Interés a menos de ${minProximity}m.`; break;
            case 'fr': noPoiMessage = `Aucun Point d'Intérêt trouvé à moins de ${minProximity}m.`; break;
            case 'it':
            default: noPoiMessage = `Nessun Punto di Interesse trovato entro ${minProximity}m.`; break;
        }
        menuHtml = `<div style="color:white; padding: 20px; text-align: center; font-size: 0.9em;">${noPoiMessage}</div>`;
    }

    // 4. Inietta l'HTML nel placeholder
    if (nearbyMenuPlaceholder) {
        nearbyMenuPlaceholder.innerHTML = menuHtml;
    }
}


// ===========================================
// FUNZIONI DI CARICAMENTO CONTENUTI (loadContent)
// ===========================================

async function loadContent(lang) {
    document.documentElement.lang = lang;

    try {
        const pageId = getCurrentPageId();
        const response = await fetch(`data/translations/${lang}/texts.json`);

        if (!response.ok) {
            console.error(`File di traduzione non trovato per la lingua: ${lang}. Tentativo di fallback su 'it'.`);
            if (lang !== 'it') {
                loadContent('it');
                return;
            }
            throw new Error(`Impossibile caricare i dati per ${lang}.`);
        }

        const data = await response.json();
        const pageData = data[pageId];

        // Correzione 1: Se non ci sono dati, mostra un errore, ma apri la pagina
        if (!pageData) {
            console.warn(`Dati non trovati per la chiave pagina: ${pageId} nel file JSON per la lingua: ${lang}.`);
            updateTextContent('pageTitle', `[ERRORE] Dati mancanti (${pageId}/${lang})`);
            // Apriamo la pagina per mostrare il messaggio d'errore.
            document.body.classList.add('content-loaded');
            return;
        }

        // AGGIORNAMENTO NAVIGAZIONE
        const navBarMain = document.getElementById('navBarMain');

        if (data.nav && navBarMain) {
            // Usa il suffisso -it anche per IT in questo blocco, per coerenza URL
            const langSuffix = lang === 'it' ? '-it' : `-${lang}`;

            // ... (lista navLinksData) ... (Tutto questo blocco è corretto e rimane)
            const navLinksData = [
                { id: 'navHome', key: 'navHome', base: 'index' },
                { id: 'navCarracci', key: 'navCarracci', base: 'carracci' },
                { id: 'navLastre', key: 'navLastre', base: 'lastre' },
                { id: 'navPugliole', key: 'navPugliole', base: 'pugliole' },
                { id: 'navGraziaxx', key: 'navGraziaxx', base: 'graziaxx' },
            ];

            // Aggiorna HREF e Testo per tutti i link del menu principale
            navLinksData.forEach(link => {
                const linkElement = document.getElementById(link.id);
                if (linkElement) {
                    // Correzione: Il link IT deve usare '-it' se la pagina IT è index-it.html
                    linkElement.href = `${link.base}${langSuffix}.html`;

                    if (data.nav[link.key]) {
                        linkElement.textContent = data.nav[link.key];
                    } else {
                        console.warn(`[Nav Warning] Chiave di navigazione mancante: ${link.key}`);
                    }
                } else {
                    // Log per avvisare di ID mancanti in HTML
                    console.warn(`[Nav Warning] Elemento HTML non trovato per l'ID: ${link.id}`);
                }
            });
        }
        // FINE AGGIORNAMENTO NAVIGAZIONE

        // AGGIORNAMENTO TESTATA (Titolo e Immagine)
        updateTextContent('pageTitle', pageData.pageTitle);
        updateHTMLContent('headerTitle', pageData.pageTitle);

        // AGGIORNAMENTO IMMAGINE DI FONDO TESTATA
        const headerImage = document.getElementById('pageImage1');
        if (headerImage && pageData.imageSource1) {
            headerImage.src = pageData.imageSource1;
            headerImage.alt = pageData.pageTitle || "Immagine di testata";
        }

        // AGGIORNAMENTO DEL CONTENUTO (Testi principali)
        updateHTMLContent('mainText', pageData.mainText || '');
        updateHTMLContent('mainText1', pageData.mainText1 || '');
        updateHTMLContent('mainText2', pageData.mainText2 || '');
        updateHTMLContent('mainText3', pageData.mainText3 || '');
        updateHTMLContent('mainText4', pageData.mainText4 || '');
        updateHTMLContent('mainText5', pageData.mainText5 || '');

        // AGGIORNAMENTO INFORMAZIONI SULLA FONTE E DATA
        if (pageData.sourceText) {
            updateTextContent('infoSource', `Fonte: ${pageData.sourceText}`);
        }
        if (pageData.creationDate) {
            updateTextContent('infoCreatedDate', `Data Creazione: ${pageData.creationDate}`);
        }
        if (pageData.lastUpdate) {
            updateTextContent('infoUpdatedDate', `Ultimo Aggiornamento: ${pageData.lastUpdate}`);
        }

        // AGGIORNAMENTO AUDIO E BOTTONE
        const currentAudioPlayer = document.getElementById('audioPlayer');
        const currentPlayButton = document.getElementById('playAudio');

        if (currentAudioPlayer && currentPlayButton && pageData.audioSource) {
            if (!currentAudioPlayer.paused) {
                currentAudioPlayer.pause();
                currentAudioPlayer.currentTime = 0;
            }
            currentPlayButton.textContent = pageData.playAudioButton;
            currentPlayButton.dataset.playText = pageData.playAudioButton;
            currentPlayButton.dataset.pauseText = pageData.pauseAudioButton;
            currentAudioPlayer.src = pageData.audioSource;
            currentAudioPlayer.load();
            currentPlayButton.classList.remove('pause-style');
            currentPlayButton.classList.add('play-style');
        } else if (currentPlayButton) {
            // Nasconde il pulsante Audio se la sorgente non è presente
            currentPlayButton.style.display = 'none';
        }

        // AGGIORNAMENTO IMMAGINI DINAMICHE (dalla 2 alla 5)
        for (let i = 2; i <= 5; i++) {
            const imageElement = document.getElementById(`pageImage${i}`);
            const imageSource = pageData[`imageSource${i}`];

            if (imageElement) {
                imageElement.src = imageSource || '';
                // Nasconde l'elemento se non c'è una sorgente
                imageElement.style.display = imageSource ? 'block' : 'none';
                imageElement.alt = pageData.pageTitle || `Immagine ${i}`;
            }
        }

        console.log(`✅ Contenuto caricato con successo per la lingua: ${lang} e pagina: ${pageId}`);

        // 🔥 CORREZIONE 2: SPOSTA LA RIGA PER MOSTRARE LA PAGINA ALLA FINE
        document.body.classList.add('content-loaded');

    } catch (error) {
        console.error('Errore critico nel caricamento dei testi:', error);
        document.body.classList.add('content-loaded'); // Apri la pagina anche in caso di errore
    }
}

// ===========================================
// FUNZIONI UTILITY PER GPS E POI
// ===========================================

const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3; // Raggio della terra in metri
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
        Math.cos(φ1) * Math.cos(φ2) *
        Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distanza in metri
};

const checkProximity = (position) => {
    const userLat = position.coords.latitude;
    const userLon = position.coords.longitude;
    const userLang = currentLang;

    if (nearbyPoiButton) {
        nearbyPoiButton.style.display = 'block';
        if (typeof updatePoiMenu === 'function') {
            updatePoiMenu(POIS_LOCATIONS, userLat, userLon, userLang);
        }
    }
};

const handleGeolocationError = (error) => {
    console.warn(`ERRORE GPS: ${error.code}: ${error.message}`);
    if (nearbyPoiButton) { nearbyPoiButton.style.display = 'none'; }
};

const startGeolocation = () => {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(checkProximity, handleGeolocationError, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        });
        console.log("Monitoraggio GPS avviato.");
    } else {
        console.error("Il tuo browser non supporta la geolocalizzazione.");
        if (nearbyPoiButton) { nearbyPoiButton.style.display = 'none'; }
    }
};

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

        const urlPath = document.location.pathname;
        const fileName = urlPath.substring(urlPath.lastIndexOf('/') + 1);

        // Correzione: Assicurati che fileBase sia 'index' se la pagina corrente è home
        let fileBase = getCurrentPageId();
        if (fileBase === 'home') fileBase = 'index';


        // L'homepage italiana è 'index-it.html' (ora abbiamo la certezza che esiste)
        // TUTTE le pagine usano il suffisso, anche la IT (index-it.html)
        const newPath = `${fileBase}-${newLang}.html`;

        document.location.href = newPath;
    }
}


// ===========================================
// ASSEGNAZIONE EVENT LISTENER (Menu Hamburger, Pulsante Verde, Audio)
// ===========================================

function initEventListeners(currentLang) {
    const menuToggle = document.querySelector('.menu-toggle');
    const navBarMain = document.getElementById('navBarMain');
    const body = document.body;

    // --- Logica Menu Hamburger Principale ---
    if (menuToggle && navBarMain && !menuToggle.dataset.listenerAttached) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            navBarMain.classList.toggle('active');

            body.classList.toggle('menu-open');

            if (nearbyMenuPlaceholder) {
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

    // --- Logica Menu Hamburger POI (Pulsante Verde) ---
    if (nearbyPoiButton && nearbyMenuPlaceholder && !nearbyPoiButton.dataset.listenerAttached) {
        nearbyPoiButton.addEventListener('click', () => {
            nearbyMenuPlaceholder.classList.toggle('poi-active');

            if (menuToggle && navBarMain) {
                menuToggle.classList.remove('active');
                navBarMain.classList.remove('active');
            }

            if (nearbyMenuPlaceholder.classList.contains('poi-active')) {
                body.classList.add('menu-open');
            } else {
                if (!navBarMain.classList.contains('active')) {
                    body.classList.remove('menu-open');
                }
            }
        });

        nearbyMenuPlaceholder.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                nearbyMenuPlaceholder.classList.remove('poi-active');
                body.classList.remove('menu-open');
            }
        });
        nearbyPoiButton.dataset.listenerAttached = 'true';
    }

    // --- Logica Audio ---
    const localAudioPlayer = document.getElementById('audioPlayer');
    const localPlayButton = document.getElementById('playAudio');

    if (localAudioPlayer && localPlayButton && !localPlayButton.dataset.listenerAttached) {
        localPlayButton.addEventListener('click', toggleAudioPlayback.bind(null, localAudioPlayer, localPlayButton));
        localAudioPlayer.addEventListener('ended', handleAudioEnded.bind(null, localAudioPlayer, localPlayButton));
        localPlayButton.dataset.listenerAttached = 'true';
    }


    // --- Logica Selettore Lingua (Bandiere) ---
    // Rimuovi la gestione duplicata degli event listener (non è necessario farlo qui, ma non fa male)
    document.querySelectorAll('.language-selector button').forEach(button => {
        button.removeEventListener('click', handleLanguageChange);
        button.addEventListener('click', handleLanguageChange);
    });
}

// ===========================================
// PUNTO DI INGRESSO (DOM LOADED)
// ===========================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. ASSEGNAZIONE DELLE VARIABILI GLOBALI
    nearbyPoiButton = document.getElementById('nearbyPoiButton');
    nearbyMenuPlaceholder = document.getElementById('nearbyMenuPlaceholder');

    // 2. DETERMINAZIONE LINGUA CORRENTE
    let finalLang = 'it';

    // A) Controlla la lingua salvata
    const savedLang = localStorage.getItem(LAST_LANG_KEY);
    if (savedLang && LANGUAGES.includes(savedLang)) {
        finalLang = savedLang;
    }

    // B) Controlla la lingua nell'URL (prevale sulla persistenza)
    const urlPath = document.location.pathname;
    const langMatch = urlPath.match(/-([a-z]{2})\.html/);
    if (langMatch && LANGUAGES.includes(langMatch[1])) {
        finalLang = langMatch[1];
        localStorage.setItem(LAST_LANG_KEY, finalLang);
    }

    // Imposta la lingua globale
    currentLang = finalLang;
    document.documentElement.lang = currentLang;

    // 3. INIZIALIZZA LA SELEZIONE LINGUA
    updateLanguageSelectorActiveState(currentLang);

    // 4. INIZIALIZZA GLI EVENT LISTENER
    initEventListeners(currentLang);

    // 5. CARICAMENTO CONTENUTO (maintext)
    loadContent(currentLang);

    // 6. AVVIA IL MONITORAGGIO GPS
    startGeolocation();

    // Invio dati a Google Analytics
    if (typeof gtag === 'function') {
        gtag('event', 'page_view', {
            'page_title': document.title,
            'page_path': window.location.pathname,
            'lingua_pagina': currentLang
        });
    }

});