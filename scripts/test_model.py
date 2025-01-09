from bert_score import BERTScorer
from dotenv import load_dotenv
from rouge_score import rouge_scorer
from scipy.spatial.distance import cosine
from transformers import MarianMTModel, MarianTokenizer
from transformers import pipeline as pipe, AutoTokenizer, AutoModelForSeq2SeqLM

import Levenshtein as lev
import numpy as np
import os
import sacrebleu
import torch

from typing import List

load_dotenv() # Load environment variables from .env file

# Load tokenizers and models
def load_model_and_tokenizer_marian(model_name):
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

def output_benchmark(translated_text: List[str], expected_text: List[str], model_name: str, source_lang: str, target_lang: str, TABLE_WIDTH = 60):
    """Outputs the benchmark results for a given pair of expected and actual translations

    Args:
        translated_text (List[str]): The list of translated sentences
        expected_text (List[str]): The corresponding list of expected sentences
        model_name (str): Name of the model
        source_lang (str): Source language
        target_lang (str): Target language
        TABLE_WIDTH (int, optional): Width of the table, in characters. Defaults to 60.
    """
    
    # Print headers
    print(f"{'':=^{TABLE_WIDTH}}")
    print(f"||{f'{model_name}: {source_lang} -> {target_lang}'.center(TABLE_WIDTH - 4)}||")
    print(f"{'':=^{TABLE_WIDTH}}")
    
    # Compute BLEU
    bleu_score = compute_bleu_score(translated_text, expected_text)
    print(f"||{f'BLEU score: {bleu_score:.2f}'.center(TABLE_WIDTH - 4)}||")
    print(f"{'':-^{TABLE_WIDTH}}")

    # Compute chrF
    chrf_score = compute_chrf_score(translated_text, expected_text)
    print(f"||{f'chrF score: {chrf_score:.2f}'.center(TABLE_WIDTH - 4)}||")
    print(f"{'':-^{TABLE_WIDTH}}")

    # Compute BERTScore
    bertscore = compute_bertscore(translated_text, expected_text)
    print(f"||{f'BERTScore: Precision: {bertscore['precision']:.2f}, Recall: {bertscore['recall']:.2f}, F1: {bertscore['f1']:.2f}'.center(TABLE_WIDTH - 4)}||")
    print(f"{'':-^{TABLE_WIDTH}}")

    # Compute ROUGE
    rouge_scores = compute_rouge_score(translated_text, expected_text)
    print(f"||{f'ROUGE-1: {rouge_scores['rouge1']:.2f}, ROUGE-2: {rouge_scores['rouge2']:.2f}, ROUGE-L: {rouge_scores['rougeL']:.2f}'.center(TABLE_WIDTH - 4)}||")
    print(f"{'':-^{TABLE_WIDTH}}")

    # TODO We need to calculate the embeddings first
    # Cosine Similarity (dummy example, replace with real embeddings)
    # dummy_embedding1 = np.random.rand(768)
    # dummy_embedding2 = np.random.rand(768)
    # cosine_similarity = compute_cosine_similarity(dummy_embedding1, dummy_embedding2)
    # print(f"||{f'Cosine Similarity: {cosine_similarity:.2f}'.center(TABLE_WIDTH - 4)}||")
    # print(f"{'':-^{TABLE_WIDTH}}")

    # Levenshtein distance
    avg_levenshtein = compute_levenshtein_distance(translated_text, expected_text)
    print(f"||{f'Average Levenshtein Distance: {avg_levenshtein:.2f}'.center(TABLE_WIDTH - 4)}||")
    print(f"{'':=^{TABLE_WIDTH}}")

