from transformers import MarianMTModel, MarianTokenizer
import sacrebleu
from bert_score import BERTScorer
from rouge_score import rouge_scorer
import numpy as np
from scipy.spatial.distance import cosine
import Levenshtein as lev

# Source and target texts
src_text = [
    ">>la<< Philisthim autem pugnabant contra Israhel fugeruntque viri Israhel Palestinos et ceciderunt vulnerati in monte Gelboe",
    ">>la<< cumque adpropinquassent Philisthei persequentes Saul et filios eius percusserunt Ionathan et Abinadab et Melchisuae filios Saul",
    ">>la<< et adgravatum est proelium contra Saul inveneruntque eum sagittarii et vulneraverunt iaculis",
    ">>la<< et dixit Saul ad armigerum suum evagina gladium tuum et interfice me ne forte veniant incircumcisi isti et inludant mihi noluit autem armiger eius hoc facere timore perterritus arripuit igitur Saul ensem et inruit in eum",
    ">>la<< quod cum vidisset armiger eius videlicet mortuum esse Saul inruit etiam ipse in gladium suum et mortuus est",
    ">>la<< interiit ergo Saul et tres filii eius et omnis domus illius pariter concidit",
    ">>la<< quod cum vidissent viri Israhel qui habitabant in campestribus fugerunt et Saul ac filiis eius mortuis dereliquerunt urbes suas et huc illucque dispersi sunt veneruntque Philisthim et habitaverunt in eis",
    ">>la<< die igitur altero detrahentes Philisthim spolia caesorum invenerunt Saul et filios eius iacentes in monte Gelboe",
    ">>la<< cumque spoliassent eum et amputassent caput armisque nudassent miserunt in terram suam ut circumferretur et ostenderetur idolorum templis et populis",
    ">>la<< arma autem eius consecraverunt in fano dei sui et caput adfixerunt in templo Dagon",
    ">>la<< hoc cum audissent viri Iabesgalaad omnia scilicet quae Philisthim fecerunt super Saul",
    ">>la<< consurrexerunt singuli virorum fortium et tulerunt cadavera Saul et filiorum eius adtuleruntque ea in Iabes et sepelierunt ossa eorum subter quercum quae erat in Iabes et ieiunaverunt septem diebus",
    ">>la<< mortuus est ergo Saul propter iniquitates suas eo quod praevaricatus sit mandatum Domini quod praeceperat et non custodierit illud sed insuper etiam pythonissam consuluerit",
    ">>la<< nec speraverit in Domino propter quod et interfecit eum et transtulit regnum eius ad David filium Isai",
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

# Define model paths
en_romance = "Helsinki-NLP/opus-mt-en-ROMANCE"
romance_en = "Helsinki-NLP/opus-mt-ROMANCE-en"

# Load tokenizers and models
tokenizer1 = MarianTokenizer.from_pretrained(romance_en)
model1 = MarianMTModel.from_pretrained(romance_en)
tokenizer2 = MarianTokenizer.from_pretrained(en_romance)
model2 = MarianMTModel.from_pretrained(en_romance)

# First translation: Latin to French
inputs = tokenizer1(src_text, return_tensors="pt", padding=True)
translated = model1.generate(**inputs)
tgt_text = [tokenizer1.decode(t, skip_special_tokens=True) for t in translated]

# Prepare the translated text with the French language token
list2 = [f">>fr<< {sentence}" for sentence in tgt_text]

# Second translation: French to English
inputs2 = tokenizer2(list2, return_tensors="pt", padding=True)
translated2 = model2.generate(**inputs2)
tgt_text2 = [tokenizer2.decode(t, skip_special_tokens=True) for t in translated2]

# BLEU score
bleu = sacrebleu.corpus_bleu(tgt_text2, [expected_text])
print(f"BLEU score: {bleu.score:.2f}")

# chrF score
chrf = sacrebleu.corpus_chrf(tgt_text2, [expected_text])
print(f"chrF score: {chrf.score:.2f}")

# BERTScore
scorer = BERTScorer(lang="fr", rescale_with_baseline=True)
P, R, F1 = scorer.score(tgt_text2, expected_text)
print(f"BERTScore: Precision: {P.mean().item():.2f}, Recall: {R.mean().item():.2f}, F1: {F1.mean().item():.2f}")

# ROUGE score
rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
rouge_scores = [rouge_scorer.score(expected, predicted) for expected, predicted in zip(expected_text, tgt_text2)]
rouge_1 = np.mean([score['rouge1'].fmeasure for score in rouge_scores])
rouge_2 = np.mean([score['rouge2'].fmeasure for score in rouge_scores])
rouge_L = np.mean([score['rougeL'].fmeasure for score in rouge_scores])
print(f"ROUGE-1: {rouge_1:.2f}, ROUGE-2: {rouge_2:.2f}, ROUGE-L: {rouge_L:.2f}")

# Cosine Similarity
def compute_cosine_similarity(text1, text2):
    # Assuming embeddings from BERT (for example)
    # Here, we could use embeddings, but for simplicity, we will use token counts.
    return 1 - cosine(text1, text2)  # Replace with actual embeddings

# Example with dummy vectors (update with real embeddings)
dummy_embedding1 = np.random.rand(768)
dummy_embedding2 = np.random.rand(768)
cosine_sim = compute_cosine_similarity(dummy_embedding1, dummy_embedding2)
print(f"Cosine Similarity: {cosine_sim:.2f}")

# Levenshtein distance
levenshtein_distances = [lev.distance(predicted, expected) for predicted, expected in zip(tgt_text2, expected_text)]
avg_levenshtein = np.mean(levenshtein_distances)
print(f"Average Levenshtein Distance: {avg_levenshtein:.2f}")