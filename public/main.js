// Seleziona il lettore audio
const audioPlayer = document.getElementById('audioPlayer');

// Seleziona il bottone "Ascolta l'audio" (questo rimane invariato)
const playButton = document.getElementById('playAudio');

// Aggiungi un listener solo al bottone "Ascolta l'audio" per gestirne la riproduzione
playButton.addEventListener('click', () => {
    if (audioPlayer.paused) {
        audioPlayer.play();
        playButton.textContent = 'Metti in pausa';
    } else {
        audioPlayer.pause();
        playButton.textContent = 'Ascolta l\'audio in italiano';
    }
});

// La funzione per il cambio lingua, che verrà richiamata dai bottoni
function changeLanguage(lang) {
    alert('Hai selezionato la lingua: ' + lang);
    
    // In futuro, qui andrà il codice per caricare i nuovi testi e audio
    // Esempio (per tua futura implementazione):
    // const newUrl = `/Quadrilatero/${lang}/index.html`;
    // window.location.href = newUrl;
}
