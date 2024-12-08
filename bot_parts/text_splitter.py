def split_text(text, chunk_size=500, overlap_chunks=0, separators=['\n\n', '.\n', ':\n', '\n', '.']):
    """
    Split text into chunks of size less than chunk_size, using separators, with optional overlapping.

    Args:
        text (str): The input text to split.
        chunk_size (int): The maximum size of each chunk.
        overlap_chunks (int): The number of overlapping characters between successive chunks.
        separators (list): A list of separators to use for splitting.

    Returns:
        list: A list of text chunks.
    """

    chunks = []

    while len(text) > 0:
        if len(text) <= chunk_size:
            chunks.append(text)
            break

        best_split = -1
        for separator in separators:
            if separator == "":
                break

            split_index = text.rfind(separator, 0, chunk_size)
            if split_index > best_split:
                best_split = split_index
                best_separator = separator

        if best_split == -1 or best_separator == "":
            chunk = text[:chunk_size]
            chunks.append(chunk)
            text = text[chunk_size - overlap_chunks:]
        else:
            chunk = text[:best_split + len(best_separator)]
            chunks.append(chunk)
            text = text[max(0, best_split + len(best_separator) - overlap_chunks):]

    return chunks
