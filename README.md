# Multi-Agent Game Testing System - POC

A production-grade Proof of Concept (POC) for an automated, multi-agent game testing system specifically designed for 32-bit Windows environments. The system uses intelligent agents to explore, test, and validate web-based math and puzzle games through dynamic DOM analysis and heuristic learning.

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for exploration, strategy, execution, and validation
- **32-bit Windows Optimized**: Specifically configured for 32-bit Windows environments
- **Dynamic DOM Analysis**: Automatically discovers and analyzes game elements without hardcoding
- **Heuristic Learning**: Learns from testing patterns to improve future test strategies
- **Flexible URL Support**: Works with any web-based game through adaptive analysis
- **Comprehensive Reporting**: Generates JSON, HTML, and text reports with detailed insights
- **Production-Ready**: Robust error handling, logging, and configuration management

## 🏗️ Architecture

The system consists of five main components:

### 1. Core Modules
- **Browser Automation**: Selenium-based browser control optimized for 32-bit systems
- **DOM Analyzer**: Intelligent page structure analysis and element discovery
- **Heuristic Learning**: Pattern recognition and adaptive strategy optimization

### 2. Agents
- **Exploration Agent**: Discovers interactive elements and game structure
- **Strategy Agent**: Generates optimal testing strategies based on game type
- **Execution Agent**: Performs test actions and interactions
- **Validation Agent**: Verifies game behavior and detects anomalies

### 3. Orchestrator
Coordinates all agents and manages the testing workflow through five phases:
1. Exploration
2. Strategy Generation
3. Execution
4. Validation
5. Learning

## 📋 Requirements

- Python 3.8+
- Google Chrome browser (32-bit or 64-bit)
- Windows (optimized for 32-bit, but works on 64-bit)
- Internet connection for ChromeDriver auto-download

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/ALAN-PSUDO/Multi-Agent-Game-Tester-POC.git
cd Multi-Agent-Game-Tester-POC
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python main.py --help
```

## 💻 Usage

### Basic Usage

Test a single game:
```bash
python main.py --url "https://example.com/math-game"
```

### Advanced Usage

Test with custom configuration:
```bash
python main.py --url "https://example.com/game" --config custom_config.yaml
```

Test multiple games:
```bash
python main.py --url "https://game1.com" "https://game2.com" "https://game3.com"
```

Run in headless mode:
```bash
python main.py --url "https://example.com/game" --headless
```

Generate specific report format:
```bash
python main.py --url "https://example.com/game" --report-format html
```

## 📊 Configuration

Edit `config.yaml` to customize the system behavior:

```yaml
# Browser Settings
browser:
  type: "chrome"
  headless: false
  window_size: "1280x720"
  architecture: "32-bit"

# Agent Configuration
agents:
  exploration:
    enabled: true
    max_depth: 5
    timeout: 60
  
  strategy:
    enabled: true
    learning_rate: 0.1
    exploration_factor: 0.2
  
  execution:
    enabled: true
    max_retries: 3
    action_delay: 0.5
  
  validation:
    enabled: true
    screenshot_on_error: true

# Game Testing Configuration
game_testing:
  test_duration: 300
  max_interactions: 100

# Heuristic Learning
heuristics:
  enabled: true
  save_patterns: true
  min_confidence: 0.6
```

## 📈 Output

The system generates three types of reports:

### 1. JSON Report
Detailed machine-readable report with all test data
```
reports/game_test_report_YYYYMMDD_HHMMSS.json
```

### 2. Text Report
Human-readable summary report
```
reports/game_test_report_YYYYMMDD_HHMMSS.txt
```

### 3. HTML Report
Visual report with interactive elements
```
reports/game_test_report_YYYYMMDD_HHMMSS.html
```

## 🎮 Supported Game Types

The system automatically detects and adapts to:
- **Math Games**: Arithmetic, equation solving, number puzzles
- **Puzzle Games**: Logic puzzles, pattern matching, spatial reasoning
- **Canvas Games**: HTML5 canvas-based interactive games
- **Input-Based Games**: Form-based games and quizzes
- **Unknown Games**: Generic testing strategy for unrecognized types

## 🔧 System Components

### Browser Automation (`src/core/browser_automation.py`)
- WebDriver initialization and management
- 32-bit architecture detection and optimization
- Screenshot capture and page navigation

### DOM Analyzer (`src/core/dom_analyzer.py`)
- Interactive element discovery
- Game indicator detection
- Page structure analysis
- Canvas element identification

### Heuristic Learning (`src/core/heuristic_learning.py`)
- Pattern recognition from test results
- Game profile management
- Strategy recommendations
- Adaptive learning from feedback

### Agents (`src/agents/`)
Each agent is specialized for a specific task:
- **Base Agent**: Abstract base class with common functionality
- **Exploration Agent**: Element discovery and categorization
- **Strategy Agent**: Test strategy generation and adaptation
- **Execution Agent**: Action execution with retry logic
- **Validation Agent**: Result validation and anomaly detection

### Orchestrator (`src/orchestrator.py`)
Main coordinator that:
- Manages agent lifecycle
- Coordinates testing phases
- Generates comprehensive reports
- Handles errors and cleanup

## 🛡️ 32-bit Windows Optimization

Special considerations for 32-bit environments:
- Disabled GPU acceleration for stability
- Optimized memory usage
- No-sandbox mode for compatibility
- Reduced shared memory usage
- Auto-detection of system architecture

## 📊 Metrics

The system tracks:
- **Success Rate**: Percentage of successful test actions
- **Health Score**: Overall game functionality (0-100)
- **Elements Discovered**: Number of interactive elements found
- **Anomalies**: Issues detected during testing
- **Patterns Learned**: Accumulated heuristic patterns

## 🔬 Testing Phases

### Phase 1: Exploration
- Navigate to game URL
- Analyze DOM structure
- Discover interactive elements
- Identify game type
- Map interface components

### Phase 2: Strategy Generation
- Analyze exploration results
- Retrieve heuristic recommendations
- Generate testing strategy
- Create test sequence
- Prioritize actions

### Phase 3: Execution
- Execute test actions
- Interact with game elements
- Record results
- Handle errors with retries
- Capture screenshots

### Phase 4: Validation
- Validate execution results
- Check page state
- Detect anomalies
- Calculate health score
- Generate validation report

### Phase 5: Learning
- Extract patterns from results
- Update heuristic database
- Adapt strategies
- Save game profiles
- Improve future tests

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📝 License

This project is a Proof of Concept for educational and demonstration purposes.

## 🔍 Troubleshooting

### ChromeDriver Issues
If ChromeDriver fails to download automatically:
1. Download manually from https://chromedriver.chromium.org/
2. Set path in config.yaml: `browser.driver_path: "path/to/chromedriver.exe"`

### 32-bit Windows Issues
- Ensure Chrome browser is installed
- Disable antivirus temporarily if browser fails to start
- Run as administrator if permission issues occur

### Test Failures
- Check game URL is accessible
- Increase timeouts in config.yaml
- Enable headless: false to see browser interactions
- Check logs in `game_tester.log`

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for automated game testing**