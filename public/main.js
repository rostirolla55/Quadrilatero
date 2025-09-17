// Funzione per determinare l'ID della pagina corrente
const getCurrentPageId = () => {
    // Ottiene il nome del file (es. "aneddoti.html")
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1); 
    
    // Rimuove l'estensione ".html" per ottenere l'ID (es. "aneddoti")
    if (fileName === '' || fileName === 'index.html') {
        return 'home'; // Se è vuoto o index.html, è la homepage
    }
    return fileName.replace('.html', '');
};


// Funzione principale per impostare la lingua
const setLanguage = async (lang) => {
    document.getElementById('audioPlayer').pause();
    document.getElementById('audioPlayer').currentTime = 0;
    try {
        const pageId = getCurrentPageId(); // <--- CHIAMIAMO LA NUOVA FUNZIONE
        
        const response = await fetch(`data/translations/${lang}/texts.json`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const translations = await response.json();
        
        // Seleziona solo i contenuti relativi alla pagina corrente
        const data = translations[pageId]; 

        // Se i dati per questa pagina non esistono, esci
        if (!data) {
             console.error(`Dati non trovati per la pagina: ${pageId} nella lingua: ${lang}`);
             return;
        }

        // AGGIORNAMENTO DEL CONTENUTO (il resto rimane simile ma usa 'data')
        document.getElementById('pageTitle').textContent = data.pageTitle;
        document.getElementById('mainText').textContent = data.mainText;
        document.getElementById('playAudio').textContent = data.playAudioButton;
        document.getElementById('audioPlayer').src = data.audioSource;

        // ... [il resto della funzione setLanguage continua come prima]
        
    } catch (error) {
        console.error('Errore nel caricamento dei testi:', error);
    }
};

// ... [il resto del tuo file main.js]

// Funzione per gestire la riproduzione e pausa dell'audio
const toggleAudio = () => {
    const audioPlayer = document.getElementById('audioPlayer');
    const playButton = document.getElementById('playAudio');
    
    if (audioPlayer.paused) {
        audioPlayer.play();
        playButton.textContent = playButton.dataset.pauseText;
        playButton.classList.remove('play-style');
        playButton.classList.add('pause-style');
    } else {
        audioPlayer.pause();
        playButton.textContent = playButton.dataset.playText;
        playButton.classList.remove('pause-style');
        playButton.classList.add('play-style');
    }
};

// Aggiungi un "ascoltatore di eventi" al bottone audio
document.getElementById('playAudio').addEventListener('click', toggleAudio);

// Imposta la lingua di default (italiano) al caricamento della pagina
window.onload = () => {
    setLanguage('it');
};
