from erpnext.stock.doctype.repost_item_valuation.repost_item_valuation import (
    on_doctype_update as create_riv_indexes,
)


def execute():
    """Ensure Repost Item Valuation indexes"""
    create_riv_indexes()
