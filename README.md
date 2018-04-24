[lc_quad]: images/lc_quad.png "Results on LC-Quad"
[webq]: images/webq.png "Results on WebQuestions"


# Query Generation

The main objective of this project is to generate SPARQL query for a given question which is annotated by its linked entities and relations.

## Challenges
To be added... 

## Approach
To be added...

## Supported Questions
Currently the following questions are supported:
* Single entity relation questions
* Compound questions
* Count questions
* Boolean questions

and the following features will be integrated:
* Aggregation 
* Sort
* Filter

## Data
* QALD dataset: https://github.com/ag-sc/QALD
* Others: https://drive.google.com/drive/folders/14cRLzgxFVrt_b9f91VKND2wu20TemYIN
    * Pretrained question classifier: output/classifer/* 
    * Bloom for DBpedia: data/blooms/*

## Evaluation
We aimed to be KB independent, thus two datasets based on two different KB has been opted to be used for the evaluation purposes:
* LC-Quad based on DBpedia
* WebQuestions based on Freebase 

![alt text][lc_quad]
![alt text][webq]

## Web API

We provide a RESTfull api for the query generator. You need to run this:
``
python sqg_webserver.py
``

Here is an example of how to use the api:
``
curl -i -H "Content-Type: application/json" -X POST -d '{"question":"What is the hometown of Nader Guirat, where Josef Johansson was born too?","relations":[{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/property/birthPlace"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/ontology/hometown"}]}],"entities":[{"surface":"","uris":[{"confidence":0.7,"uri":"http://dbpedia.org/resource/Josef_Johansson"},{"confidence":0.3,"uri":"http://dbpedia.org/resource/Barack_Obama"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/resource/Nader_Guirat"}]}],"kb":"dbpedia"}' http://localhost:5000/qg/api/v1.0/query
``


## Docker
docker build -t sqg -f docker/Dockerfile .
docker stop sqg
docker run -d -p 5000:5000 -it --rm --name sqg sqg

curl --noproxy "*" -i -H "Content-Type: application/json" -X POST -d '{"question":"What is the hometown of Nader Guirat, where Josef Johansson was born too?","relations":[{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/property/birthPlace"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/ontology/hometown"}]}],"entities":[{"surface":"","uris":[{"confidence":0.7,"uri":"http://dbpedia.org/resource/Josef_Johansson"},{"confidence":0.3,"uri":"http://dbpedia.org/resource/Barack_Obama"}]},{"surface":"","uris":[{"confidence":1,"uri":"http://dbpedia.org/resource/Nader_Guirat"}]}],"kb":"dbpedia", "timeout": 60}' http://localhost:5000/qg/api/v1.0/query