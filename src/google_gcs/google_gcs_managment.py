import subprocess

from google.cloud import storage
import os


class GoogleCloudConnector:
    def __init__(self, credentials_json: str):
        """
        Inicializa la conexión con Google Cloud usando credenciales de la cuenta de servicio.

        :param credentials_json: Credenciales en formato JSON.
        """
        self.credentials_json = credentials_json
        self.client = None

    def authenticate(self):
        """Autentica con Google Cloud usando las credenciales proporcionadas."""
        # Escribir credenciales en un archivo temporal
        credentials_path = "temp_gcs_credentials.json"
        with open(credentials_path, "w") as cred_file:
            cred_file.write(self.credentials_json)

        # Configurar la variable de entorno para Google Cloud
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Crear un cliente de almacenamiento
        self.client = storage.Client()
        print("Autenticación con Google Cloud completada.")

        # Eliminar el archivo de credenciales después de la autenticación
        os.remove(credentials_path)

    async def list_blobs(self, bucket_name):
        """Lists all the blobs in the bucket."""
        # bucket_name = "your-bucket-name"

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = self.client.list_blobs(bucket_name)
        dir = []
        for blob in blobs:
            if 'leones/supervisor/2024-12-04' in blob.name:
                dir.append(blob.name)
        return dir

    async def search_files(self, bucket_name: str, prefix: str, date: str):
        """
        Busca archivos en un bucket de GCS que coincidan con un prefijo y un patrón de fecha.

        :param bucket_name: Nombre del bucket donde buscar.
        :param prefix: Prefijo para filtrar archivos.
        :param date: Patrón de fecha para filtrar archivos (por ejemplo, '2023-12-03').
        :return: Lista de nombres de archivos encontrados que coinciden con el patrón.
        """
        print(':: Entro a buscar ::')
        if not self.client:
            raise Exception("El cliente no está autenticado. Llame a authenticate primero.")

        # Obtener el bucket
        blobs = self.client.list_blobs(prefix=prefix, bucket_name=bucket_name)
        for blob in blobs:
            print(blob.name)

        matched_files = [blob.name for blob in blobs if date in blob.name]
        return matched_files

    async def listar_directorios(self, bucket_name, prefix, filtro_fecha):
        """Lista los nombres de directorios que coinciden con una fecha específica."""
        blobs = self.client.list_blobs(bucket_name, prefix=prefix, delimiter='/')

        # Recorrer blobs y filtrar los que coincidan con la fecha
        directorios = []
        for page in blobs.pages:
            if 'prefixes' in page:
                for directorio in page['prefixes']:
                    print(directorio)
                    if filtro_fecha in directorio:
                        directorios.append(directorio)

        return directorios

    def fetch_history(self, environment, date):
        try:
            dires = []
            perfiles = ['agente', 'supervisor', 'bot']
            # Construir el comando gsutil con la variable `environment`
            bucket_url = f"gs://qa-allure-report-storage-automation/{environment}/"
            for perfil in perfiles:
                result = subprocess.run(
                    ["gsutil", "ls", bucket_url + perfil],
                    capture_output=True, text=True, check=True
                )

                # Filtrar líneas que contienen la fecha
                lines = [line for line in result.stdout.splitlines() if date in line]

                # Retornar las líneas filtradas
                for line in lines:
                    dires.append(line)
            return dires

        except subprocess.CalledProcessError as e:
            print(f"Error ejecutando gsutil: {e}")
            print(f"Salida estándar: {e.stdout}")
            print(f"Error estándar: {e.stderr}")
            return []

