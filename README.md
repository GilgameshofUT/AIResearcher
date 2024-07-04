# AIResearcher
This is a very simple RAG/AI system I put together. All the ones I was seeing were overly complicated. It uses Chromadb and Gemini 1.5, both of which are free at low usage levels. the intent here is to be dead simple but sophisticated enough you can import hundreds of books on a subject and get good answers from AI. In future I may try other AI tools. It would not be hard to change it out for Ollama, Claude, GPT-4o or whatever.

# Installation
1. create a new virtual environment
   > conda create -n "researcher" python=3.11
   
   > conda activate researcher
2. Get an API key from Google
    > https://aistudio.google.com/app/apikey
3. Install Chromadb
    > pip install chromadb
4. Install dependancies
    > pip install -r requirements.txt
5. Collect source material

    The script will import PDF, epub, txt, markdown. This is all text based so it won't work with photos, graphs, etc. You should organize the books to a single subject for best results. You should also limit it to quality sources you want providing answers. If you have two wildly divergent viewpoints you may do better to make two collections so you know which viewpoint you are getting. 
6. Import source material to Chroma

    Edit the script to reflect the location of your source material, your collection name and your database location. For large books it may take a while to import but it should handle dozens or even hundreds of books on ordinary hardware. Embedding as all handled by Chroma making it very easy.
   > python3 importall.py
7. Set up config script

     Edit the config script to match your setup. I recommend using multiple collections for multiple subjects. Just make new config scripts for each collection/subject. I like to direct the output to a markdown file in Obsidian but any text reader will work, though a markdown reader will be nicer.  
8. Research
   > python3 research-main.py config_subject.py

   You will type your questions into the terminal and you can either read the response there or much nicer is to just follow the output in Obsidian. I use the plugin Admonition to make some nicer callout formatting. I have it set currently to output sources into the markdown.

