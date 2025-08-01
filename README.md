# Relationship Simulation Frontend

A beautiful, modern web interface for the AI-powered relationship dynamics simulation.

## Features

- **Modern UI**: Clean, responsive design with smooth animations
- **Agent Selection**: Choose from available AI agents (celebrities, fictional characters)
- **Scenario Selection**: Pick from different relationship scenarios
- **Simulation Modes**: Run simulations automatically or scene by scene
- **Real-time Results**: View simulation output with color-coded messages
- **Save/Load**: Save simulation progress and load previous sessions
- **Interactive Controls**: Start, pause, and control simulation flow

## Quick Start

1. **Install Dependencies** (if not already installed):
   ```bash
   pip install flask openai
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5000`

## How to Use

### 1. Setup Simulation
- Select two different agents from the dropdown menus
- Choose a scenario (e.g., "Work Stress", "Vacation", "Living Together")
- Set the number of interactions per scene (default: 5)
- Click "Start Simulation"

### 2. Run Simulation
- **Run Auto**: Executes the simulation automatically
- **Run Scene**: Runs one scene at a time
- **Save**: Save your current simulation progress
- **Reset**: Start over with a new simulation

### 3. View Results
- Results are displayed in real-time with color coding:
  - 🔵 **Scene Master**: Blue - Scene descriptions and context
  - 🟢 **Agent 1**: Green - First agent's actions and thoughts
  - 🔴 **Agent 2**: Red - Second agent's actions and thoughts

### 4. Save/Load Simulations
- **Save**: Click "Save" to save current progress
- **Load**: Click "Load Saved" to browse and load previous simulations

## Available Agents

The system includes various AI agents based on:
- **Celebrities**: Ryan Reynolds, Blake Lively, Taylor Swift, etc.
- **Personalities**: Each with unique traits, goals, and relationship dynamics

## Available Scenarios

- **Work Stress**: Relationship challenges during stressful work periods
- **Vacation**: Romantic getaway scenarios
- **Living Together**: Daily life and cohabitation challenges
- **Holiday with Family**: Family gathering dynamics

## Technical Details

### Frontend
- **HTML5**: Semantic markup with modern structure
- **CSS3**: Responsive design with gradients and animations
- **JavaScript**: ES6+ with async/await for API calls
- **Font Awesome**: Icons for better UX

### Backend
- **Flask**: Python web framework
- **RESTful API**: JSON-based communication
- **Session Management**: Persistent simulation state
- **Error Handling**: Comprehensive error messages

### Architecture
- **Separation of Concerns**: Frontend/backend separation
- **Modular Design**: Reusable components
- **Responsive**: Works on desktop and mobile devices
- **Accessible**: Keyboard navigation and screen reader support

## Customization

### Adding New Agents
1. Create a new folder in `sample_agents/`
2. Add `basics.json` with agent information
3. Add `id_mem.json` for identity memories (optional)

### Adding New Scenarios
1. Create a new folder in `scene_templates/`
2. Add `initial_state.json` and `scenes.json`
3. Follow the existing schema structure

### Styling
- Modify `static/css/style.css` for visual changes
- Update color schemes, fonts, or layout as needed

## Troubleshooting

### Common Issues

1. **Simulation won't start**:
   - Ensure you've selected different agents
   - Check that all required fields are filled

2. **No results displayed**:
   - Check browser console for JavaScript errors
   - Verify Flask server is running

3. **Save/Load not working**:
   - Ensure `saves/` directory exists
   - Check file permissions

### Debug Mode
Run with debug enabled for detailed error messages:
```bash
python app.py
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/start_simulation` - Initialize new simulation
- `POST /api/run_simulation` - Execute simulation
- `POST /api/save_simulation` - Save current state
- `POST /api/load_simulation` - Load saved state
- `GET /api/simulation_status` - Get current status
- `GET /api/agents` - List available agents
- `GET /api/scenarios` - List available scenarios

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes.

---

**Enjoy exploring AI-powered relationship dynamics!** 💕 