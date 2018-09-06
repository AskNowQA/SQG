[lc_quad]: images/lc_quad.png "Results on LC-Quad"

# Query Generation

Question answering (QA) systems over Knowledge Graph often consist of several components such as Named Entity Disambiguation (NED), Relation Extraction (RE), and Query Generation (QG). The main objective of this project is to generate SPARQL query for a given question which is annotated by its linked entities and relations.

SQG is a SPARQL Query Generator with modular architecture, enabling easy integration with other components for the construction of a fully functional QA pipeline. To increase the chance constructthe correct query, SQG is able to handle a set of annotations including several incorrect ones. It also benefits from Tree-LSTM model to deal with syntactic ambiguity of the input questions. Special adjustment is considered in order to cope with large-scale knowledge base. 

## Supported Questions
Currently the following questions are supported:
* Single entity relation questions
* Compound questions
* Count questions
* Boolean questions


## Cite
If you would use the codebase, please cite our paper as well:
```
@inproceedings{zafar2018formal,
  title={Formal query generation for question answering over knowledge bases},
  author={Zafar, Hamid and Napolitano, Giulio and Lehmann, Jens},
  booktitle={European Semantic Web Conference},
  pages={714--728},
  year={2018},
  organization={Springer}
}
```
## How-to 

### Data
* LC-QuAD dataset: https://github.com/AskNowQA/LC-QuAD
* Others: https://drive.google.com/drive/folders/14cRLzgxFVrt_b9f91VKND2wu20TemYIN
    * Pretrained question classifier: output/classifer/* 
    * Bloom for DBpedia: data/*.blooms
    
### Getting Started

To run it (python 2.7 is required):
```
python sqg_webserver.py
```


### Consume Web API

SQG provides a RESTfull api for the query generator. 

Here is an example of how to use the api:
```
curl -i -H "Content-Type: application/json" -X POST -d '{"question":"What is the hometown of Nader Guirat, where Josef Johansson was born too?","relations":[{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/property/birthPlace"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/ontology/hometown"}]}],"entities":[{"surface":"","uris":[{"confidence":0.7,"uri":"http://dbpedia.org/resource/Josef_Johansson"},{"confidence":0.3,"uri":"http://dbpedia.org/resource/Barack_Obama"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/resource/Nader_Guirat"}]}],"kb":"dbpedia"}' http://localhost:5000/qg/api/v1.0/query
```

