# -*- coding: utf-8 -*-
"""
Term Dictionary Parser
==========================

Classes to handle multi-word-token building and the parsing of sentences to extract matched terms.

For performance, both One-word-terms and multi-word-terms are handled using the `treelib` implementation of a Tree.

Requirements:
 - `treelib`: `pip install treelib`

"""
#    Copyright (C) 2016 by
#    Rion Brattig Correia <rionbr@gmail.com>
#    Ian B. Wood <ibwood@iu.edu>
#    All rights reserved.
#    MIT license.
from treelib import Node, Tree

try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)
from nltk.tokenize import TweetTokenizer, word_tokenize, sent_tokenize

__author__ = """\n""".join([
    'Rion Brattig Correia <rionbr@gmail.com>',
    'Ian B. Wood <ibwood@iu.edu>'
])

__all__ = [
    'TermDictionaryParser',
    'TermDictionaryParser.build_vocabulary',
    'TermDictionaryParser.extract_terms_from_sentence',
]


#


def preprocess(sentence):
    """ A simple function to handle preprocessing of a sentence"""
    # Lowercase sentence
    sentence = sentence.lower()
    # Remove @ mentions
    sentence = re.sub('@[a-z0-9_]+', '', sentence)
    # Remove URLs
    sentence = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", '', sentence)
    # Remove NewLines
    sentence = sentence.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    return sentence


#
#
#
class Match(object):
    """
    """

    def __init__(self, id=None, tokens=tuple, si=None, wi=None, ti=None):
        self.id = id
        self.tokens = tokens
        self.si = si  # sentence i
        self.wi = wi  # token i start
        self.ti = ti  # token i end

    def __str__(self):
        return "<Match(id=%s, tokens=%s>" % (self.id, self.tokens)


#
#
#
class Sentences(object):
    """

    """

    def __init__(self, text):
        self.text = self.text_pp = text

    def preprocess(self, lower=True):
        if lower:
            self.text_pp = self.text_pp.lower()
        return self

    def tokenize(self):
        tokenizer_words = TweetTokenizer()
        self.tokens_sentences = [tokenizer_words.tokenize(t) for t in sent_tokenize(self.text_pp)]
        return self

    def match_tokens(self, parser=None):
        self.matches = [Match(id, tokens, si, wi, ti) for (id, tokens, si, wi, ti) in
                        parser.match_tokens(self.tokens_sentences)]
        return self

    def has_match(self):
        """ Returns True if there are matches, False otherwise"""
        return (True if len(self.matches) else False)

    def get_matches(self):
        return self.matches

    def get_unique_matches(self):
        seen = set()
        return [seen.add(obj.tokens) or obj for obj in self.matches if obj.tokens not in seen]

    def tag_sentence(self, html_tag="<match>\\1</match>"):
        """ Tags the sentence """
        if self.has_match():
            matches_sorted = sorted(self.matches, key=lambda x: len(x.tokens), reverse=True)
            tokens = [' '.join(m.tokens) for m in matches_sorted]
            return re.compile("(%s)" % "|".join(map(re.escape, tokens)), re.I | re.UNICODE).sub(html_tag, self.text)
        else:
            return self.text

    def __str__(self):
        return "<Sentencess(%s)>" % len(self.sentence)


