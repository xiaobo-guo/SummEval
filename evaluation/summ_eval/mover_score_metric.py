# pylint: disable=C0415,C0103
import os
from collections import defaultdict
import gin
import numpy as np
import tqdm

from summ_eval.metric import Metric

dirname = os.path.dirname(__file__)

@gin.configurable
class MoverScoreMetric(Metric):
    def __init__(self, version=2, stop_wordsf=os.path.join(dirname, 'examples/stopwords.txt'), \
                 n_gram=1, remove_subwords=True, batch_size=48):
        """
        Mover Score metric
        Interfaces https://github.com/AIPHES/emnlp19-moverscore

        NOTE: mover score assumes GPU usage

        Args:
                :param version: Which version of moverscore to use; v2 makes use of DistilBert and will
                        run quicker.
                :param stop_wordsf: path to file with space-separated list of stopwords
                :param n_gram: n_gram size to use in mover score calculation; see Section 3.1 of paper for details
                :param remove_subwords: whether to remove subword tokens before calculating n-grams and proceeding
                        with mover score calculation
                :param batch_size:
                        batch size for mover score calculation; change according to hardware for improved speed
        """
        self.version = version
        if self.version == 1:
            from summ_eval.moverscore.moverscore import get_idf_dict, word_mover_score
        else:
            from summ_eval.moverscore.moverscore_v2 import get_idf_dict, word_mover_score
        self.get_idf_dict = get_idf_dict
        self.word_mover_score = word_mover_score
        stop_words = []
        if stop_wordsf is not None:
            with open(stop_wordsf) as inputf:
                stop_words = inputf.read().strip().split(' ')
        self.stop_words = stop_words
        self.n_gram = n_gram
        self.remove_subwords = remove_subwords
        self.batch_size = batch_size

    def evaluate_example(self, summary, reference):
        idf_dict_ref = defaultdict(lambda: 1.)
        idf_dict_hyp = defaultdict(lambda: 1.)
        score = self.word_mover_score([reference], [summary], idf_dict_ref, idf_dict_hyp, \
                          stop_words=self.stop_words, n_gram=self.n_gram, remove_subwords=self.remove_subwords)
        score_dict = {"mover_score" : score[0]}
        return score_dict

    def evaluate_batch(self, summaries, references, aggregate=True, show_progress_bar=False):
        refs = references
        if isinstance(references[0], list):
            refs = [" ".join(ref) for ref in references]
            
        idf_dict_summ = self.get_idf_dict(summaries)
        idf_dict_ref = self.get_idf_dict(refs)
        scores = []
        if isinstance(references[0], list):
            for reference, summary in tqdm.tqdm(zip(references, summaries),total=len(references), desc='Calculate MoverScore', disable= not show_progress_bar,dynamic_ncols=True,leave=False):
                s = self.word_mover_score(reference, [summary]*len(reference), idf_dict_ref, idf_dict_summ, \
                          stop_words=self.stop_words, n_gram=self.n_gram, remove_subwords=self.remove_subwords,\
                          batch_size=self.batch_size)
                scores.append(np.mean(s))
        else:
            scores = self.word_mover_score(references, summaries, idf_dict_ref, idf_dict_summ, \
                            stop_words=self.stop_words, n_gram=self.n_gram, remove_subwords=self.remove_subwords,\
                            batch_size=self.batch_size, show_progress_bar=show_progress_bar)
        if aggregate:
            return {"mover_score": sum(scores)/len(scores)}
        else:
            score_dict = [{"mover_score" : score} for score in scores]
            return score_dict

    @property
    def supports_multi_ref(self):
        return True
