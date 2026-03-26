"""Translation management using Qt QTranslator."""
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QTranslator
from .app_paths import get_translations_dir, resolve_app_path, make_relative_to_app
from .ui_fallback_translations import UK_UI_FALLBACKS


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
        return self._translations.get((context, source_text), "")


class DictTranslator(QTranslator):
    """Fallback translator that resolves known UI strings from a Python dict."""

    def __init__(self, translations: Dict[str, str]):
        super().__init__()
        self._translations = translations

    def translate(self, context, source_text, disambiguation=None, n=-1):  # noqa: ANN001
        return self._translations.get(source_text, "")


class CompositeTranslator(QTranslator):
    """Translator that resolves strings through multiple sources in a fixed order."""

    def __init__(self, translators: List[QTranslator], source_fallbacks: Optional[Dict[str, str]] = None):
        super().__init__()
        self._translators = translators
        self._source_fallbacks = source_fallbacks or {}

    def translate(self, context, source_text, disambiguation=None, n=-1):  # noqa: ANN001
        for translator in self._translators:
            translated = translator.translate(context, source_text, disambiguation, n)
            if translated:
                return translated
        if source_text in self._source_fallbacks:
            return self._source_fallbacks[source_text]
        return source_text


class I18nManager(QObject):
    """Manages language settings and translators."""

    language_changed = Signal(str)

    def __init__(self, settings: QSettings):
        super().__init__()
        self._settings = settings
        self._translators: List[QTranslator] = []
        self._current_language = "uk"

    def current_language(self) -> str:
        return self._current_language

    def load_from_settings(self) -> None:
        language = self._settings.value("ui/language", "uk")
        self.set_language(language, persist=False)

    @staticmethod
    def _derive_language_path(base_path: Path, language: str) -> Path:
        stem = base_path.stem
        match = re.match(r"^(.*?)(?:[_-](uk|en))$", stem, flags=re.IGNORECASE)
        if not match:
            return base_path
        prefix = match.group(1)
        if not prefix:
            return base_path
        return base_path.with_name(f"{prefix}_{language}{base_path.suffix}")

    def _resolve_language_translation_paths(self, language: str) -> tuple[Path | None, Path | None]:
        settings = QSettings()
        translations_path = settings.value("app/translations_path", "")
        if translations_path:
            configured_path = resolve_app_path(translations_path)
            if str(configured_path) != str(translations_path):
                settings.setValue("app/translations_path", make_relative_to_app(configured_path))
            language_path = self._derive_language_path(configured_path, language)
            if language_path.suffix.lower() == ".qm":
                qm_path = language_path
                ts_path = language_path.with_suffix(".ts")
            else:
                ts_path = language_path
                qm_path = language_path.with_suffix(".qm")
            if (qm_path and qm_path.exists()) or (ts_path and ts_path.exists()):
                return qm_path, ts_path

        translations_dir = get_translations_dir()
        return (
            translations_dir / f"app_{language}.qm",
            translations_dir / f"app_{language}.ts",
        )

    def set_language(self, language: str, persist: bool = True) -> None:
        language = "uk" if language not in {"uk", "en"} else language
        if self._current_language == language and self._translators:
            return

        for translator in reversed(self._translators):
            QCoreApplication.removeTranslator(translator)
        self._translators = []

        qm_path, ts_path = self._resolve_language_translation_paths(language)

        backend_translators: List[QTranslator] = []
        if qm_path and qm_path.exists():
            translator = QTranslator()
            translator.load(str(qm_path))
            backend_translators.append(translator)
        if ts_path and ts_path.exists():
            backend_translators.append(TsTranslator(str(ts_path)))

        source_fallbacks = UK_UI_FALLBACKS if language == "uk" else {}
        composite = CompositeTranslator(backend_translators, source_fallbacks)
        QCoreApplication.installTranslator(composite)
        self._translators.append(composite)

        self._current_language = language
        if persist:
            self._settings.setValue("ui/language", language)
        self.language_changed.emit(language)
