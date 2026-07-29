# Codenames GloVe

## Table of Contents

- [About The Project](#1-about-the-project)
- [Overview / Features](#2-overview--features)
- [Prerequisites & Requirements](#3-prerequisites--requirements)
- [Getting Started / Installation](#4-getting-started--installation)
- [Usage / Quickstart](#5-usage--quickstart)
- [Configuration](#6-configuration)
- [Authors](#7-authors)

## 1. About The Project

Modern Natural Language Processing (NLP) models have achieved proficiency in sentence analysis and text generation. However, their ability to understand ambiguous semantic relationships between words remains a challenge. Our research project focuses on this area—our goal is to test and evaluate the ability of artificial intelligence to navigate conceptual spaces.

The main research problem is the difference in how humans and machines understand meanings. Natural communication relies on so-called common ground—a subconscious set of shared experiences and intuition. When humans seek associations, they can model the interlocutor's state of mind in order to reach mutual understanding.

Artificial intelligence, operating on static language representations, lacks real-world experience. Machine understanding of concepts relies on a mathematical approximation of calculating the probability of given words appearing next to each other in large knowledge repositories, such as Wikipedia articles. The clash between these two ways of interpreting meaning often leads to cognitive dissonance, which forms part of our analysis.

To study these phenomena in a repeatable manner, the scope of our project also included creating dedicated testing software for AI model evaluation. We designed and implemented an automated analytical environment equipped with a data collection system. The software we built allows running thousands of simulations, logging the history of decisions made by the model (along with their mathematical rationale), and gathering data for subsequent analysis.

### Research Environment

#### Classic Gameplay
In its original form, *Codenames* is a complex party game based on competition between two teams. Its most important mechanism is asymmetrical communication: in each team, one person acts as the Spymaster, who sees the hidden board layout and tries to guide their Guessers to the correct words among the 25 cards on the table.

On their turn, the Spymaster may give only a single word as a clue and a number specifying how many words on the board connect with that clue. Furthermore, this clue cannot be any of the words currently visible on the table.

#### Our Environment Deconstruction
For the purposes of this project, we decided to deconstruct the original game rules. The board in our implementation consists of a grid of 25 unique words, which we divided into three classes:
- **TARGET**: 9 cards that the algorithm must identify.
- **NEUTRAL**: 15 cards whose selection ends the turn, delaying victory.
- **ASSASSIN**: 1 card whose selection results in an immediate defeat.

The algorithm's goal in our environment is to identify all 9 targets in the minimum number of turns while avoiding selecting the Assassin.

#### Why Did We Remove Competition?
The key change was removing the second opposing team. This allowed us to test artificial intelligence strictly in terms of navigating through semantic space. By eliminating the opposing team, we remove the need to analyze the opponent's moves to gain an advantage.


## 2. Overview / Features

This repository includes:

- A playable Codenames game engine with spymaster/guesser logic and board generation
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
- scripts for analysis and evaluation in `scripts/`
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

This opens the main menu which offers the following functionality:

- generating a dataset of boards
- playing a single game
- running batch evaluation over many boards
- viewing saved replays

#### Play a single game in GUI

<img width="800" height="405" alt="output_play" src="https://github.com/user-attachments/assets/c2dcea82-f9ba-429a-9dc6-a99ad41fc862" />

#### Running a batch evaluation

<img width="800" height="405" alt="output_run_batch" src="https://github.com/user-attachments/assets/23b27a7d-47be-4d50-b99a-819d3c1e3a4b" />

#### Watching a replay

<img width="800" height="405" alt="output_replay" src="https://github.com/user-attachments/assets/28b6b31c-d77b-4b69-8577-f3590f0df430" />


### Play from the terminal

```bash
python main.py
```

The terminal app offers a menu with options for:

- generating a dataset of boards
- playing a single game
- running batch evaluation over many boards
- viewing saved replays

#### Generate a board dataset

From the main menu in `main.py`, choose the dataset generation option to create a board set under `data/`.

#### Run batch evaluation

The batch evaluation flow is built into `main.py`. You can run many games against the prepared agents and save results to `stats/`.

### Replay statistics and plots

Extract which target words the model attempted to link with a clue:
```bash
python scripts/extract_clues.py <batch-directory-name>
```

Generate replay statistics:

```bash
python scripts/analyze_replays.py <batch-directory-name>
```

Generate more detailed analysis and plots:

```bash
python scripts/advanced_analytics.py <batch-directory-name>
```

Replace `<batch-directory-name>` with a directory inside `stats/`, such as `normal` or `target1`.

## 6. Configuration

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

`glove_spymaster` tuning parameters for clue selection and scoring

- `type`: selects the spymaster behavior (There are 2 types avaiable: historic - the bot uses `historic` knowledge to select clues and `normal` - which uses no extra information)
(default: `normal`)
- `number_targets`: the number of targets the bot will target when selecting the clue, when set to `0` the bot will check every possible combination and select the one with the highest score (default: `0`)
- `time limit`: if `number_targets` is set to 0 the agent will run a timer and stop early returning the best clue found so far (default: `10.0`)

 `game` controls settings of the game runner

- `game.record_table`: controls whether board table data is recorded

You can adjust these values to change how the AI behaves during play and evaluation.

## 7. Authors

- [@michaelgrab](https://github.com/michaelgrab)
- [@irunislaw](https://github.com/irunislaw)
- [@MichalKazm](https://github.com/MichalKazm)

If you want to contribute, feel free to open an issue or submit a pull request.
