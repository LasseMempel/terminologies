import requests
import pandas as pd
import urllib.parse
import datetime
from rdflib import Graph, URIRef, BNode, Literal, Namespace, XSD
from rdflib.namespace import SKOS, RDF, DC, PROV

df = pd.read_csv("items.csv")
parentDf = pd.read_csv("parent.csv")
#print(df)

baseUri = "https://www.lassemempel.github.io/Terminologien/NAVISone"

parentDfColumns = ["id","navisid","de","en","dk","nl","fr","it","es","pl","gr","he"]

dfColumns = ["id","navisid","fk_id_parent","de","en","es","it","nl","dk","gr","fr","pl","he","desc_en","desc_de","origindesc","gettyaat","gettyaatrelationtype","wikidata","wikidatarelationtype"]

g = Graph()

pythonScript = URIRef("https://github.com/LasseMempel/Terminologien/blob/main/navisOne/navisOne.py")
thesaurusCreation = BNode() # URIRef("https://github.com/LasseMempel/Terminologien/blob/main/navisOne/") #
thesaurus = URIRef(baseUri)

g.add((thesaurusCreation, PROV.wasAssociatedWith, pythonScript))
g.add((thesaurusCreation, PROV.startedAtTime, Literal(datetime.datetime.now(), datatype=XSD.dateTime)))

g.add((pythonScript, RDF.type, PROV.SoftwareAgent))
g.add((thesaurusCreation, RDF.type, PROV.Activity))
g.add((thesaurus, RDF.type, PROV.Entity))

g.add((thesaurus, PROV.wasGeneratedBy, thesaurusCreation))
g.add((thesaurus, PROV.wasAttributedTo, pythonScript))

g.add((thesaurus, RDF.type, SKOS.ConceptScheme))
g.add((thesaurus, DC.title, Literal("NAVIS.one Maritime Thesaurus", lang="en")))
g.add((thesaurus, DC.description, Literal("NAVIS.one deals with nautic terms", lang="en")))
g.add((thesaurus, DC.creator, Literal("Florian Thiery")))

thesaurusAddendum = URIRef(baseUri + "/")

for index, row in parentDf.iterrows():
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

g.add((thesaurusCreation, PROV.endedAtTime, Literal(datetime.datetime.now(), datatype=XSD.dateTime)))
g.serialize(destination="navisOne.ttl", format="turtle")