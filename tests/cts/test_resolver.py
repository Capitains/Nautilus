# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES, get_graph, set_graph, bind_graph
from MyCapytain.common.reference import URN, CtsReference
from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.resources.prototypes.cts.inventory import (
    CtsTextgroupMetadata,
    CtsTextMetadata,
    CtsTranslationMetadata,
    CtsTextInventoryMetadata
)
from MyCapytain.resources.prototypes.text import InteractiveTextualNode
from MyCapytain.resolvers.utils import CollectionDispatcher
from unittest import TestCase

from capitains_nautilus.cts.resolver import NautilusCtsResolver
from capitains_nautilus.errors import CtsUnknownCollection, CtsInvalidURN, CtsUndispatchedTextError


class TestXmlFolderResolverBehindTheScene(TestCase):
    """ Test behind the scene functions of the Resolver """
    RESOLVER_CLASS = NautilusCtsResolver

    def setUp(self):
        set_graph(bind_graph())

    def generate_repository(self, *args, **kwargs):
        Repository = self.RESOLVER_CLASS(*args, **kwargs)
        Repository.parse()
        return Repository

    def test_resource_parser(self):
        """ Test that the initiation finds correctly the resources """
        Repository = self.generate_repository(["./tests/testing_data/farsiLit"])

        self.assertEqual(
            Repository.inventory["urn:cts:farsiLit:hafez"].urn, URN("urn:cts:farsiLit:hafez"),
            "Hafez is found"
        )
        self.assertEqual(
            len(Repository.inventory["urn:cts:farsiLit:hafez"].works), 1,
            "Hafez has one child"
        )
        self.assertEqual(
            Repository.inventory["urn:cts:farsiLit:hafez.divan"].urn, URN("urn:cts:farsiLit:hafez.divan"),
            "Divan is found"
        )

        self.assertEqual(
            len(Repository.inventory["urn:cts:farsiLit:hafez.divan"].texts), 3,
            "Divan has 3 children"
        )

    def test_text_resource(self):
        """ Test to get the text resource to perform other queries """
        Repository = self.generate_repository(["./tests/testing_data/farsiLit"])
        text, metadata = Repository.__getText__("urn:cts:farsiLit:hafez.divan.perseus-eng1")
        self.assertEqual(
            len(text.citation), 4,
            "Object has a citation property of length 4"
        )
        self.assertEqual(
            text.getTextualNode(CtsReference("1.1.1.1")).export(output=Mimetypes.PLAINTEXT),
            "Ho ! Saki, pass around and offer the bowl (of love for God) : ### ",
            "It should be possible to retrieve text"
        )

    def test_missing_text_resource(self):
        """ Test to make sure an UnknownCollection error is raised when a text is missing """
        Repository = self.generate_repository(["./tests/test_data/missing_text"])
        with self.assertRaises(CtsUnknownCollection):
            text, metadata = Repository.__getText__("urn:cts:farsiLit:hafez.divan.missing_text")

    def test_get_capabilities(self):
        """ Check Get Capabilities """

        Repository = self.generate_repository(
            ["./tests/testing_data/farsiLit"]
        )
        Repository.parse()
        self.assertEqual(
            len(Repository.__getTextMetadata__()[0]), 4,
            "General no filter works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="edition")[0]), 2,
            "Type filter works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(lang="ger")[0]), 1,
            "Filtering on language works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="edition", lang="ger")[0]), 0,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="translation", lang="ger")[0]), 1,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(page=1, limit=2, pagination=True)[0]), 2,
            "Pagination works without other filters"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(page=2, limit=2, pagination=True)[0]), 2,
            "Pagination works without other filters at list end"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:farsiLit")[0]), 3,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit")[0]), 1,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:farsiLit:hafez.divan.perseus-eng1")[0]), 1,
            "Complete URN filtering works"
        )

    def test_get_shared_textgroup_cross_repo(self):
        """ Check Get Capabilities """
        Repository = self.generate_repository(
            [
                "./tests/testing_data/farsiLit",
                "./tests/testing_data/latinLit2"
            ]
        )
        self.assertIsNotNone(
            Repository.__getText__("urn:cts:latinLit:phi1294.phi002.perseus-lat2"),
            "We should find perseus-lat2"
        )
        self.assertIsNotNone(
            Repository.__getText__("urn:cts:latinLit:phi1294.phi002.opp-lat2"),
            "We should find perseus-lat2"
        )

    def test_get_capabilities_nocites(self):
        """ Check Get Capabilities latinLit data"""
        Repository = self.generate_repository(
            ["./tests/testing_data/latinLit"]
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit:stoa0045.stoa008.perseus-lat2")[0]), 0,
            "Texts without citations were ignored"
        )

    def test_pagination(self):
        self.assertEqual(
            NautilusCtsResolver.pagination(2, 30, 150), (30, 60, 2, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            NautilusCtsResolver.pagination(4, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            NautilusCtsResolver.pagination(5, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            NautilusCtsResolver.pagination(5, 100, 150), (100, 150, 2, 50),
            " Pagination should give corrected page and correct count"
        )
        self.assertEqual(
            NautilusCtsResolver.pagination(5, 110, 150), (40, 50, 5, 10),
            " Pagination should use default limit (10) when getting too much "
        )


class TextXmlFolderResolver(TestCase):
    """ Ensure working state of resolver """
    RESOLVER_CLASS = NautilusCtsResolver

    def setUp(self):
        set_graph(bind_graph())
        self.resolver = self.RESOLVER_CLASS(["./tests/testing_data/latinLit2"])
        self.resolver.parse()

    def test_getPassage_full(self):
        """ Test that we can get a full text """
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertIsInstance(
            passage, InteractiveTextualNode,
            "GetPassage should always return passages objects"
        )

        children = passage.getReffs()

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], CtsReference('1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(
                output=Mimetypes.PYTHON.ETREE
            ).xpath(
                ".//tei:div[@n='1']/tei:div[@n='1']/tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False
            ),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_no_canonical(self):
        """ Test that we can get a subreference text passage where no canonical exists"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi0959.phi010.perseus-eng2", "2")
        self.assertEqual(
            passage.export(Mimetypes.PLAINTEXT), "Omne fuit Musae carmen inerme meae; ",
            "Passage should resolve if directly asked"
        )
        with self.assertRaises(CtsUnknownCollection):
            passage = self.resolver.getTextualNode("urn:cts:latinLit:phi0959.phi010", "2")
        with self.assertRaises(CtsInvalidURN):
            passage = self.resolver.getTextualNode("urn:cts:latinLit:phi0959", "2")

    def test_getPassage_subreference(self):
        """ Test that we can get a subreference text passage"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")

        # We check we made a reroute to GetPassage request
        self.assertIsInstance(
            passage, InteractiveTextualNode,
            "GetPassage should always return passages objects"
        )

        children = passage.getReffs()

        self.assertEqual(
            children[0], CtsReference('1.1.1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )
        canonical = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002", "1.1")
        self.assertEqual(
            passage.export(output=Mimetypes.PLAINTEXT),
            canonical.export(output=Mimetypes.PLAINTEXT),
            "Canonical text should work"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_full_metadata(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", metadata=True)

        self.assertIsInstance(
            passage, InteractiveTextualNode,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("title"), "eng"]), "Epigrammata",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("groupname"),"eng"]), "Martial",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("label"), "eng"]), "Epigrams",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("description"), "eng"]),
            "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.name, "book",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.depth, 3,
            "Local Inventory Files should be parsed and aggregated correctly"
        )

        children = passage.getReffs(level=3)
        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], CtsReference('1.pr.1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(
                output=Mimetypes.PYTHON.ETREE
            ).xpath(
                ".//tei:div[@n='1']/tei:div[@n='1']/tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False
            ),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1",  metadata=True
        )

        self.assertIsInstance(
            passage, InteractiveTextualNode,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            passage.prevId, CtsReference("1.pr"),
            "Previous Passage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, CtsReference("1.2"),
            "Next Passage ID should be parsed"
        )

        children = passage.getReffs()
        # Ensure navigability
        self.assertIn(
            "verentia ludant; quae adeo antiquis auctoribus defuit, ut",
            passage.prev.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )
        self.assertIn(
            "Qui tecum cupis esse meos ubicumque libellos ",
            passage.next.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], CtsReference('1.1.1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_metadata_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1", metadata=True, prevnext=True
        )
        self.assertIsInstance(
            passage, InteractiveTextualNode,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("title"), "eng"]), "Epigrammata",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("groupname"), "eng"]), "Martial",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("label"), "eng"]), "Epigrams",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("description"), "eng"]),
            "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.root.name, "book",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.name, "poem",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.root.depth, 3,
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.prevId, CtsReference("1.pr"),
            "Previous Passage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, CtsReference("1.2"),
            "Next Passage ID should be parsed"
        )
        children = passage.getReffs()
        # Ensure navigability
        self.assertIn(
            "verentia ludant; quae adeo antiquis auctoribus defuit, ut",
            passage.prev.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )
        self.assertIn(
            "Qui tecum cupis esse meos ubicumque libellos ",
            passage.next.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], CtsReference('1.1.1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getMetadata_full(self):
        """ Checks retrieval of Metadata information """
        metadata = self.resolver.getMetadata()
        self.assertIsInstance(
            metadata, Collection,
            "Resolver should return a collection object"
        )
        self.assertIsInstance(
            metadata.members[0], Collection,
            "Members of Inventory should be TextGroups"
        )
        self.assertEqual(
            len(metadata.descendants), 43,
            "There should be as many descendants as there is edition, translation, works and textgroup + 1 for "
            "default inventory"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 25,
            "There should be as many readable descendants as there is edition, translation(25 ed+tr)"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, CtsTextMetadata)]), 25,
            "There should be 24 editions + 1 translations in readableDescendants"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath(
                "//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=XPATH_NAMESPACES)), 1,
            "There should be one node in exported format corresponding to lat2"
        )

    def test_getMetadata_subset(self):
        """ Checks retrieval of Metadata information """
        metadata = self.resolver.getMetadata(objectId="urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(
            metadata, Collection,
            "Resolver should return a collection object"
        )
        self.assertIsInstance(
            metadata.members[0], CtsTextMetadata,
            "Members of PrototypeWork should be Texts"
        )
        self.assertEqual(
            len(metadata.descendants), 1,
            "There should be as many descendants as there is edition, translation"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 1,
            "There should be 1 edition in readableDescendants"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, CtsTextMetadata)]), 1,
            "There should be 1 edition in readableDescendants"
        )
        self.assertIsInstance(
            metadata.parent, CtsTextgroupMetadata,
            "First parent should be PrototypeTextGroup"
        )
        self.assertIsInstance(
            metadata.parents[0], CtsTextgroupMetadata,
            "First parent should be PrototypeTextGroup"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath(
                "//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=XPATH_NAMESPACES)), 1,
            "There should be one node in exported format corresponding to lat2"
        )

        tr = self.resolver.getMetadata(objectId="urn:cts:greekLit:tlg0003.tlg001.opp-fre1")
        self.assertIsInstance(
            tr, CtsTranslationMetadata, "Metadata should be translation"
        )
        self.assertIn(
            "Histoire de la Guerre du Péloponnése",
            tr.get_description("eng"),
            "Description should be the right one"
        )

    def test_getSiblings(self):
        """ Ensure getSiblings works well """
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1"
        )
        self.assertEqual(
            previous, CtsReference("1.pr"),
            "Previous should be well computed"
        )
        self.assertEqual(
            nextious, CtsReference("1.2"),
            "Previous should be well computed"
        )

    def test_getSiblings_nextOnly(self):
        """ Ensure getSiblings works well when there is only the next passage"""
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.pr"
        )
        self.assertEqual(
            previous, None,
            "Previous Should not exist"
        )
        self.assertEqual(
            nextious, CtsReference("1.1"),
            "Next should be well computed"
        )

    def test_getSiblings_prevOnly(self):
        """ Ensure getSiblings works well when there is only the previous passage"""
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="14.223"
        )
        self.assertEqual(
            previous, CtsReference("14.222"),
            "Previous should be well computed"
        )
        self.assertEqual(
            nextious, None,
            "Next should not exist"
        )

    def test_getReffs_full(self):
        """ Ensure getReffs works well """
        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=1)
        self.assertEqual(
            len(reffs), 14,
            "There should be 14 books"
        )
        self.assertEqual(
            reffs[0], CtsReference("1")
        )

        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2)
        self.assertEqual(
            len(reffs), 1527,
            "There should be 1527 poems"
        )
        self.assertEqual(
            reffs[0], CtsReference("1.pr")
        )

        reffs = self.resolver.getReffs(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            subreference="1.1",
            level=1
        )
        self.assertEqual(
            len(reffs), 6,
            "There should be 6 references"
        )
        self.assertEqual(
            reffs[0], CtsReference("1.1.1")
        )


