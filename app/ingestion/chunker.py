from transformers import AutoTokenizer


class TextChunker:

    def __init__(
        self,
        model_name="BAAI/bge-small-en-v1.5",
        chunk_size=350,
        overlap=70
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer.model_max_length = 10**9

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_page(self, page_text, page_number, document_id):

        encoded = self.tokenizer(
            page_text,
            add_special_tokens=False,
            truncation=False,
            return_attention_mask=False
        )

        tokens = encoded["input_ids"]

        chunks = []

        start = 0
        chunk_number = 0

        step = self.chunk_size - self.overlap

        while start < len(tokens):

            end = start + self.chunk_size

            chunk_tokens = tokens[start:end]

            text = self.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True
            )

            chunks.append({
                "chunk_id": f"{document_id}_p{page_number}_c{chunk_number}",
                "document_id": document_id,
                "page": page_number,
                "chunk_number": chunk_number,
                "text": text,
                "token_count": len(chunk_tokens)
            })

            chunk_number += 1
            start += step

        return chunks