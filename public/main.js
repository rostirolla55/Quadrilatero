// Funzione asincrona per caricare il file JSON di una lingua
async function fetchTranslations(lang) {
  try {
    const response = await fetch(`../data/translations/${lang}/${lang}.json`);
    if (!response.ok) {
      throw new Error(`Impossibile caricare il file di traduzione per la lingua: ${lang}`);
    }
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
}

// Funzione principale per cambiare la lingua del sito
async function setLanguage(lang) {
  const translations = await fetchTranslations(lang);
  if (!translations) {
    console.error('Traduzioni non disponibili.');
    return;
  }

  // Aggiorna il testo di ogni elemento con l'attributo data-lang
  document.querySelectorAll('[data-lang]').forEach(element => {
    const key = element.getAttribute('data-lang');
    if (translations[key]) {
      element.textContent = translations[key];
    }
  });

  // Aggiorna l'attributo lang del tag html per l'accessibilità
  document.documentElement.lang = lang;

  // Gestisci il cambio di audio
  const audioPlayer = document.getElementById('audioPlayer');
  if (audioPlayer) {
      // Sostituisci il percorso dell'audio con la nuova lingua
      audioPlayer.src = `../assets/audio/${lang}/home_bologna.mp3`;
      // L'audio si metterà automaticamente in pausa se era in riproduzione
  }
}

// Chiamata iniziale: imposta la lingua di default all'avvio
document.addEventListener('DOMContentLoaded', () => {
    setLanguage('it'); // Lingua di default
});
