from app.services.quality_evaluator import bleu_score, evaluate_batch, lexical_diversity, rouge_l


def test_bleu_identical():
    assert bleu_score("hello world", "hello world") > 0.9


def test_rouge_partial():
    score = rouge_l("the cat sat", "the cat")
    assert 0 < score <= 1


def test_evaluate_batch():
    candidates = ["great trip to chengdu", "local food is amazing"]
    refs = ["great trip to chengdu", "local food is amazing"]
    scores = evaluate_batch(candidates, refs, ["bleu", "rouge", "diversity"])
    assert "overall" in scores
    assert scores["diversity"] == lexical_diversity(candidates)
