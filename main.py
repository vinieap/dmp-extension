"""
Interactive DataMapPlot - Add clickable detail panels to your data visualizations.

Simple usage:
    from interactive_datamapplot import create_interactive_plot
    import pandas as pd

    # Your data
    df = pd.DataFrame({
        'title': ['Item 1', 'Item 2', ...],
        'description': ['Details...', 'More details...', ...],
        'url': ['http://...', 'http://...', ...]
    })

    # Create plot
    plot = create_interactive_plot(
        data_map_2d,           # Your 2D coordinates from UMAP/t-SNE
        details_df=df,         # DataFrame with extra details
        hover_text=df['title'] # What shows on hover
    )

    plot.save("my_interactive_plot.html")
"""

from pathlib import Path

import datamapplot
import orjson
import pandas as pd


def create_interactive_plot(
    data_map,
    details_df=None,
    hover_text=None,
    label_layers=None,
    title="Interactive Data Map",
    **datamapplot_kwargs,
):
    """
    Create an interactive datamapplot with clickable points showing detailed information.

    Parameters
    ----------
    data_map : array-like, shape (n_samples, 2)
        2D coordinates for your data points (e.g., from UMAP or t-SNE)

    details_df : pandas.DataFrame, optional
        DataFrame containing detailed information for each point.
        Each row corresponds to a data point. All columns will be displayed
        in the detail panel when a point is clicked.

    hover_text : array-like, optional
        Text to show on hover. Keep this short (e.g., titles or names).
        If not provided, will use the first column of details_df.

    label_layers : list of arrays, optional
        Cluster labels for hierarchical labeling. Each array contains
        labels for all points at that hierarchy level.

    title : str, default="Interactive Data Map"
        Title for your visualization

    **datamapplot_kwargs : dict
        Additional arguments passed to datamapplot.create_interactive_plot()
        Common options:
        - enable_search=True : Add search functionality
        - enable_table_of_contents=True : Add table of contents
        - marker_size_array : Array of marker sizes
        - marker_color_array : Array of marker colors

    Returns
    -------
    plot : datamapplot plot object
        Use plot.save("filename.html") to save the interactive plot

    Examples
    --------
    Basic usage with a DataFrame:

    >>> df = pd.DataFrame({
    ...     'title': papers['title'],
    ...     'authors': papers['authors'],
    ...     'abstract': papers['abstract'],
    ...     'year': papers['year'],
    ...     'url': papers['url']
    ... })
    >>>
    >>> plot = create_interactive_plot(
    ...     embeddings_2d,
    ...     details_df=df,
    ...     hover_text=df['title'],
    ...     enable_search=True
    ... )
    >>> plot.save("papers.html")

    With clustering:

    >>> plot = create_interactive_plot(
    ...     embeddings_2d,
    ...     details_df=df,
    ...     label_layers=[clusters_level1, clusters_level2],
    ...     enable_table_of_contents=True
    ... )
    """
    # Handle label_layers argument
    if label_layers is None:
        label_layers = []
    elif not isinstance(label_layers, (list, tuple)):
        label_layers = [label_layers]

    # Prepare hover text
    if hover_text is None and details_df is not None:
        # Use first column as hover text if not specified
        hover_text = details_df.iloc[:, 0].astype(str).values

    # Convert DataFrame to the format expected by the JavaScript
    extra_data = []
    if details_df is not None:
        extra_data = details_df.reset_index().to_dict("records")
        # Ensure each record has an index
        for i, record in enumerate(extra_data):
            if "index" not in record:
                record["index"] = i

    # Add cluster information if provided
    if label_layers:
        num_points = (
            len(data_map) if hasattr(data_map, "__len__") else data_map.shape[0]
        )

        # Create or update extra_data with cluster info
        extra_data_dict = {d.get("index", i): d for i, d in enumerate(extra_data)}

        for i in range(num_points):
            if i not in extra_data_dict:
                extra_data_dict[i] = {"index": i}

            # Add cluster labels efficiently
            cluster_info = {
                f"Cluster Level {idx + 1}": str(layer[i])
                for idx, layer in enumerate(label_layers)
                if layer is not None
                and i < len(layer)
                and layer[i]
                and str(layer[i]) not in ["", "-1", "None", "null"]
            }

            if cluster_info:
                extra_data_dict[i]["_cluster_info"] = cluster_info

        extra_data = list(extra_data_dict.values())

    # Load JavaScript assets
    js_dir = Path(__file__).parent
    custom_js_path = js_dir / "custom_js.js"
    on_click_path = js_dir / "on_click.js"

    # Read base JavaScript
    with open(custom_js_path, "r") as f:
        custom_js_base = f.read()

    with open(on_click_path, "r") as f:
        on_click_template = f.read()

    # Serialize data efficiently with orjson
    extra_data_json = orjson.dumps(extra_data, option=orjson.OPT_NON_STR_KEYS).decode(
        "utf-8"
    )

    # Create the enhanced JavaScript
    enhanced_js = f"""
{custom_js_base}

// Inject the detailed data for all points
window.pointDetailsData = {extra_data_json};

// Override the showPointDetails function to use our enhanced data
window.showPointDetails = function(hoverText, pointIndex) {{
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-panel-content');
    
    // Get enhanced data for this point
    let detailData = null;
    if (window.pointDetailsData && pointIndex !== undefined) {{
        detailData = window.pointDetailsData.find(d => d.index === pointIndex);
    }}
    
    // Build content using array for performance
    const parts = [];
    
    // Add title
    const title = detailData?.title || detailData?.name || `Point #${{pointIndex + 1}}`;
    parts.push(`<div class="detail-title">${{title}}</div>`);
    parts.push('<div class="detail-metadata">');
    
    // Add cluster information if present
    if (detailData && detailData._cluster_info) {{
        parts.push('<div class="detail-section">');
        parts.push('<div class="detail-label">Clusters</div>');
        parts.push('<div class="detail-value">');
        for (const [level, label] of Object.entries(detailData._cluster_info)) {{
            parts.push(`<div>${{level}}: <strong>${{label}}</strong></div>`);
        }}
        parts.push('</div></div>');
    }}
    
    // Add all other fields
    if (detailData) {{
        const skipFields = ['index', 'title', 'name', '_cluster_info'];
        
        for (const [key, value] of Object.entries(detailData)) {{
            if (skipFields.includes(key) || value == null) continue;
            
            // Format field name
            const label = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
            
            // Format value
            let displayValue = value;
            if (Array.isArray(value)) {{
                displayValue = value.join(', ');
            }} else if (typeof value === 'object') {{
                displayValue = JSON.stringify(value, null, 2);
            }} else if (typeof value === 'string' && value.startsWith('http')) {{
                displayValue = `<a href="${{value}}" target="_blank" rel="noopener">${{value}}</a>`;
            }}
            
            parts.push(`
                <div class="detail-section">
                    <div class="detail-label">${{label}}</div>
                    <div class="detail-value">${{displayValue}}</div>
                </div>
            `);
        }}
    }}
    
    // Show basic hover info if no detail data
    if (!detailData) {{
        parts.push('<div class="detail-section">');
        parts.push('<div class="detail-value">');
        parts.push(hoverText || 'No details available');
        parts.push('</div></div>');
    }}
    
    parts.push('</div>');
    
    content.innerHTML = parts.join('');
    panel.classList.add('active');
}};
"""

    # Create the plot with all enhancements
    plot = datamapplot.create_interactive_plot(
        data_map,
        *label_layers,
        hover_text=hover_text,
        custom_js=enhanced_js,
        on_click=on_click_template,
        title=title,
        **datamapplot_kwargs,
    )

    return plot


