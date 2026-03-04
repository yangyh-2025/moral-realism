import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store';
import Dashboard from './pages/Dashboard';
import Configuration from './pages/Configuration';
import AgentsManagement from './pages/AgentsManagement';
import SimulationMonitor from './pages/SimulationMonitor';

function App() {
  const currentView = useStore((state) => state.currentView);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-bg-secondary">
        <div className="flex">
          {/* Main content area */}
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route
                path="/dashboard"
                element={<Dashboard />}
              />
              <Route
                path="/configuration"
                element={<Configuration />}
              />
              <Route
                path="/agents"
                element={<AgentsManagement />}
              />
              <Route
                path="/monitor"
                element={<SimulationMonitor />}
              />
              <Route
                path="*"
                element={<Navigate to="/dashboard" replace />}
              />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
