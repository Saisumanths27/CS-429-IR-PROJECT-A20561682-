from flask import Flask, request, jsonify, render_template
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup

app = Flask(__name__)

class Indexer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.documents, self.file_doc_pairs = self._retrieve_documents()

        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def _retrieve_documents(self):
        documents = []
        file_doc_pairs = []  # List to store pairs of filename and corresponding document
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                title = item.get('title', '')
                price = item.get('price', '')
                availability = item.get('availability', '')
                text = f"Title: {title}\nPrice: {price}\nAvailability: {availability}"
                documents.append(text)
                file_doc_pairs.append((self.json_file_path, text))  # Store the pair of filename and document
        return documents, file_doc_pairs

    def search(self, query):
        query_vector = self.vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix)
        scores = list(cosine_similarities[0])
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        result = []
        for i in sorted_indices:
            if scores[i] > 0:
                result.append((self.file_doc_pairs[i][1], scores[i]))  # Append document and score
        return result

# Initialize the Indexer with the JSON file path
json_file_path = "C:\\Users\\saisu\\OneDrive\\Desktop\\IR Project\\Project\\crawling\\output.json"
indexer = Indexer(json_file_path)

# Endpoint for home page
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return jsonify({'message': 'Favicon not found'}), 404


# Endpoint for query processing
@app.route('/query', methods=['POST'])
def process_query():
    data = request.form
    if 'query' not in data:
        return jsonify({'error': 'Query is missing'}), 400
    query = data['query']
    results = indexer.search(query)
    if not results:
        return jsonify({'message': 'Results not found'})

    formatted_results = []
    k = 10 
    for i, (document, score) in enumerate(results):
        if i >= k:
            break
        formatted_result = {
            'document': document,
            'cosine_similarity_score': score
        }
        formatted_results.append(formatted_result)

    return jsonify({'results': formatted_results})

if __name__ == '__main__':
    app.run(debug=True)
