// Keep input value preserved
let currentPrompt = '';

document.getElementById('prompt-input').addEventListener('input', function(e) {
    currentPrompt = e.target.value;
    document.getElementById('char-count').textContent = 
        `${e.target.value.length}/1000`;
});

// Add auto-scroll to results after analysis
function scrollToResults() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}

async function analyzePrompt() {
    const analyzeBtn = document.querySelector('[onclick="analyzePrompt()"]'); // Moved up
    if (!currentPrompt) {
        alert('Kérjük először írj be egy promptot!');
        return;
    }

    try {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Elemzés folyamatban...';
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes timeout
        
        const response = await fetch('http://localhost:5001/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prompt: currentPrompt }),
            credentials: 'same-origin',  // Important for CORS
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        
        const data = await response.json();  // Parse first
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        document.getElementById('suggestions').textContent = data.analysis;
        
    } catch (error) {
        console.error('Error:', error);
        if (error.name === 'AbortError') {
            alert('Az elemzés túl sokáig tart. Kérjük próbáld újra rövidesen!');
        } else {
            alert('Elemzési hiba: ' + error.message);
        }
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Elemzés';
    }
}

async function optimizePrompt() {
    const optimizeBtn = document.querySelector('[onclick="optimizePrompt()"]');
    const optimizedPanel = document.getElementById('optimized-prompt');
    
    try {
        optimizeBtn.disabled = true;
        optimizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Optimalizálás...';
        optimizedPanel.textContent = ''; // Clear previous content
        
        const response = await fetch('http://localhost:5001/optimize', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prompt: currentPrompt })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Optimization failed');
        }
        
        optimizedPanel.textContent = data.optimized;
        document.getElementById('optimized-panel').classList.add('active'); // Ensure panel is visible
        
    } catch (error) {
        console.error('Optimization Error:', error);
        optimizedPanel.textContent = `Error: ${error.message}`;
        alert('Optimalizálási hiba: ' + error.message);
    } finally {
        optimizeBtn.disabled = false;
        optimizeBtn.innerHTML = '<i class="fas fa-magic"></i> Optimalizálás';
        scrollToResults();
    }
}
