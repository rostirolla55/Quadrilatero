// Funzione per determinare l'ID della pagina corrente
const getCurrentPageId = () => {
    // Ottiene il nome del file (es. "aneddoti.html")
    const path = window.location.pathname;
    const fileName = path.substring(path.lastIndexOf('/') + 1); 
    
    // Rimuove l'estensione ".html" per ottenere l'ID (es. "aneddoti")
    if (fileName === '' || fileName === 'index.html') {
        return 'home'; // Se è vuoto o index.html, è la homepage
    }
        // 🔥 CORREZIONE: Converte l'ID in minuscolo per la corrispondenza JSON
    return fileName.replace('.html', '').toLowerCase(); 
   };

getCurrentPageId()

// Funzione principale per impostare la lingua
const setLanguage = async (lang) => {

    // ⬇️ CORREZIONE QUI: Controlla se l'audio player esiste prima di usarlo ⬇️
    const audioPlayer = document.getElementById('audioPlayer');
    if (audioPlayer) {
        // Pausa l'audio SOLO se l'elemento audio è presente
        audioPlayer.pause(); 
        audioPlayer.currentTime = 0;
    }
        
    try {
        const pageId = getCurrentPageId();
        
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

       // AGGIORNAMENTO DEL CONTENUTO (Versione FLESSIBILE)
const updateTextContent = (id, value) => {
    const element = document.getElementById(id);
    if (element) { // Controlla: l'elemento esiste?
        element.textContent = value || ''; // Assegna il valore o una stringa vuota
    }
};

updateTextContent('pageTitle', data.pageTitle);
updateTextContent('mainText', data.mainText);
updateTextContent('mainText1', data.mainText1);
updateTextContent('mainText2', data.mainText2);
updateTextContent('mainText3', data.mainText3);
updateTextContent('mainText4', data.mainText4);
updateTextContent('mainText5', data.mainText5); 

updateTextContent('playAudio', data.playAudioButton); // Aggiorna il testo del bottone

document.getElementById('audioPlayer').src = data.audioSource; 
        const playButton = document.getElementById('playAudio'); 
        
        // 1. SALVA I TESTI PLAY/PAUSE PER IL toggleAudio
        playButton.dataset.playText = data.playAudioButton;
        playButton.dataset.pauseText = data.pauseAudioButton;
        
        // 2. APPLICA LO STILE INIZIALE CORRETTO (BLU)
        playButton.classList.remove('pause-style');
        playButton.classList.add('play-style');
        
        console.log(`Lingua impostata su: ${lang}`);
        document.documentElement.lang = lang;

    } catch (error) {
        // Blocco catch finale
        console.error('Errore nel caricamento dei testi:', error);
    }
};


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
// cancellato document.getElementById('playAudio').addEventListener('click', toggleAudio);

// Imposta la lingua di default (italiano) al caricamento della pagina
window.onload = () => {
    document.getElementById('playAudio').addEventListener('click', toggleAudio);
    setLanguage('it');
};
