# tests/test_translation.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.translation_service import TranslationPackageManager

class TestTranslationService:
    """Tests for the translation service"""
    
    @pytest.fixture
    def mock_argos(self):
        """Mock argostranslate for testing"""
        with patch('app.services.translation_service.argostranslate.package'), \
             patch('app.services.translation_service.argostranslate.translate'):
            yield
    
    def test_init(self, mock_argos):
        """Test initialization"""
        manager = TranslationPackageManager()
        assert isinstance(manager.installed_packages, set)
        assert len(manager.installed_packages) == 0
    
    def test_install_package(self, mock_argos):
        """Test package installation"""
        with patch('app.services.translation_service.argostranslate.package') as mock_package:
            # Create a mock package
            mock_pkg = MagicMock()
            mock_pkg.from_code = "en"
            mock_pkg.to_code = "es"
            
            # Set up mocks
            mock_package.get_available_packages.return_value = [mock_pkg]
            mock_pkg.download.return_value = "/tmp/package.argosmodel"
            
            # Create manager and test installation
            manager = TranslationPackageManager()
            result = manager.install_package("en", "es")
            
            # Assertions
            assert result is True
            assert "en-es" in manager.installed_packages
            mock_pkg.download.assert_called_once()
            mock_package.install_from_path.assert_called_once_with("/tmp/package.argosmodel")
    
    def test_install_configured_packages(self, mock_argos):
        """Test installation of multiple packages"""
        manager = TranslationPackageManager()
        
        # Mock the install_package method
        manager.install_package = MagicMock(return_value=True)
        
        # Install packages
        manager.install_configured_packages(["en-es", "fr-en", "de-en"])
        
        # Verify calls
        assert manager.install_package.call_count == 3
        manager.install_package.assert_any_call("en", "es")
        manager.install_package.assert_any_call("fr", "en")
        manager.install_package.assert_any_call("de", "en")
    
    def test_translate(self, mock_argos):
        """Test translation functionality"""
        with patch('app.services.translation_service.argostranslate.translate') as mock_translate:
            # Set up mocks
            mock_from_lang = MagicMock()
            mock_to_lang = MagicMock()
            mock_translation = MagicMock()
            
            mock_from_lang.code = "en"
            mock_to_lang.code = "es"
            mock_translate.get_installed_languages.return_value = [mock_from_lang, mock_to_lang]
            mock_from_lang.get_translation.return_value = mock_translation
            mock_translation.translate.return_value = "Hola mundo"
            
            # Create manager
            manager = TranslationPackageManager()
            manager.installed_packages.add("en-es")  # Pretend the package is installed
            
            # Test translation
            result = manager.translate("Hello world", "en", "es", "Fallback")
            
            # Assertions
            assert result == "Hola mundo"
            mock_from_lang.get_translation.assert_called_once_with(mock_to_lang)
            mock_translation.translate.assert_called_once_with("Hello world")
    
    def test_translate_fallback(self, mock_argos):
        """Test fallback when translation fails"""
        manager = TranslationPackageManager()
        
        # Mock install_package to fail
        manager.install_package = MagicMock(return_value=False)
        
        # Test translation with package installation failure
        result = manager.translate("Hello world", "en", "es", "Fallback message")
        
        # Assertions
        assert result == "Fallback message"
        manager.install_package.assert_called_once_with("en", "es")
    
    def test_translate_exception(self, mock_argos):
        """Test handling of exceptions during translation"""
        with patch('app.services.translation_service.argostranslate.translate') as mock_translate:
            # Set up mock to raise exception
            mock_translate.get_installed_languages.side_effect = Exception("Test error")
            
            # Create manager
            manager = TranslationPackageManager()
            manager.installed_packages.add("en-es")  # Pretend the package is installed
            
            # Test translation with exception
            result = manager.translate("Hello world", "en", "es", "Fallback for error")
            
            # Assertions
            assert result == "Fallback for error"