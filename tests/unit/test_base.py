import unittest

from tests.constants import TESTING_TEMP_FOLDER

from raiden_installer.account import Account
from raiden_installer.base import PassphraseFile, RaidenConfigurationFile
from raiden_installer.network import Network


class PassphraseFileTestCase(unittest.TestCase):
    def setUp(self):
        self.file_path = TESTING_TEMP_FOLDER.joinpath("passphrase")
        self.passphrase_file = PassphraseFile(self.file_path)

    def test_store_and_retrieve_passphrase(self):
        password = "test_password"
        self.passphrase_file.store(password)
        self.assertEqual(self.passphrase_file.retrieve(), password)

    def tearDown(self):
        try:
            self.file_path.unlink()
        except FileNotFoundError:
            pass


class RaidenConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        RaidenConfigurationFile.FOLDER_PATH = TESTING_TEMP_FOLDER.joinpath("config")

        keystore_folder = TESTING_TEMP_FOLDER.joinpath("keystore")
        self.account = Account.create(keystore_folder, passphrase="test_raiden_config")
        self.network = Network.get_by_name("goerli")

        self.configuration_file = RaidenConfigurationFile(
            self.account.keystore_file_path,
            "demo_env",
            "http://localhost:8545",
        )

    def test_can_save_configuration(self):
        self.configuration_file.save()
        self.assertTrue(self.configuration_file.path.exists())

    def test_can_create_configuration(self):
        self.configuration_file.save()
        all_configs = RaidenConfigurationFile.get_available_configurations()
        self.assertEqual(len(all_configs), 1)

    def test_can_get_by_filename(self):
        self.configuration_file.save()
        try:
            RaidenConfigurationFile.get_by_filename(self.configuration_file.file_name)
        except ValueError:
            self.fail("should load configuration by file name")

    def test_cannot_get_by_not_existing_filename(self):
        with self.assertRaises(ValueError):
            RaidenConfigurationFile.get_by_filename("invalid")

    def tearDown(self):
        for config in RaidenConfigurationFile.get_available_configurations():
            config.path.unlink()
        self.account.keystore_file_path.unlink()