# Main pipeline function
def evaluate_translation_pipeline(model: str, src_text: List[str] | None = None, expected_text: List[str] | None = None):
    with open('scripts/test_model_files/fr-fro/fr_fro-fr.txt', 'r') as f:
        fr_to_fro_ref = f.read().split('\n')
        
    with open('scripts/test_model_files/fr-fro/fr_fro-fro.txt', 'r') as f:
        fro_ref = f.read().split('\n')
    
    with open('scripts/test_model_files/fr-la/fr_la-fr.txt', 'r') as f:
        fr_to_la_ref = f.read().split('\n')
        
    with open('scripts/test_model_files/fr-la/fr_la-la.txt', 'r') as f:
        la_ref = f.read().split('\n')
    
    if model == "MarianMT":
        # Define model paths
        # en_romance = os.getenv("OPUS_MT_EN_ROMANCE")
        # romance_en = os.getenv("OPUS_MT_ROMANCE_EN")
        # # Add language token
        # src_text_with_token = [f">>la<< {sentence}" for sentence in src_text]
        
        # # Load models and tokenizers
        # tokenizer1, model1 = load_model_and_tokenizer_marian(romance_en)  # Latin to English
        # tokenizer2, model2 = load_model_and_tokenizer_marian(en_romance)  # English to French

        # # First translation: Latin to English
        # english_translation = translate_text(tokenizer1, model1, src_text_with_token)

        # # Add French token for the next step
        # english_translation_with_token = [f">>en<< {sentence}" for sentence in english_translation]

        # # Second translation: English to French
        # french_translation = translate_text(tokenizer2, model2, english_translation_with_token)
        
        
        with open(os.path.join('scripts', 'test_model_files', 'fr-la', 'la_to_fr-marianmt01.txt'), 'r', encoding='utf-8') as f:
            french_translation = f.readlines()
            
        output_benchmark(french_translation, fr_to_la_ref, model, 'Latin', 'French')
        
    elif model == "Llama-8B":
        # Prompts
        """Translate the following sentences from Old French to Modern French, while keeping the structure of the text, i.e. your output must contain the same number of lines and we should be able to closely follow the translation by aligning both paragraphs:"""
        """Translate the following sentences from Modern French to Old French (circa 900-1000 AD), while keeping the structure of the text, i.e. your output must contain the same number of lines and we should be able to closely follow the translation by aligning both paragraphs:"""
        """Translate the following sentences from Latin to French, while keeping the structure of the text, i.e. your output must contain the same number of lines and we should be able to closely follow the translation by aligning both paragraphs:"""
        """Translate the following sentences from French to Classical Latin, while keeping the structure of the text, i.e. your output must contain the same number of lines and we should be able to closely follow the translation by aligning both paragraphs:"""
        
        # model_id = "meta-llama/Meta-Llama-3-8B"

        # for sentence in src_text:
        #     pipeline = pipe("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device_map="auto")
        #     pipeline(f"Translate the following sentence from Latin to French, and reply only with the translation: {sentence}")
        
        with open('scripts/test_model_files/fr-fro/fro_to_fr-llama_70B.txt', 'r') as f:
            fro_to_fr = f.read().split('\n')

        with open('scripts/test_model_files/fr-fro/fr_to_fro-llama_70B.txt', 'r') as f:
            fr_to_fro = f.read().split('\n')
        
        with open('scripts/test_model_files/fr-la/la_to_fr-llama_70B.txt', 'r') as f:
            la_to_fr = f.read().split('\n')

        with open('scripts/test_model_files/fr-la/fr_to_la-llama_70B.txt', 'r') as f:
            fr_to_la = f.read().split('\n')
        
        output_benchmark(fr_to_fro_ref, fro_to_fr, 'Llama-3.1-70B', 'Old French', 'French')
        output_benchmark(fro_ref, fr_to_fro, 'Llama-3.1-70B', 'French', 'Old French')
        output_benchmark(fr_to_la_ref, la_to_fr, 'Llama-3.1-70B', 'Latin', 'French')
        output_benchmark(la_ref, fr_to_la, 'Llama-3.1-70B', 'French', 'Latin')

    elif model == "Llama-8B_finetuned":
        fr_to_fro-llama_8B_finetuned.txt
        with open(os.path.join('scripts', 'test_model_files', 'fr-fro', 'la_to_fr-marianmt01.txt'), 'r', encoding='utf-8') as f:
            french_translation = f.readlines()
            
        output_benchmark(french_translation, fr_to_la_ref, model, 'Latin', 'French')
        

    elif model == "GPT-4o":
        
        # Prompts
        """Translate the following sentences from Old French to Modern French, while keeping the structure of the text, i.e. your output must contain the same number of lines and we should be able to closely follow the translation by aligning both paragraphs:"""
        """Translate the following sentences from Modern French to Old French (circa 900-1000 AD), while keeping the structure of the text, i.e. your output must contain the same number of lines and we should be able to closely follow the translation by aligning both paragraphs:"""
        
        with open('scripts/test_model_files/fr-fro/fro_to_fr-gpt_4o.txt', 'r') as f:
            fro_to_fr = f.read().split('\n')

        with open('scripts/test_model_files/fr-fro/fr_to_fro-gpt_4o.txt', 'r') as f:
            fr_to_fro = f.read().split('\n')
        
        output_benchmark(fr_to_fro_ref, fro_to_fr, 'GPT-4o', 'Old French', 'French')
        output_benchmark(fro_ref, fr_to_fro, 'GPT-4o', 'French', 'Old French')

    elif model == "Google Translate":
        with open('scripts/test_model_files/fr-la/la_to_fr-google_translate.txt', 'r') as f:
            la_to_fr = f.read().split('\n')

        with open('scripts/test_model_files/fr-la/fr_to_la-google_translate.txt', 'r') as f:
            fr_to_la = f.read().split('\n')
        
        output_benchmark(fr_to_la_ref, la_to_fr, 'Google Translate', 'Latin', 'French')
        output_benchmark(la_ref, fr_to_la, 'Google Translate', 'French', 'Latin')

    else:
        print("Incorrect model name!")
        return