class TextXmlFolderResolverDispatcher(TestCase):
    """ Ensure working state of resolver """
    RESOLVER_CLASS = NautilusCtsResolver

    def setUp(self):
        set_graph(bind_graph())

    def generate_repository(self, resource, dispatcher=None, remove_empty=True):
        Repository = self.RESOLVER_CLASS(resource, dispatcher=dispatcher)
        Repository.logger.disabled = True
        Repository.REMOVE_EMPTY = remove_empty
        Repository.parse()
        return Repository

    def test_dispatching_latin_greek(self):
        tic = self.RESOLVER_CLASS.CLASSES["inventory_collection"]()
        latin = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:latinLit", parent=tic)
        latin.set_label("Classical Latin", "eng")
        farsi = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:farsiLit", parent=tic)
        farsi.set_label("Farsi", "eng")
        gc = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:greekLit", parent=tic)
        gc.set_label("Ancient Greek", "eng")
        gc.set_label("Grec Ancien", "fre")

        dispatcher = CollectionDispatcher(tic)

        @dispatcher.inventory("urn:perseus:latinLit")
        def dispatchLatinLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:latinLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:farsiLit")
        def dispatchfFarsiLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:farsiLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:greekLit")
        def dispatchGreekLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:greekLit:"):
                return True
            return False

        resolver = self.generate_repository(
            ["./tests/testing_data/latinLit2"],
            dispatcher=dispatcher,
            remove_empty=False
        )
        latin_stuff = resolver.getMetadata("urn:perseus:latinLit")
        greek_stuff = resolver.getMetadata("urn:perseus:greekLit")
        farsi_stuff = resolver.getMetadata("urn:perseus:farsiLit")
        self.assertEqual(
            len(latin_stuff.readableDescendants), 19,
            "There should be 19 readable descendants in Latin"
        )
        self.assertIsInstance(
            latin_stuff, CtsTextInventoryMetadata, "should be textinventory"
        )
        self.assertEqual(
            len(greek_stuff.readableDescendants), 6,
            "There should be 6 readable descendants in Greek [6 only in __cts__.xml]"
        )
        self.assertEqual(
            len(farsi_stuff.descendants), 0,
            "There should be nothing in FarsiLit"
        )
        self.assertEqual(
            str(greek_stuff.get_label("fre")), "Grec Ancien",
            "Label should be correct"
        )

        with self.assertRaises(KeyError):
            _ = latin_stuff["urn:cts:greekLit:tlg0003"]

    def test_dispatching_error(self):
        tic = self.RESOLVER_CLASS.CLASSES["inventory_collection"]()
        latin = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:latinLit", parent=tic)
        latin.set_label("Classical Latin", "eng")
        dispatcher = CollectionDispatcher(tic)
        # We remove default dispatcher
        dispatcher.__methods__ = []

        @dispatcher.inventory("urn:perseus:latinLit")
        def dispatchLatinLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:latinLit:"):
                return True
            return False

        self.RESOLVER_CLASS.RAISE_ON_UNDISPATCHED = True
        with self.assertRaises(Exception):
            resolver = self.generate_repository(
                ["./tests/testing_data/latinLit2"],
                dispatcher=dispatcher
            )

        self.RESOLVER_CLASS.RAISE_ON_UNDISPATCHED = False
        try:
            resolver = self.generate_repository(
                ["./tests/testing_data/latinLit2"],
                dispatcher=dispatcher,
                remove_empty=False
            )
        except CtsUndispatchedTextError as E:
            self.fail("UndispatchedTextError should not have been raised")

    def test_dispatching_output(self):
        tic = self.RESOLVER_CLASS.CLASSES["inventory_collection"]()
        latin = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:latinLit", parent=tic)
        latin.set_label("Classical Latin", "eng")
        farsi = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:farsiLit", parent=tic)
        farsi.set_label("Farsi", "eng")
        gc = self.RESOLVER_CLASS.CLASSES["inventory"]("urn:perseus:greekLit", parent=tic)
        gc.set_label("Ancient Greek", "eng")
        gc.set_label("Grec Ancien", "fre")

        dispatcher = CollectionDispatcher(tic)

        @dispatcher.inventory("urn:perseus:latinLit")
        def dispatchLatinLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:latinLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:farsiLit")
        def dispatchfFarsiLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:farsiLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:greekLit")
        def dispatchGreekLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:greekLit:"):
                return True
            return False

        resolver = self.generate_repository(
            ["./tests/testing_data/latinLit2"],
            dispatcher=dispatcher,
            remove_empty=False
        )

        all = resolver.getMetadata().export(Mimetypes.XML.CTS)
        latin_stuff = resolver.getMetadata("urn:perseus:latinLit").export(Mimetypes.XML.CTS)
        greek_stuff = resolver.getMetadata("urn:perseus:greekLit").export(Mimetypes.XML.CTS)
        farsi_stuff = resolver.getMetadata("urn:perseus:farsiLit").export(Mimetypes.XML.CTS)
        get_graph().remove((None, None, None))
        latin_stuff, greek_stuff, farsi_stuff = XmlCtsTextInventoryMetadata.parse(latin_stuff), \
                                                XmlCtsTextInventoryMetadata.parse(greek_stuff), \
                                                XmlCtsTextInventoryMetadata.parse(farsi_stuff)
        self.assertEqual(
            len(latin_stuff.readableDescendants), 19,
            "There should be 19 readable descendants in Latin"
        )
        self.assertIsInstance(
            latin_stuff, CtsTextInventoryMetadata, "should be textinventory"
        )
        self.assertEqual(
            len(greek_stuff.readableDescendants), 6,
            "There should be 6 readable descendants in Greek [6 only in __cts__.xml]"
        )
        self.assertEqual(
            len(farsi_stuff.descendants), 0,
            "There should be nothing in FarsiLit"
        )
        self.assertEqual(
            greek_stuff.get_label("fre"), None,  # Text inventory have no label in CTS
            "Label should be correct"
        )
        get_graph().remove((None, None, None))
        all = XmlCtsTextInventoryMetadata.parse(all)
        self.assertEqual(
            len(all.readableDescendants), 25,
            "There should be all 25 readable descendants in the master collection"
        )
