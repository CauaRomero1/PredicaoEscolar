import unittest
import json
import logging
import warnings
from pymongo import MongoClient, errors
from main import app

# Oculta os ResourceWarnings (ex: conexões Mongo não fechadas)
warnings.simplefilter("ignore", ResourceWarning)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        logger.info("✅ Rota '/' respondeu com 200 OK.")

    def test_dashboard_route(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        logger.info("✅ Rota '/dashboard' respondeu com 200.")

    def test_predict_route_valid(self):
        payload = {
            "features": [16, 1, 2, 3, 10, 2, 1, 1, 1, 0, 0, 1]
        }
        response = self.app.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("predicao", response.get_json())
        logger.info("✅ Rota '/predict' com dados válidos funcionou corretamente.")

    def test_predict_route_invalid_features(self):
        payload = {
            "features": [16, 1]  # Dados incompletos
        }
        response = self.app.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("erro", response.get_json())
        logger.info("✅ Rota '/predict' respondeu corretamente com erro para dados inválidos.")

    def test_dashboard_data_route(self):
        response = self.app.get('/dashboard_data')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("prediction_counts", json_data)
        self.assertIn("distribution_data", json_data)
        logger.info("✅ Rota '/dashboard_data' respondeu com dados esperados.")

    def test_connection_failure(self):
        """Simula falha de conexão com o MongoDB"""
        bad_uri = 'mongodb://localhost:9999'  # Porta errada para simular falha
        client = None
        try:
            client = MongoClient(bad_uri, serverSelectionTimeoutMS=1000)
            client.server_info()  # Força conexão
            self.fail("Era esperado falhar na conexão com o MongoDB, mas conseguiu conectar.")
        except errors.ServerSelectionTimeoutError:
            logger.info("❌ Falha simulada na conexão com o MongoDB ocorreu como esperado.")
        finally:
            if client:
                client.close()

if __name__ == '__main__':
    unittest.main()
