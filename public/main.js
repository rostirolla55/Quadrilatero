// Funzione principale per impostare la lingua
const setLanguage = async (lang) => {
    try {
        // Carica il file JSON corretto in base alla lingua
        const response = await fetch(`data/translations/${lang}/texts.json`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();

        // Aggiorna gli elementi della pagina con i testi dal file JSON
        document.getElementById('page-title').textContent = data.pageTitle;
        document.getElementById('main-text').textContent = data.mainText;
        document.getElementById('playAudio').textContent = data.playAudioButton;
        document.getElementById('audioPlayer').src = data.audioSource;

        // Salva il testo originale del bottone per la funzione pausa/riproduci
        document.getElementById('playAudio').dataset.originalText = data.playAudioButton;

        console.log(`Lingua impostata su: ${lang}`);
        
        // Aggiorna l'attributo lang del tag html per l'accessibilità
        document.documentElement.lang = lang;

    } catch (error) {
        console.error('Errore nel caricamento dei testi:', error);
    }
};

// Funzione per gestire la riproduzione e pausa dell'audio
const toggleAudio = () => {
    const audioPlayer = document.getElementById('audioPlayer');
    const playButton = document.getElementById('playAudio');
    
    if (audioPlayer.paused) {
        audioPlayer.play();
        playButton.textContent = 'Metti in pausa';
    } else {
        audioPlayer.pause();
        playButton.textContent = playButton.dataset.originalText;
    }
};

// Aggiungi un "ascoltatore di eventi" al bottone audio
document.getElementById('playAudio').addEventListener('click', toggleAudio);

// Aggiungi i listener ai bottoni delle bandiere per cambiare lingua
document.querySelector('.language-selector').addEventListener('click', (event) => {
    const button = event.target.closest('button');
    if (button) {
        // Interrompi l'audio corrente se ne stai riproducendo uno
        document.getElementById('audioPlayer').pause();
        document.getElementById('audioPlayer').currentTime = 0; // Torna all'inizio

        const lang = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        setLanguage(lang);
    }
});

// Imposta la lingua di default (italiano) al caricamento della pagina
window.onload = () => {
    setLanguage('it');
};
