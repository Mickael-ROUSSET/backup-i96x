import logging
import os
import tempfile
import unittest
from unittest.mock import patch
from backup_trend.execution import executer_cycle
from backup_trend.rotation import appliquer_rotation
from backup_trend.sql_backup import _echapper_identifiant_sql, _echapper_sql_literal

class BackupTests(unittest.TestCase):
    def test_echappement_sql(self):
        self.assertEqual(_echapper_identifiant_sql("i]96X"), "i]]96X")
        self.assertEqual(_echapper_sql_literal("c'backup"), "c''backup")

    def test_pas_de_rotation_si_verification_echoue(self):
        cfg = {"verification": True}
        with patch("backup_trend.execution.creer_backup", return_value="test.bak"), \
             patch("backup_trend.execution.verifier_backup", side_effect=RuntimeError("verify failed")), \
             patch("backup_trend.execution.appliquer_rotation") as rotation:
            with self.assertRaises(RuntimeError):
                executer_cycle(cfg, logging.getLogger("test"))
            rotation.assert_not_called()

    def test_rotation_limitee_au_prefixe(self):
        with tempfile.TemporaryDirectory() as folder:
            for i in range(4):
                path = os.path.join(folder, "i96X_%d.bak" % i)
                with open(path, "wb") as f:
                    f.write(b"backup")
                os.utime(path, (100+i, 100+i))
            other = os.path.join(folder, "autre.bak")
            with open(other, "wb") as f:
                f.write(b"intact")
            appliquer_rotation({"repertoire":folder, "prefixe":"i96X", "nombre_a_conserver":2}, logging.getLogger("test"))
            self.assertEqual(len([x for x in os.listdir(folder) if x.startswith("i96X_")]), 2)
            self.assertTrue(os.path.exists(other))

if __name__ == "__main__":
    unittest.main()
