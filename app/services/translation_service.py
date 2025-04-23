# app/services/translation_service.py
import logging
import argostranslate.package
import argostranslate.translate
import os # Import os for path operations if needed, though argostranslate handles paths internally

logger = logging.getLogger(__name__)

class TranslationPackageManager:
    """
    Manages translation packages and performs translations.
    Checks the actual installation directory for packages.
    """
    def __init__(self):
        self.installed_packages = set()
        self.update_available_packages()
        self._sync_installed_packages() # Sync with disk on init

    def _sync_installed_packages(self) -> None:
        """Synchronize the internal set with actually installed packages."""
        logger.debug("Syncing installed packages from disk...")
        self.installed_packages.clear()
        try:
            installed = argostranslate.package.get_installed_packages()
            for pkg in installed:
                # Assuming pkg object has from_code and to_code attributes
                # Adjust if the structure is different
                if hasattr(pkg, 'from_code') and hasattr(pkg, 'to_code'):
                     package_key = f"{pkg.from_code}-{pkg.to_code}"
                     self.installed_packages.add(package_key)
                # Handle potential variations in package object structure if necessary
                # elif hasattr(pkg, 'metadata'): # Example alternative check
                #    metadata = pkg.metadata
                #    if 'from_code' in metadata and 'to_code' in metadata:
                #       package_key = f"{metadata['from_code']}-{metadata['to_code']}"
                #       self.installed_packages.add(package_key)
            logger.info(f"Found {len(self.installed_packages)} installed packages on disk.")
        except Exception as e:
            logger.error(f"Error syncing installed packages: {str(e)}")


    def update_available_packages(self) -> None:
        """Download package index and update available packages."""
        try:
            argostranslate.package.update_package_index()
            self.available_packages = argostranslate.package.get_available_packages()
            logger.info(f"Available packages index updated. Found {len(self.available_packages)} packages.")
        except Exception as e:
             logger.error(f"Failed to update package index: {str(e)}")
             self.available_packages = [] # Ensure it's an empty list on failure


    def install_package(self, from_code: str, to_code: str) -> bool:
        """
        Install a specific language package if not already installed on disk.

        Args:
            from_code: Source language code
            to_code: Target language code

        Returns:
            bool: Success status (True if already installed or installed successfully)
        """
        package_key = f"{from_code}-{to_code}"

        # Quick check against internal cache
        if package_key in self.installed_packages:
            logger.debug(f"Package {package_key} already tracked as installed.")
            return True

        # Re-sync with disk to get the most current state
        self._sync_installed_packages()
        if package_key in self.installed_packages:
            logger.info(f"Package {package_key} found on disk (previously untracked).")
            return True

        logger.info(f"Attempting to install package {package_key}...")

        # Find the package in the available index
        available_package = next(
            (
                pkg for pkg in self.available_packages
                if hasattr(pkg, 'from_code') and hasattr(pkg, 'to_code') and \
                   pkg.from_code == from_code and pkg.to_code == to_code
            ),
            None
        )

        if not available_package:
            logger.warning(f"Package {package_key} not found in available package index.")
            # Attempt to update index again in case it was stale
            self.update_available_packages()
            available_package = next(
                (
                    pkg for pkg in self.available_packages
                    if hasattr(pkg, 'from_code') and hasattr(pkg, 'to_code') and \
                       pkg.from_code == from_code and pkg.to_code == to_code
                ),
                None
            )
            if not available_package:
                 logger.error(f"Package {package_key} still not found after index update.")
                 return False


        # Download and install the package
        try:
            logger.info(f"Downloading package {package_key}...")
            download_path = available_package.download()
            logger.info(f"Installing package {package_key} from {download_path}...")
            argostranslate.package.install_from_path(download_path)
            # Successfully installed, update internal set
            self.installed_packages.add(package_key)
            logger.info(f"Package {package_key} installed successfully.")
            # Clean up downloaded file if necessary (optional)
            # os.remove(download_path)
            return True
        except Exception as e:
            logger.error(f"Failed to install package {package_key}: {str(e)}")
            return False

    def install_configured_packages(self, packages_list) -> None:
        """
        Install all packages in the provided list if not already present.

        Args:
            packages_list: List of package codes in format "from-to"
        """
        if not packages_list:
            logger.warning("No packages configured for installation.")
            return

        logger.info(f"Checking and installing configured packages: {packages_list}")
        # Sync once before starting batch install for efficiency
        self._sync_installed_packages()

        for package_code in packages_list:
            try:
                from_code, to_code = package_code.split("-")
                # install_package now handles the check for existing installs
                self.install_package(from_code, to_code)
            except ValueError:
                logger.error(f"Invalid package code format in configuration: {package_code}")
            except Exception as e:
                 logger.error(f"Error processing configured package {package_code}: {str(e)}")


    def translate(self, text: str, from_code: str, to_code: str, fallback_response: str) -> str:
        """
        Translate text using installed language packages.

        Args:
            text: Text to translate
            from_code: Source language code
            to_code: Target language code
            fallback_response: Response to return if translation fails

        Returns:
            str: Translated text or fallback response
        """
        # Rely directly on get_installed_languages which checks the actual installation
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
            to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

            if not from_lang:
                logger.warning(f"Source language '{from_code}' not installed or available.")
                # Optionally attempt installation here if desired, but might slow down requests
                # if not self.install_package(from_code, to_code): # Example: try installing on-demand
                #    return fallback_response
                # # Re-fetch languages if install was attempted
                # installed_languages = argostranslate.translate.get_installed_languages()
                # from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
                # if not from_lang: return fallback_response # Still not available
                return fallback_response # Keep it simple: return fallback if not found initially

            if not to_lang:
                 logger.warning(f"Target language '{to_code}' not installed or available.")
                 # Optionally attempt installation here
                 return fallback_response

            translation = from_lang.get_translation(to_lang)
            if not translation:
                 logger.error(f"Could not get translation object from '{from_code}' to '{to_code}'. Package might be corrupted or incomplete.")
                 return fallback_response

            logger.debug(f"Performing translation from {from_code} to {to_code}")
            translated_text = translation.translate(text)
            return translated_text

        except argostranslate.translate.LanguageNotInstalledError as e:
             logger.warning(f"Translation failed: {str(e)}. Package for {from_code}-{to_code} might be missing or corrupted.")
             return fallback_response
        except Exception as e:
            # Catch other potential errors during translation
            logger.error(f"An unexpected error occurred during translation from {from_code} to {to_code}: {str(e)}", exc_info=True)
            return fallback_response