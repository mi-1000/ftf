var _CURRENT_SOURCE_LANGUAGE = 'fr'
var _CURRENT_TARGET_LANGUAGE = 'fro'
var _CURRENT_SOURCE_PERIOD = 'eu'
var _CURRENT_TARGET_PERIOD = 'ear'

var _ATTESTATION_DATES = {}

document.addEventListener('DOMContentLoaded', (e) => {
    handleSourceTextInput();
    handleLanguageChange();
    handleCopyIPA();
    handleIPADropdown();
    handleIPAPeriodChange();
});

function handleSourceTextInput(sourceTag = 'sourceText') {
    const sourceText = document.getElementById(sourceTag);

    sourceText.addEventListener('keyup', (e) => {
        if (e.key === 'Backspace') {
            updateEtymology(e.target.value); // Update if backspace is pressed
        }
    });
    sourceText.addEventListener('input', (e) => {
        newTargetText = e.target.value;
        updateFieldsHeight();
        updateEtymology(newTargetText);
        updateTargetText(newTargetText); // TODO: Change with model output
        if (newTargetText) handleIPAChange();
        else {
            document.getElementById("sourceText").value = "";
            document.getElementById("sourceIPA").innerText = "";
            document.getElementById("targetText").innerText = "";
            document.getElementById("targetIPA").innerText = "";
        }
    });
}

/**
 * Updates the target text (duh)
 * 
 * @param {String} text The new text to be printed out
 * @param {String} tag The HTML tag for the target text container
 */
function updateTargetText(text, tag = 'targetText') {
    const targetText = document.getElementById(tag);
    targetText.innerText = text;
}

function updateFieldsHeight(sourceTag = 'sourceText', targetTag = 'targetText') {

    const sourceText = document.getElementById(sourceTag);
    const targetText = document.getElementById(targetTag);

    sourceText.style.height = 'auto';
    targetText.style.height = 'auto';
    const newHeight = sourceText.scrollHeight;
    sourceText.style.height = `${newHeight}px`;
    targetText.style.height = `${newHeight}px`;
}

function handleLanguageChange(sourceTag = 'sourceLang', targetTag = 'targetLang', exchangeTag = 'exchangeLanguages') {
    const sourceLangDropdown = document.getElementById(sourceTag);
    const targetLangDropdown = document.getElementById(targetTag);
    const exchangingArrow = document.getElementById(exchangeTag);

    sourceLangDropdown.value = _CURRENT_SOURCE_LANGUAGE;
    targetLangDropdown.value = _CURRENT_TARGET_LANGUAGE;

    exchangingArrow.addEventListener('click', (e) => exchangeLanguages(e));
    sourceLangDropdown.addEventListener('change', (e) => exchangeLanguages(e, _CURRENT_SOURCE_LANGUAGE));
    targetLangDropdown.addEventListener('change', (e) => exchangeLanguages(e, _CURRENT_TARGET_LANGUAGE));

    function exchangeLanguages(e, initialLanguage = undefined) {
        const sourceTextArea = document.getElementById('sourceText');
        const targetTextArea = document.getElementById('targetText');
        if (e.currentTarget === exchangingArrow) {

            sourceLangDropdown.value = _CURRENT_TARGET_LANGUAGE;
            targetLangDropdown.value = _CURRENT_SOURCE_LANGUAGE;
            _CURRENT_SOURCE_LANGUAGE = sourceLangDropdown.value;
            _CURRENT_TARGET_LANGUAGE = targetLangDropdown.value;

            sourceTextArea.innerText = targetTextArea.innerText;
            targetTextArea.innerText = "Just switched languages 😎"; // TODO
        }
        else if (e.currentTarget !== sourceLangDropdown && e.currentTarget !== targetLangDropdown) {
            console.error("Error in language change handling.");
            return;
        } else if (e.currentTarget === sourceLangDropdown && e.target.value === targetLangDropdown.value) {
            targetLangDropdown.value = initialLanguage;
        } else if (e.currentTarget === targetLangDropdown && e.target.value === sourceLangDropdown.value) {
            sourceLangDropdown.value = initialLanguage;
        }
        _CURRENT_SOURCE_LANGUAGE = sourceLangDropdown.value;
        _CURRENT_TARGET_LANGUAGE = targetLangDropdown.value;
        _CURRENT_SOURCE_PERIOD = getDefaultPeriod(_CURRENT_SOURCE_LANGUAGE);
        _CURRENT_TARGET_PERIOD = getDefaultPeriod(_CURRENT_TARGET_LANGUAGE);
        updateEtymology(sourceTextArea.value);
        handleIPADropdown();
        handleIPAChange();
    }
}

function handleCopyIPA(className=".api-section") {
    sections = document.querySelectorAll(className);
    sections.forEach(section => {
        section.addEventListener('click', (e) => {
            navigator.clipboard.writeText(e.target.innerText); // Copy IPA text to clipboard
        });
    });
}

/**
 * Get default period for a given language
 * 
 * @param {String} lang 
 * @returns {String | undefined}
 */
function getDefaultPeriod(lang) {
    switch (lang) {
        case "fr":
            return "eu";
        case "la":
            return "clas";
        case "fro":
            return "ear";
        case "grc":
            return "cla";
        default:
            break;
    }
}

