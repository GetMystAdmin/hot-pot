# HTML Template Extractor

This script processes HTML files to identify and extract repeatable sections, making them into templates using OpenAI's Assistant API.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone this repository or download the script recursive
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup

1. Create a `.env` file in the same directory as the script with the following content:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=your_assistant_id_here
LANGFLOW_TOKEN=
ASTRA_DB_APPLICATION_TOKEN=
```

2. Replace the placeholders:
   - `your_openai_api_key_here`: Your OpenAI API key
   - `your_assistant_id_here`: The ID of your OpenAI Assistant configured for HTML processing

## Usage

Run the script from the command line:
```bash
python browser.py
```

The script will:
1. Extract the body content from the input HTML file
2. Process it with the OpenAI Assistant
3. Identify repeatable sections
4. Create a new file called `example-fixed.html` with the templated version

## Output

The script generates:
- `example-fixed.html`: The processed HTML file with template sections marked
- Console output showing the processing status and location of the fixed file

## Error Handling

The script handles various errors including:
- Missing input file
- Invalid HTML content
- Encoding issues
- OpenAI API errors

Error messages will be printed to stderr with appropriate exit codes.

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)
