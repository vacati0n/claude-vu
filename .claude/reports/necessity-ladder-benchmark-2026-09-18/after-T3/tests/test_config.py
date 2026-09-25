import json
import os
import tempfile
import unittest

from app.config import Config, load_config
from app.errors import ConfigError


class LoadConfigTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)

    def _write(self, content: str) -> str:
        path = os.path.join(self._tmpdir.name, "config.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def _write_json(self, obj) -> str:
        return self._write(json.dumps(obj))

    # -- success cases -----------------------------------------------------

    def test_loads_all_fields(self):
        path = self._write_json({"port": 8080, "host": "example.com", "debug": True})
        config = load_config(path)
        self.assertEqual(config, Config(port=8080, host="example.com", debug=True))

    def test_applies_defaults_for_optional_fields(self):
        path = self._write_json({"port": 8080})
        config = load_config(path)
        self.assertEqual(config.host, "localhost")
        self.assertFalse(config.debug)

    def test_config_is_immutable(self):
        path = self._write_json({"port": 8080})
        config = load_config(path)
        with self.assertRaises(Exception):
            config.port = 9090

    # -- D-003 failure conditions -------------------------------------------

    def test_missing_file_raises_config_error(self):
        missing_path = os.path.join(self._tmpdir.name, "does-not-exist.json")
        with self.assertRaises(ConfigError):
            load_config(missing_path)

    def test_invalid_json_raises_config_error(self):
        path = self._write("{not valid json")
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_non_object_root_raises_config_error(self):
        path = self._write_json([1, 2, 3])
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_missing_port_raises_config_error(self):
        path = self._write_json({"host": "example.com"})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_port_wrong_type_string_raises_config_error(self):
        path = self._write_json({"port": "8080"})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_port_wrong_type_boolean_raises_config_error(self):
        path = self._write_json({"port": True})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_port_out_of_range_low_raises_config_error(self):
        path = self._write_json({"port": 0})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_port_out_of_range_high_raises_config_error(self):
        path = self._write_json({"port": 65536})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_unknown_field_raises_config_error(self):
        path = self._write_json({"port": 8080, "extra": "nope"})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_host_wrong_type_raises_config_error(self):
        path = self._write_json({"port": 8080, "host": 123})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_debug_wrong_type_raises_config_error(self):
        path = self._write_json({"port": 8080, "debug": "yes"})
        with self.assertRaises(ConfigError):
            load_config(path)

    def test_config_error_is_app_error(self):
        from app.errors import AppError

        missing_path = os.path.join(self._tmpdir.name, "does-not-exist.json")
        with self.assertRaises(AppError):
            load_config(missing_path)


if __name__ == "__main__":
    unittest.main()
