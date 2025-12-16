As someone who enjoys writing and worldbuilding, I'm used to taking notes and writing pages about characters, locations, and so on. Since LLMs have gone mainstream and building chatbots has become easier than ever, I decided to create a chatbot for my own notes.

So I came up with an idea that I thought was pleasant and practical.

In this article I used a set of three small, simplified notes that I made from my scribbles.

## The Foundation: Obsidian MD

For my notes, I've been using **Obsidian MD**. It's a well-known tool for note-taking, used by writers, D&D enthusiasts, and others who enjoy writing or keeping detailed notes like I do.

Obsidian MD has many features and supports plugins, and it also allows you to develop extensions. It supports themes as well, so you can create very nice-looking pages.

Obsidian MD projects are organized into **vaults**, which are essentially folders containing Markdown files along with additional configuration files such as themes, plugins, and CSS.

Since every note is a Markdown file, data ingestion simply boils down to processing those files.

## Building the Chatbot: The Stack

So how would the chatbot work? The idea was to leverage a **retrieval-augmented generation (RAG)** technique using the following stack:

- Python / uv  
- Docker / docker-compose  
- Ollama / llama3.2:3b / mxbai-embed-large  
- ChromaDB  

### How RAG Works

At its core, the RAG workflow boils down to the following steps:

1. When you ask a question, the query goes to RAG to retrieve the context (data) needed for the response.  
2. Because the context (data) is stored in a vector database, the database returns associated records that are similar to what has been requested.  
3. The retrieved records become the context that is passed to the LLM, which then tries to make sense of it and generate a response.

Pretty straightforward.

## Setting Up the Infrastructure

To start, I created a simple `docker-compose.yaml` where I defined the services and the network they would use to communicate with each other.

Since both Ollama and ChromaDB have official Docker support, I handled them first by adding them to `docker-compose`. Specifically for Ollama, I did two additional things:

- Leveraged my GPU (so that the RTX 5090 wouldn't feel bored)  
- Added a shell script to download the necessary models on startup  

When running, the Ollama service was available at `http://localhost:11434` and the ChromaDB service at `http://localhost:8000`. With that in place, I could start developing the RAG part.

## The Ingestion Pipeline

To develop the RAG pipeline, I used an excellent article as a foundation.

To make RAG work, I needed to ingest data and store it in the vector database—ChromaDB, in my case. To provide it with data, I mounted the repository with my notes directly and, just to be safe, set it to read-only mode.

I created a simple Dockerfile for the Python project that did only one thing: ingest data by running `main.py`.

Whenever I needed to update something, I just ran it again manually. This was the simplest and most straightforward approach for my case, considering that I tend to change the notes frequently and the scale of my notes is nowhere near millions of documents. I could freely remove the entire collection from ChromaDB anytime if needed.

### The Process

The ingestion process itself was simple:

- I iterated over my note folders and picked up Markdown files.  
- Each file was then processed section by section, subsection by subsection.  
- To create identifiers for them in the database, I generated a hash for each file path and then appended the chunk number.  
- Each index, the chunk itself, and some additional metadata were then added to the vector database collection.

For chunking, I decided not to reinvent the wheel and used the hierarchical chunking strategy from that article.

In this setup, the script reads the Markdown file and splits it by section (`#`) and subsection (`##`). I could always add additional nested layers—like `###`—if necessary.

## Adding the Frontend

With the data in the database, I could now add some frontend. To create a UI, I decided to go with **Gradio**.

Gradio is a UI framework commonly used when developing or experimenting with AI-based solutions, prototypes, and demos. It supports various components, from plots and dataframes to image galleries and 3D model rendering.

Out of the box, it provides a lot of components, and one of them is `ChatInterface`. To create a chatbot with Gradio, you just need to create an instance of `ChatInterface`, provide a chatting function, and launch Gradio.

For the chatting function, I used the one from the article mentioned above.

It looks nice. You can chat with it for a bit. At first glance, everything seems fine—impressive, even.

However, when you start asking certain questions, its limits become quite apparent.

In this case, it provided a response containing the direct statement from the notes, but it was unable to specify who exactly it was talking about, no matter how I asked. It also sometimes provided incorrect answers.

## The Realization

While these limits can be addressed by using more complex solutions (more advanced chunking, storing whole notes, leveraging metadata, etc.), they also made me realize something else: **my notes themselves were not clear enough.**

LLMs, vector databases, and RAG are just observers—readers. They ingest and process the data—the notes—I provide to them. Notes that I wrote myself, for myself.

When storing the data, the system does not care about the broader context—it just takes paragraphs and stores them as vectors in the database. The RAG pipeline does not care about the context either—it simply uses the database to find matching (or similar) records and then passes them to the LLM to generate a response. It relies entirely on what I've written, without knowing the bigger picture I have in mind.

### The Problem

For example, in the context of the query *"Who has white hair?"* the matching result was a subsection describing the appearance of Adapa in a paragraph. The retrieved text was exactly the same as the response.

While the answer was technically correct, it highlighted a problem: the paragraph itself did not mention the name **Adapa** anywhere. Essentially, the paragraph was missing its subject.

I realized this was actually a common issue in my notes. I had never thought of it as a problem before, because I was always aware of the subject of the note—I wrote them myself, after all.

So I decided to go through my notes and update such occurrences.

For example, instead of using a paragraph that implicitly referred to "him," I rewrote it to explicitly mention the character's name.

And so on.

## The Solution

These small improvements actually solved two problems.

- **First**, they added context to each subsection, meaning RAG now had access to that previously missing piece of information. It no longer referred to an unknown "he." It became clear who the text was about.  
- **Second**, they improved the notes themselves, because each description now had a clear subject—making it easier to understand for me or for anyone else reading that specific section.

Missing the subject is actually one of the common mistakes people make when writing notes—they silently drop the subject, assuming that readers will start from the very beginning or keep the subject in mind the whole time.

### Addressing Semantic Issues

I was also able to address certain semantic (and grammatical) issues in my notes. For example, in one of the paragraphs I had something like this:

> The catch here is that *their leader* does not mean anything in this paragraph.

While this might have been grammatically acceptable, it was semantically wrong, because it depended on some missing context that I was aware of, but RAG was not. In fact, it added a wrong assumption in the paragraph that Ashur took orders from some unknown group, which was what was implied in the paragraph but wasn't true in reality. I also found in other notes that sometimes the meaning of "they" or "their" is not mentioned anywhere near the section at all—maybe only once at the beginning of some other paragraph.

By addressing small issues like this, the notes become clearer; the sections and subsections stand more on their own.

So after addressing these issues, the quality of answers definitely improved. I started with the original question.

It returned the exact same sentence as in the note, but it was pretty clear that the context was there. So even if I asked a question from a different angle, it was able to answer it properly.

When asking a more complex question—something that was not mentioned anywhere and something that the system would not have been able to answer before—the original system would have answered like this.

Putting aside some incorrect assumptions in the response, the answer was correct in that it was indeed not mentioned explicitly anywhere that Ashur belonged to any group. However, now with fixed context, I got a much better answer. The chatbot clearly became smarter, and I did not even change the code.

## The Takeaway

Writing clear notes is important not only because someone else might read them or because they might become a source of data in the future, but also because it makes them better for you as well. In fact, by adding the missing context, I was able to simplify cases where I needed to copy-paste text between notes or post it somewhere else, since I already had a clearly stated subject. And grammar or semantic mistakes - well, there's no debate that fixing them helps in general.
This realization gave a slightly different flavor to the pleasant and practical idea I had when I started developing the chatbot.

## Code Repository

For this article, I've created a repository that contains the code.
