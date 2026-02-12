"""Translation management using Qt QTranslator."""
from typing import Dict, Optional, Tuple
import xml.etree.ElementTree as ET
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QTranslator
from .app_paths import get_translations_dir, resolve_app_path, make_relative_to_app


class TsTranslator(QTranslator):
    """Fallback translator that reads .ts files directly."""

    def __init__(self, ts_path: str):
        super().__init__()
        self._translations: Dict[Tuple[str, str], str] = {}
        self._load_ts(ts_path)

    def _load_ts(self, ts_path: str) -> None:
        tree = ET.parse(ts_path)
        root = tree.getroot()
        for context in root.findall("context"):
            name_elem = context.find("name")
            if name_elem is None or not name_elem.text:
                continue
            context_name = name_elem.text
            for message in context.findall("message"):
                source_elem = message.find("source")
                translation_elem = message.find("translation")
                if source_elem is None or translation_elem is None:
                    continue
                source_text = source_elem.text or ""
                translation_text = translation_elem.text or ""
                if source_text:
                    self._translations[(context_name, source_text)] = translation_text

    def translate(self, context, source_text, disambiguation=None, n=-1):  # noqa: ANN001
        return self._translations.get((context, source_text), source_text)


class I18nManager(QObject):
    """Manages language settings and translators."""

    language_changed = Signal(str)

    def __init__(self, settings: QSettings):
        super().__init__()
        self._settings = settings
        self._translator: Optional[QTranslator] = None
        self._current_language = "uk"

    def current_language(self) -> str:
        return self._current_language

    def load_from_settings(self) -> None:
        language = self._settings.value("ui/language", "uk")
        self.set_language(language, persist=False)

    def set_language(self, language: str, persist: bool = True) -> None:
        language = "uk" if language not in {"uk", "en"} else language
        if self._current_language == language and self._translator is not None:
            return

        if self._translator is not None:
            QCoreApplication.removeTranslator(self._translator)

        settings = QSettings()
        translations_path = settings.value("app/translations_path", "")
        if translations_path:
            path = resolve_app_path(translations_path)
            if str(path) != str(translations_path):
                settings.setValue("app/translations_path", make_relative_to_app(path))
            if path.suffix.lower() == ".qm":
                qm_path = path
                ts_path = None
            else:
                ts_path = path
                qm_path = None
        else:
            translations_dir = get_translations_dir()
            qm_path = translations_dir / f"app_{language}.qm"
            ts_path = translations_dir / f"app_{language}.ts"

        if qm_path and qm_path.exists():
            translator = QTranslator()
            translator.load(str(qm_path))
            QCoreApplication.installTranslator(translator)
            self._translator = translator
        else:
            if ts_path and ts_path.exists():
                translator = TsTranslator(str(ts_path))
                QCoreApplication.installTranslator(translator)
                self._translator = translator
            else:
                self._translator = None

        self._current_language = language
        if persist:
            self._settings.setValue("ui/language", language)
        self.language_changed.emit(language)
