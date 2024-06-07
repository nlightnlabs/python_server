import nltk

# Specify the NLTK data path
nltk.data.path.append("/Users/avikghosh/Documents/Programming/python_server/apps/nltk_data/")

# Download the punkt tokenizer data
nltk.download('punkt')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.sentiment import SentimentIntensityAnalyzer


def naturalLanguageProcessing(text):
    # Tokenization
    tokens = word_tokenize(text)

    # Stopword removal
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]

    # Frequency distribution
    fdist = FreqDist(filtered_tokens)

    # Sentiment analysis
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(text)

    # Create an object with NLP results and descriptions
    output_object = {
        'Tokenization': {
            'Value': tokens,
            'Description': 'Tokenization is the process of splitting text into individual words or tokens.'
        },
        'Stopword Removal': {
            'Value': filtered_tokens,
            'Description': 'Stopword removal involves filtering out common words that do not carry much meaning.'
        },
        'Frequency Distribution': {
            'Value': dict(fdist),
            'Description': 'Frequency distribution shows the count of each token after stopword removal.'
        },
        'Sentiment Analysis': {
            'Value': sentiment_scores,
            'Description': 'Sentiment analysis assigns a sentiment score (positive, negative, neutral) to the text.'
        }
    }

    # Display the output object
    print(output_object)

    return output_object


# Sample text for NLP tasks
text = "Who is the president of the united states?"

naturalLanguageProcessing(text)

