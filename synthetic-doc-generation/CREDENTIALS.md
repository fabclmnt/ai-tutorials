# Credentials and Environment Setup

This project requires API credentials for OpenAI and YData SDK. The Makefile provides an easy way to manage these credentials and set up the environment.

## Quick Start

1. **Set up credentials** (choose one method):
   ```bash
   # Method 1: JSON format
   cp credentials.json.template credentials.json
   # Edit credentials.json with your actual API keys
   
   # Method 2: Environment file format
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

2. **Run the complete setup**:
   ```bash
   make quick-start
   ```

## Available Make Commands

Run `make help` to see all available commands:

```bash
make help
```

### Key Commands

- `make setup-env` - Load credentials and set environment variables
- `make check-credentials` - Verify that required credentials are set
- `make install-deps` - Install Python dependencies
- `make status` - Show current environment status

### Workflow Commands

- `make setup` - Complete setup (install deps + setup env + check credentials)
- `make quick-start` - Full workflow: setup + generate docs + run agent
- `make dev-setup` - Development setup without credentials check

## Credentials Format

### JSON Format (credentials.json)
```json
{
  "openai_api_key": "your-openai-api-key-here",
  "ydata_license_key": "your-ydata-license-key-here",
  "openai_model": "gpt-4o-mini"
}
```

### Environment File Format (.env)
```bash
OPENAI_API_KEY=your-openai-api-key-here
YDATA_LICENSE_KEY=your-ydata-license-key-here
OPENAI_MODEL=gpt-4o-mini
```

## Required Credentials

1. **OpenAI API Key**: Required for AI agent functionality
   - Get from: https://platform.openai.com/api-keys
   - Used for: AI agent responses and document analysis

2. **YData License Key**: Required for synthetic document generation
   - Get from: https://ydata.ai/
   - Used for: Generating synthetic invoices and bank statements

## Environment Variables

The Makefile automatically sets these environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key
- `YDATA_LICENSE_KEY` - Your YData SDK license key  
- `OPENAI_MODEL` - OpenAI model to use (defaults to "gpt-4o-mini")

## Security Notes

- **Never commit credentials files** - They are automatically ignored by git
- **Use templates** - Copy from `.env.example` or `credentials.json.template`
- **Keep credentials secure** - Store them safely and don't share them

## Troubleshooting

### Missing Credentials Error
```bash
make check-credentials
```
This will show which credentials are missing.

### Environment Not Set
```bash
make status
```
This shows the current environment status and file locations.