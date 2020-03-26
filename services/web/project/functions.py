def tokenize_text(text):
    return text.split()

def tokenize_documents(text_list):
    return [tokenize_text(doc) for doc in text_list]
