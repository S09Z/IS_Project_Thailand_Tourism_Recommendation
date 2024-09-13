import re
import os
import string
import numpy as np
import pandas as pd
import nltk

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords 
from constant import PROJECT_ROOT

# from constant import NLTK_DATA_PATH
nltk.data.path.append(f'{PROJECT_ROOT}/pretained_or_finetune-models/nltk_data')
# nltk.data.path.append(NLTK_DATA_PATH)
nltk.download ('all', download_dir=f'{PROJECT_ROOT}/pretained_or_finetune-models/nltk_data')

print("Numpy version:", np.__version__)
print("Pandas version:", pd.__version__)

class DataPreparation:

    def __init__(self) -> None:
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def check_nltk_path(self) -> None:
        print(os.path.exists(f"{PROJECT_ROOT}/pretained_or_finetune-models/nltk_data/tokenizers/punkt"))

    def clean_text(self, text) -> str:
        text = text.lower()  # Convert text to lowercase
        text = re.sub(r'\[.*?\]', '', text)  # Remove content within square brackets
        text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
        text = re.sub(r'<.*?>+', '', text)  # Remove HTML tags
        text = re.sub(r'\n', '', text)  # Remove newlines
        text = re.sub(r'[^a-zA-Z]', ' ', text)  # Keep only alphabets
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
        words = word_tokenize(text)
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        words = [word for word in words if word not in string.punctuation]
        return ' '.join(words)

    def map_rating_to_sentiment(self, rating) -> str:
        if rating in [1, 2]:
            return 'negative'
        elif rating in [3, 4]:
            return 'neutral'
        else:  # 4 or 5
            return 'positive'

    def text_to_word2vec(self, tokens, model, max_length=300):
        vector = np.zeros((max_length, 300))
        for i, word in enumerate(tokens):
            if i < max_length:
                if word in model.wv:
                    vector[i] = model.wv[word]
        return vector

if __name__ == "__main__":
    DF = DataPreparation()
    DF.check_nltk_path()
    print(f"{PROJECT_ROOT} ::: {nltk.data.path}")