import re


def text_to_html_paragraphs(text):
    # First, replace multiple newlines with a single newline,
    # so you don't get empty paragraphs
    text = re.sub(r'\n\s*\n', '\n', text)

    # Split the text into lines
    lines = text.split('\n')

    # Wrap each line in a <p> tag and join them
    return ''.join(f'<p>{line.strip()}</p>\n' for line in lines)


if __name__ == "__main__":
    text = """His this 

    is 

    a sample

    String"""

    html_paragraphs = text_to_html_paragraphs(text)
    print(html_paragraphs)
