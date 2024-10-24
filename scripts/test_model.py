from transformers import MarianMTModel, MarianTokenizer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import sacrebleu
from bert_score import BERTScorer
from rouge_score import rouge_scorer
import numpy as np
from scipy.spatial.distance import cosine
import Levenshtein as lev

# Define model paths
en_romance = "Helsinki-NLP/opus-mt-en-ROMANCE"
romance_en = "Helsinki-NLP/opus-mt-ROMANCE-en"

# Load tokenizers and models
def load_model_and_tokenizer(model_name):
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def load_model_and_tokenizer_llama(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

# Translation function
def translate_text(tokenizer, model, text):
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    return [tokenizer.decode(t, skip_special_tokens=True) for t in translated]

# BLEU score function
def compute_bleu_score(translated_text, reference_text):
    bleu = sacrebleu.corpus_bleu(translated_text, [reference_text])
    return bleu.score

# chrF score function
def compute_chrf_score(translated_text, reference_text):
    chrf = sacrebleu.corpus_chrf(translated_text, [reference_text])
    return chrf.score

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

# Cosine Similarity function
def compute_cosine_similarity(embedding1, embedding2):
    return 1 - cosine(embedding1, embedding2)

# Levenshtein distance function
def compute_levenshtein_distance(translated_text, reference_text):
    distances = [lev.distance(pred, ref) for pred, ref in zip(translated_text, reference_text)]
    return np.mean(distances)

# Main pipeline function
def evaluate_translation_pipeline(src_text, expected_text, model="MarianMT"):
    if model == "MarianMT":
        # Add language token
        src_text_with_token = [f">>la<< {sentence}" for sentence in src_text]
        
        # Load models and tokenizers
        tokenizer1, model1 = load_model_and_tokenizer(romance_en)  # Latin to English
        tokenizer2, model2 = load_model_and_tokenizer(en_romance)  # French to French

        # First translation: Latin to English
        english_translation = translate_text(tokenizer1, model1, src_text_with_token)

        # Add French token for the next step
        english_translation_with_token = [f">>en<< {sentence}" for sentence in english_translation]

        # Second translation: French to English
        french_translation = translate_text(tokenizer2, model2, english_translation_with_token)
    elif model == "Llama-8B":
        model_id = "meta-llama/Meta-Llama-3-8B"

        pipeline = transformers.pipeline("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device_map="auto")
        pipeline(f"Can you translate this {src_text} in latin to french ? And stock it in a variable called 'french_translation'.")
    elif model == "GPT-4o":
        french_translation = [
            "Les Philistins faisaient la guerre contre Israël et les hommes d'Israël fuirent devant les Philistins et tombèrent blessés sur le mont Gelboé.",
            "Et lorsque les Philistins se rapprochèrent, poursuivant Saül et ses fils, ils frappèrent Jonathan, Abinadab et Melchiséa, les fils de Saül.",
            "Et le combat devint intense contre Saül, et les archers le trouvèrent et le blessèrent avec des flèches.",
            "Et Saül dit à son porteur d'armes : 'Dégaine ton épée et tue-moi, de peur que ces incirconcis ne viennent et ne se moquent de moi.' Mais son porteur d'armes refusa de le faire, effrayé de peur, alors Saül prit une épée et se jeta dessus.",
            "Quand son porteur d'armes vit que Saül était mort, il se jeta aussi sur son épée et mourut.",
            "Ainsi moururent Saül, ses trois fils, et toute sa maison tomba ensemble.",
            "Lorsque les hommes d'Israël qui habitaient dans les plaines virent cela, ils fuirent. Et à la mort de Saül et de ses fils, ils abandonnèrent leurs villes et se dispersèrent çà et là. Les Philistins vinrent alors et habitèrent dans ces villes.",
            "Le lendemain, les Philistins vinrent pour dépouiller les morts et trouvèrent Saül et ses fils gisant sur le mont Gelboé.",
            "Après l'avoir dépouillé, ils lui coupèrent la tête et le dévêtirent de ses armes. Ils envoyèrent ces trophées dans leur pays pour qu'ils soient portés et exposés dans les temples de leurs idoles et montrés au peuple.",
            "Quant à ses armes, ils les consacrèrent dans le temple de leur dieu, et ils fixèrent sa tête dans le temple de Dagon.",
            "Lorsque les hommes de Jabès en Galaad entendirent tout ce que les Philistins avaient fait à Saül,",
            "Tous les hommes vaillants se levèrent et prirent les cadavres de Saül et de ses fils. Ils les apportèrent à Jabès et enterrèrent leurs os sous le chêne de Jabès, et ils jeûnèrent pendant sept jours.",
            "Saül mourut à cause de ses propres iniquités, parce qu'il avait transgressé le commandement du Seigneur qu'il avait reçu, et qu'il ne l'avait pas gardé, mais en plus il avait consulté une voyante.",
            "Il n'avait pas mis sa confiance dans le Seigneur, c'est pourquoi il le fit mourir et transféra son royaume à David, fils d'Isaï."
        ]

    else:
        print("Incorrect model name!")
        return

    # Compute BLEU
    bleu_score = compute_bleu_score(french_translation, expected_text)
    print(f"BLEU score: {bleu_score:.2f}")

    # Compute chrF
    chrf_score = compute_chrf_score(french_translation, expected_text)
    print(f"chrF score: {chrf_score:.2f}")

    # Compute BERTScore
    bertscore = compute_bertscore(french_translation, expected_text)
    print(f"BERTScore: Precision: {bertscore['precision']:.2f}, Recall: {bertscore['recall']:.2f}, F1: {bertscore['f1']:.2f}")

    # Compute ROUGE
    rouge_scores = compute_rouge_score(french_translation, expected_text)
    print(f"ROUGE-1: {rouge_scores['rouge1']:.2f}, ROUGE-2: {rouge_scores['rouge2']:.2f}, ROUGE-L: {rouge_scores['rougeL']:.2f}")

    # Cosine Similarity (dummy example, replace with real embeddings)
    dummy_embedding1 = np.random.rand(768)
    dummy_embedding2 = np.random.rand(768)
    cosine_similarity = compute_cosine_similarity(dummy_embedding1, dummy_embedding2)
    print(f"Cosine Similarity: {cosine_similarity:.2f}")

    # Levenshtein distance
    avg_levenshtein = compute_levenshtein_distance(french_translation, expected_text)
    print(f"Average Levenshtein Distance: {avg_levenshtein:.2f}")

# Source and target texts
src_text = [
    "Philisthim autem pugnabant contra Israhel fugeruntque viri Israhel Palestinos et ceciderunt vulnerati in monte Gelboe",
    "cumque adpropinquassent Philisthei persequentes Saul et filios eius percusserunt Ionathan et Abinadab et Melchisuae filios Saul",
    "et adgravatum est proelium contra Saul inveneruntque eum sagittarii et vulneraverunt iaculis",
    "et dixit Saul ad armigerum suum evagina gladium tuum et interfice me ne forte veniant incircumcisi isti et inludant mihi noluit autem armiger eius hoc facere timore perterritus arripuit igitur Saul ensem et inruit in eum",
    "quod cum vidisset armiger eius videlicet mortuum esse Saul inruit etiam ipse in gladium suum et mortuus est",
    "interiit ergo Saul et tres filii eius et omnis domus illius pariter concidit",
    "quod cum vidissent viri Israhel qui habitabant in campestribus fugerunt et Saul ac filiis eius mortuis dereliquerunt urbes suas et huc illucque dispersi sunt veneruntque Philisthim et habitaverunt in eis",
    "die igitur altero detrahentes Philisthim spolia caesorum invenerunt Saul et filios eius iacentes in monte Gelboe",
    "cumque spoliassent eum et amputassent caput armisque nudassent miserunt in terram suam ut circumferretur et ostenderetur idolorum templis et populis",
    "arma autem eius consecraverunt in fano dei sui et caput adfixerunt in templo Dagon",
    "hoc cum audissent viri Iabesgalaad omnia scilicet quae Philisthim fecerunt super Saul",
    "consurrexerunt singuli virorum fortium et tulerunt cadavera Saul et filiorum eius adtuleruntque ea in Iabes et sepelierunt ossa eorum subter quercum quae erat in Iabes et ieiunaverunt septem diebus",
    "mortuus est ergo Saul propter iniquitates suas eo quod praevaricatus sit mandatum Domini quod praeceperat et non custodierit illud sed insuper etiam pythonissam consuluerit",
    "nec speraverit in Domino propter quod et interfecit eum et transtulit regnum eius ad David filium Isai",
]

expected_text = [
    "Les Philistins livrèrent bataille à Israël, et les hommes d'Israël prirent la fuite devant les Philistins et tombèrent morts sur la montagne de Guilboa.",
    "Les Philistins poursuivirent Saül et ses fils, et tuèrent Jonathan, Abinadab et Malki-Schua, fils de Saül.",
    "L'effort du combat porta sur Saül; les archers l'atteignirent et le blessèrent.",
    "Saül dit alors à celui qui portait ses armes: Tire ton épée, et transperce-m'en, de peur que ces incirconcis ne viennent me faire subir leurs outrages. Celui qui portait ses armes ne voulut pas, car il était saisi de crainte. Et Saül prit son épée, et se jeta dessus.",
    "Celui qui portait les armes de Saül, le voyant mort, se jeta aussi sur son épée, et mourut.",
    "Ainsi périrent Saül et ses trois fils, et toute sa maison périt en même temps.",
    "Tous ceux d'Israël qui étaient dans la vallée, ayant vu qu'on avait fui et que Saül et ses fils étaient morts, abandonnèrent leurs villes pour prendre aussi la fuite. Et les Philistins allèrent s'y établir.",
    "Le lendemain, les Philistins vinrent pour dépouiller les morts, et ils trouvèrent Saül et ses fils tombés sur la montagne de Guilboa.",
    "Ils le dépouillèrent, et emportèrent sa tête et ses armes. Puis ils firent annoncer ces bonnes nouvelles par tout le pays des Philistins à leurs idoles et au peuple.",
    "Ils mirent les armes de Saül dans la maison de leur dieu, et ils attachèrent son crâne dans le temple de Dagon.",
    "Tout Jabès en Galaad ayant appris tout ce que les Philistins avaient fait à Saül,",
    "tous les hommes vaillants se levèrent, prirent le corps de Saül et ceux de ses fils, et les transportèrent à Jabès. Ils enterrèrent leurs os sous le térébinthe, à Jabès, et ils jeûnèrent sept jours.",
    "Saül mourut, parce qu'il se rendit coupable d'infidélité envers l'Eternel, dont il n'observa point la parole, et parce qu'il interrogea et consulta ceux qui évoquent les morts.",
    "Il ne consulta point l'Eternel; alors l'Eternel le fit mourir, et transféra la royauté à David, fils d'Isaï.",
]

if __name__ == "__main__":
    evaluate_translation_pipeline(src_text, expected_text, "MarianMT")
    # evaluate_translation_pipeline(src_text, expected_text, "Llama-8B")
    evaluate_translation_pipeline(src_text, expected_text, model="GPT-4o")