# src_text_mfr_to_fr = [
#     "Notez ci que histoires de Tobie devroit selonc le maistre en hystoires tantost suivant après le quart livre des roys.",
#     "Mais j'ai ci mys devant Thobie le commencement et la fin du livre Job, pour ce qu'il gist en la Bible devant Thobie.", 
#     "Et ne pourquant ne deussent il mie estre en cest livre, car il ne suit mis hytoires, ne li mestre n'en traite mie en hystoires, mais je les ai mis en cest livre pour la voire et la biaute deus, en tel ordre come il gist en la Bible. "
#     "Quant Job ot moult parlé à ses amis, nostres sires parla à lui, et il à nostre seigneur moult de manieres.",
#     "Et ce ne fait mie aussi à translater pour les grans misteres qui sunt ès paroles, si les trespasserai ci aussi et vai avant en histoire."
#     "Li tres sainz Job vesqui .c. et .xl. ans apres les grans tribulacions qu'il avoit souffertes.",
#     "Et vit ses enfans et les enfans de ses enfans jusques en la quarte lingniee.",
#     "Et lors morut viele et anciens et plains de jours."
#     "Ci fine li quart livre des rois.",
#     "Ci commence li livres de Job."
#     "Apres ce ouvri Job sa bouc(h)e si maudi l'eure qu'il (est) nez, et dist moult de paroles que nus ne doit translater, et si parlerent moult longuement si ami à lui.",
#     "Et ces paroles qu'il distrent li uns à l'autre sont de si fort larme et plainnes de si grant m(auvesaitié) que nus n'en puet l(e) mistere entendre s'il n'est trop grans clers de divinité.",
#     "Et pour ce les trespasserai je ci, car nus ne les devroit oser translater, car lait gent i pouraient ouvrer, si m'en irai avant la fin du livre Job."
# ]

