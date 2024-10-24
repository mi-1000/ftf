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

        #pipeline = transformers.pipeline("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device_map="auto")
        #pipeline(f"Can you translate this {src_text} in latin to french ? And stock it in a variable called 'french_translation'.")

        french_translation = [
            "Le roi Charles, notre grand empereur,",
            "A passé sept ans complets en Espagne :",
            "Jusqu'à la mer, il a conquis la terre haute.",
            "Il n'y a pas de château qui résiste devant lui ;",
            "Pas de mur ni de ville qui n'ait été pris,",
            "Excepté Saragosse, qui est dans une montagne.",
            "Le roi Marsile la tient, qui n'aime pas Dieu.",
            "Il sert Mahomet et appelle Apollin :",
            "Il ne peut éviter que le malheur ne l'atteigne. aoi."
        ]
        src_text = french_translation

    elif model == "GPT-4o":
        french_translation = [
            "Charles, le roi, notre grand empereur,",
            "A passé sept années complètes en Espagne :",
            "Jusqu'à la mer, il a conquis la terre lointaine.",
            "Il n'y a pas de château qui tienne devant lui ;",
            "Il ne reste ni mur ni cité à détruire,",
            "Sauf Saragosse, qui est sur une montagne.",
            "Le roi Marsile la détient, lui qui n'aime pas Dieu.",
            "Il sert Mahomet et invoque Apollon :",
            "Mais ils ne peuvent le protéger du mal qui l'atteint. aoi."    
        ]
        src_text = french_translation

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

src_text_la_to_fr = [
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
    "nec speraverit in Domino propter quod et interfecit eum et transtulit regnum eius ad David filium Isai"
]

src_text_ofr_to_fr = [
    "CARLES li reis, nostre emperere magnes,",
    "Set anz tuz pleins ad estet en Espaigne :",
    "Tresqu’en la mer cunquist la tere altaigne.",
    "N’i ad castel ki devant lui remaigne ;",
    "Mur ne citet n’i est remés a fraindre,",
    "Fors Sarraguce, ki est en une muntaigne.",
    "Li reis Marsilie la tient, ki Deu nen aimet.",
    "Mahumet sert e Apollin recleimet :",
    "Nes poet guarder que mals ne l’i ateignet. aoi."
]

src_text_mfr_to_fr = [
    ""
]

