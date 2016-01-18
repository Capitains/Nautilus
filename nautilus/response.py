"""
    Response generator for the queries
"""
import json
from collections import OrderedDict
from copy import copy
from MyCapytain.resources.inventory import TextInventory


JSON = "application/text"
XML = "text/xml"


def capabilities(texts, page=None, count=None, format=XML):
    """ Transform a list of texts into a string representation

    :param texts: List of Text objects
    :return: String representation of the Inventory
    """
    inventory = TextInventory()
    for text in texts:
        tg_urn = str(text.parents[1].urn)
        wk_urn = str(text.parents[0].urn)
        txt_urn = str(text.urn)
        if tg_urn not in inventory.textgroups:
            # Use another variable to avoid pointer ?
            # Try to see what is most optimized
            inventory.textgroups[tg_urn] = copy(text.parents[1])
            inventory.textgroups[tg_urn].works = OrderedDict()
        if wk_urn not in inventory.textgroups[tg_urn].works:
            inventory.textgroups[tg_urn].works[wk_urn] = copy(text.parents[0])
            inventory.textgroups[tg_urn].works[wk_urn].parents = tuple(
                [inventory, inventory.textgroups[tg_urn]]
            )
            inventory.textgroups[tg_urn].works[wk_urn].texts = OrderedDict()
        __text = copy(text)
        inventory.textgroups[tg_urn].works[wk_urn].texts[txt_urn] = __text
        __text.parents = tuple([
            inventory,
            inventory.textgroups[tg_urn],
            inventory.textgroups[tg_urn].works[wk_urn]
        ])
    if format is JSON:
        inventory_str = ""
    else:
        inventory_str = str(inventory)

    return inventory_str
