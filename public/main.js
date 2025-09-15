<script>
// Seleziona il lettore audio e i due bottoni
const audioPlayer = document.getElementById('audioPlayer');
const playButton = document.getElementById('playAudio');
const itFlagButton = document.getElementById('it-flag-button');

// FUNZIONE UNIFICATA PER AVVIARE/METTERE IN PAUSA L'AUDIO
const toggleAudio = () => {
    if (audioPlayer.paused) {
        audioPlayer.play();
        playButton.textContent = 'Metti in pausa';
    } else {
        audioPlayer.pause();
        playButton.textContent = 'Ascolta l\'audio in italiano';
    }
};

// Assegna la funzione a entrambi i bottoni
playButton.addEventListener('click', toggleAudio);

itFlagButton.addEventListener('click', () => {
    toggleAudio();
    alert('Hai selezionato la lingua: Italiano');
});

// Le altre funzioni del tuo codice
audioPlayer.addEventListener('loadeddata', () => {
    console.log("Audio caricato e pronto per la riproduzione.");
});

function changeLanguage(lang) {
    alert('Hai selezionato la lingua: ' + lang);
}
</script>
