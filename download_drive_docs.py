import io
import os
import sys
import argparse
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']
CARTELLA_ARCHIVIO_ID_DEFAULT = "1RmRjM5op1iRFEEEavih6SIujbHJS1PLw"
DEFAULT_OUTPUT_DIR = "DOCS_DA_CONVERTIRE"

def get_gdrive_service(token_file: str = 'token.json', credentials_file: str = 'credentials.json'):
    """
    Gestisce l'autenticazione con l'API Google Drive e restituisce il servizio.
    """
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"ERRORE: File delle credenziali '{credentials_file}' non trovato. "
                    "Scaricalo dalla Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def download_word_files(
    id_pagina: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    archive_folder_id: str = CARTELLA_ARCHIVIO_ID_DEFAULT,
    token_file: str = 'token.json',
    credentials_file: str = 'credentials.json'
) -> int:
    """
    Scarica da Google Drive tutti i file Word o Google Docs che contengono
    nel nome l'ID della pagina specificato e li sposta nella cartella di archivio.

    :param id_pagina: Nome o identificativo della pagina (es. 'carracci', 'chiesasancarlo').
    :param output_dir: Cartella locale dove salvare i file scaricati.
    :param archive_folder_id: ID della cartella di archivio su Google Drive.
    :return: Numero di file scaricati con successo.
    """
    # Determinazione del filtro
    filtro_nome = id_pagina.strip().lower() if id_pagina else 'carracci'
    print(f"\n[CONFIGURAZIONE] ID Pagina / Filtro: '{filtro_nome}'")
    print(f"[CONFIGURAZIONE] Cartella Destinazione Locale: '{output_dir}'")

    # Assicura l'esistenza della cartella locale
    os.makedirs(output_dir, exist_ok=True)

    # Inizializza servizio Google Drive
    service = get_gdrive_service(token_file, credentials_file)

    # Query: cerca i documenti escludendo quelli già archiviati e che contengono il filtro
    query = (
        f"not '{archive_folder_id}' in parents and "
        f"name contains '{filtro_nome}' and "
        "(mimeType = 'application/vnd.google-apps.document' or "
        "mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')"
    )

    print("Esecuzione query di ricerca su Google Drive...")
    results = service.files().list(
        q=query,
        pageSize=50,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print(f"⚠️ Nessun nuovo documento trovato con '{filtro_nome}' nel nome.")
        return 0

    print(f"✅ Trovati {len(items)} file corrispondenti al filtro '{filtro_nome}'.")

    downloaded_count = 0

    for item in items:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']

        # Normalizzazione estensione localmente
        clean_name = file_name.replace('.gdoc', '')
        if clean_name.lower().endswith('.docx'):
            clean_name = clean_name[:-5]
        clean_name += '.docx'

        # Percorso completo di destinazione locale
        local_filepath = os.path.join(output_dir, clean_name)

        print(f"\nDownload in corso: '{clean_name}' (ID Drive: {file_id})")

        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            request = service.files().get_media(fileId=file_id)

        # Salvataggio su disco locale
        with io.FileIO(local_filepath, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"  Progresso download: {int(status.progress() * 100)}%")

        print(f"  OK: Salvato in locale -> {local_filepath}")
        downloaded_count += 1

        try:
            print("  Archiviazione su Google Drive in corso...")
            file_metadata = service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file_metadata.get('parents', []))

            service.files().update(
                fileId=file_id,
                addParents=archive_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            print("  OK: Spostato nella cartella di archivio su Drive.")
        except Exception as e:
            print(f"  ❌ Errore durante lo spostamento su Drive: {e}")

    print(f"\n✅ Procedura completata! Totale file scaricati: {downloaded_count}")
    return downloaded_count

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Scarica da Google Drive i documenti associati ad una pagina specifica."
    )
    parser.add_argument(
        'page_id',
        nargs='?',
        default=None,
        help="ID o nome della pagina da filtrare (es. 'carracci', 'chiesasancarlo')"
    )
    parser.add_argument(
        '--output', '-o',
        default=DEFAULT_OUTPUT_DIR,
        help="Cartella di destinazione locale (default: 'DOCS_DA_CONVERTIRE')"
    )
    parser.add_argument(
        '--archive-id', '-a',
        default=CARTELLA_ARCHIVIO_ID_DEFAULT,
        help="ID della cartella di archivio su Google Drive"
    )

    args = parser.parse_args()

    # Esegue il download con i parametri passati
    download_word_files(
        id_pagina=args.page_id,
        output_dir=args.output,
        archive_folder_id=args.archive_id
    )