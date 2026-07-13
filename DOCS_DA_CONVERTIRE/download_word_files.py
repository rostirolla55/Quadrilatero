import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Ambiti (Scopes): usiamo 'drive' invece di 'drive.readonly' 
# perché ora dobbiamo anche SPOSTARE i file di cartella (operazione di modifica)
SCOPES = ['https://www.googleapis.com/auth/drive']

# ID della tua cartella di destinazione su Google Drive
CARTELLA_ARCHIVIO_ID = "16ISHTqT5BKr-gBj-XdN8m_sszaMaEie9"

def get_gdrive_service():
    creds = None
    # Il file token.json memorizza i token di accesso dell'utente.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se non ci sono credenziali valide, avvia il login nel browser
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def download_word_files():
    service = get_gdrive_service()

    # Inserisci qui la stringa che vuoi cercare nel nome del file
    filtro_nome = "_analysis_"

    # Query aggiornata: esclude l'archivio, filtra per tipo di file E pretende il testo nel nome
    query = (
        f"not '{CARTELLA_ARCHIVIO_ID}' in parents and "
        f"name contains '{filtro_nome}' and "
        "(mimeType = 'application/vnd.google-apps.document' or "
        "mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')"
    )
    
    print(f"Ricerca dei file che contengono '{filtro_nome}' nel nome...")
    results = service.files().list(
        q=query, 
        pageSize=20, 
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    
    items = results.get('files', [])

    if not items:
        print(f"Nessun nuovo documento con '{filtro_nome}' nel nome trovato.")
        return

    print(f"Trovati {len(items)} file corrispondenti al filtro.")
    
    for item in items:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']
        
        print(f"\nDownload in corso: {file_name} ({file_id})")

        # Caso 1: È un Google Doc nativo -> Esportazione in formato Word (.docx)
        if mime_type == 'application/vnd.google-apps.document':
            if not file_name.endswith('.docx'):
                file_name += '.docx'
            
            request = service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        # Caso 2: È già un file Word (.docx) -> Download diretto del file binario
        else:
            request = service.files().get_media(fileId=file_id)

        # Salvataggio del file sul computer locale
        fh = io.FileIO(file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Progresso download: {int(status.progress() * 100)}%")
            
        print(f"Salvato localmente come: {file_name}")

        # --- LOGICA DI SPOSTAMENTO SU GOOGLE DRIVE ---
        try:
            print(f"Archiviazione in corso su Google Drive...")
            file_metadata = service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file_metadata.get('parents', []))

            service.files().update(
                fileId=file_id,
                addParents=CARTELLA_ARCHIVIO_ID,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            print(f"OK: Spostato nella cartella di archivio su Drive.")

        except Exception as e:
            print(f"Errore durante lo spostamento del file su Drive: {e}")
            
    print("\nProcedura terminata!")
if __name__ == '__main__':
    download_word_files()