# src_text_gr_to_fr = [
#     "Διωρισμένων δὲ τούτων φανερὸν ὅτι καὶ τὰ μοναχῶς λεγόμενα καὶ κατὰ πάντων ἀδύνατον ὑπάρχειν ὥσπερ τινὲς λέγουσιν, οἱ μὲν οὐθὲν φάσκοντες ἀληθὲς εἶναι (οὐθὲν γὰρ κωλύειν φασὶν οὕτως ἅπαντα εἶναι ὥσπερ τὸ τὴν διάμετρον σύμμετρον εἶναι), οἱ δὲ πάντ' ἀληθῆ. Σχεδὸν γὰρ οὗτοι οἱ λόγοι οἱ αὐτοὶ τῷ Ἡρακλείτου· ὁ γὰρ λέγων ὅτι πάντ' ἀληθῆ καὶ πάντα ψευδῆ, καὶ χωρὶς λέγει τῶν λόγων ἑκάτερον τούτων, ὥστ' εἴπερ ἀδύνατα ἐκεῖνα, καὶ ταῦτα ἀδύνατον εἶναι. Ἔτι δὲ φανερῶς ἀντιφάσεις εἰσὶν ἃς οὐχ οἷόν τε ἅμα ἀληθεῖς εἶναι οὐδὲ δὴ ψευδεῖς πάσας· καίτοι δόξειέ γ' ἂν μᾶλλον ἐνδέχεσθαι ἐκ τῶν εἰρημένων. Ἀλλὰ πρὸς πάντας τοὺς τοιούτους λόγους αἰτεῖσθαι δεῖ, καθάπερ ἐλέχθη καὶ ἐν τοῖς ἐπάνω λόγοις, οὐχὶ εἶναί τι ἢ μὴ εἶναι ἀλλὰ σημαίνειν τι, ὥστε ἐξ ὁρισμοῦ διαλεκτέον λαβόντας τί σημαίνει τὸ ψεῦδος ἢ τὸ ἀληθές. Εἰ δὲ μηθὲν ἄλλο τὸ ἀληθὲς φάναι ἢ ἀποφάναι ψεῦδός ἐστιν, ἀδύνατον πάντα ψευδῆ εἶναι· ἀνάγκη γὰρ τῆς ἀντιφάσεως θάτερον εἶναι μόριον ἀληθές. Ἔτι εἰ πᾶν ἢ φάναι ἢ ἀποφάναι ἀναγκαῖον, ἀδύνατον ἀμφότερα ψευδῆ εἶναι· θάτερον γὰρ μόριον τῆς ἀντιφάσεως ψεῦδός ἐστιν. Συμβαίνει δὴ καὶ τὸ θρυλούμενον πᾶσι τοῖς τοιούτοις λόγοις, αὐτοὺς ἑαυτοὺς ἀναιρεῖν. Ὁ μὲν γὰρ πάντα ἀληθῆ λέγων καὶ τὸν ἐναντίον αὑτοῦ λόγον ἀληθῆ ποιεῖ, ὥστε τὸν ἑαυτοῦ οὐκ ἀληθῆ (ὁ γὰρ ἐναντίος οὔ φησιν αὐτὸν ἀληθῆ), ὁ δὲ πάντα ψευδῆ καὶ αὐτὸς αὑτόν. Ἐὰν δ' ἐξαιρῶνται ὁ μὲν τὸν ἐναντίον ὡς οὐκ ἀληθὴς μόνος ἐστίν, ὁ δὲ τὸν αὑτοῦ ὡς οὐ ψευδής, οὐδὲν ἧττον ἀπείρους συμβαίνει αὐτοῖς αἰτεῖσθαι λόγους ἀληθεῖς καὶ ψευδεῖς· ὁ γὰρ λέγων τὸν ἀληθῆ λόγον ἀληθῆ ἀληθής, τοῦτο δ' εἰς ἄπειρον βαδιεῖται. Φανερὸν δ' ὅτι οὐδ' οἱ πάντα ἠρεμεῖν λέγοντες ἀληθῆ λέγουσιν οὐδ' οἱ πάντα κινεῖσθαι. Εἰ μὲν γὰρ ἠρεμεῖ πάντα, ἀεὶ ταὐτὰ ἀληθῆ καὶ ψευδῆ ἔσται, φαίνεται δὲ τοῦτο μεταβάλλον ̔ὁ γὰρ λέγων ποτὲ αὐτὸς οὐκ ἦν καὶ πάλιν οὐκ ἔσταἰ· εἰ δὲ πάντα κινεῖται, οὐθὲν ἔσται ἀληθές· πάντα ἄρα ψευδῆ· ἀλλὰ δέδεικται ὅτι ἀδύνατον. Ἔτι ἀνάγκη τὸ ὂν μεταβάλλειν· ἔκ τινος γὰρ εἴς τι ἡ μεταβολή. Ἀλλὰ μὴν οὐδὲ πάντα ἠρεμεῖ ἢ κινεῖται ποτέ, ἀεὶ δ' οὐθέν· ἔστι γάρ τι ὃ ἀεὶ κινεῖ τὰ κινούμενα, καὶ τὸ πρῶτον κινοῦν ἀκίνητον αὐτό."
# ]

# expected_text_fr_to_mfr = [
#     "Remarquez que les Histoires de Tobie devraient selon le Maître en histoires suivre le Quatrième Livre des Rois.",
#     "Mais j'ai décidé de mettre avant Tobie le commencement et la fin du livre de Job, parce qu'ils se trouvent ainsi dans la Bible.",
#     "Et même si ce début et cette fin ne devaient pas se trouver là, car cela ne correspond aux histoires et le Maître n'en parle pas dans son ouvrage, je les ai ajoutés à ce livre à cause de la beauté qu'ils renferment dans l'ordre suivi par la Bible."
#     "Quant Job eu longtemps parlé à ses amis, Notre Seigneur lui parla, et Job Lui répondit longuement.",
#     "Et je ne traduirai pas à cause des grands mystères qui sont contenus dans ces paroles, je les passerai sous silence et continue plus avant dans les histoires.",
#     "Le très saint Job vécut cent quarante ans après les grandes épreuves qu'il avait endurées.",
#     "Et il connut ses enfants, et les enfants de ses enfants jusqu'à la quatrième génération.",
#     "Et il mourut vieux et sage après très longtemps.",
#     "Ici se termine le Quatrième Livre des Rois.",
#     "Ici commence le Livre de Job.",
#     "Ensuite, Job ouvrit la bouche pour maudire l'heure de sa naissance et il ajouta beaucoup de paroles que personne ne doit traduire, et ses amis parlèrent longuement avec lui.",
#     "Et les paroles qu'ils échangèrent sont si pleines de récriminations et de méchanceté que personne ne peut en entendre le mystère, à moins d'être très savant théologien.",
#     "C'est pour cela que je vais passer outre, car personne ne devrait les traduire et seuls des gens très laids le feraient.",
#     "Je me rendrai donc directement à la fin du Livre."
# ]

