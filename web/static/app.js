var _INITIAL_SOURCE_LANGUAGE = 'fr'
var _INITIAL_TARGET_LANGUAGE = 'fro'

document.addEventListener('DOMContentLoaded', (e) => {
    handleSourceTextInput();
    handleLanguageChange();
});

function handleSourceTextInput(sourceTag = 'sourceText') {
    const sourceText = document.getElementById(sourceTag);

    sourceText.addEventListener('input', (e) => {
        newTargetText = e.target.value;
        updateFieldsHeight();
        if (_INITIAL_SOURCE_LANGUAGE == "fr" && e.inputType == "insertText" && (/^.*\b\s{1}$/).test(e.target.value)) {
            lastWord = e.target.value.match(/\b(\w|[^\x00-\x7F])+\b/ug).pop();
            if (lastWord.length > 3) { // Not verifying too short words
                verifyEtymology(lastWord);
            }
        }
        updateTargetText(newTargetText); // TODO: Change with model output
        handleIPAChange(newTargetText); // TODO: Same
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

    sourceLangDropdown.value = _INITIAL_SOURCE_LANGUAGE;
    targetLangDropdown.value = _INITIAL_TARGET_LANGUAGE;

    exchangingArrow.addEventListener('click', (e) => exchangeLanguages(e));
    sourceLangDropdown.addEventListener('change', (e) => exchangeLanguages(e, _INITIAL_SOURCE_LANGUAGE));
    targetLangDropdown.addEventListener('change', (e) => exchangeLanguages(e, _INITIAL_TARGET_LANGUAGE));

    function exchangeLanguages(e, initialLanguage = undefined) {
        if (e.currentTarget === exchangingArrow) {
            const sourceTextArea = document.getElementById('sourceText');
            const targetTextArea = document.getElementById('targetText');

            sourceLangDropdown.value = _INITIAL_TARGET_LANGUAGE;
            targetLangDropdown.value = _INITIAL_SOURCE_LANGUAGE;
            _INITIAL_SOURCE_LANGUAGE = sourceLangDropdown.value;
            _INITIAL_TARGET_LANGUAGE = targetLangDropdown.value;

            sourceTextArea.innerText = targetTextArea.innerText;
            targetTextArea.innerText = "Just switched languages 😎"; // TODO
            return;
        }
        if (e.currentTarget !== sourceLangDropdown && e.currentTarget !== targetLangDropdown) {
            console.log("Error in language change handling.");
            return;
        }
        console.log(initialLanguage, e.currentTarget.value, e.target.value);

        if (e.currentTarget === sourceLangDropdown && e.target.value === targetLangDropdown.value) {
            targetLangDropdown.value = initialLanguage;
        } else if (e.currentTarget === targetLangDropdown && e.target.value === sourceLangDropdown.value) {
            sourceLangDropdown.value = initialLanguage;
        }
        _INITIAL_SOURCE_LANGUAGE = sourceLangDropdown.value;
        _INITIAL_TARGET_LANGUAGE = targetLangDropdown.value;
    }
}

function handleIPAChange(text, sourceTag = 'sourceIPA', targetTag = 'targetIPA') {
    const sourceSection = document.getElementById(sourceTag);
    const targetSection = document.getElementById(targetTag);

    const dummyText = "This is dummy text representing the IPA transcription of the above text.";

    sourceSection.innerText = dummyText.slice(0, text.length % dummyText.length);
    targetSection.innerText = dummyText.slice(0, text.length % dummyText.length);
}

async function verifyEtymology(word) {
    rep = await sendRequest({ "word": word });
    console.log(`${word} : ${rep["date"]}`);
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