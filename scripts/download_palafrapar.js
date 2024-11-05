// pageNum = 1; /* Run only at the beginning */
// $0.onclick = () => {pageNum++}; /* Select the right arrow first */

function downloadText(filename, text) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    
    element.style.display = 'none';
    document.body.appendChild(element);
    
    element.click();
    document.body.removeChild(element);
}

function scrapeAndDownload() {
    const contentElement = document.querySelector('#isc_XX'); // TODO Change the ID every time
    if (contentElement) {
        const textContent = contentElement.innerText;
        const filename = `dialgreg_${pageNum}.txt`;
        downloadText(filename, textContent);
        console.log(`Downloaded ${filename}`);
    }
}

scrapeAndDownload();