const API_BASE = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const generateBtn = document.getElementById('generate-btn');
    const debugModeToggle = document.getElementById('debug-mode');
    
    const uploadSection = document.getElementById('upload-section');
    const processingSection = document.getElementById('processing-section');
    const resultsSection = document.getElementById('results-section');
    
    const originalImg = document.getElementById('original-img');
    const resultImg = document.getElementById('result-img');
    const downloadBtn = document.getElementById('download-btn');
    const statusText = document.getElementById('status-text');
    
    const standardResults = document.getElementById('standard-results');
    const debugResults = document.getElementById('debug-results');
    
    const resetBtn = document.getElementById('reset-btn');
    
    let selectedFile = null;

    // File Selection Handlers
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    function handleFileSelect(file) {
        if (!file.type.match('image.*')) {
            alert('Please select an image file (JPEG, PNG, WebP)');
            return;
        }
        selectedFile = file;
        dropZone.querySelector('p').textContent = file.name;
        dropZone.classList.add('has-file');
        generateBtn.disabled = false;
        
        // Setup local preview for original image
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImg.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    // Generate Button Handler
    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        
        const isDebug = debugModeToggle.checked;
        const endpoint = isDebug ? '/api/v1/ghost-mannequin/debug' : '/api/v1/ghost-mannequin';
        
        // UI State Update
        uploadSection.classList.add('hidden');
        processingSection.classList.remove('hidden');
        
        const formData = new FormData();
        formData.append('image', selectedFile);
        
        try {
            statusText.textContent = 'Processing Garment...';
            
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Unknown processing error');
            }
            
            displayResults(data, isDebug);
            
        } catch (error) {
            alert(`Error: ${error.message}`);
            uploadSection.classList.remove('hidden');
            processingSection.classList.add('hidden');
        }
    });
    
    function getFullUrl(path) {
        if (!path) return '';
        if (path.startsWith('http')) return path;
        return `${API_BASE}${path}`;
    }

    function displayResults(data, isDebug) {
        processingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Populate Metadata
        document.getElementById('meta-type').textContent = data.garment_type || 'Unknown';
        document.getElementById('meta-time').textContent = data.processing_time_ms || 0;
        document.getElementById('meta-version').textContent = data.pipeline_version || 'N/A';
        
        // Warnings
        const warningsDiv = document.getElementById('meta-warnings');
        if (data.warnings && data.warnings.length > 0) {
            warningsDiv.innerHTML = data.warnings.map(w => `<p>⚠️ ${w}</p>`).join('');
            warningsDiv.classList.remove('hidden');
        } else {
            warningsDiv.classList.add('hidden');
        }

        if (isDebug && data.stages) {
            standardResults.classList.add('hidden');
            debugResults.classList.remove('hidden');
            debugResults.innerHTML = ''; // clear
            
            Object.keys(data.stages).sort().forEach(stageName => {
                const url = getFullUrl(data.stages[stageName]);
                const card = document.createElement('div');
                card.className = 'image-card';
                card.innerHTML = `
                    <h3>${stageName.replace(/_/g, ' ')}</h3>
                    <div class="img-container">
                        <img src="${url}" alt="${stageName}">
                    </div>
                    <a href="${url}" download="${stageName}.png" class="secondary-btn" style="padding: 0.25rem 0.5rem; margin-top: 0.5rem;">Save</a>
                `;
                debugResults.appendChild(card);
            });
            
        } else {
            debugResults.classList.add('hidden');
            standardResults.classList.remove('hidden');
            
            const finalUrl = getFullUrl(data.output_url);
            resultImg.src = finalUrl;
            downloadBtn.href = finalUrl;
        }
    }
    
    resetBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        dropZone.classList.remove('has-file');
        dropZone.querySelector('p').textContent = 'Drag & Drop your garment image here';
        generateBtn.disabled = true;
        
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
    });
});
