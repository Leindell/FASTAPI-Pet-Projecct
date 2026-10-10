import unittest

from fastapi.testclient import TestClient
from pydantic import ValidationError

from config import load_settings
from main import app


class SettingsTest(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(load_settings({}).token_minutes, 30)

    def test_from_env(self):
        settings = load_settings({
            "CRYPTID_TOKEN_MINUTES": "60",
            "CRYPTID_CORS_ORIGINS": "http://a.ru,http://b.ru",
            "PATH": "не наша переменная",
        })
        self.assertEqual(settings.token_minutes, 60)
        self.assertEqual(settings.cors_origins, ["http://a.ru", "http://b.ru"])

    def test_invalid_env(self):
        with self.assertRaises(ValidationError):
            load_settings({"CRYPTID_TOKEN_MINUTES": "много"})


class MiddlewareTest(unittest.TestCase):
    def test_health_and_timing_header(self):
        with TestClient(app) as client:  # with запускает lifespan
            response = client.get("/health")
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("x-process-time-ms", response.headers)

    def test_cors(self):
        response = TestClient(app).get("/health", headers={"Origin": "http://localhost:3000"})
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:3000")
        response = TestClient(app).get("/health", headers={"Origin": "http://evil.example"})
        self.assertNotIn("access-control-allow-origin", response.headers)


if __name__ == "__main__":
    unittest.main()
