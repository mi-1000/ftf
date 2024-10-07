
function downloadLegalTexts() {
    let downloadedItems = [];

    // Get all texts
    const listItems = document.querySelectorAll('.mat-list-item-content');

    listItems.forEach(item => {
        // Check if the lock is open (legal to download)
        const legalIcon = item.querySelector('.legal-icon mat-icon');
        if (legalIcon && legalIcon.textContent === 'lock_open') {

            // Get metadata information
            const date = item.querySelector('.shelf-date .date').textContent.trim(); // Get date
            const frantextId = item.querySelector('.shelf-date .shelf').textContent.trim(); // Get Frantext ID
            const title = item.querySelector('.mat-line.title').textContent.trim(); // Get title
            const titleA = title.replace(/\s+/g, '_'); // Replace spaces by underscores in title
            const titleB = titleA.replace(/\'+/g, '_'); // Replace apostrophes by underscores in title
            const titleC = titleB.replace(/\"+/g, '_'); // Replace quotes by underscores in title
            const titleFormatted = titleC.normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Remove diacritics from title
            // const author = item.querySelector('.mat-line.authors .author').textContent.trim();
            const downloadIcon = item.querySelector('.download'); // Get download icon

            if (downloadIcon) {
                downloadIcon.click(); // Triggers the download
            }

            // Add metadata to the list
            downloadedItems.push({
                frantextId: frantextId,
                title: title,
                titleFormatted: titleFormatted,
                date: date
            });
        }
    });

    // Generate XML string for all downloaded items
    let xmlString = "";
    downloadedItems.forEach(item => {
        xmlString += `<item link="https://www.frantext.fr" frantext-id="${item.frantextId}" language="old-french" `;
        xmlString += `filename="data/raw/data_old_french/${item.titleFormatted}.xml" date="${item.date}" place="" />\n`;
    });

    return xmlString;
}

// Execute the function and log the resulting XML
console.log(downloadLegalTexts());