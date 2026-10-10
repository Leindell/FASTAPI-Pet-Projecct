"""Unit-тесты уровня данных: вызываем функции напрямую, без HTTP."""
import unittest

import data.creature as data
from errors import Duplicate, Missing
from model.creature import Creature, CreatureUpdate
from tests import reset_db

NESSIE = Creature(name="Nessie", country="GB", area="Loch Ness", aka="Nessiteras rhombopteryx")


class CreatureDataTest(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_create_and_get(self):
        data.create(NESSIE)
        self.assertEqual(data.get_one("Nessie"), NESSIE)

    def test_create_duplicate(self):
        data.create(NESSIE)
        with self.assertRaises(Duplicate):
            data.create(NESSIE)

    def test_get_missing(self):
        with self.assertRaises(Missing):
            data.get_one("Chupacabra")

    def test_get_all_sorted_by_name(self):
        self.assertEqual([c.name for c in data.get_all()], ["Bigfoot", "Yeti"])

    def test_modify_only_sent_fields(self):
        updated = data.modify("Yeti", CreatureUpdate(area="Tibet"))
        self.assertEqual(updated.area, "Tibet")
        self.assertEqual(updated.aka, "Abominable Snowman")

    def test_delete(self):
        data.delete("Yeti")
        with self.assertRaises(Missing):
            data.get_one("Yeti")


if __name__ == "__main__":
    unittest.main()
