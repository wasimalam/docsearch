if(document.getElementById('toggleAdvanced')){

    document.getElementById('toggleAdvanced').addEventListener('click', function() {
        const advancedSearchDiv = document.getElementById('advancedSearch');
        if (advancedSearchDiv.classList.contains('show')) {
            advancedSearchDiv.classList.remove('show');
            this.textContent = 'Advanced Search';
        } else {
            advancedSearchDiv.classList.add('show');
            this.textContent = 'Hide Advanced Search';
        }
    });
}
if(document.getElementById('searchForm')){

    document.getElementById('searchForm').addEventListener('submit', function(event) {
        event.preventDefault();
        // Collect form data
        const query = document.getElementById('query').value;
        const tags = document.getElementById('tags').value;
        const author = document.getElementById('author').value;
        const from_date = document.getElementById('from_date').value;
        const to_date = document.getElementById('to_date').value;
        
        // Prepare the search request payload
        const searchPayload = {
            query: query,
            tags: tags,
            author: author,
            from_date: from_date,
            to_date: to_date,
            size : 10,
            offset : 0

        };
        
        sendDataRequest(searchPayload);
    });
}



document.addEventListener('DOMContentLoaded', function() {
    sendDataRequest();
});



function sendDataRequest(searchPayload){
    // Clear previous results
    const tbody = document.querySelector(".container");
    // tbody.innerHTML ='';
    while (tbody.lastChild.id !== 'resultrow' && tbody.lastChild.id !=='noresults') {
        tbody.removeChild(tbody.lastChild);
    }

    // Send the AJAX request to the server
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/search', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const result = JSON.parse(xhr.responseText);
            const tbody = document.querySelector('[data-type="result-records"]');
            tbody.replaceChildren();
            if (result && result.hits && result.hits.length > 0) {
                // Generate the results table
                result.hits.forEach(result => {
                    fillsearchdataTemplate(result);
                });
               
            } else {
                const noresults = document.querySelector("#noresults");
                noresults.classList.remove("displaynone");
            }
        }
    };
    const urlParams = new URLSearchParams(window.location.search);
    const myParam = urlParams.get('query');
    xhr.send(searchPayload ? JSON.stringify(searchPayload) : JSON.stringify({
        query: myParam ? myParam : "",
        tags: "",
        author: "",
        from_date: "",
        to_date: "",
        size : 100,
        offset : 0
    }));
}

function fillsearchdataTemplate(result){
    const tbody = document.querySelector('[data-type="result-records"]');
    const template = document.querySelector("#resultrow");
    // Clone the new row and insert it into the table
    const clone = template.content.cloneNode(true);
    const anchor = clone.querySelector('[data-type="link"]') ;
    if(anchor)
        anchor.href = `/api/download/${result._id}`;
    const titleEl = clone.querySelector('[data-type="title"]');
    if(titleEl)
        titleEl.textContent = result._source.title.trim() ? result._source.title.trim() : result._source.filename.trim();
    const authorEl = clone.querySelector('[data-type="author"]')
    if(authorEl)
        authorEl.textContent = result._source.author;
    const uploadDateEl = clone.querySelector('[data-type="uploaddate"]');
    if(uploadDateEl)
        uploadDateEl.textContent = convertToLocalDateTime(result._source.upload_date);
    const tagsEl = clone.querySelector('[data-type="tags"]');
    if(tagsEl)
        tagsEl.textContent = result._source.tags;
    const contentEl = clone.querySelector('[data-type="content"]');
    if(contentEl)
    {
        if(result.highlight){
            contentEl.classList.remove('truncate');
            for(let idx=0; idx< result.highlight.content.length; idx++)
                contentEl.innerHTML += '<span>' + encodeHtmlExceptEm(result.highlight.content[idx]) + '</span>';
        } else {
            contentEl.textContent = result._source.content;
        }
    }
  
    tbody.appendChild(clone);
}
function encodeHtmlExceptEm(htmlString) {
    // Replace all <em> tags with placeholders
    const placeholderStart = '##EM_START##';
    const placeholderEnd = '##EM_END##';
    
    htmlString = htmlString
        .replace(/<em>/g, placeholderStart)
        .replace(/<\/em>/g, placeholderEnd);
    
    // Encode the entire string (including the placeholders)
    const encodedString = htmlString.replace(/[&<>"']/g, function (char) {
        switch (char) {
            case '&': return '&amp;';
            case '<': return '&lt;';
            case '>': return '&gt;';
            case '"': return '&quot;';
            case "'": return '&#39;';
        }
    });
    
    // Replace the placeholders back with <em> tags
    return encodedString
        .replace(new RegExp(placeholderStart, 'g'), '<em>')
        .replace(new RegExp(placeholderEnd, 'g'), '</em>');
}