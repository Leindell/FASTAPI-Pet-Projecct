import unittest

from fastapi.testclient import TestClient

from main import app
from service.security import create_token, decode_token, hash_password, verify_password
from tests import auth_headers, reset_db


class SecurityTest(unittest.TestCase):
    def test_password_hash(self):
        stored = hash_password("qwerty123")
        self.assertNotIn("qwerty123", stored)
        self.assertTrue(verify_password("qwerty123", stored))
        self.assertFalse(verify_password("qwerty124", stored))

    def test_same_password_different_hash(self):
        self.assertNotEqual(hash_password("qwerty123"), hash_password("qwerty123"))

    def test_token_roundtrip(self):
        self.assertEqual(decode_token(create_token("alice")), "alice")

    def test_tampered_token(self):
        header, payload, signature = create_token("alice").split(".")
        forged = create_token("admin").split(".")[1]
        self.assertIsNone(decode_token(f"{header}.{forged}.{signature}"))
        self.assertIsNone(decode_token("мусор"))
        self.assertIsNone(decode_token("a.b.ключ"))


class AuthApiTest(unittest.TestCase):
    def setUp(self):
        reset_db()
        self.client = TestClient(app)

    def test_register_hides_hash(self):
        response = self.client.post("/users", json={"name": "alice", "password": "secret-pass"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"name": "alice"})

    def test_register_duplicate(self):
        body = {"name": "alice", "password": "secret-pass"}
        self.client.post("/users", json=body)
        self.assertEqual(self.client.post("/users", json=body).status_code, 409)

    def test_short_password(self):
        response = self.client.post("/users", json={"name": "alice", "password": "123"})
        self.assertEqual(response.status_code, 422)

    def test_login_wrong_password(self):
        self.client.post("/users", json={"name": "alice", "password": "secret-pass"})
        response = self.client.post("/users/token", data={"username": "alice", "password": "wrong-pass"})
        self.assertEqual(response.status_code, 401)

    def test_me(self):
        self.assertEqual(self.client.get("/users/me").status_code, 401)
        response = self.client.get("/users/me", headers=auth_headers(self.client, "alice"))
        self.assertEqual(response.json(), {"name": "alice"})

    def test_bad_token(self):
        response = self.client.get("/users/me", headers={"Authorization": "Bearer a.b.c"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