# Convenience function for quick plotting
def plot_with_dataframe(data_map, df, title_column=None, **kwargs):
    """
    Convenience function to quickly create a plot from coordinates and a DataFrame.

    Parameters
    ----------
    data_map : array-like, shape (n_samples, 2)
        2D coordinates for your data points

    df : pandas.DataFrame
        DataFrame with details for each point

    title_column : str, optional
        Column name to use for hover text. If not specified,
        uses the first column.

    **kwargs : dict
        Additional arguments passed to create_interactive_plot()

    Returns
    -------
    plot : datamapplot plot object

    Example
    -------
    >>> plot = plot_with_dataframe(embeddings_2d, papers_df, title_column='title')
    >>> plot.save("papers.html")
    """
    hover_text = df[title_column] if title_column else df.iloc[:, 0]
    return create_interactive_plot(
        data_map, details_df=df, hover_text=hover_text, **kwargs
    )


if __name__ == "__main__":
    # Example usage
    import numpy as np

    # Create sample data
    n_points = 100
    data_2d = np.random.randn(n_points, 2) * 10

    # Create sample DataFrame with details
    sample_df = pd.DataFrame(
        {
            "title": [f"Item {i+1}" for i in range(n_points)],
            "description": [
                f"This is a detailed description for item {i+1}"
                for i in range(n_points)
            ],
            "category": np.random.choice(["A", "B", "C", "D"], n_points),
            "score": np.random.rand(n_points),
            "url": [f"https://example.com/item/{i+1}" for i in range(n_points)],
        }
    )

    # Create sample clusters
    clusters = np.random.randint(0, 5, n_points)

    # Create the interactive plot
    plot = create_interactive_plot(
        data_2d,
        details_df=sample_df,
        hover_text=sample_df["title"],
        label_layers=[clusters],
        title="Sample Interactive Plot",
        enable_search=True,
    )

    # Save the plot
    plot.save("sample_interactive_plot.html")
    print("Sample plot saved as 'sample_interactive_plot.html'")
