import unittest
import os
import sys
from unittest.mock import MagicMock, patch
from BoxUtils.box_utils import BoxUtils

class TestBoxUtils(unittest.TestCase):

    def setUp(self):
        # Mock the BoxClient and authentication to avoid actual network calls during basic tests
        # For integration tests, we might want to use real credentials or a more sophisticated mock
        self.mock_client = MagicMock()
        
    @patch('BoxUtils.box_utils.ConfigJWT')
    def test_initialization(self, mock_config_jwt):
        # Test that BoxUtils initializes correctly
        mock_config_instance = mock_config_jwt.return_value
        mock_config_instance.get_jwt_enterprise_client.return_value = self.mock_client
        
        box_utils = BoxUtils(env='dummy.env', config='dummy.config.json')
        self.assertIsNotNone(box_utils.client)
        
    @patch('BoxUtils.box_utils.ConfigJWT')
    def test_search_items_bug_fix(self, mock_config_jwt):
        # Verify the fix for search_items calling index_folder_recursively
        mock_config_instance = mock_config_jwt.return_value
        mock_config_instance.get_jwt_enterprise_client.return_value = self.mock_client
        
        box_utils = BoxUtils(env='dummy.env', config='dummy.config.json')
        
        # Mock index_folder_recursively to populate folder_contents
        box_utils.index_folder_recursively = MagicMock()
        box_utils.folder_contents = [
            {'full_path': 'folder/file.txt', 'name': 'file.txt', 'type': 'file'},
            {'full_path': 'folder/image.png', 'name': 'image.png', 'type': 'file'}
        ]
        
        # Test search
        results = box_utils.search_items('*.txt')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'file.txt')

if __name__ == '__main__':
    unittest.main()
