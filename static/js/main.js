document.addEventListener('DOMContentLoaded', function() {
    // Load cached categories when the page loads
    loadCachedCategories();
    
    // Set up form submission handler
    const form = document.getElementById('category-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        generateWordCloud(false); // Not from cache list when submitting form
    });
    
    // Set up dropdown for category input
    const categoryInput = document.getElementById('category-input');
    categoryInput.addEventListener('focus', function() {
        document.getElementById('category-dropdown').style.display = 'block';
    });
    
    categoryInput.addEventListener('blur', function() {
        // Small delay to allow clicks on dropdown items
        setTimeout(() => {
            document.getElementById('category-dropdown').style.display = 'none';
        }, 200);
    });
    
    categoryInput.addEventListener('input', function() {
        filterCategoryDropdown(this.value);
    });
});

function loadCachedCategories() {
    // Get the list of cached categories from the server
    fetch('/get_categories')
        .then(response => response.json())
        .then(categories => {
            updateCachedCategoriesList(categories);
            populateCategoryDropdown(categories);
        })
        .catch(error => {
            console.error('Error loading cached categories:', error);
        });
}

function updateCachedCategoriesList(categories) {
    const cachedList = document.getElementById('cached-list');
    cachedList.innerHTML = '';
    
    if (categories.length === 0) {
        cachedList.innerHTML = '<li>No cached categories yet</li>';
        return;
    }
    
    categories.forEach(category => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = '#';
        link.textContent = category;
        link.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('category-input').value = category;
            generateWordCloud(true); // This is from cached list
        });
        li.appendChild(link);
        cachedList.appendChild(li);
    });
}

function populateCategoryDropdown(categories) {
    const dropdown = document.getElementById('cached-categories');
    dropdown.innerHTML = '';
    
    categories.forEach(category => {
        const li = document.createElement('li');
        li.textContent = category;
        li.addEventListener('click', function() {
            document.getElementById('category-input').value = category;
            document.getElementById('category-dropdown').style.display = 'none'; 
        });
        dropdown.appendChild(li);
    });
}

function filterCategoryDropdown(query) {
    const items = document.querySelectorAll('#cached-categories li');
    query = query.toLowerCase();
    
    items.forEach(item => {
        if (item.textContent.toLowerCase().includes(query)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function generateWordCloud(fromCachedList = false) {
    const category = document.getElementById('category-input').value.trim();
    
    if (!category) {
        updateStatus('Please enter a Wikipedia category');
        return;
    }
    
    // Update status message
    updateStatus(`Generating word cloud for "${category}"...`);
    
    // Clear any existing word cloud
    document.getElementById('word-cloud').innerHTML = '';
    
    // Only show loading indicator if not from cached list
    if (!fromCachedList) {
        document.getElementById('loading-indicator').style.display = 'flex';
    }
    
    // Get word frequencies from the server
    const formData = new FormData();
    formData.append('category', category);
    
    fetch('/word_frequencies', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Error getting word frequencies');
            });
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        document.getElementById('loading-indicator').style.display = 'none';
        
        if (data.length === 0) {
            updateStatus('No words found for this category');
            return;
        }
        
        updateStatus(`Displaying word cloud for "${category}"`);
        createWordCloud(data);
        
        // Refresh the cached categories list
        loadCachedCategories();
    })
    .catch(error => {
        document.getElementById('loading-indicator').style.display = 'none';
        updateStatus(`Error: ${error.message}`);
        console.error('Error:', error);
    });
}

function createWordCloud(words) {
    // Calculate dimensions
    const container = document.getElementById('word-cloud');
    const width = container.offsetWidth || 800;
    const height = 500;
    
    // Find max and min sizes for scaling
    const maxFreq = words[0].size;
    const minFreq = words[words.length - 1].size;
    
    // Scale for font sizes (between 10 and 100)
    const fontScale = d3.scaleLog()
        .domain([minFreq, maxFreq])
        .range([15, 80]);
    
    // Generate color scheme
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
    
    // Configure the layout
    const layout = d3.layout.cloud()
        .size([width, height])
        .words(words)
        .padding(5)
        .rotate(() => ~~(Math.random() * 2) * 90)
        .fontSize(d => fontScale(d.size))
        .on('end', draw);
    
    // Start the layout algorithm
    layout.start();
    
    // Function to draw the word cloud
    function draw(words) {
        d3.select('#word-cloud').append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'word-cloud-svg')
            .append('g')
            .attr('transform', `translate(${width/2},${height/2})`)
            .selectAll('text')
            .data(words)
            .enter()
            .append('text')
            .style('font-size', d => `${d.size}px`)
            .style('font-family', 'Arial, sans-serif')
            .style('fill', (d, i) => colorScale(i % 10))
            .attr('text-anchor', 'middle')
            .attr('transform', d => `translate(${d.x},${d.y}) rotate(${d.rotate})`)
            .text(d => d.text)
            .append('title')  // Tooltip showing exact frequency
            .text(d => `${d.text}: ${d.size}`);
    }
}

function updateStatus(message) {
    const statusElement = document.getElementById('status-message');
    statusElement.textContent = message;
}
