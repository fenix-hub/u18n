# app/services/translation_service.py
import logging
import argostranslate.package
import argostranslate.translate

logger = logging.getLogger(__name__)

class TranslationPackageManager:
    """
    Manages translation packages and performs translations
    """
    def __init__(self):
        self.installed_packages = set()
        self.update_available_packages()
    
    def update_available_packages(self) -> None:
        """Download package index and update available packages."""
        argostranslate.package.update_package_index()
        self.available_packages = argostranslate.package.get_available_packages()
        logger.info(f"Available packages updated. Found {len(self.available_packages)} packages.")
    
    def install_package(self, from_code: str, to_code: str) -> bool:
        """
        Install a specific language package.
        
        Args:
            from_code: Source language code
            to_code: Target language code
        
        Returns:
            bool: Success status
        """
        package_key = f"{from_code}-{to_code}"
        
        # Check if already installed
        if package_key in self.installed_packages:
            return True
        
        # Find the package
        available_package = next(
            (
                pkg for pkg in self.available_packages
                if pkg.from_code == from_code and pkg.to_code == to_code
            ),
            None
        )
        
        if not available_package:
            logger.warning(f"Package {package_key} not found.")
            return False
        
        # Download and install the package
        try:
            download_path = available_package.download()
            argostranslate.package.install_from_path(download_path)
            self.installed_packages.add(package_key)
            logger.info(f"Package {package_key} installed successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to install package {package_key}: {str(e)}")
            return False
    
    def install_configured_packages(self, packages_list) -> None:
        """
        Install all packages in the provided list
        
        Args:
            packages_list: List of package codes in format "from-to"
        """
        for package_code in packages_list:
            try:
                from_code, to_code = package_code.split("-")
                self.install_package(from_code, to_code)
            except ValueError:
                logger.error(f"Invalid package code format: {package_code}")
    
    def translate(self, text: str, from_code: str, to_code: str, fallback_response: str) -> str:
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            from_code: Source language code
            to_code: Target language code
            fallback_response: Response to return if translation fails
            
        Returns:
            str: Translated text or fallback response
        """
        package_key = f"{from_code}-{to_code}"
        
        # Install package if not already installed
        if package_key not in self.installed_packages:
            if not self.install_package(from_code, to_code):
                return fallback_response
        
        # Perform translation
        try:
            translations = argostranslate.translate.get_installed_languages()
            from_lang = next((l for l in translations if l.code == from_code), None)
            to_lang = next((l for l in translations if l.code == to_code), None)
            
            if not from_lang or not to_lang:
                logger.error(f"Language pair {from_code}-{to_code} not found in installed languages.")
                return fallback_response
            
            translation = from_lang.get_translation(to_lang)
            return translation.translate(text)
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return fallback_response