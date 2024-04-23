from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
from io import BytesIO
import pickle

class Indexer:
    def __init__(self, filenames):
        self.filenames = filenames
        self.documents, self.file_doc_pairs = self._retrieve_documents()
        print("Retrieved documents:", self.documents)

        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        print("TF-IDF matrix shape:", self.tfidf_matrix.shape)

        self.inverted_index = self._build_inverted_index()
        print("Inverted index:", self.inverted_index)

    def _retrieve_documents(self):
        documents = []
        file_doc_pairs = []  # List to store pairs of filename and corresponding document
        for filename in self.filenames:
            with open(filename, 'r', encoding='latin-1') as f:
                html_content = f.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                book_entries = soup.find_all('body')
                for entry in book_entries:
                    title = entry.find('h1').get_text(strip=True)
                    price = entry.find_all('p')[0].get_text(strip=True)
                    availability = entry.find_all('p')[1].get_text(strip=True)
                    text = f"Title: {title}\nPrice: {price}\nAvailability: {availability}"
                    documents.append(text)
                    file_doc_pairs.append((filename, text))  # Store the pair of filename and document
        return documents, file_doc_pairs

    def _build_inverted_index(self):
     inverted_index = {}
     for i, (_, doc) in enumerate(self.file_doc_pairs):  # Iterate over filename-document pairs
        terms_in_doc = set(self.vectorizer.build_analyzer()(doc))  # Extract terms from the document
        for term in terms_in_doc:
            if term not in inverted_index:
                inverted_index[term] = []
            inverted_index[term].append(i)
     return inverted_index


    def display_inverted_index(self):
        with BytesIO() as f:
            pickle.dump(self.inverted_index, f)
            f.seek(0)
            print("Inverted index (pickle format):")
            print(f.read())

    def search(self, query):
        query_vector = self.vectorizer.transform([query])
        print("Query vector shape:", query_vector.shape)
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix)
        print("Cosine similarities shape:", cosine_similarities.shape)
        scores = list(cosine_similarities[0])
        print("Cosine similarity scores:", scores)
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        result = []
        for i in sorted_indices:
            if scores[i] > 0:
                result.append((self.file_doc_pairs[i][0], scores[i], self.tfidf_matrix[i]))
        return result

# Example usage
filenames = [
    "C:\\Users\\saisu\\OneDrive\\Desktop\\IR Project\\Project\\crawling\\output.html",
]

indexer = Indexer(filenames)
indexer.display_inverted_index()

# Search with a query
query = input("Enter your query: ")
results = indexer.search(query)
print("Search results:")
for filename, score, tfidf_score in results:
    print(f"TF-IDF Score: {tfidf_score}, Cosine Similarity Score: {score}")