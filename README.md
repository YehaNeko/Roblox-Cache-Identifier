# Binary Header Ident

This project helps identify headers of Roblox cache files.

## Development Environment

### Dependencies

- **Windows 10/11**
- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### 1. Clone the Repository

```sh
git clone https://github.com/YehaNeko/Roblox-Cache-Identifier.git
cd Roblox-Cache-Identifier
```

### 2. Sync the Project Dependencies

To install all dependencies specified in `pyproject.toml`, run:

```sh
uv sync
```

This will create a virtual environment (if one does not exist) and install all required packages.

### 3. Activate the Virtual Environment (if needed)

If `uv` created a virtual environment, activate it:

```sh
.venv\Scripts\activate
```

### 4. Run the Project

You can now run the project with:

```sh
uv run ./src/main.py
```
