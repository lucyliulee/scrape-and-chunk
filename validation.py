import json
from collections import Counter

def validate_chunk(chunk, max_length=750):
    """
    Validate a single chunk.
    
    Args:
    chunk (str): The chunk to validate.
    max_length (int): Maximum allowed length for a chunk.

    Returns:
    dict: A dictionary with validation results.
    """
    lines = chunk.strip().split('\n\n')
    return {
        'length': len(chunk),
        'valid_length': len(chunk) <= max_length,
        'valid_header': len(lines) > 0 and lines[0].startswith('HEADER:'),
        'valid_content': len(lines) > 1 and lines[1].startswith('CONTENT:'),
        'num_lines': len(lines)
    }

def validate_chunks(chunks, max_length=750):
    """
    Validate all chunks.
    
    Args:
    chunks (list): List of chunks to validate.
    max_length (int): Maximum allowed length for a chunk.

    Returns:
    list: List of dictionaries with validation results.
    """
    return [validate_chunk(chunk, max_length) for chunk in chunks]

def display_metrics(validation_results):
    """
    Display metrics based on validation results.
    
    Args:
    validation_results (list): List of dictionaries with validation results.

    Returns:
    dict: A dictionary with summary metrics.
    """
    total_chunks = len(validation_results)
    metrics = Counter()
    length_distribution = Counter()

    for result in validation_results:
        metrics['valid_length'] += result['valid_length']
        metrics['valid_header'] += result['valid_header']
        metrics['valid_content'] += result['valid_content']
        length_distribution[result['length'] // 100 * 100] += 1

    print(f"Total chunks: {total_chunks}")
    print(f"Valid lengths: {metrics['valid_length']}/{total_chunks} ({metrics['valid_length']/total_chunks:.2%})")
    print(f"Valid headers: {metrics['valid_header']}/{total_chunks} ({metrics['valid_header']/total_chunks:.2%})")
    print(f"Valid contents: {metrics['valid_content']}/{total_chunks} ({metrics['valid_content']/total_chunks:.2%})")
    
    print("\nLength distribution:")
    for length, count in sorted(length_distribution.items()):
        print(f"{length}-{length+99} chars: {count} chunks")

    return dict(metrics)

if __name__ == '__main__':
    try:
        with open('notion_help_chunks.json', 'r') as f:
            chunks = json.load(f)
        
        validation_results = validate_chunks(chunks)
        metrics = display_metrics(validation_results)

        # Additional analysis
        print("\nDetailed analysis:")
        invalid_chunks = [i for i, result in enumerate(validation_results) if not all(result.values())]
        if invalid_chunks:
            print(f"Found {len(invalid_chunks)} invalid chunks at indices: {invalid_chunks}")
            print(f"Example of invalid chunk: {chunks[invalid_chunks[0]]}")
        else:
            print("All chunks are valid.")

    except FileNotFoundError:
        print("Error: File 'notion_help_chunks.json' not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in 'notion_help_chunks.json'.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")