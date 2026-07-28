# Codenames GloVe

## Table of Contents

- [About The Project](#1-project-title-and-pitch)
- [Overview / Features](#2-overview--features)
- [Prerequisites & Requirements](#3-prerequisites--requirements)
- [Getting Started / Installation](#4-getting-started--installation)
- [Usage / Quickstart](#5-usage--quickstart)
- [Configuration](#6-configuration)
- [Authors](#7-authors)

## 1. About The Project

Codenames GloVe is a Python-based implementation of the party game Codenames with AI-driven agents powered by GloVe word embeddings. The project lets you play the game interactively, compare human and bot play, run batch evaluations over many boards, and analyze replays and statistics.

It is a strong fit for experimenting with word-association strategies, testing different spymaster/guesser behaviors, and exploring how semantic similarity can improve clue generation.


## 2. Overview / Features

This repository includes:

- A playable Codenames game engine with red/blue team logic and board generation
- Human and AI-controlled spymasters and guessers
- A GloVe-based bot that uses semantic similarity to choose clues and guesses
- A graphical user interface for playing and replaying games
- Batch evaluation tools for running many games automatically
- Replay logging and statistics generation for deeper analysis
- Configurable behavior through YAML settings

The project is organized around a modular architecture with separate components for:

- game logic in the `game/` package
- player strategies in `players/`
- GUI components in `GUI/`
- analysis and evaluation utilities in `utils/`
- datasets and stats in `data/` and `stats/`

## 3. Prerequisites & Requirements

### Software requirements

- Python 3.9+ (recommended: 3.10 or 3.11)
- pip
- A working Tkinter installation for the GUI

### Python dependencies

Install the required packages with:

```bash
pip install -r requirements.txt
```

The main dependencies are:

- `customtkinter` for the graphical interface
- `gensim` for embedding-based functionality
- `pandas`, `matplotlib`, `seaborn` for analysis and plotting
- `tqdm` for progress bars
- `PyYAML` for configuration loading

> On Debian/Ubuntu systems, you may need to install the Tkinter support package separately if the GUI fails to open.

## 4. Getting Started / Installation

1. Clone the repository:

```bash
git clone https://github.com/irunislaw/codenames-GloVe.git
cd codenames-GloVe
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Make sure the required data files are present under the `data/` directory.

## 5. Usage / Quickstart

### Launch the graphical interface

```bash
python gui_main.py
```

This opens the main menu and lets you start games, inspect replays, and interact with the interface.

### Play from the terminal

```bash
python main.py
```

The terminal app offers a menu with options for:

- generating a dataset of boards
- playing a single game
- running batch evaluation over many boards
- viewing saved replays

### Generate a board dataset

From the main menu in `main.py`, choose the dataset generation option to create a board set under `data/`.

### Run batch evaluation

The batch evaluation flow is built into `main.py`. You can run many games against the prepared agents and save results to `stats/`.

### Replay statistics and plots

Generate replay statistics:

```bash
python scripts/analyze_replays.py <batch-directory-name>
```

Generate more detailed analysis and plots:

```bash
python scripts/advanced_analytics.py <batch-directory-name>
```

Replace `<batch-directory-name>` with a directory inside `stats/`, such as `normal` or `target1`.

## 7. Configuration

The project uses a YAML configuration file at `config.yaml`.

Example configuration:

```yaml
glove_spymaster:
  type: normal
  weight_assassin: 1.0
  weight_neutral: 0.1
  word_bonus: 0.05
  number_targets: 1
  clue_validation: true
  time_limit: 10.0
game:
  record_table: false
```

Key settings include:

- `glove_spymaster.type`: selects the spymaster behavior
- `glove_spymaster.*`: tuning parameters for clue selection and scoring
- `game.record_table`: controls whether board table data is recorded

You can adjust these values to change how the AI behaves during play and evaluation.

## 8. Authors

- Project maintainer: irunislaw
- Contributors: see the repository history and pull requests for additional contributions

If you want to contribute, feel free to open an issue or submit a pull request.
