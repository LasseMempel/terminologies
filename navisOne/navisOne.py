import requests

import pandas as pd

import urllib.parse

from rdflib import Graph, URIRef, BNode, Literal, Namespace

from rdflib.namespace import SKOS, RDF, DC, VANN



df = pd.read_csv("items.csv")

parentDf = pd.read_csv("parent.csv")

#print(df)



#baseUri = "https://www.lassemempel.github.io/Terminologien/NAVISone"
#baseUri = "https://www.lassemempel.github.io/terminologies/NAVISone"
# baseUri = "https://www.lassemempel.github.io/LEIZA-Terminologien/NAVISone"
baseUri = "https://lassemempel.github.io/LEIZA-Terminologien/NAVISone"

thesaurus = URIRef(baseUri)

thesaurusAddendum = URIRef(baseUri + "/")


parentDfColumns = ["id","navisid","de","en","dk","nl","fr","it","es","pl","gr","he"]



dfColumns = ["id","navisid","fk_id_parent","de","en","es","it","nl","dk","gr","fr","pl","he","desc_en","desc_de","origindesc","gettyaat","gettyaatrelationtype","wikidata","wikidatarelationtype"]



g = Graph()


g.add((thesaurus, RDF.type, SKOS.ConceptScheme))


g.add((thesaurus, DC.title, Literal("NAVISone", lang="de")))


g.add((thesaurus, DC.description, Literal("NAVISone ist ein Thesaurus über Schiffsbegriffe", lang="de")))


g.add((thesaurus, DC.creator, Literal("Florian Thiery")))

g.add((thesaurus, VANN.preferredNamespaceUri, Literal(thesaurusAddendum)))


for index, row in parentDf.iterrows():


    #concept = URIRef(baseUri + str(row["id"]))


    concept = URIRef(thesaurusAddendum + str(row["id"]))

    g.add((concept, RDF.type, SKOS.Concept))

    for language in parentDfColumns[2:]:

        if not pd.isnull(row[language]):

            g.add((concept, SKOS.prefLabel, Literal(row[language], lang=language)))


    g.add((concept, SKOS.inScheme, thesaurus))

    # top concept


    g.add((concept, SKOS.topConceptOf, thesaurus))


    g.add((thesaurus, SKOS.hasTopConcept, concept))

    # iterate over all rows in df where fk_id_parent == id

    for index2, row2 in df[df["fk_id_parent"] == row["id"]].iterrows():


        #concept2 = URIRef(baseUri + str(row2["id"]))


        concept2 = URIRef(thesaurusAddendum + str(row2["id"]))

        g.add((concept2, RDF.type, SKOS.Concept))

        for language in dfColumns[3:12]:

            if not pd.isnull(row2[language]):

                g.add((concept2, SKOS.prefLabel, Literal(row2[language], lang=language)))


        g.add((concept2, SKOS.inScheme, thesaurus))

        g.add((concept, SKOS.narrower, concept2))

        g.add((concept2, SKOS.broader, concept))

        # add relations

        if not pd.isnull(row2["gettyaat"]):

            g.add((concept2, SKOS.exactMatch, URIRef("http://vocab.getty.edu/aat/300263190")))

        if not pd.isnull(row2["wikidata"]):

            g.add((concept2, SKOS.exactMatch, URIRef("https://www.wikidata.org/wiki/Q582062")))

        # add descriptions

        if not pd.isnull(row2["desc_en"]):

            g.add((concept2, SKOS.definition, Literal(row2["desc_en"], lang="en")))

        if not pd.isnull(row2["desc_de"]):

            g.add((concept2, SKOS.definition, Literal(row2["desc_de"], lang="de")))

        if not pd.isnull(row2["origindesc"]):

            g.add((concept2, DC.source, Literal(row2["origindesc"])))



g.serialize(destination="navisOne.ttl", format="turtle")
