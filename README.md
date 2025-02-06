# Nimba SMS CLI

Official command-line interface for Nimba SMS API. Manage your SMS, extensions, contacts, and more directly from your terminal.
[![Build and Release](https://github.com/nimbasms/nimbasms-cli/actions/workflows/release.yml/badge.svg)](https://github.com/nimbasms/nimbasms-cli/actions/workflows/release.yml)

## Installation

### Linux/macOS
```bash
curl -sSL https://raw.githubusercontent.com/nimbasms/nimbasms-cli/main/scripts/install.sh | bash
```

### Windows
Run PowerShell as administrator and execute:
```powershell
iwr -useb https://raw.githubusercontent.com/nimbasms/nimbasms-cli/main/scripts/install.ps1 | iex
```

### Manual Installation
You can also download the binary directly from the [releases page](https://github.com/nimbasms/nimbasms-cli/releases/latest).

Available binaries:
- `nimbasms-linux-amd64` - Linux (64-bit)
- `nimbasms-linux-arm64` - Linux ARM (64-bit)
- `nimbasms-darwin-amd64` - macOS (Intel)
- `nimbasms-darwin-arm64` - macOS (Apple Silicon)
- `nimbasms-windows-amd64.exe` - Windows (64-bit)

## Managing Extensions with Nimba SMS CLI

The CLI provides comprehensive tools for building and managing extensions. Here's how to use them:

### Basic Extension Commands

```bash
# List all extensions
nimbasms extensions list

# View extension details
nimbasms extensions get EXTENSION_ID

# Create a new extension
nimbasms extensions create \
  --name "My Extension" \
  --description "A powerful extension for Nimba SMS" \
  --base-api-url "https://api.myextension.com" \
  --auth-type api_key

# Update an extension
nimbasms extensions update EXTENSION_ID \
  --name "Updated Name" \
  --description "Updated description"
```

### Extension Development Workflow

1. **Create Extension**
   ```bash
   nimbasms extensions create \
     --name "My Extension" \
     --description "Extension description" \
     --base-api-url "https://api.myextension.com" \
     --auth-type api_key \
     --docs-url "https://docs.myextension.com"
   ```

2. **Add Actions**
   ```bash
   # Add an action to your extension
   nimbasms extensions EXTENSION_ID actions add \
     --name "send_message" \
     --method POST \
     --endpoint "/messages" \
     --description "Send a message through the extension"
   ```

3. **Configure OAuth (if needed)**
   ```bash
   nimbasms extensions update EXTENSION_ID \
     --auth-type oauth2 \
     --oauth2-config '{
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "authorization_url": "https://auth.myext.com/authorize",
       "token_url": "https://auth.myext.com/token"
     }'
   ```

4. **Upload Logo**
   ```bash
   nimbasms extensions upload-logo EXTENSION_ID path/to/logo.png
   ```

5. **Publish Extension**
   ```bash
   nimbasms extensions publish EXTENSION_ID
   ```

### Managing Extension Actions

```bash
# List all actions
nimbasms extensions EXTENSION_ID actions list

# Get action details
nimbasms extensions EXTENSION_ID actions get ACTION_ID

# Update an action
nimbasms extensions EXTENSION_ID actions update ACTION_ID \
  --name "updated_action" \
  --description "Updated description"

# Delete an action
nimbasms extensions EXTENSION_ID actions delete ACTION_ID
```

### Extension Plans

```bash
# Add a pricing plan
nimbasms extensions EXTENSION_ID plans add \
  --name "Basic" \
  --price "10000" \
  --billing-period monthly \
  --features '{"messages": 1000, "premium_support": false}'

# List pricing plans
nimbasms extensions EXTENSION_ID plans list
```

## Contributing

We welcome contributions to the Nimba SMS CLI! Here's how you can help:

### Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/nimbasms/nimbasms-cli.git
   cd nimbasms-cli
   ```

2. **Install Dependencies**
   ```bash
   make install
   ```

3. **Run Tests**
   ```bash
   make test
   ```

4. **Check Code Style**
   ```bash
   make lint
   ```

### Making Changes

1. **Create a New Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow PEP 8 style guide
   - Add tests for new features
   - Update documentation as needed

3. **Verify Your Changes**
   ```bash
   make verify
   make test
   make lint
   ```

4. **Create a Release (for maintainers)**
   ```bash
   # For bug fixes
   make release-patch

   # For new features
   make release-minor

   # For breaking changes
   make release-major
   ```

### Pull Request Guidelines

1. **Before Submitting**
   - Ensure all tests pass
   - Update documentation if needed
   - Add tests for new features
   - Follow code style guidelines

2. **Pull Request Process**
   - Create a descriptive PR title
   - Fill out the PR template
   - Reference any related issues
   - Update CHANGELOG.md if applicable

### Code Style Guidelines

- Use type hints
- Keep functions focused and small
- Write descriptive docstrings
- Follow PEP 8 guidelines
- Use meaningful variable names

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
poetry run pytest tests/test_commands_extensions.py

# Run with coverage report
poetry run pytest --cov=src tests/
```

### Documentation

When adding new features, please:
1. Update the README.md if needed
2. Add docstrings to new functions/classes
3. Update the command help text
4. Add examples to the documentation

For more information, technical@nimbasms.com.