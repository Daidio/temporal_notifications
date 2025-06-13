import dotenv, os

dotenv.load_dotenv()

# Clave secreta que el cliente debe enviar en el header "X-API-KEY"
API_KEY = os.getenv("API_KEY")

print(f'LA API KEY ES: {API_KEY}')