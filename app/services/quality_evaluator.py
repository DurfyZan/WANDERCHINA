import math
import re
from collections import Counter
from typing import Sequence


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def bleu_score(candidate: str, reference: str, max_n: int = 4) -> float:
    ref_tokens = _tokenize(reference)
    cand_tokens = _tokenize(candidate)
    if not cand_tokens:
        return 0.0
    precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams = Counter(tuple(ref_tokens[i : i + n]) for i in range(len(ref_tokens) - n + 1))
        cand_ngrams = Counter(tuple(cand_tokens[i : i + n]) for i in range(len(cand_tokens) - n + 1))
        overlap = sum((ref_ngrams & cand_ngrams).values())
        total = sum(cand_ngrams.values()) or 1
        precisions.append(overlap / total)
    geo = math.exp(sum(math.log(p) for p in precisions if p > 0) / max_n) if any(p > 0 for p in precisions) else 0.0
    bp = min(1.0, math.exp(1 - len(ref_tokens) / max(len(cand_tokens), 1)))
    return geo * bp


def rouge_l(candidate: str, reference: str) -> float:
    c, r = _tokenize(candidate), _tokenize(reference)
    if not c or not r:
        return 0.0
    m, n = len(c), len(r)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if c[i - 1] == r[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    prec, rec = lcs / m, lcs / n
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def lexical_diversity(texts: Sequence[str]) -> float:
    tokens = [t for text in texts for t in _tokenize(text)]
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def perplexity_proxy(texts: Sequence[str]) -> float:
    """Unigram entropy proxy; lower is smoother (not true model perplexity)."""
    tokens = [t for text in texts for t in _tokenize(text)]
    if not tokens:
        return float("inf")
    counts = Counter(tokens)
    total = len(tokens)
    entropy = -sum((c / total) * math.log(c / total) for c in counts.values())
    return math.exp(entropy)


def evaluate_batch(
    candidates: list[str],
    references: list[str] | None,
    metrics: list[str],
) -> dict[str, float]:
    scores: dict[str, float] = {}
    refs = references or candidates

    if "bleu" in metrics and candidates and refs:
        pairs = zip(candidates, refs[: len(candidates)], strict=False)
        scores["bleu"] = sum(bleu_score(c, r) for c, r in pairs) / len(candidates)
    if "rouge" in metrics and candidates and refs:
        pairs = zip(candidates, refs[: len(candidates)], strict=False)
        scores["rouge_l"] = sum(rouge_l(c, r) for c, r in pairs) / len(candidates)
    if "diversity" in metrics:
        scores["diversity"] = lexical_diversity(candidates)
    if "perplexity" in metrics:
        scores["perplexity"] = perplexity_proxy(candidates)

    if scores:
        scores["overall"] = sum(scores.values()) / len(scores)
    return scores
