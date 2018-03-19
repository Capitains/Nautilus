from flask import render_template, Markup, request

from MyCapytain.common.reference import URN
from MyCapytain.common.constants import Mimetypes, RDF_NAMESPACES

from capitains_nautilus.apis.base import AdditionalAPIPrototype
from capitains_nautilus.errors import NautilusError, MissingParameter, InvalidURN


class CTSApi(AdditionalAPIPrototype):
    NAME = "CTS"
    ROUTES = [
        ('/cts', "r_cts", ["GET"])
    ]
    Access_Control_Allow_Methods = {
        "r_cts": "OPTIONS, GET"
    }
    CACHED = [
        #  CTS
        "_get_capabilities", "_get_passage", "_get_passage_plus",
        "_get_valid_reff", "_get_prev_next", "_get_first_urn", "_get_label",
        "cts_error"
    ]

    def r_cts(self):
        """ Actual main route of CTS APIs. Transfer typical requests through the ?request=REQUESTNAME route

        :return: Response
        """
        _request = request.args.get("request", None)
        if _request is not None:
            try:
                if _request.lower() == "getcapabilities":
                    return self._get_capabilities(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getpassage":
                    return self._get_passage(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getpassageplus":
                    return self._get_passage_plus(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getlabel":
                    return self._get_label(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getfirsturn":
                    return self._get_first_urn(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getprevnexturn":
                    return self._get_prev_next(
                        urn=request.args.get("urn", None)
                    )
                elif _request.lower() == "getvalidreff":
                    return self._get_valid_reff(
                        urn=request.args.get("urn", None),
                        level=request.args.get("level", 1, type=int)
                    )
            except NautilusError as E:
                return self.cts_error(error_name=E.__class__.__name__, message=E.__doc__)
        return self.cts_error(MissingParameter.__name__, message=MissingParameter.__doc__)

    def cts_error(self, error_name, message=None):
        """ Create a CTS Error reply

        :param error_name: Name of the error
        :param message: Message of the Error
        :return: CTS Error Response with information (XML)
        """
        self.nautilus_extension.logger.info(
            "CTS error thrown {} for {} ({})".format(
                error_name,
                request.query_string.decode(),
                message)
        )
        return render_template(
            "cts/Error.xml",
            errorType=error_name,
            message=message
        ), 404, {"content-type": "application/xml"}

    def _get_capabilities(self, urn=None):
        """ Provisional route for GetCapabilities request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetCapabilities response
        """
        r = self.resolver.getMetadata(objectId=urn)
        if len(r.parents) > 0:
            r = r.parents[-1]
        r = render_template(
            "cts/GetCapabilities.xml",
            filters="urn={}".format(urn),
            inventory=Markup(r.export(Mimetypes.XML.CTS))
        )
        return r, 200, {"content-type": "application/xml"}

    def _get_passage(self, urn):
        """ Provisional route for GetPassage request

        :param urn: URN to filter the resource
        :return: GetPassage response
        """
        urn = URN(urn)
        subreference = None
        if len(urn) < 4:
            raise InvalidURN
        if urn.reference is not None:
            subreference = str(urn.reference)
        node = self.resolver.getTextualNode(textId=urn.upTo(URN.NO_PASSAGE), subreference=subreference)

        r = render_template(
            "cts/GetPassage.xml",
            filters="urn={}".format(urn),
            request_urn=str(urn),
            full_urn=node.urn,
            passage=Markup(node.export(Mimetypes.XML.TEI))
        )
        return r, 200, {"content-type": "application/xml"}

    def _get_passage_plus(self, urn):
        """ Provisional route for GetPassagePlus request

        :param urn: URN to filter the resource
        :return: GetPassagePlus response
        """
        urn = URN(urn)
        subreference = None
        if len(urn) < 4:
            raise InvalidURN
        if urn.reference is not None:
            subreference = str(urn.reference)
        node = self.resolver.getTextualNode(textId=urn.upTo(URN.NO_PASSAGE), subreference=subreference)
        r = render_template(
            "cts/GetPassagePlus.xml",
            filters="urn={}".format(urn),
            request_urn=str(urn),
            full_urn=node.urn,
            prev_urn=node.prevId,
            next_urn=node.nextId,
            metadata={
                "groupname": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.groupname)],
                "title": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.title)],
                "description": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.description)],
                "label": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.label)]
            },
            citation=Markup(node.citation.export(Mimetypes.XML.CTS)),
            passage=Markup(node.export(Mimetypes.XML.TEI))
        )
        return r, 200, {"content-type": "application/xml"}

    def _get_valid_reff(self, urn, level):
        """ Provisional route for GetValidReff request

        :param urn: URN to filter the resource
        :return: GetValidReff response
        """
        urn = URN(urn)
        subreference = None
        textId=urn.upTo(URN.NO_PASSAGE)
        if urn.reference is not None:
            subreference = str(urn.reference)
        reffs = self.resolver.getReffs(textId=textId, subreference=subreference, level=level)
        r = render_template(
            "cts/GetValidReff.xml",
            reffs=reffs,
            urn=textId,
            level=level,
            request_urn=str(urn)
        )
        return r, 200, {"content-type": "application/xml"}

    def _get_prev_next(self, urn):
        """ Provisional route for GetPrevNext request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetPrevNext response
        """
        urn = URN(urn)
        subreference = None
        textId = urn.upTo(URN.NO_PASSAGE)
        if urn.reference is not None:
            subreference = str(urn.reference)
        previous, nextious = self.resolver.getSiblings(textId=textId, subreference=subreference)
        r = render_template(
            "cts/GetPrevNext.xml",
            prev_urn=previous,
            next_urn=nextious,
            urn=textId,
            request_urn=str(urn)
        )
        return r, 200, {"content-type": "application/xml"}

    def _get_first_urn(self, urn):
        """ Provisional route for GetFirstUrn request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetFirstUrn response
        """
        urn = URN(urn)
        subreference = None
        textId = urn.upTo(URN.NO_PASSAGE)
        if urn.reference is not None:
            subreference = str(urn.reference)
        firstId = self.resolver.getTextualNode(textId=textId, subreference=subreference).firstId
        r = render_template(
            "cts/GetFirstUrn.xml",
            firstId=firstId,
            full_urn=textId,
            request_urn=str(urn)
        )
        return r, 200, {"content-type": "application/xml"}

    def _get_label(self, urn):
        """ Provisional route for GetLabel request

        :param urn: URN to filter the resource
        :param inv: Inventory Identifier
        :return: GetLabel response
        """
        node = self.resolver.getTextualNode(textId=urn)
        r = render_template(
            "cts/GetLabel.xml",
            request_urn=str(urn),
            full_urn=node.urn,
            metadata={
                "groupname": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.groupname)],
                "title": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.title)],
                "description": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.description)],
                "label": [(literal.language, str(literal)) for literal in node.metadata.get(RDF_NAMESPACES.CTS.label)]
            },
            citation=Markup(node.citation.export(Mimetypes.XML.CTS))
        )
        return r, 200, {"content-type": "application/xml"}
