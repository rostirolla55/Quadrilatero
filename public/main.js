const setLanguage = async (lang) => {
    try {
        const response = await fetch(`data/translations/${lang}/texts.json`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();

        // Aggiorna gli elementi della pagina con i contenuti del JSON
        document.getElementById('pageTitle').textContent = data.pageTitle;
        document.getElementById('mainText').textContent = data.mainText;
        document.getElementById('playAudio').textContent = data.playAudioButton;
        document.getElementById('audioPlayer').src = data.audioSource;
        
        // SALVA QUI IL TESTO ORIGINALE DEL BOTTONE 
        // DOPO CHE E' STATO CARICATO DAL JSON
        document.getElementById('playAudio').dataset.originalText = data.playAudioButton;
        
        console.log(`Lingua impostata su: ${lang}`);
        document.documentElement.lang = lang;

    } catch (error) {
        console.error('Errore nel caricamento dei testi:', error);
    }
};

// Funzione per gestire la riproduzione e pausa dell'audio (NON CAMBIA)
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

// Aggiungi un "ascoltatore di eventi" al bottone audio (NON CAMBIA)
document.getElementById('playAudio').addEventListener('click', toggleAudio);

// Aggiungi i listener ai bottoni delle bandiere per cambiare lingua (NON CAMBIA)
document.querySelector('.language-selector').addEventListener('click', (event) => {
    const button = event.target.closest('button');
    if (button) {
        document.getElementById('audioPlayer').pause();
        document.getElementById('audioPlayer').currentTime = 0;
        const lang = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        setLanguage(lang);
    }
});

// Imposta la lingua di default (italiano) al caricamento della pagina
window.onload = () => {
    setLanguage('it');
};
