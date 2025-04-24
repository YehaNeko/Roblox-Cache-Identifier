# Binary Header Ident

This project helps identify binary file headers. To get started, follow the instructions below to clone the repository and set up the project using [uv](https://github.com/astral-sh/uv).

## 1. Clone the Repository

Open your terminal and run:

```sh
git clone https://github.com/YehaNeko/Roblox-Cache-Identifier
cd Binary-Header-Ident
```

## 2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

Follow the instructions in the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) to install `uv`.

## 3. Sync the Project Dependencies

To install all dependencies specified in `pyproject.toml`, run:

```sh
uv sync
```

This will create a virtual environment (if one does not exist) and install all required packages.

## 4. Activate the Virtual Environment (if needed)

If `uv` created a virtual environment, activate it:

- **Windows:**

  ```sh
  .venv\Scripts\activate
  ```

- **macOS/Linux:**

  ```sh
  source .venv/bin/activate
  ```

## 5. Run the Project

You can now run the project as needed, for example:

```sh
uv run ./src/main.py
```

---

For more information, see the documentation for [uv](https://github.com/astral-sh/uv) or open an issue if you have any problems.
