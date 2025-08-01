// Relationship Simulation Frontend JavaScript

class SimulationApp {
    constructor() {
        this.currentSimulation = null;
        this.isRunning = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkSimulationStatus();
    }

    bindEvents() {
        // Setup panel events
        document.getElementById('startSimBtn').addEventListener('click', () => this.startSimulation());
        document.getElementById('loadSimBtn').addEventListener('click', () => this.showSavedSimulations());

        // Control panel events
        document.getElementById('runAutoBtn').addEventListener('click', () => this.runSimulation('auto'));
        document.getElementById('runSceneBtn').addEventListener('click', () => this.runSimulation('scene'));
        document.getElementById('saveSimBtn').addEventListener('click', () => this.showSaveModal());
        document.getElementById('resetSimBtn').addEventListener('click', () => this.resetSimulation());

        // Results panel events
        document.getElementById('clearResultsBtn').addEventListener('click', () => this.clearResults());

        // Modal events
        document.getElementById('closeSavedModal').addEventListener('click', () => this.hideModal('savedSimModal'));
        document.getElementById('closeSaveModal').addEventListener('click', () => this.hideModal('saveSimModal'));
        document.getElementById('confirmSaveBtn').addEventListener('click', () => this.saveSimulation());
        document.getElementById('cancelSaveBtn').addEventListener('click', () => this.hideModal('saveSimModal'));

        // Load simulation buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('load-sim-btn')) {
                const item = e.target.closest('.saved-simulation-item');
                const filename = item.dataset.filename;
                this.loadSimulation(filename);
            }
        });

        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }

    async startSimulation() {
        const agent1 = document.getElementById('agent1').value;
        const agent2 = document.getElementById('agent2').value;
        const scenario = document.getElementById('scenario').value;
        const interactions = document.getElementById('interactions').value;

        if (!agent1 || !agent2 || !scenario) {
            this.showNotification('Please select both agents and a scenario', 'error');
            return;
        }

        if (agent1 === agent2) {
            this.showNotification('Please select different agents', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/start_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_1: agent1,
                    agent_2: agent2,
                    scenario: scenario,
                    interactions_per_scene: parseInt(interactions)
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentSimulation = data.simulation_info;
                this.showControlPanel();
                this.updateSimulationInfo();
                this.showNotification('Simulation started successfully!', 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error starting simulation: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async runSimulation(mode) {
        if (this.isRunning) {
            this.showNotification('Simulation is already running', 'warning');
            return;
        }

        const interactions = document.getElementById('interactions').value;

        // this.showLoading(true);
        this.isRunning = true;
        this.updateRunButtons();
        this.clearResults(); // Clear previous results
        
        // Hide control panel and make results full height
        document.getElementById('controlPanel').classList.add('hidden');
        document.getElementById('resultsPanel').classList.add('full-width');
        document.getElementById('resultsContainer').classList.add('full-height');

        try {
            // Use streaming endpoint for real-time results
            const response = await fetch('/api/run_simulation_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mode: mode,
                    interactions_per_scene: parseInt(interactions)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.addResult(data);
                        } catch (e) {
                            console.error('Error parsing stream data:', e);
                        }
                    }
                }
            }

            this.showNotification(`Simulation completed successfully!`, 'success');
        } catch (error) {
            this.showNotification('Error running simulation: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
            this.isRunning = false;
            this.updateRunButtons();
            
            // Restore control panel and results container
            document.getElementById('controlPanel').classList.remove('hidden');
            document.getElementById('resultsPanel').classList.remove('full-width');
            document.getElementById('resultsContainer').classList.remove('full-height');
        }
    }

    async saveSimulation() {
        const filename = document.getElementById('saveFilename').value;
        
        if (!filename.trim()) {
            this.showNotification('Please enter a filename', 'error');
            return;
        }

        try {
            const response = await fetch('/api/save_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: filename
                })
            });

            const data = await response.json();

            if (data.success) {
                this.hideModal('saveSimModal');
                this.showNotification('Simulation saved successfully!', 'success');
                document.getElementById('saveFilename').value = '';
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error saving simulation: ' + error.message, 'error');
        }
    }

    async loadSimulation(filename) {
        this.showLoading(true);

        try {
            const response = await fetch('/api/load_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: filename
                })
            });

            const data = await response.json();

            if (data.success) {
                this.hideModal('savedSimModal');
                this.showControlPanel();
                this.updateSimulationInfo();
                this.showNotification('Simulation loaded successfully!', 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error loading simulation: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async checkSimulationStatus() {
        try {
            const response = await fetch('/api/simulation_status');
            const data = await response.json();

            if (data.has_simulation) {
                this.currentSimulation = data.simulation_info;
                this.showControlPanel();
                this.updateSimulationInfo();
            }
        } catch (error) {
            console.error('Error checking simulation status:', error);
        }
    }

    showControlPanel() {
        document.getElementById('setupPanel').style.display = 'none';
        document.getElementById('controlPanel').style.display = 'block';
        document.getElementById('resultsPanel').style.display = 'block';
    }

    showSetupPanel() {
        document.getElementById('setupPanel').style.display = 'block';
        document.getElementById('controlPanel').style.display = 'none';
        document.getElementById('resultsPanel').style.display = 'none';
    }

    updateSimulationInfo() {
        if (!this.currentSimulation) return;

        const infoDiv = document.getElementById('simulationInfo');
        infoDiv.innerHTML = `
            <h3><i class="fas fa-info-circle"></i> Current Simulation</h3>
            <p><strong>Agent 1:</strong> ${this.currentSimulation.agent_1}</p>
            <p><strong>Agent 2:</strong> ${this.currentSimulation.agent_2}</p>
            <p><strong>Scenario:</strong> ${this.currentSimulation.scenario}</p>
            <p><strong>Interactions per Scene:</strong> ${this.currentSimulation.interactions_per_scene}</p>
            <p><strong>Started:</strong> ${new Date(this.currentSimulation.started_at).toLocaleString()}</p>
        `;
    }

    addResult(result) {
        const container = document.getElementById('resultsContainer');
        
        let typeClass = 'general';
        let typeLabel = 'Output';

        // Determine the type of output based on result type and content
        if (result.type === 'error') {
            typeClass = 'error';
            typeLabel = 'Error';
        } else if (result.type === 'scene-master' || result.content.includes('[Scene Master]') || result.content.includes('[Scene Master:]')) {
            typeClass = 'scene-master';
            typeLabel = 'Scene Master';
        } else if (result.type === 'agent-1' || (result.content.match(/\[([^\]]+)\]/) && result.type === 'agent-1')) {
            typeClass = 'agent-1';
            // Extract agent name from content if it's in brackets
            const agentMatch = result.content.match(/\[([^\]]+)\]/);
            // Convert snake_case to Title Case (e.g., blake_lively -> Blake Lively)
            if (this.currentSimulation && this.currentSimulation.agent_1) {
                typeLabel = this.currentSimulation.agent_1
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            } else {
                typeLabel = 'Agent 1';
            }
        } else if (result.type === 'agent-2' || (result.content.match(/\[([^\]]+)\]/) && result.type === 'agent-2')) {
            typeClass = 'agent-2';
            // Extract agent name from content if it's in brackets
            const agentMatch = result.content.match(/\[([^\]]+)\]/);
            if (this.currentSimulation && this.currentSimulation.agent_2) {
                typeLabel = this.currentSimulation.agent_2
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            } else {
                typeLabel = 'Agent 2';
            }
        } else if (result.content.includes('is appraising') || result.content.includes('is making a choice') || result.content.includes('Adding scene conflict')) {
            typeClass = 'general';
            typeLabel = 'System';
        }

        const resultElement = document.createElement('div');
        resultElement.className = `result-item ${typeClass}`;
        resultElement.innerHTML = `
            <div class="result-header">
                <span class="result-type">${typeLabel}</span>
            </div>
            <div class="result-content">${this.escapeHtml(result.content)}</div>
        `;

        container.appendChild(resultElement);
        container.scrollTop = container.scrollHeight;
    }

    displayResults(results) {
        const container = document.getElementById('resultsContainer');
        
        if (!results || results.length === 0) {
            container.innerHTML = '<p class="no-results">No results to display</p>';
            return;
        }

        let html = '';
        
        results.forEach(result => {
            let typeClass = 'general';
            let typeLabel = 'Output';

            // Determine the type of output based on result type and content
            if (result.type === 'error') {
                typeClass = 'error';
                typeLabel = 'Error';
            } else if (result.type === 'scene-master' || result.content.includes('[Scene Master]') || result.content.includes('[Scene Master:]')) {
                typeClass = 'scene-master';
                typeLabel = 'Scene Master';
            } else if (result.type === 'agent-1' || (result.content.match(/\[([^\]]+)\]/) && result.type === 'agent-1')) {
                typeClass = 'agent-1';
                // Extract agent name from content if it's in brackets
                const agentMatch = result.content.match(/\[([^\]]+)\]/);
                typeLabel = agentMatch ? agentMatch[1] : 'Agent 1';
            } else if (result.type === 'agent-2' || (result.content.match(/\[([^\]]+)\]/) && result.type === 'agent-2')) {
                typeClass = 'agent-2';
                // Extract agent name from content if it's in brackets
                const agentMatch = result.content.match(/\[([^\]]+)\]/);
                typeLabel = agentMatch ? agentMatch[1] : 'Agent 2';
            } else if (result.content.includes('is appraising') || result.content.includes('is making a choice') || result.content.includes('Adding scene conflict')) {
                typeClass = 'general';
                typeLabel = 'System';
            }

            html += `
                <div class="result-item ${typeClass}">
                    <div class="result-header">
                        <span class="result-type">${typeLabel}</span>
                    </div>
                    <div class="result-content">${this.escapeHtml(result.content)}</div>
                </div>
            `;
        });

        container.innerHTML = html;
        container.scrollTop = container.scrollHeight;
    }

    clearResults() {
        document.getElementById('resultsContainer').innerHTML = '';
        this.showNotification('Results cleared', 'info');
    }

    resetSimulation() {
        if (confirm('Are you sure you want to reset the simulation? This will clear all progress.')) {
            this.currentSimulation = null;
            this.showSetupPanel();
            this.clearResults();
            this.showNotification('Simulation reset', 'info');
        }
    }

    showSavedSimulations() {
        document.getElementById('savedSimModal').style.display = 'block';
    }

    showSaveModal() {
        document.getElementById('saveSimModal').style.display = 'block';
        document.getElementById('saveFilename').focus();
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    showLoading(show) {
        document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
    }

    updateRunButtons() {
        const runAutoBtn = document.getElementById('runAutoBtn');
        const runSceneBtn = document.getElementById('runSceneBtn');
        
        if (this.isRunning) {
            runAutoBtn.disabled = true;
            runSceneBtn.disabled = true;
            runAutoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
            runSceneBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
        } else {
            runAutoBtn.disabled = false;
            runSceneBtn.disabled = false;
            runAutoBtn.innerHTML = '<i class="fas fa-rocket"></i> Run Auto';
            runSceneBtn.innerHTML = '<i class="fas fa-step-forward"></i> Run Scene';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 3000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 400px;
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || '#17a2b8';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SimulationApp();
});

// Add some additional utility functions
window.addEventListener('beforeunload', () => {
    // Clean up any running simulations if needed
    if (window.simulationApp && window.simulationApp.isRunning) {
        return 'Simulation is still running. Are you sure you want to leave?';
    }
}); 