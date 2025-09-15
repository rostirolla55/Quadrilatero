<script>
    const playButton = document.getElementById('playAudio');
    const audioPlayer = document.getElementById('audioPlayer');

    const itFlagButton = document.getElementById('it-flag-button'); // Seleziona il bottone con l'ID

    audioPlayer.addEventListener('loadeddata', () => {
        console.log("Audio caricato e pronto per la riproduzione.");
    });

    playButton.addEventListener('click', () => {
        if (audioPlayer.paused) {
            audioPlayer.play();
            playButton.textContent = 'Metti in pausa';
        } else {
            audioPlayer.pause();
            playButton.textContent = 'Ascolta l\'audio in italiano';
        }
    });

    // Aggiungi l'evento al bottone della bandiera italiana
    itFlagButton.addEventListener('click', () => {
        audioPlayer.play();
        alert('Hai selezionato la lingua: Italiano');
    });

    function changeLanguage(lang) {
        alert('Hai selezionato la lingua: ' + lang);
    }
</script>