src_text_gr_to_fr = [
    "Διωρισμένων δὲ τούτων φανερὸν ὅτι καὶ τὰ μοναχῶς λεγόμενα καὶ κατὰ πάντων ἀδύνατον ὑπάρχειν ὥσπερ τινὲς λέγουσιν, οἱ μὲν οὐθὲν φάσκοντες ἀληθὲς εἶναι (οὐθὲν γὰρ κωλύειν φασὶν οὕτως ἅπαντα εἶναι ὥσπερ τὸ τὴν διάμετρον σύμμετρον εἶναι), οἱ δὲ πάντ' ἀληθῆ. Σχεδὸν γὰρ οὗτοι οἱ λόγοι οἱ αὐτοὶ τῷ Ἡρακλείτου· ὁ γὰρ λέγων ὅτι πάντ' ἀληθῆ καὶ πάντα ψευδῆ, καὶ χωρὶς λέγει τῶν λόγων ἑκάτερον τούτων, ὥστ' εἴπερ ἀδύνατα ἐκεῖνα, καὶ ταῦτα ἀδύνατον εἶναι. Ἔτι δὲ φανερῶς ἀντιφάσεις εἰσὶν ἃς οὐχ οἷόν τε ἅμα ἀληθεῖς εἶναι οὐδὲ δὴ ψευδεῖς πάσας· καίτοι δόξειέ γ' ἂν μᾶλλον ἐνδέχεσθαι ἐκ τῶν εἰρημένων. Ἀλλὰ πρὸς πάντας τοὺς τοιούτους λόγους αἰτεῖσθαι δεῖ, καθάπερ ἐλέχθη καὶ ἐν τοῖς ἐπάνω λόγοις, οὐχὶ εἶναί τι ἢ μὴ εἶναι ἀλλὰ σημαίνειν τι, ὥστε ἐξ ὁρισμοῦ διαλεκτέον λαβόντας τί σημαίνει τὸ ψεῦδος ἢ τὸ ἀληθές. Εἰ δὲ μηθὲν ἄλλο τὸ ἀληθὲς φάναι ἢ ἀποφάναι ψεῦδός ἐστιν, ἀδύνατον πάντα ψευδῆ εἶναι· ἀνάγκη γὰρ τῆς ἀντιφάσεως θάτερον εἶναι μόριον ἀληθές. Ἔτι εἰ πᾶν ἢ φάναι ἢ ἀποφάναι ἀναγκαῖον, ἀδύνατον ἀμφότερα ψευδῆ εἶναι· θάτερον γὰρ μόριον τῆς ἀντιφάσεως ψεῦδός ἐστιν. Συμβαίνει δὴ καὶ τὸ θρυλούμενον πᾶσι τοῖς τοιούτοις λόγοις, αὐτοὺς ἑαυτοὺς ἀναιρεῖν. Ὁ μὲν γὰρ πάντα ἀληθῆ λέγων καὶ τὸν ἐναντίον αὑτοῦ λόγον ἀληθῆ ποιεῖ, ὥστε τὸν ἑαυτοῦ οὐκ ἀληθῆ (ὁ γὰρ ἐναντίος οὔ φησιν αὐτὸν ἀληθῆ), ὁ δὲ πάντα ψευδῆ καὶ αὐτὸς αὑτόν. Ἐὰν δ' ἐξαιρῶνται ὁ μὲν τὸν ἐναντίον ὡς οὐκ ἀληθὴς μόνος ἐστίν, ὁ δὲ τὸν αὑτοῦ ὡς οὐ ψευδής, οὐδὲν ἧττον ἀπείρους συμβαίνει αὐτοῖς αἰτεῖσθαι λόγους ἀληθεῖς καὶ ψευδεῖς· ὁ γὰρ λέγων τὸν ἀληθῆ λόγον ἀληθῆ ἀληθής, τοῦτο δ' εἰς ἄπειρον βαδιεῖται. Φανερὸν δ' ὅτι οὐδ' οἱ πάντα ἠρεμεῖν λέγοντες ἀληθῆ λέγουσιν οὐδ' οἱ πάντα κινεῖσθαι. Εἰ μὲν γὰρ ἠρεμεῖ πάντα, ἀεὶ ταὐτὰ ἀληθῆ καὶ ψευδῆ ἔσται, φαίνεται δὲ τοῦτο μεταβάλλον ̔ὁ γὰρ λέγων ποτὲ αὐτὸς οὐκ ἦν καὶ πάλιν οὐκ ἔσταἰ· εἰ δὲ πάντα κινεῖται, οὐθὲν ἔσται ἀληθές· πάντα ἄρα ψευδῆ· ἀλλὰ δέδεικται ὅτι ἀδύνατον. Ἔτι ἀνάγκη τὸ ὂν μεταβάλλειν· ἔκ τινος γὰρ εἴς τι ἡ μεταβολή. Ἀλλὰ μὴν οὐδὲ πάντα ἠρεμεῖ ἢ κινεῖται ποτέ, ἀεὶ δ' οὐθέν· ἔστι γάρ τι ὃ ἀεὶ κινεῖ τὰ κινούμενα, καὶ τὸ πρῶτον κινοῦν ἀκίνητον αὐτό."
]

expected_text_fr_to_la = [
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
    "Il ne consulta point l'Eternel; alors l'Eternel le fit mourir, et transféra la royauté à David, fils d'Isaï."
]

expected_text_fr_to_ofr = [
    "LE roi Charles, notre empereur, le Grand,",
    "sept ans tout pleins est resté dans l’Espagne :",
    "jusqu’à la mer il a conquis la terre hautaine.",
    "Plus un château qui devant lui résiste,",
    "plus une muraille à forcer, plus une cité,",
    "hormis Saragosse, qui est dans une montagne.",
    "Le roi Marsile la tient, qui n’aime pas Dieu.",
    "C’est Mahomet qu’il sert, Apollin qu’il prie.",
    "Il ne peut pas s’en garder : le malheur l’atteindra."
]

expected_text_fr_to_mfr = [
    ""
]

