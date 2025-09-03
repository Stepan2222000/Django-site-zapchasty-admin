from typing import Optional


class SellshipRouter:
    """
    Роутер БД:
    - Модель sellship.EbayShippingInfo → БД 'parts_admin'
    - Остальные модели → default
    """

    parts_admin_alias = 'parts_admin'

    def _is_ebay_shipping_info(self, model) -> bool:
        try:
            return (
                getattr(model._meta, 'app_label', None) == 'sellship'
                and getattr(model._meta, 'model_name', None) == 'ebayshippinginfo'
            )
        except Exception:
            return False

    def db_for_read(self, model, **hints) -> Optional[str]:
        if self._is_ebay_shipping_info(model):
            return self.parts_admin_alias
        return None  # default

    def db_for_write(self, model, **hints) -> Optional[str]:
        if self._is_ebay_shipping_info(model):
            return self.parts_admin_alias
        return None  # default

    def allow_relation(self, obj1, obj2, **hints) -> Optional[bool]:
        # Разрешаем связи между объектами, находящимися в любой БД
        return True

    def allow_migrate(self, db: str, app_label: str, model_name: Optional[str] = None, **hints) -> Optional[bool]:
        # Миграции EbayShippingInfo только в parts_admin
        if app_label == 'sellship' and model_name == 'ebayshippinginfo':
            return db == self.parts_admin_alias

        # Все остальные модели НЕ в parts_admin
        if db == self.parts_admin_alias:
            return False

        # Для остальных БД (включая default) разрешаем
        return None


