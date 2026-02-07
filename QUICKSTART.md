# Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Clone the Repository
```bash
git clone https://github.com/ALAN-PSUDO/Multi-Agent-Game-Tester-POC.git
cd Multi-Agent-Game-Tester-POC
```

### Step 2: Install Dependencies

**On Windows:**
```bash
setup.bat
```

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Or manually:**
```bash
pip install -r requirements.txt
```

### Step 3: Run the Demo
```bash
python demo.py
```

This will show you the system architecture and capabilities without requiring a browser.

### Step 4: Test Your First Game

```bash
python main.py --url "https://www.mathplayground.com/ASB_Index.html"
```

The system will:
1. ✓ Open the game in Chrome
2. ✓ Analyze the page structure
3. ✓ Discover interactive elements
4. ✓ Generate a testing strategy
5. ✓ Execute test actions
6. ✓ Validate behavior
7. ✓ Generate reports

### Step 5: View Results

Reports are saved in the `reports/` directory:
- **HTML Report**: Open in browser for visual results
- **JSON Report**: Machine-readable detailed data
- **Text Report**: Human-readable summary

## Common Use Cases

### Testing a Math Game
```bash
python main.py --url "https://example.com/math-game" --report-format html
```

### Testing Multiple Games
```bash
python main.py --url \
  "https://game1.com" \
  "https://game2.com" \
  "https://game3.com"
```

### Running in Headless Mode (No Browser Window)
```bash
python main.py --url "https://example.com/game" --headless
```

### Using Custom Configuration
```bash
python main.py --url "https://example.com/game" --config config.example.yaml
```

## Configuration

Edit `config.yaml` to customize:

### Browser Settings
```yaml
browser:
  headless: false        # true = no browser window
  window_size: "1280x720"
  architecture: "32-bit" # Optimized for 32-bit Windows
```

### Agent Behavior
```yaml
agents:
  execution:
    max_retries: 3       # Retry failed actions
    action_delay: 0.5    # Seconds between actions
```

### Testing Parameters
```yaml
game_testing:
  test_duration: 300     # Maximum test time (seconds)
  max_interactions: 100  # Maximum actions to perform
```

## Troubleshooting

### "ChromeDriver not found"
The system auto-downloads ChromeDriver. If it fails:
1. Download manually from https://chromedriver.chromium.org/
2. Set path in config.yaml: `browser.driver_path: "path/to/chromedriver.exe"`

### "Module not found" errors
Install dependencies:
```bash
pip install -r requirements.txt
```

### Browser doesn't open
- Ensure Chrome is installed
- Try headless mode: `--headless`
- Check antivirus isn't blocking

### Tests are failing
- Verify game URL is accessible
- Increase timeouts in config.yaml
- Check logs: `game_tester.log`

## Next Steps

1. **Read Documentation**
   - [README.md](README.md) - Full documentation
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design

2. **Customize Configuration**
   - Copy `config.example.yaml` for templates
   - Adjust for your specific games

3. **Review Reports**
   - HTML reports show visual results
   - JSON reports for automation
   - Text reports for quick review

4. **Learn from Heuristics**
   - System learns from each test
   - Patterns saved in `heuristics.json`
   - Improves strategies over time

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review logs in `game_tester.log`

## Key Features

✓ **32-bit Windows Optimized** - Works on legacy systems
✓ **Dynamic DOM Analysis** - No hardcoding required
✓ **Multi-Agent Architecture** - Specialized agents for each task
✓ **Heuristic Learning** - Improves with each test
✓ **Comprehensive Reports** - JSON, HTML, and Text formats
✓ **Batch Testing** - Test multiple games at once
✓ **Production Ready** - Robust error handling

---

**Ready to test games automatically? Start with `python demo.py`**