expected_text_fr_to_gr = [
    "Après tout ce qui précède, on doit voir que ces assertions appliquées à un seul cas, et celles qui s'appliquent à tout, sont insoutenables au sens où les comprennent ceux qui les défendent; les uns affirmant que rien n'est vrai, puisque, selon eux, il se peut fort bien que toutes les; propositions soient fausses, comme celle où l'on avancerait que la diagonale est commensurable au côté ; les autres affirmant au contraire que tout est vrai. Ce sont là des théories qui se rapprochent beaucoup des opinions d'Héraclite et se confondent presque avec elles. En effet, celui qui prétend  que tout est vrai et que tout est faux, maintient aussi chacune de ces assertions prises à part; et par conséquent si, considérées séparément, elles sont fausses,  elles le sont également quand on les considère ensemble. D'ailleurs, il y a évidemment des contradictoires qui ne peuvent pas être vraies toutes les deux à la fois, mais qui ne peuvent pas non plus être à la fois toutes les deux fausses, bien que cette dernière alternative pût paraître plus possible que l'autre, d'après les théories qu'on vient d'exposer. Mais, pour réfuter toutes ces doctrines, il faut, ainsi que nous l'avons déjà indiqué un peu plus haut, demander à son adversaire, non pas de dire si la chose est ou si elle n'est pas, mais il faut le sommer d'exprimer et de préciser une pensée quelconque ; de manière qu'on puisse la discuter, en s'appuyant sur la définition même de ce que c'est que le vrai et de ce que c'est que le faux. Si la vérité n'est pas autre chose que d'affirmer le le vrai et de nier le faux, il est dès lors impossible que tout soit faux, puisqu'il y a nécessité absolue que l'une des deux parties de la contradiction soit vraie. D'autre part, si pour toute chose quelconque il faut nécessairement ou l'affirmer ou la nier, il est impossible que les deux parties soient fausses, puisque, dans la contradiction, il n'y en a jamais qu'une seule qui le soit. Le malheur commun de toutes ces belles théories, c'est, comme on l'a répété cent fois, de se réfuter ellesmêmes. Et en effet, quand on avance que tout est vrai, on rend vraie par cela même l'assertion opposée à celle qu'on défend; et, par conséquent, on rend fausse la sienne propre, puisque l'assertion contraire nie que vous soyez dans le vrai. Également, quand on dit que tout est faux, on se condamne du même coup soimême. Que si l'on veut faire des exceptions, et dire que l'opinion contraire à celle qu'on soutient est la seule à n'être pas vraie, et que celle qu'on embrasse soimême est la seule à n'être pas fausse,  on n'en suppose pas moins alors un nombre infini d'assertions vraies et fausses; car, lorsqu'on dit de telle assertion vraie qu'elle est vraie, on sousentend toujours que celui qui dit qu'elle est vraie est dans le vrai; et ces répétitions pourraient aller à l'infini.Il est d'ailleurs évident que ceux qui prétendent que tout est en repos, ne sont pas plus dans le vrai que ceux qui prétendent que tout est en mouvement. Si tout est en repos, alors les mêmes choses seront éternellement vraies et  éternellement fausses. Mais le changement en ce monde est de toute évidence ; et votre interlocuteur luimême doit se dire qu'il fut un temps où il n'existait pas, et qu'il y aura bientôt un temps où il n'existera plus. Mais, si tout est en mouvement, rien ne sera vrai; tout sera faux. Or nous avons démontré que c'était là une impossibilité absolue. Enfin, c'est l'être qui doit nécessairement changer, puisque lechangement n'est que le passage d'un état à un autre état.Mais certainement les choses ne sont pas toutes en repos  ou en mouvement ; elles n'y sont qu'à certains moments donnés ; aucune n'y est éternellement. Ce qui est vrai, c'est qu'il existe un principe qui meut éternellement tout ce qui est mû; et que le moteur premier est luimême immobile."
]

# Source and target texts
src_text = src_text_ofr_to_fr

expected_text = expected_text_fr_to_ofr

if __name__ == "__main__":
    # evaluate_translation_pipeline(src_text, expected_text, "MarianMT")
    evaluate_translation_pipeline(src_text, expected_text, "Llama-8B")
    # evaluate_translation_pipeline(src_text, expected_text, model="GPT-4o")