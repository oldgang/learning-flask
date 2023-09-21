import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from selenium.webdriver.chrome.options import Options
from .helperFunctions import fetch_wave, sign_in_wave, driver_init

def create_plot_url(freq5G, node, channels):
    x = range(4700, 6300)
    y = [0 if num not in freq5G else 1 for num in x]
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(15, 2))
    # Define custom colors with opacity
    bar_color = (0.2, 0.4, 0.6, 0.8)  # RGBA format
    # Plot the bars with custom colors and opacity
    ax.bar(x, y, color=bar_color, width=1)
    # Customize the plot
    ax.set_xlabel('Frequency [MHz]', fontsize=12)
    ax.set_ylabel('Occupancy', fontsize=12)
    ax.set_title(f'Occupied 5 GHz Frequency on {node}', fontsize=14, fontweight='bold')
    # Adjust tick labels and spacing
    ax.set_xticks(range(4700, 6300, 100))
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Free', 'Occupied'], fontsize=10)
    # Add grid lines
    ax.grid(axis='y', linestyle='--')
    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Set the background color of the plot
    ax.set_facecolor('#f5f5f5')
    # Join channels that are overlapping
    channels.sort()
    i = 0
    while i < len(channels)-1:
        start1, end1 = channels[i].split('-')
        start2, end2 = channels[i+1].split('-')
        if int(start2) <= int(end1):
            channels[i] = f"{start1}-{end2}"
            channels.pop(i+1)
        else:
            i += 1
    # Add channel annotations
    for channel in channels:
        start, end = channel.split('-')
        start = int(start)
        end = int(end)
        textPosition = end - (end - start)/2 - 7
        ax.annotate(f"{start}-{end}", xy=(textPosition, 0.13), xytext=(textPosition, 0.13), rotation=90)
    # Adjust plot margins
    plt.margins(x=0)
    # Show the plot
    plt.tight_layout()
    # Save the plot to a file-like object
    image = io.BytesIO()
    plt.savefig(image, format='png')
    image.seek(0)
    plot_url = base64.b64encode(image.getvalue()).decode()
    return plot_url

# NODE SELECTION
def get_plot_urls(nodes):

    # WEBDRIVER INIT
    driver = driver_init()

    # FETCH DATA
    nodeFreqDictionary = dict()
    driver = sign_in_wave(driver) # sign in to page
    for node in nodes:
        driver, freq5G, channels = fetch_wave(driver, node)
        if freq5G != []:
            nodeFreqDictionary[node] = create_plot_url(freq5G, node, channels)
    driver.quit()

    return nodeFreqDictionary

if __name__ == "__main__":
    pass