# expected_text_fr_to_gr = [
#     "Après tout ce qui précède, on doit voir que ces assertions appliquées à un seul cas, et celles qui s'appliquent à tout, sont insoutenables au sens où les comprennent ceux qui les défendent; les uns affirmant que rien n'est vrai, puisque, selon eux, il se peut fort bien que toutes les; propositions soient fausses, comme celle où l'on avancerait que la diagonale est commensurable au côté ; les autres affirmant au contraire que tout est vrai. Ce sont là des théories qui se rapprochent beaucoup des opinions d'Héraclite et se confondent presque avec elles. En effet, celui qui prétend  que tout est vrai et que tout est faux, maintient aussi chacune de ces assertions prises à part; et par conséquent si, considérées séparément, elles sont fausses,  elles le sont également quand on les considère ensemble. D'ailleurs, il y a évidemment des contradictoires qui ne peuvent pas être vraies toutes les deux à la fois, mais qui ne peuvent pas non plus être à la fois toutes les deux fausses, bien que cette dernière alternative pût paraître plus possible que l'autre, d'après les théories qu'on vient d'exposer. Mais, pour réfuter toutes ces doctrines, il faut, ainsi que nous l'avons déjà indiqué un peu plus haut, demander à son adversaire, non pas de dire si la chose est ou si elle n'est pas, mais il faut le sommer d'exprimer et de préciser une pensée quelconque ; de manière qu'on puisse la discuter, en s'appuyant sur la définition même de ce que c'est que le vrai et de ce que c'est que le faux. Si la vérité n'est pas autre chose que d'affirmer le le vrai et de nier le faux, il est dès lors impossible que tout soit faux, puisqu'il y a nécessité absolue que l'une des deux parties de la contradiction soit vraie. D'autre part, si pour toute chose quelconque il faut nécessairement ou l'affirmer ou la nier, il est impossible que les deux parties soient fausses, puisque, dans la contradiction, il n'y en a jamais qu'une seule qui le soit. Le malheur commun de toutes ces belles théories, c'est, comme on l'a répété cent fois, de se réfuter ellesmêmes. Et en effet, quand on avance que tout est vrai, on rend vraie par cela même l'assertion opposée à celle qu'on défend; et, par conséquent, on rend fausse la sienne propre, puisque l'assertion contraire nie que vous soyez dans le vrai. Également, quand on dit que tout est faux, on se condamne du même coup soimême. Que si l'on veut faire des exceptions, et dire que l'opinion contraire à celle qu'on soutient est la seule à n'être pas vraie, et que celle qu'on embrasse soimême est la seule à n'être pas fausse,  on n'en suppose pas moins alors un nombre infini d'assertions vraies et fausses; car, lorsqu'on dit de telle assertion vraie qu'elle est vraie, on sousentend toujours que celui qui dit qu'elle est vraie est dans le vrai; et ces répétitions pourraient aller à l'infini.Il est d'ailleurs évident que ceux qui prétendent que tout est en repos, ne sont pas plus dans le vrai que ceux qui prétendent que tout est en mouvement. Si tout est en repos, alors les mêmes choses seront éternellement vraies et  éternellement fausses. Mais le changement en ce monde est de toute évidence ; et votre interlocuteur luimême doit se dire qu'il fut un temps où il n'existait pas, et qu'il y aura bientôt un temps où il n'existera plus. Mais, si tout est en mouvement, rien ne sera vrai; tout sera faux. Or nous avons démontré que c'était là une impossibilité absolue. Enfin, c'est l'être qui doit nécessairement changer, puisque lechangement n'est que le passage d'un état à un autre état.Mais certainement les choses ne sont pas toutes en repos  ou en mouvement ; elles n'y sont qu'à certains moments donnés ; aucune n'y est éternellement. Ce qui est vrai, c'est qu'il existe un principe qui meut éternellement tout ce qui est mû; et que le moteur premier est luimême immobile."
# ]

if __name__ == "__main__":
    evaluate_translation_pipeline("MarianMT")
    # evaluate_translation_pipeline("GPT-4o")
    # evaluate_translation_pipeline("Llama-8B")
    # evaluate_translation_pipeline("Google Translate")