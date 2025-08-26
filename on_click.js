// Click handler for DataMapPlot points
// This code is injected into the plot to handle point clicks
if (window.showPointDetails) {
    // Only respond to left clicks (button 0)
    if (!event || event.button === undefined || event.button === 0) {
        // Pass both hover text and point index to the detail panel
        window.showPointDetails(hoverData.hover_text[index], index);
    }
}