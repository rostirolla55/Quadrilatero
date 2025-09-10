// Gestione del pulsante per l'audio
const playButton = document.getElementById('playAudio');
const audioPlayer = document.getElementById('audioPlayer');

if (playButton && audioPlayer) {
    playButton.addEventListener('click', () => {
        if (audioPlayer.paused) {
            audioPlayer.play();
            playButton.textContent = 'Metti in pausa';
        } else {
            audioPlayer.pause();
            playButton.textContent = 'Ascolta l\'audio';
        }
    });
}

// Funzione per il cambio lingua (probabilmente già presente nel tuo file)
function setLanguage(lang) {
    // Logica per cambiare la lingua del sito
    console.log('Cambio lingua in: ' + lang);
    // Esempio: reindirizzare alla pagina corretta
    window.location.href = `../${lang}/index.html`;
}
