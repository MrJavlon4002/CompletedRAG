def split_text(text, chunk_size=800, overlap_sentences=1, separators=['\n\n', '.\n', ':\n', '\n', '.']):
    """
    Split text into chunks of size less than chunk_size, ensuring that each chunk is meaningful and retains context.
    If a paragraph is smaller than chunk_size, it is treated as a single chunk.
    If a paragraph is larger than chunk_size, it is split into parts while preserving context.

    Args:
        text (str): The input text to split.
        chunk_size (int): The maximum size of each chunk.
        overlap_sentences (int): The number of overlapping sentences between successive chunks.
        separators (list): A list of separators to use for splitting.

    Returns:
        list: A list of text chunks.
    """
    chunks = []
    paragraphs = text.split('\n\n')

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            chunks.append(paragraph)
        else:
            sentences = []
            temp_text = paragraph
            while temp_text:
                best_split = -1
                # Initialize best_separator to avoid UnboundLocalError if no
                # separator is found in the current text chunk
                best_separator = ""
                for separator in separators:
                    if separator == "":
                        break

                    split_index = temp_text.find(separator)
                    if split_index > best_split:
                        best_split = split_index
                        best_separator = separator

                if best_split == -1 or best_separator == "":
                    sentences.append(temp_text)
                    break
                else:
                    sentence = temp_text[:best_split + len(best_separator)]
                    sentences.append(sentence)
                    temp_text = temp_text[best_split + len(best_separator):]

            current_chunk = []
            current_length = 0
            for i, sentence in enumerate(sentences):
                if current_length + len(sentence) <= chunk_size:
                    current_chunk.append(sentence)
                    current_length += len(sentence)
                else:
                    # Finalize the current chunk
                    if current_chunk:
                        chunks.append("".join(current_chunk))
                    
                    # Start a new chunk with overlapping sentences for context
                    current_chunk = sentences[max(0, i - overlap_sentences):i + 1]
                    current_length = sum(len(s) for s in current_chunk)

            # Add the last chunk
            if current_chunk:
                chunks.append("".join(current_chunk))

    return chunks