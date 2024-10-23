import sacrebleu
from bert_score import BERTScorer
from rouge_score import rouge_scorer
import numpy as np
from scipy.spatial.distance import cosine
import Levenshtein as lev
import transformers 

# BERTScore function
def compute_bertscore(translated_text, reference_text, lang="fr"):
    scorer = BERTScorer(lang=lang, rescale_with_baseline=True)
    P, R, F1 = scorer.score(translated_text, reference_text)
    return {
        "precision": P.mean().item(),
        "recall": R.mean().item(),
        "f1": F1.mean().item(),
    }

# ROUGE score function
def compute_rouge_score(translated_text, reference_text):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = [scorer.score(ref, pred) for ref, pred in zip(reference_text, translated_text)]
    rouge_1 = np.mean([score['rouge1'].fmeasure for score in scores])
    rouge_2 = np.mean([score['rouge2'].fmeasure for score in scores])
    rouge_L = np.mean([score['rougeL'].fmeasure for score in scores])
    return {"rouge1": rouge_1, "rouge2": rouge_2, "rougeL": rouge_L}

# Cosine Similarity function (replace dummy embeddings with real embeddings from a model like BERT)
def compute_cosine_similarity(embedding1, embedding2):
    return 1 - cosine(embedding1, embedding2)

# Levenshtein distance function
def compute_levenshtein_distance(translated_text, reference_text):
    distances = [lev.distance(pred, ref) for pred, ref in zip(translated_text, reference_text)]
    return np.mean(distances)

# BLEU score function (make sure the format is correct for sacrebleu)
def compute_bleu_score(translated_text, reference_text):
    bleu = sacrebleu.corpus_bleu(translated_text, [reference_text])
    return bleu.score

# chrF score function (same as BLEU, input format must be tokenized)
def compute_chrf_score(translated_text, reference_text):
    chrf = sacrebleu.corpus_chrf(translated_text, [reference_text])
    return chrf.score

# Provided translations
expected_trad = [
    "Le roi Charles, notre empereur, le Grand, sept ans tout pleins est resté dans l’Espagne : jusqu’à la mer il a conquis la terre hautaine. Plus un château qui devant lui résiste, plus une muraille à forcer, plus une cité, hormis Saragosse, qui est dans une montagne. Le roi Marsile la tient, qui n’aime pas Dieu. C’est Mahomet qu’il sert, Apollin qu’il prie. Il ne peut pas s’en garder : le malheur l’atteindra."
]
gpt_trad = [
    "Charlemagne, notre grand empereur, A passé sept années pleines en Espagne : Il a conquis toute la terre jusqu’à la mer. Il n’y a plus de château qui lui résiste ; Mur ou cité, il n'en reste aucun à détruire, Sauf Saragosse, qui est sur une montagne. Le roi Marsile la tient, lui qui n'aime pas Dieu. Il sert Mahomet et invoque Apollon : Mais ils ne peuvent le protéger du mal qui l'attend."
]

# Compute BLEU
bleu_score = compute_bleu_score(gpt_trad, expected_trad)
print(f"BLEU score: {bleu_score:.2f}")

# Compute chrF
chrf_score = compute_chrf_score(gpt_trad, expected_trad)
print(f"chrF score: {chrf_score:.2f}")

# Compute BERTScore
bertscore = compute_bertscore(gpt_trad, expected_trad)
print(f"BERTScore: Precision: {bertscore['precision']:.2f}, Recall: {bertscore['recall']:.2f}, F1: {bertscore['f1']:.2f}")

# Compute ROUGE
rouge_scores = compute_rouge_score(gpt_trad, expected_trad)
print(f"ROUGE-1: {rouge_scores['rouge1']:.2f}, ROUGE-2: {rouge_scores['rouge2']:.2f}, ROUGE-L: {rouge_scores['rougeL']:.2f}")

# Cosine Similarity (replace dummy example with real embeddings from a model)
dummy_embedding1 = np.random.rand(768)  # Replace with actual embeddings from a language model
dummy_embedding2 = np.random.rand(768)  # Replace with actual embeddings from a language model
cosine_similarity = compute_cosine_similarity(dummy_embedding1, dummy_embedding2)
print(f"Cosine Similarity: {cosine_similarity:.2f}")

# Levenshtein distance
avg_levenshtein = compute_levenshtein_distance(gpt_trad, expected_trad)
print(f"Average Levenshtein Distance: {avg_levenshtein:.2f}")