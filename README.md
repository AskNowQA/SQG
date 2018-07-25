[lc_quad]: images/lc_quad.png "Results on LC-Quad"

# Query Generation

Question answering (QA) systems over Knowledge Graph often consist of several components such as Named Entity Disambiguation (NED), Relation Extraction (RE), and Query Generation (QG). The main objective of this project is to generate SPARQL query for a given question which is annotated by its linked entities and relations.

SQG is a SPARQL Query Generator with modular architecture, enabling easy integration with other components for the construction of a fully functional QA pipeline. 

## Supported Questions
Currently the following questions are supported:
* Single entity relation questions
* Compound questions
* Count questions
* Boolean questions

## Data
* LC-QuAD dataset: https://github.com/AskNowQA/LC-QuAD
* Others: https://drive.google.com/drive/folders/14cRLzgxFVrt_b9f91VKND2wu20TemYIN
    * Pretrained question classifier: output/classifer/* 
    * Bloom for DBpedia: data/blooms/*

## Evaluation
We aimed to be KB independent, thus two datasets based on two different KB has been opted to be used for the evaluation purposes:
* LC-Quad based on DBpedia
* WebQuestions based on Freebase 

![alt text][lc_quad]

## Web API

We provide a RESTfull api for the query generator. You need to run this:
``
python sqg_webserver.py
``

Here is an example of how to use the api:
``
curl -i -H "Content-Type: application/json" -X POST -d '{"question":"What is the hometown of Nader Guirat, where Josef Johansson was born too?","relations":[{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/property/birthPlace"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/ontology/hometown"}]}],"entities":[{"surface":"","uris":[{"confidence":0.7,"uri":"http://dbpedia.org/resource/Josef_Johansson"},{"confidence":0.3,"uri":"http://dbpedia.org/resource/Barack_Obama"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/resource/Nader_Guirat"}]}],"kb":"dbpedia"}' http://localhost:5000/qg/api/v1.0/query
``
## Cite

``
@inproceedings{zafar2018formal,
  title={Formal query generation for question answering over knowledge bases},
  author={Zafar, Hamid and Napolitano, Giulio and Lehmann, Jens},
  booktitle={European Semantic Web Conference},
  pages={714--728},
  year={2018},
  organization={Springer}
}
``
