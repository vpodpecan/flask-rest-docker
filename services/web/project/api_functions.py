from gensim.utils import tokenize


def tokenize_text(text):
    return list(tokenize(text))

def tokenize_documents(text_list):
    return [tokenize_text(doc) for doc in text_list]
