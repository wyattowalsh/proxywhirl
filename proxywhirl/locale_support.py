"""Internationalization (i18n) support for proxywhirl.

Provides multi-language support for UI messages, error messages, and documentation.
Supports translation of CLI output, TUI, and API responses.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "ja", "zh", "pt", "ru"}


class TranslationManager:
    """Manages translations for UI and error messages."""

    def __init__(self, language: str = "en") -> None:
        """Initialize translation manager.

        Args:
            language: ISO 639-1 language code (default: 'en')
        """
        self.language = language if language in SUPPORTED_LANGUAGES else "en"
        self._translations: dict[str, dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load translation files from disk or defaults."""
        self._translations = {
            "en": self._get_en_translations(),
            "es": self._get_es_translations(),
            "fr": self._get_fr_translations(),
            "de": self._get_de_translations(),
            "ja": self._get_ja_translations(),
            "zh": self._get_zh_translations(),
            "pt": self._get_pt_translations(),
            "ru": self._get_ru_translations(),
        }
        logger.debug(f"Loaded translations for: {', '.join(self._translations.keys())}")

    def translate(self, key: str, **kwargs: Any) -> str:
        """Translate a message key to current language.

        Args:
            key: Translation key (e.g., 'error.pool_empty')
            **kwargs: Format arguments

        Returns:
            Translated message or key if not found
        """
        if self.language not in self._translations:
            self.language = "en"

        messages = self._translations.get(self.language, {})
        text = messages.get(key, key)

        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                logger.warning(f"Missing format args for translation: {key}")
                return text

        return text

    def set_language(self, language: str) -> None:
        """Change active language.

        Args:
            language: ISO 639-1 language code
        """
        if language not in SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language: {language}, using English")
            language = "en"
        self.language = language

    @staticmethod
    def _get_en_translations() -> dict[str, str]:
        """English translations."""
        return {
            "error.pool_empty": "Proxy pool is empty",
            "error.invalid_proxy": "Invalid proxy format",
            "error.connection_failed": "Connection failed: {error}",
            "error.health_check_failed": "Health check failed for proxy",
            "status.active": "Active",
            "status.inactive": "Inactive",
            "status.degraded": "Degraded",
            "message.rotating": "Rotating to next proxy",
            "message.initializing": "Initializing proxy pool",
            "message.pool_ready": "Pool ready with {count} proxies",
        }

    @staticmethod
    def _get_es_translations() -> dict[str, str]:
        """Spanish translations."""
        return {
            "error.pool_empty": "El grupo de proxies está vacío",
            "error.invalid_proxy": "Formato de proxy inválido",
            "error.connection_failed": "Conexión fallida: {error}",
            "error.health_check_failed": "Verificación de salud fallida para proxy",
            "status.active": "Activo",
            "status.inactive": "Inactivo",
            "status.degraded": "Degradado",
            "message.rotating": "Rotando al siguiente proxy",
            "message.initializing": "Inicializando grupo de proxies",
            "message.pool_ready": "Grupo listo con {count} proxies",
        }

    @staticmethod
    def _get_fr_translations() -> dict[str, str]:
        """French translations."""
        return {
            "error.pool_empty": "Le pool de proxies est vide",
            "error.invalid_proxy": "Format de proxy invalide",
            "error.connection_failed": "Échec de la connexion: {error}",
            "error.health_check_failed": "Vérification de santé échouée pour le proxy",
            "status.active": "Actif",
            "status.inactive": "Inactif",
            "status.degraded": "Dégradé",
            "message.rotating": "Rotation vers le proxy suivant",
            "message.initializing": "Initialisation du pool de proxies",
            "message.pool_ready": "Pool prêt avec {count} proxies",
        }

    @staticmethod
    def _get_de_translations() -> dict[str, str]:
        """German translations."""
        return {
            "error.pool_empty": "Proxy-Pool ist leer",
            "error.invalid_proxy": "Ungültiges Proxy-Format",
            "error.connection_failed": "Verbindung fehlgeschlagen: {error}",
            "error.health_check_failed": "Statusprüfung für Proxy fehlgeschlagen",
            "status.active": "Aktiv",
            "status.inactive": "Inaktiv",
            "status.degraded": "Beeinträchtigt",
            "message.rotating": "Rotation zum nächsten Proxy",
            "message.initializing": "Proxy-Pool wird initialisiert",
            "message.pool_ready": "Pool bereit mit {count} Proxies",
        }

    @staticmethod
    def _get_ja_translations() -> dict[str, str]:
        """Japanese translations."""
        return {
            "error.pool_empty": "プロキシプールが空です",
            "error.invalid_proxy": "無効なプロキシ形式",
            "error.connection_failed": "接続失敗: {error}",
            "error.health_check_failed": "プロキシのヘルスチェック失敗",
            "status.active": "アクティブ",
            "status.inactive": "非アクティブ",
            "status.degraded": "劣化",
            "message.rotating": "次のプロキシに回転中",
            "message.initializing": "プロキシプール初期化中",
            "message.pool_ready": "{count}個のプロキシでプール準備完了",
        }

    @staticmethod
    def _get_zh_translations() -> dict[str, str]:
        """Chinese (Simplified) translations."""
        return {
            "error.pool_empty": "代理池为空",
            "error.invalid_proxy": "无效的代理格式",
            "error.connection_failed": "连接失败: {error}",
            "error.health_check_failed": "代理健康检查失败",
            "status.active": "活跃",
            "status.inactive": "非活跃",
            "status.degraded": "性能下降",
            "message.rotating": "旋转至下一个代理",
            "message.initializing": "初始化代理池",
            "message.pool_ready": "代理池就绪，包含{count}个代理",
        }

    @staticmethod
    def _get_pt_translations() -> dict[str, str]:
        """Portuguese translations."""
        return {
            "error.pool_empty": "Pool de proxies vazio",
            "error.invalid_proxy": "Formato de proxy inválido",
            "error.connection_failed": "Conexão falhou: {error}",
            "error.health_check_failed": "Verificação de saúde do proxy falhou",
            "status.active": "Ativo",
            "status.inactive": "Inativo",
            "status.degraded": "Degradado",
            "message.rotating": "Rotacionando para o próximo proxy",
            "message.initializing": "Inicializando pool de proxies",
            "message.pool_ready": "Pool pronto com {count} proxies",
        }

    @staticmethod
    def _get_ru_translations() -> dict[str, str]:
        """Russian translations."""
        return {
            "error.pool_empty": "Пул прокси пуст",
            "error.invalid_proxy": "Неверный формат прокси",
            "error.connection_failed": "Ошибка подключения: {error}",
            "error.health_check_failed": "Проверка здоровья прокси не пройдена",
            "status.active": "Активно",
            "status.inactive": "Неактивно",
            "status.degraded": "Деградировано",
            "message.rotating": "Ротация на следующий прокси",
            "message.initializing": "Инициализация пула прокси",
            "message.pool_ready": "Пул готов с {count} прокси",
        }


_default_translator: TranslationManager | None = None


def get_translator() -> TranslationManager:
    """Get global translator instance."""
    global _default_translator
    if _default_translator is None:
        _default_translator = TranslationManager()
    return _default_translator


def set_language(language: str) -> None:
    """Set global language preference."""
    get_translator().set_language(language)


def translate(key: str, **kwargs: Any) -> str:
    """Translate a message key."""
    return get_translator().translate(key, **kwargs)