#
#
#
class TermDictionaryParser(object):
    """

    """

    def __init__(self):

        # An extended `treelib` object, called terms
        self.tokens = Tree()
        self.tokens.create_node('root', 'root', data=WordNodeData(id=None, endTermWord=False))

    def __str__(self):
        return "<TermDicionatyParser()>"

    def build_vocabulary(self, tokens=[], re_tokenizer=r"[a-zA-Z0-9(-+.)']+"):
        """ Given a list of terms, builds the Vocabulary.

        Args:
            terms (list): The list of terms to compose the vocabulary
            re_tokenizer (string): Regular Expression string used to separates the tokens. Default: `[\\w']+`

        Return:
            Nothing
        """
        wtree = self.tokens
        root = self.tokens.get_node('root')

        for id, token in tokens:

            token = token.lower()
            # wordlist = re.findall(re_tokenizer, token, re.UNICODE)
            wordlist = token.split()  # split on white space

            nodes = list()
            term_size = len(wordlist)

            for i, word in enumerate(wordlist, start=1):
                # print '- Word:', word
                # Parent is root or last inserted node
                parent = root if len(nodes) == 0 else nodes[-1]
                # Is the last word in the term?
                if i < term_size:
                    endTermWord = False
                else:
                    endTermWord = True
                # NodeIdentifier
                if i == 1:
                    identifier = '-'.join([str(i) + '.' + word])
                else:
                    identifier = '-'.join([nodes[-1].identifier] + [str(i) + '.' + word])

                # print '> Identifier:',identifier

                # Node already in the tree?
                node = wtree.get_node(identifier)
                if node:
                    # Is this node now a endTermWord?
                    if endTermWord and not node.data.endTermWord:
                        node.data.id = id
                        node.data.endTermWord = endTermWord
                else:
                    node = wtree.create_node(
                        word,
                        identifier,
                        parent=parent.identifier,
                        data=WordNodeData(
                            id=id if endTermWord else None,
                            endTermWord=endTermWord)
                    )
                nodes.append(node)

    def make_identifier(self, tokenseq, starti, endi):
        """Separate identifier creation """
        idstring = ''
        maxi = endi - starti - 1
        for i in range(endi - starti):
            idstring += str(i + 1) + '.' + tokenseq[starti + i]
            if not i == maxi:
                idstring += '-'
        return (idstring)

    # return('-'.join( [str(i)+'.'+x for i,x in enumerate(wordseq, start=1)] ))

    def get_node(self, tokenseq, starti, endi):
        """Get a tree node from a list of words"""
        identifier = self.make_identifier(tokenseq, starti, endi)
        return (self.tokens.get_node(identifier))

    def in_tree(self, tokenseq, starti, endi):
        """Check if a list of words corresponds to a node in the tree"""
        node = self.get_node(tokenseq, starti, endi)
        return (node is not None)

    def is_end_term_word(self, tokenseq, starti, endi):
        """ Check if the list of words corresponds to a finished phrase """
        node = self.get_node(tokenseq, starti, endi)
        return (node.data.endTermWord)

    def printout(self, tokenseq, starti, endi, pstarti, pendi):
        """For debugging, uncomment printout call"""
        print([tokenseq[starti + i] for i in range(endi - starti)])
        print([tokenseq[pstarti + i] for i in range(pendi - pstarti)])

    def match_tokens(self, tokens_sentences, verbose=False):
        """
        Matches one- and multi-words-terms from a tokenized sentence.

        Args:
            tokens_sentences (list of lists): the already tokenized sentence of tokens. Use `nltk.tokenize` for best results.
            verbose (bool): prints verbose statements.

        Returns:
            ParsedSentences (object)

        Note:
            use `<TermDictionaryParser object>.terms.show()` to see the term tree structure.

        See also:
            build_vocabulary, extract_terms_from_sentence2
        """
        matches = list()
        for si, tokens_sentence in enumerate(tokens_sentences):
            tokenlen = len(tokens_sentence)
            wi = 0
            ti = 0
            pi = 0
            while wi < tokenlen:

                pi += 1
                if pi > tokenlen:
                    if wi != ti:
                        node = self.get_node(tokens_sentence, wi, ti)
                        matches.append((node.data.id, tuple(tokens_sentence[wi:ti]), si, wi, ti))
                        wi = ti
                        pi = wi
                    else:
                        wi += 1
                        ti += 1
                        pi = wi
                else:
                    if self.in_tree(tokens_sentence, wi, pi):
                        if self.is_end_term_word(tokens_sentence, wi, pi):
                            ti = pi
                    else:
                        if wi != ti:
                            node = self.get_node(tokens_sentence, wi, ti)
                            matches.append((node.data.id, tuple(tokens_sentence[wi:ti]), si, wi, ti))
                            wi = ti
                            pi = wi
                        else:
                            wi += 1
                            ti += 1
                            pi = wi
        return matches


