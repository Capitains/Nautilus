"""
    Response generator for the queries
"""
import json
from collections import OrderedDict
from copy import copy
from MyCapytain.resources.inventory import TextInventory
from lxml import etree

JSON = "application/text"
XML = "text/xml"
CTS_XML = "text/xml:CTS"


def getcapabilities(texts, page=None, count=None, format=XML, **kwargs):
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
    if format == JSON:
        inventory_str = ""
    elif format == CTS_XML:
        return str(inventory)
    else:
        return """
            <GetCapabilities xmlns="http://chs.harvard.edu/xmlns/cts">
            <request>
                <requestName>GetInventory</requestName>
                <requestFilters>{filters}</requestFilters>
            </request>
            <reply>
                {inventory}
            </reply>
            </GetCapabilities>""".format(
                inventory=str(inventory),
                filters=", ".join("{0}={1}".format(key, value) for key, value in kwargs.items() if value is not None)
            )


def getpassage(passage, metadata, request_urn, format=XML):
    if format == XML:
        return """
            <GetPassage xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://chs.harvard.edu/xmlns/cts">
            <request>
                <requestName>GetPassage</requestName>
                <requestUrn>{request_urn}</requestUrn>
            </request>
            <reply>
                <urn>{full_urn}</urn>
                <passage>
                    <TEI xmlns="http://www.tei-c.org/ns/1.0">
                        <text>
                            <body>
                                <div type="{category}" n="{urn}" xml:lang="{lang}">{passage}</div>
                            </body>
                        </text>
                    </TEI>
                </passage>
            </reply>
            </GetPassage>""".format(
            request_urn=request_urn,
            full_urn=str(passage.urn),
            category=metadata.subtype.lower(),
            urn=str(metadata.urn),
            lang=metadata.lang,
            passage=etree.tostring(passage.xml, encoding=str)
        )
