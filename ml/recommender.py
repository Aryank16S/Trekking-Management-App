import re
import math
import numpy as np

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
    "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}

DIFFICULTY_MAP = {
    "Easy": 1.0,
    "Moderate": 2.0,
    "Hard": 3.0
}

FITNESS_DIFFICULTY_PREF = {
    "Beginner": "Easy",
    "Intermediate": "Moderate",
    "Advanced": "Hard"
}

def tokenize(text):
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in STOP_WORDS]

class PureNumpyTFIDF:
    """
    Pure NumPy implementation of TF-IDF feature extraction.
    Zero binary DLL dependencies; runs seamlessly on all environments.
    """
    def __init__(self):
        self.vocabulary_ = {}
        self.idf_ = {}

    def fit_transform(self, documents):
        tokenized_docs = [tokenize(doc) for doc in documents]
        n_docs = len(documents)

        # Build vocabulary
        vocab = {}
        doc_freq = {}
        for tokens in tokenized_docs:
            seen_terms = set(tokens)
            for t in tokens:
                if t not in vocab:
                    vocab[t] = len(vocab)
            for t in seen_terms:
                doc_freq[t] = doc_freq.get(t, 0) + 1

        self.vocabulary_ = vocab
        n_vocab = len(vocab)
        if n_vocab == 0:
            return np.zeros((n_docs, 1))

        # Compute smoothed IDF
        self.idf_ = {}
        for term, df in doc_freq.items():
            self.idf_[term] = math.log((1.0 + n_docs) / (1.0 + df)) + 1.0

        # Build TF-IDF matrix
        matrix = np.zeros((n_docs, n_vocab), dtype=np.float32)
        for i, tokens in enumerate(tokenized_docs):
            if not tokens:
                continue
            t_counts = {}
            for t in tokens:
                t_counts[t] = t_counts.get(t, 0) + 1
            for term, count in t_counts.items():
                if term in vocab:
                    j = vocab[term]
                    tf = count / len(tokens)
                    matrix[i, j] = tf * self.idf_[term]

            # L2 normalize row
            norm = np.linalg.norm(matrix[i])
            if norm > 0:
                matrix[i] = matrix[i] / norm

        return matrix

class TrekRecommender:
    """
    Content-Based Trek Recommendation & AI Matchmaker Engine
    using pure TF-IDF vectorization and cosine similarity.
    """

    def __init__(self):
        self.tfidf = PureNumpyTFIDF()

    def _build_features(self, treks):
        if not treks:
            return None

        corpus = [
            f"{t.name} {t.location} {t.difficulty} difficulty {t.description}"
            for t in treks
        ]
        text_matrix = self.tfidf.fit_transform(corpus)

        # Numerical features: duration, price, difficulty
        durations = np.array([float(t.duration or 1) for t in treks])
        prices = np.array([float(t.price or 1000) for t in treks])
        difficulties = np.array([DIFFICULTY_MAP.get(t.difficulty, 2.0) for t in treks])

        # Min-max scale numerical features
        def scale(arr):
            mn, mx = arr.min(), arr.max()
            if mx == mn:
                return np.zeros_like(arr)
            return (arr - mn) / (mx - mn)

        num_matrix = np.column_stack([scale(durations), scale(prices), scale(difficulties)])

        # Hybrid weighting: 65% textual trail context + 35% numerical specs
        feature_matrix = np.hstack([text_matrix * 0.65, num_matrix * 0.35])
        return feature_matrix

    def get_similar_treks(self, target_trek, all_treks, top_n=3):
        """
        Calculates cosine similarity to recommend top_n similar treks.
        """
        if not all_treks or len(all_treks) <= 1:
            return []

        target_idx = None
        for i, t in enumerate(all_treks):
            if t.id == target_trek.id:
                target_idx = i
                break

        if target_idx is None:
            return []

        features = self._build_features(all_treks)
        if features is None:
            return []

        target_vec = features[target_idx]
        target_norm = np.linalg.norm(target_vec) + 1e-9

        scores = []
        for i, row in enumerate(features):
            if i == target_idx:
                continue
            row_norm = np.linalg.norm(row) + 1e-9
            cos_sim = float(np.dot(target_vec, row) / (target_norm * row_norm))
            match_pct = int(min(98, max(52, round(cos_sim * 100))))

            matched_trek = all_treks[i]
            reasons = []
            if matched_trek.difficulty == target_trek.difficulty:
                reasons.append(f"matching {matched_trek.difficulty} grade")
            if abs(matched_trek.duration - target_trek.duration) <= 2:
                reasons.append("similar trek duration")
            if matched_trek.location.lower() in target_trek.location.lower() or target_trek.location.lower() in matched_trek.location.lower():
                reasons.append("same scenic region")
            if not reasons:
                reasons.append("comparable trail profile and terrain")

            scores.append({
                "trek": matched_trek,
                "score": match_pct,
                "reason": f"{match_pct}% Match: " + ", ".join(reasons).capitalize()
            })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_n]

    def recommend_for_user_preferences(self, all_treks, fitness_level="Intermediate",
                                       max_budget=15000, max_duration=7,
                                       terrain_pref="All", top_n=4):
        """
        Personalized AI Matchmaker ranking.
        """
        if not all_treks:
            return []

        ideal_diff = FITNESS_DIFFICULTY_PREF.get(fitness_level, "Moderate")
        scored_treks = []

        for trek in all_treks:
            score = 68.0

            # Difficulty alignment
            if trek.difficulty == ideal_diff:
                score += 18.0
            elif (ideal_diff == "Moderate" and trek.difficulty in ["Easy", "Hard"]) or \
                 (ideal_diff == "Advanced" and trek.difficulty == "Moderate"):
                score += 8.0
            else:
                score -= 8.0

            # Budget alignment
            if max_budget and max_budget > 0:
                if trek.price <= max_budget:
                    savings = (max_budget - trek.price) / max_budget
                    score += min(10.0, 4.0 + savings * 6.0)
                else:
                    over = (trek.price - max_budget) / max_budget
                    score -= min(25.0, over * 30.0)

            # Duration alignment
            if max_duration and max_duration > 0:
                if trek.duration <= max_duration:
                    score += 8.0
                else:
                    score -= min(20.0, (trek.duration - max_duration) * 5.0)

            # Terrain / keyword alignment
            if terrain_pref and terrain_pref.lower() != "all":
                pref_lower = terrain_pref.lower()
                text_content = f"{trek.name} {trek.location} {trek.description}".lower()
                if pref_lower in text_content:
                    score += 10.0
                elif any(w in text_content for w in pref_lower.split()):
                    score += 5.0

            final_score = int(min(99, max(50, round(score))))

            highlights = []
            if trek.difficulty == ideal_diff:
                highlights.append(f"Ideal for {fitness_level} fitness")
            if max_budget and trek.price <= max_budget:
                highlights.append("Comfortably within budget")
            if max_duration and trek.duration <= max_duration:
                highlights.append(f"{trek.duration}-day trail fits your schedule")
            if not highlights:
                highlights.append("Scenic trail & experienced guide")

            scored_treks.append({
                "trek": trek,
                "score": final_score,
                "highlights": highlights
            })

        scored_treks.sort(key=lambda x: x["score"], reverse=True)
        return scored_treks[:top_n]


# Singleton instance
recommender = TrekRecommender()