async function handleIPAChange(sourceTag = 'sourceIPA', targetTag = 'targetIPA') {
    const sourceSection = document.getElementById(sourceTag);
    const targetSection = document.getElementById(targetTag);

    const sourceText = document.getElementById("sourceText").value;
    const targetText = document.getElementById("targetText").innerText;

    if (sourceText) {
        let sourceReq = await sendRequest({ "text": sourceText, "lang": _CURRENT_SOURCE_LANGUAGE, "period": _CURRENT_SOURCE_PERIOD }, '/ipa')
        let targetReq = await sendRequest({ "text": targetText, "lang": _CURRENT_TARGET_LANGUAGE, "period": _CURRENT_TARGET_PERIOD }, '/ipa')
        
        const sourceIPA = sourceReq?.ipa ? sourceReq.ipa : `<span style="color: red;">An error has occured: <b>${sourceReq?.error}</b></span>`; // IPA if exists else error message
        const targetIPA = targetReq?.ipa ? targetReq.ipa : `<span style="color: red;">An error has occured: <b>${targetReq?.error}</b></span>`; // IPA if exists else error message

        sourceSection.innerHTML = sourceIPA;
        targetSection.innerHTML = targetIPA;
    }

    updateFieldsHeight(sourceTag, targetTag);
}

function handleIPAPeriodChange(sourceTag = 'sourcePeriod', targetTag = 'targetPeriod') {
    const sourceDropdown = document.getElementById(sourceTag);
    const targetDropdown = document.getElementById(targetTag);

    sourceDropdown.addEventListener('change', (e) => {
        _CURRENT_SOURCE_PERIOD = e.target.value.split('-')[1];
        handleIPAChange();
    });
    targetDropdown.addEventListener('change', (e) => {
        _CURRENT_TARGET_PERIOD = e.target.value.split('-')[1];
        handleIPAChange();
    });
}

function handleIPADropdown(sourceDropdown = 'sourcePeriod', targetDropdown = 'targetPeriod') {
    const sourcePeriodDropdown = document.getElementById(sourceDropdown);
    const targetPeriodDropdown = document.getElementById(targetDropdown);

    sourcePeriodDropdown.value = _CURRENT_SOURCE_LANGUAGE + '-' + _CURRENT_SOURCE_PERIOD;
    targetPeriodDropdown.value = _CURRENT_TARGET_LANGUAGE + '-' + _CURRENT_TARGET_PERIOD;

    sourcePeriodDropdown.querySelectorAll('option').forEach(period => { // Only display periods for current language
        if (!period.value.startsWith(_CURRENT_SOURCE_LANGUAGE + '-'))
            period.style.display = 'none';
        else period.style.display = 'initial';
    });
    targetPeriodDropdown.querySelectorAll('option').forEach(period => {
        if (!period.value.startsWith(_CURRENT_TARGET_LANGUAGE + '-'))
            period.style.display = 'none';
        else period.style.display = 'initial';
    });
}


async function getFirstAttestationDate(word) {
    rep = await sendRequest({ "word": word });
    date = rep["date"];
    return (date ? Number.parseInt(date) : null); // Return date if exists else null
}

async function updateEtymology(text, dateThreshold = 1800) { // Default corresponds to industrial revolution and mitigates false positives
    _ATTESTATION_DATES = {};

    const infoIcon = document.getElementById("anachronousInfoIcon");
    const infoAnchor = infoIcon.querySelector('a');

    console.log(_CURRENT_SOURCE_LANGUAGE)
    if (!text || _CURRENT_SOURCE_LANGUAGE != "fr") {
        infoIcon.style.display = "none";
        infoAnchor.href = "#";
        infoAnchor.target = "_self";
        return;
    }
    
    let words = (text.trim().split(/\s+/)).filter(word => word.length > 3); // Only track words longer than 3 characters
    for (const word of words) {
        _ATTESTATION_DATES[word] = await getFirstAttestationDate(word);
    }

    thresholdHit = false;
    wordFound = "";
    Object.entries(_ATTESTATION_DATES).forEach(([word, date], index) => {
        if (date && date >= dateThreshold) {
            thresholdHit = true;
            wordFound = word;
            return;
        }
    });

    if (thresholdHit && wordFound) { // Text contains anachronous elements relative to threshold set
        infoIcon.style.display = "block";
        infoAnchor.href = "https://www.cnrtl.fr/definition/" + wordFound;
        infoAnchor.target = "_blank";
    } else {
        infoIcon.style.display = "none";
        infoAnchor.href = "#";
        infoAnchor.target = "_self";
    }
}

/**
 * Sends a POST request
 * 
 * @param {Array} data The data to be sent
 * @param {String} url The URL to receive the request (defaults to `'/'`)
 * @return {Promise} The server response
 */
async function sendRequest(data, url = '/') {
    let headers = new Headers();
    headers.append("Content-Type", "application/json; charset=UTF-8");
    // headers.append("Origin", window.location.href);
    let config = {
        method: "POST",
        headers: headers,
        body: JSON.stringify(data),
    };
    let reponse = await fetch(url, config);
    return await reponse.json();
}