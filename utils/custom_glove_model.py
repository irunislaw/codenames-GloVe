from gensim.models import KeyedVectors
from numpy import ndarray, dot
from numbers import Integral
import numpy as np
from gensim import matutils
_KEY_TYPES = (str, int, np.integer)
_EXTENDED_KEY_TYPES = (str, int, np.integer, np.ndarray)
import re

def _ensure_list(value):
    """Ensure that the specified value is wrapped in a list, for those supported cases
    where we also accept a single key or vector."""
    if value is None:
        return []

    if isinstance(value, _KEY_TYPES) or (isinstance(value, ndarray) and len(value.shape) == 1):
        return [value]

    if isinstance(value, ndarray) and len(value.shape) == 2:
        return list(value)

    return value

class CustomGloveModel(KeyedVectors):
    def most_similar(
            self, positive=None, negative=None, topn=10, clip_start=0, clip_end=None,
            restrict_vocab=None, indexer=None,
        ):
        """Find the top-N most similar keys.
        Positive keys contribute positively towards the similarity, negative keys negatively.

        This method computes cosine similarity between a simple mean of the projection
        weight vectors of the given keys and the vectors for each key in the model.
        The method corresponds to the `word-analogy` and `distance` scripts in the original
        word2vec implementation.

        Parameters
        ----------
        positive : list of (str or int or ndarray) or list of ((str,float) or (int,float) or (ndarray,float)), optional
            List of keys that contribute positively. If tuple, second element specifies the weight (default `1.0`)
        negative : list of (str or int or ndarray) or list of ((str,float) or (int,float) or (ndarray,float)), optional
            List of keys that contribute negatively. If tuple, second element specifies the weight (default `-1.0`)
        topn : int or None, optional
            Number of top-N similar keys to return, when `topn` is int. When `topn` is None,
            then similarities for all keys are returned.
        clip_start : int
            Start clipping index.
        clip_end : int
            End clipping index.
        restrict_vocab : int, optional
            Optional integer which limits the range of vectors which
            are searched for most-similar values. For example, restrict_vocab=10000 would
            only check the first 10000 key vectors in the vocabulary order. (This may be
            meaningful if you've sorted the vocabulary by descending frequency.) If
            specified, overrides any values of ``clip_start`` or ``clip_end``.

        Returns
        -------
        list of (str, float) or numpy.array
            When `topn` is int, a sequence of (key, similarity) is returned.
            When `topn` is None, then similarities for all keys are returned as a
            one-dimensional numpy array with the size of the vocabulary.

        """
        if isinstance(topn, Integral) and topn < 1:
            return []

        # allow passing a single string-key or vector for the positive/negative arguments
        positive = _ensure_list(positive)
        negative = _ensure_list(negative)

        self.fill_norms()
        clip_end = clip_end or len(self.vectors)

        if restrict_vocab:
            clip_start = 0
            clip_end = restrict_vocab

        # add weights for each key, if not already present; default to 1.0 for positive and -1.0 for negative keys
        keys = []
        weight = np.concatenate((np.ones(len(positive)), -1.0 * np.ones(len(negative))))
        for idx, item in enumerate(positive + negative):
            if isinstance(item, _EXTENDED_KEY_TYPES):
                keys.append(item)
            else:
                keys.append(item[0])
                weight[idx] = item[1]

        # compute the weighted average of all keys
        # by all keys are meant the negative and positive words joined together
        mean = self.get_mean_vector(keys, weight, pre_normalize=True, post_normalize=True, ignore_missing=False)
        all_keys = [
            self.get_index(key) for key in keys if isinstance(key, _KEY_TYPES) and self.has_index_for(key)
        ]

        if indexer is not None and isinstance(topn, int):
            return indexer.most_similar(mean, topn)

        dists = dot(self.vectors[clip_start:clip_end], mean) / self.norms[clip_start:clip_end]
        if not topn:
            return dists
        best = matutils.argsort(dists, topn=topn + len(all_keys), reverse=True)
        # ignore (don't return) keys from the input
        result = [
            (self.index_to_key[sim + clip_start], float(dists[sim]))
            for sim in best if (sim + clip_start) not in all_keys
            # added for validating the vocabulary
            and re.match("^[A-Za-z]*$", self.index_to_key[sim + clip_start])
        ]
        return result[:topn]    