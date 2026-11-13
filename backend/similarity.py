
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_similar_posts(posts, threshold=0.75):
    """
    Find pairs of posts with similar text.

    posts: list of dictionaries containing id, account and text
    threshold: minimum similarity score (0 to 1)
    """

    if len(posts) < 2:
        return []

    texts = [post["text"] for post in posts]

    # Convert text into numerical vectors
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Happens if there are no usable words
        return []

    # Compare every post with every other post
    similarities = cosine_similarity(matrix)

    matches = []

    for i in range(len(posts)):
        for j in range(i + 1, len(posts)):

            score = similarities[i][j]

            if score >= threshold:
                matches.append({
                    "post_1": posts[i]["id"],
                    "post_2": posts[j]["id"],
                    "account_1": posts[i]["account"],
                    "account_2": posts[j]["account"],
                    "similarity": round(float(score), 3)
                })

    return matches
