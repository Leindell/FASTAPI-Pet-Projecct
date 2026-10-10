"""Сквозные тесты: настоящие HTTP-запросы через все слои, но без запуска сервера."""
import unittest

from fastapi.testclient import TestClient

from main import app
from tests import auth_headers, reset_db

NESSIE = {"name": "Nessie", "country": "GB", "area": "Loch Ness"}


class CreatureApiTest(unittest.TestCase):
    def setUp(self):
        reset_db()
        self.client = TestClient(app)
        self.auth = auth_headers(self.client)

    def test_get_all(self):
        response = self.client.get("/creatures")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([c["name"] for c in response.json()], ["Bigfoot", "Yeti"])

    def test_filter_by_country(self):
        response = self.client.get("/creatures", params={"country": "US"})
        self.assertEqual([c["name"] for c in response.json()], ["Bigfoot"])

    def test_pagination(self):
        response = self.client.get("/creatures", params={"limit": 1, "offset": 1})
        self.assertEqual([c["name"] for c in response.json()], ["Yeti"])

    def test_pagination_validation(self):
        self.assertEqual(self.client.get("/creatures", params={"limit": 0}).status_code, 422)

    def test_get_one(self):
        response = self.client.get("/creatures/Yeti")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["country"], "CN")

    def test_get_missing(self):
        self.assertEqual(self.client.get("/creatures/Chupacabra").status_code, 404)

    def test_create(self):
        response = self.client.post("/creatures", json=NESSIE, headers=self.auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get("/creatures/Nessie").json()["area"], "Loch Ness")

    def test_create_duplicate(self):
        self.client.post("/creatures", json=NESSIE, headers=self.auth)
        self.assertEqual(self.client.post("/creatures", json=NESSIE, headers=self.auth).status_code, 409)

    def test_create_invalid_country(self):
        response = self.client.post("/creatures", json={**NESSIE, "country": "uk"}, headers=self.auth)
        self.assertEqual(response.status_code, 422)

    def test_create_aka_equals_name(self):
        response = self.client.post("/creatures", json={**NESSIE, "aka": "nessie"}, headers=self.auth)
        self.assertEqual(response.status_code, 400)

    def test_patch(self):
        response = self.client.patch("/creatures/Yeti", json={"area": "Tibet", "aka": None}, headers=self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["area"], "Tibet")
        self.assertEqual(response.json()["aka"], "Abominable Snowman")

    def test_patch_missing(self):
        self.assertEqual(self.client.patch("/creatures/Nope", json={"area": "x"}, headers=self.auth).status_code, 404)

    def test_write_requires_auth(self):
        self.assertEqual(self.client.post("/creatures", json=NESSIE).status_code, 401)
        self.assertEqual(self.client.delete("/creatures/Yeti").status_code, 401)

    def test_delete(self):
        self.assertEqual(self.client.delete("/creatures/Yeti", headers=self.auth).status_code, 204)
        self.assertEqual(self.client.get("/creatures/Yeti").status_code, 404)


if __name__ == "__main__":
    unittest.main()