class WordNodeData(object):
    """ A simple object to hold end-term-word in the tree nodes.
    Used when there are multiple multi-word terms, and some are complete words withing the tree structure.
    Also included are the original id and type of the term (drug, symp, etc).
    Example: `weight loss` and `weight loss diet` are both terms and belong to the same tree branch.
    """

    def __init__(self, endTermWord=False, type=None, id=None):
        self.id = id
        self.endTermWord = endTermWord


#
# DEBug
#
if __name__ == '__main__':

    tdp = TermDictionaryParser()

    print('--- Build Vocabulary ---')
    terms = [
        (0o1, 'asthma/bronchitis'),
        (0o2, 'linhaça'),  # unicode characteç'
        ('D03', 'ADHD'),  # acym
        ('D02', 'N.E.E.'),  # acym
        ('DB01', 'fluoxetine'),
        (0o3, 'weight loss diet'),
        (0o4, 'weight gain diet'),
        (0o3, 'losing weight'),
        (0o3, 'weight loss'),
        (10, 'brain cancer'),
        (10, 'brain cancer carcinoma'),
        (10, 'brain cancer carcinoma twice'),
        (13, "breast cancer"),
        (14, "cancer"),
        (20, "partial seizures, complex"),
        (50, "first"),
        (51, "second"),
        (52, 'third'),
        (53, 'second third'),
        (54, "first second third fourth"),
        ((61, 62, 63), "Multi Vitamins"),
    ]
    tdp.build_vocabulary(terms)
    print(tdp.tokens.show(data_property=None))

    print('--- Sequence (1) Extraction ---')
    s1 = "I am having FLuoXeTiNe high ADHD, ADHD! #LINHAÇA!weight loss but not because I'm doing a weight loss diet, linhaça. It's my Nerve block back again with FLuoxetine. Perhaps I need to take some multi vitamins. huh nerve. #first. #second."
    # s1 = u"Eu decidi #linhaça o meu amor com todo meu #weight #loss. #first."
    s1 = Sentences(s1).preprocess(lower=True).tokenize().match_tokens(parser=tdp)
    print('S1 Has Matchs: {:b}'.format(s1.has_match()))
    print('S1 (All) Matches:')
    for match in s1.get_matches():
        print(match)
    print('S1 (Unique) Matches')
    for match in s1.get_unique_matches():
        print(match)

    print(s1.tag_sentence())

    print('--- Sequence (2) Extraction ---')
    """
    start = time.time()
    iterations = int(1e3)
    print('max iterations %d'%iterations)
    
    for i in range(iterations):
        if i %1000 == 0:
            print(i)
        s2 = Sentences(u"I dont have weight any mentions").preprocess(lower=True).tokenize().match_tokens(parser=tdp)
        s2 = Sentences(u"Sometimes when you're suffering you forget the people around you but they are suffering with you just in a different way #fibromyalgia #chronicpain #chronicallyill #spoonie #butyoudontlooksick #depression").tokenize().match_tokens(parser=tdp)
        s2 = Sentences(u"The grey brain cancer carcinoma twice is for. brain cancer carcinoma three.").tokenize().match_tokens(parser=tdp)
        s2 = Sentences(u"Support Women battling Breast Cancer.").tokenize().match_tokens(parser=tdp)
        s2 = Sentences(u"I have partial seizures (complex).").tokenize().match_tokens(parser=tdp)
        s2 = Sentences(u"I have first second third word").tokenize().match_tokens(parser=tdp)	
    
    end = time.time()
    print(end-start)
    """
