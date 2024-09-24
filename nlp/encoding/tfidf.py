"""
This module contains class for embedding documents.
It includes functionalities for keyword extraction and document submission.
"""
import json
import math
from collections import Counter
from typing import List, Tuple

from nlp.encoding.base import BaseEncoder
from pandas.core.api import DataFrame


class TfIdf(BaseEncoder):
    r""" """

    def __init__(self, documents: List[str], is_sklearn=False) -> None:
        """

        Args:
            documents:
            is_sklearn:

        """
        super().__init__(documents, is_sklearn)
        self.vocab = {}
        self.inverse_vocab = {}
        self.idf = {}

    def fit(
        self,
        is_pyvi=True,
        vocab_cached_path: str = "nlp/cached/vocab_tfidf.json",
        use_cached=False,
        unknown_token="#sep",
        smooth=True,
    ) -> Tuple:
        """
        Args:
            is_pyvi: bool, default = True
                Mean True if used pyvi library to tokenizer
            vocab_cached_path: str default = nlp/cached/vocab.json
                Mean path to save cached vocab
            use_cached: bool, default = False
                Mean True if used cached to load vocab or save vocab
            unknown_token: str = #sep
                Mean token not in vocab change to #sep
            smooth
        Returns:Dict[str, int], Dict[int, str]
            vocab and idf cached vocab
        """
        if use_cached:
            with open(vocab_cached_path, "w") as fp:
                vocab_map = json.load(fp)
                self.vocab, self.inverse_vocab = vocab_map.get("vocab"), vocab_map.get(
                    "idf_cached"
                )
            return self.vocab, self.inverse_vocab

        token_documents = self.tokenizer_documents(is_pyvi=is_pyvi)
        self.vocab = {unknown_token: 0}
        index = 1
        for token_doc in token_documents:
            for token in token_doc:
                if token not in self.vocab:
                    self.vocab[token] = index
                    index += 1
        self.idf = ()

        if smooth:
            d = len(self.documents) + 1
            for word in self.vocab.keys():
                count = 0
                for doc in self.documents:
                    if word in doc:
                        count += 1
                self.idf += (math.log(d + 1 / (count + 1)),)
        else:
            raise "We need smooth"

        if not use_cached and vocab_cached_path:
            cache = {"vocab": self.vocab, "idf_cached": self.idf}
            with open(vocab_cached_path, "w") as fp:
                json.dump(cache, fp=fp, indent=4, ensure_ascii=False)
        return self.vocab, self.idf

    def transform(self, docs: List[str], less_memory: True) -> Tuple | DataFrame:
        """

         Args:
             docs:
             less_memory:
         Returns:
             Tuple of vector embedding or DataFrame embedding
         """
        for doc in docs:
            self.__transform_sentence(doc)
        return ()

    def __transform_sentence(self, sentence: str, is_pyvi=True):
        """

        Args:
            sentence: Sentence need to embedding
            is_pyvi: bool = True
                Mean True if user pyvi library to tokenizer

        Returns:Tuple
            Vector tokenizer
        """
        tokens_sentence = self.tokenizer_documents([sentence])
        token_count_dict = Counter(tokens_sentence)
        len_tokens_sentences = len(tokens_sentence)
        tf_idf = tuple()

        for token in tokens_sentence:
            idx = self.vocab.get(token)
            value = token_count_dict.get(token) / len_tokens_sentences
            tf_idf += (value / len_tokens_sentences) * self.idf[idx]
        return tf_idf

    def vector_to_sentence(self, vector: List[int,]) -> str:
        raise "Module not implement"
