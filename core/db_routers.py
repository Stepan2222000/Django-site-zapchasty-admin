from typing import Optional
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SellshipRouter:
    """
    Роутер БД:
    - Модель sellship.EbayShippingInfo → БД 'parts_admin'
    - Остальные модели → default
    """

    parts_admin_alias = 'default'
    parts_info_alias = 'parts_info'

    def __init__(self) -> None:
        # Если алиас 'parts_admin' не определён в settings.DATABASES,
        # используем 'default' как запасной вариант. Это покрывает конфигурации,
        # где parts_admin фактически является default.
        try:
            if self.parts_admin_alias not in settings.DATABASES:
                self.parts_admin_alias = 'default'

            # Если alias для parts_info не задан, пробуем найти по имени БД среди подключений.
            if self.parts_info_alias not in settings.DATABASES:
                # Попробуем вычислить alias по имени БД в конфиге (если alias назван иначе)
                for alias, cfg in settings.DATABASES.items():
                    if (cfg or {}).get('NAME') == 'parts_info':
                        self.parts_info_alias = alias
                        break
                # Fallback на default, если отдельной БД нет
                if self.parts_info_alias not in settings.DATABASES:
                    self.parts_info_alias = 'default'
        except Exception as e:
            # В крайних случаях, когда settings недоступны, безопасно падать на 'default'.
            logging.getLogger(__name__).warning(
                f"SellshipRouter: fallback to 'default' due to error: {e}"
            )
            self.parts_admin_alias = 'default'

    def _is_ebay_shipping_info(self, model) -> bool:
        try:
            app_label = getattr(model._meta, 'app_label', None)
            model_name = getattr(model._meta, 'model_name', None)
            logger.info(f"Checking model: app_label={app_label}, model_name={model_name}")
            return (
                app_label == 'sellship'
                and model_name == 'ebayshippinginfo'
            )
        except Exception as e:
            logger.error(f"Error checking model: {e}")
            return False

    def _is_item_fdw(self, model) -> bool:
        try:
            app_label = getattr(model._meta, 'app_label', None)
            model_name = getattr(model._meta, 'model_name', None)
            logger.info(f"Checking model: app_label={app_label}, model_name={model_name}")
            return (
                app_label == 'sellship'
                and model_name == 'itemfdw'
            )
        except Exception as e:
            logger.error(f"Error checking model: {e}")
            return False

    def _is_item(self, model) -> bool:
        try:
            app_label = getattr(model._meta, 'app_label', None)
            model_name = getattr(model._meta, 'model_name', None)
            logger.info(f"Checking model: app_label={app_label}, model_name={model_name}")
            return (
                app_label == 'sellship'
                and model_name == 'item'
            )
        except Exception as e:
            logger.error(f"Error checking model: {e}")
            return False

    def _should_route_to_parts_admin(self, model) -> bool:
        return self._is_ebay_shipping_info(model) or self._is_item_fdw(model)

    def _should_route_to_parts_info(self, model) -> bool:
        return self._is_item(model)

    def db_for_read(self, model, **hints) -> Optional[str]:
        logger.info(f"db_for_read called for model: {model}")
        if self._should_route_to_parts_admin(model):
            logger.info(f"Routing {model} to {self.parts_admin_alias}")
            return self.parts_admin_alias
        if self._should_route_to_parts_info(model):
            logger.info(f"Routing {model} to {self.parts_info_alias}")
            return self.parts_info_alias
        logger.info(f"Routing {model} to default")
        return None  # default

    def db_for_write(self, model, **hints) -> Optional[str]:
        logger.info(f"db_for_write called for model: {model}")
        if self._should_route_to_parts_admin(model):
            logger.info(f"Routing {model} to {self.parts_admin_alias}")
            return self.parts_admin_alias
        if self._should_route_to_parts_info(model):
            logger.info(f"Routing {model} to {self.parts_info_alias}")
            return self.parts_info_alias
        logger.info(f"Routing {model} to default")
        return None  # default

    def allow_relation(self, obj1, obj2, **hints) -> Optional[bool]:
        # Разрешаем связи между объектами, находящимися в любой БД
        return True

    def allow_migrate(self, db: str, app_label: str, model_name: Optional[str] = None, **hints) -> Optional[bool]:
        # Миграции EbayShippingInfo только в parts_admin
        # if app_label == 'sellship' and model_name == 'ebayshippinginfo':
        #     return db == self.parts_admin_alias
        #
        # # ItemFDW - unmanaged модель, миграции не нужны
        # if app_label == 'sellship' and model_name == 'itemfdw':
        #     return False
        #
        # # Модель Item мигрируем только в базу parts_info
        # if app_label == 'sellship' and model_name == 'item':
        #     return db == self.parts_info_alias
        #
        # # Все остальные модели НЕ в parts_admin
        # if db == self.parts_admin_alias:
        #     return False
        #
        # # Для остальных БД (включая default) разрешаем
        # return None
        return True


