let searchTimeout;
const csrfToken = window.csrfToken;

document.getElementById('search-input').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const query = this.value;
    
    if (query.length < 3) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    searchTimeout = setTimeout(() => {
        fetch(`/restaurants/search/api/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }
                
                const container = document.getElementById('search-results');
                
                if (data.results.length === 0) {
                    container.innerHTML = '<p>No results found</p>';
                    return;
                }

                container.innerHTML = data.results.map(r => `
                    <div class="card mb-2">
                        <div class="card-body d-flex justify-content-between align-items-center">
                            <div>
                                <h5 class="mb-1">${r.name}</h5>
                                <p class="mb-1 text-muted">${r.address}</p>
                                <small>⭐ ${r.rating || 'N/A'} (${r.user_ratings_total || 0} reviews)</small>
                            </div>
                            <form method="post" action="/restaurants/add-from-google/">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                                <input type="hidden" name="place_id" value="${r.place_id}">
                                <button type="submit" class="btn btn-primary btn-sm">Add</button>
                            </form>
                        </div>
                    </div>
                `).join('');
            });
    }, 500);
});
