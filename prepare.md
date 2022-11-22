# Prepare for working

## setting rouge relevant things

Please run the following command and add it to your startup script: 
> export ROUGE_HOME=/home/xiaobo/SummEval/evaluation/summ_eval/ROUGE-1.5.5/
Please also run this command: 
> pip install -U  git+https://github.com/bheinzerling/pyrouge.git

> export PYTHONPATH=$PYTHONPATH:/home/xiaobo/SLP/SummEval/evaluation/summ_eval
## Download nltk relevant things
> import nltk

> nltk.download('stopwords')

## download scikit-learn

> pip install scikit-learn

## install jave

> sudo apt install openjdk-8-jdk

## install corenlp

> pip install stanze

> import stanza

> stanza.install_corenlp()

## install sentence transformers

> pip install sentence_transformers

## install wmd

> pip install wmd