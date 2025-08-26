// Interactive Detail Panel for DataMapPlot
// This creates a slide-out panel that shows detailed information when points are clicked

// Create styles for the detail panel
const style = document.createElement('style');
style.textContent = `
    /* Main detail panel */
    #detail-panel {
        position: fixed;
        top: 0;
        right: -420px;
        width: 420px;
        height: 100vh;
        background: white;
        box-shadow: -2px 0 10px rgba(0,0,0,0.15);
        transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow-y: auto;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }
    
    #detail-panel.active {
        right: 0;
    }
    
    /* Panel header */
    #detail-panel-header {
        position: sticky;
        top: 0;
        background: white;
        padding: 20px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1;
    }
    
    #detail-panel-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
    }
    
    /* Close button */
    #detail-panel-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6b7280;
        padding: 4px;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    
    #detail-panel-close:hover {
        background: #f3f4f6;
        color: #1f2937;
    }
    
    /* Panel content */
    #detail-panel-content {
        padding: 20px;
    }
    
    /* Detail title */
    .detail-title {
        font-size: 20px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 20px;
        line-height: 1.4;
        word-wrap: break-word;
    }
    
    /* Metadata container */
    .detail-metadata {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    /* Individual sections */
    .detail-section {
        padding: 12px;
        background: #f9fafb;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .detail-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    
    .detail-value {
        font-size: 14px;
        color: #374151;
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Links styling */
    .detail-value a {
        color: #2563eb;
        text-decoration: none;
        word-break: break-all;
    }
    
    .detail-value a:hover {
        text-decoration: underline;
        color: #1d4ed8;
    }
    
    /* Cluster info styling */
    .detail-value div {
        padding: 2px 0;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        #detail-panel {
            width: 100%;
            right: -100%;
        }
    }
    
    /* Dark mode support (if parent has dark class) */
    .dark #detail-panel {
        background: #1f2937;
        color: #f9fafb;
    }
    
    .dark #detail-panel-header {
        background: #1f2937;
        border-bottom-color: #374151;
    }
    
    .dark #detail-panel-header h3 {
        color: #f9fafb;
    }
    
    .dark #detail-panel-close {
        color: #9ca3af;
    }
    
    .dark #detail-panel-close:hover {
        background: #374151;
        color: #f9fafb;
    }
    
    .dark .detail-title {
        color: #f9fafb;
    }
    
    .dark .detail-section {
        background: #111827;
        border-color: #374151;
    }
    
    .dark .detail-label {
        color: #9ca3af;
    }
    
    .dark .detail-value {
        color: #e5e7eb;
    }
`;
document.head.appendChild(style);

// Create the detail panel element
const detailPanel = document.createElement('div');
detailPanel.id = 'detail-panel';
detailPanel.innerHTML = `
    <div id="detail-panel-header">
        <h3>Details</h3>
        <button id="detail-panel-close" aria-label="Close panel" title="Close (Esc)">×</button>
    </div>
    <div id="detail-panel-content"></div>
`;
document.body.appendChild(detailPanel);

// Panel interaction handlers
document.getElementById('detail-panel-close').addEventListener('click', () => {
    detailPanel.classList.remove('active');
});

// Close on Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && detailPanel.classList.contains('active')) {
        detailPanel.classList.remove('active');
    }
});

// Close when clicking outside the panel (but not on data points)
document.addEventListener('click', (event) => {
    if (!detailPanel.contains(event.target) && 
        !event.target.closest('circle') && 
        !event.target.closest('path') &&
        !event.target.closest('canvas')) {
        detailPanel.classList.remove('active');
    }
});

// Prevent right-click context menu on the visualization
document.addEventListener('contextmenu', (event) => {
    if (event.target.closest('canvas')) {
        event.preventDefault();
        return false;
    }
});

// Basic showPointDetails function (will be overridden by main.py)
window.showPointDetails = function(pointData, pointIndex) {
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-panel-content');
    
    // Simple display for basic hover data
    let html = '<div class="detail-metadata">';
    
    if (typeof pointData === 'string') {
        html += `
            <div class="detail-section">
                <div class="detail-value">${pointData}</div>
            </div>
        `;
    } else {
        html += `
            <div class="detail-section">
                <div class="detail-value">Point ${pointIndex + 1}</div>
            </div>
        `;
    }
    
    html += '</div>';
    
    content.innerHTML = html;
    panel.classList.add('active');
};