// Funzione per determinare l'ID della pagina corrente
const getCurrentPageId = () => {
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1); 
    
    if (fileName === '' || fileName === 'index.html') {
        return 'home';
    }
    return fileName.replace('.html', '').toLowerCase(); 
};

// Funzione flessibile per aggiornare il contenuto solo se l'elemento esiste
const updateTextContent = (id, value) => {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value || '';
    }
};

// Funzione principale per impostare la lingua
const setLanguage = async (lang) => {

    const audioPlayer = document.getElementById('audioPlayer');
    if (audioPlayer) { // Controllo robusto audio player
        audioPlayer.pause(); 
        audioPlayer.currentTime = 0;
    }
    
    // ⬇️ TUTTO IL CODICE RELATIVO AL FETCH E AGGIORNAMENTO DATI ⬇️
    try {
        const pageId = getCurrentPageId();
        
        const response = await fetch(`data/translations/${lang}/texts.json`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const translations = await response.json();
        
        const data = translations[pageId]; 
        
        // 🔥 DEBUG: Controlla i dati che JavaScript ha letto (Adesso funzionerà!)
        console.log('Dati JSON caricati per la pagina:', data); 
        
        if (!data) {
             console.error(`Dati non trovati per la pagina: ${pageId} nella lingua: ${lang}`);
             return;
        }

        // AGGIORNAMENTO DEL CONTENUTO (Versione FLESSIBILE)
        updateTextContent('pageTitle', data.pageTitle);
        updateTextContent('mainText', data.mainText);
        updateTextContent('mainText1', data.mainText1);
        updateTextContent('mainText2', data.mainText2);
        updateTextContent('mainText3', data.mainText3);
        updateTextContent('mainText4', data.mainText4);
        updateTextContent('mainText5', data.mainText5); 

        updateTextContent('playAudio', data.playAudioButton); 
        
        // 🚨 CORREZIONE: Imposta SRC solo se l'audio player esiste
        if (audioPlayer) {
            audioPlayer.src = data.audioSource;
        }
        
        // 🚨 CORREZIONE: Controlla se il bottone audio esiste prima di usare dataset/classList
        const playButton = document.getElementById('playAudio'); 
        
        if (playButton) {
            // 1. SALVA I TESTI PLAY/PAUSE PER IL toggleAudio
            playButton.dataset.playText = data.playAudioButton;
            playButton.dataset.pauseText = data.pauseAudioButton;
            
            // 2. APPLICA LO STILE INIZIALE CORRETTO (BLU)
            playButton.classList.remove('pause-style');
            playButton.classList.add('play-style');
        }
        
        console.log(`Lingua impostata su: ${lang}`);
        document.documentElement.lang = lang;

    } catch (error) {
        // Blocco catch finale
        console.error('Errore nel caricamento dei testi:', error);
    }
};


// Funzione per gestire la riproduzione e pausa dell'audio (Nessuna modifica qui)
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

// Imposta la lingua di default (italiano) al caricamento della pagina
window.onload = () => {
    // 🚨 CORREZIONE: Controlla se il bottone esiste prima di agganciare l'evento
    const playButton = document.getElementById('playAudio'); 
    
    if (playButton) {
        playButton.addEventListener('click', toggleAudio);
    }
    
    setLanguage('it');
};
