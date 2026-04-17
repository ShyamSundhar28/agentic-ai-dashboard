import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Bot, 
  Activity, 
  Settings, 
  Search, 
  Bell, 
  Cpu, 
  Zap, 
  Shield, 
  ChevronRight,
  Plus
} from 'lucide-react';
import './App.css';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'busy' | 'offline';
  tasks: number;
  uptime: string;
}

const App: React.FC = () => {
  const [agents] = useState<Agent[]>([
    { id: '1', name: 'Neural-Alpha', type: 'Data Analyst', status: 'online', tasks: 12, uptime: '24d 12h' },
    { id: '2', name: 'Cyber-Sentinel', type: 'Security auditor', status: 'busy', tasks: 45, uptime: '12d 4h' },
    { id: '3', name: 'Quantum-Flow', type: 'Workflow Optimizer', status: 'offline', tasks: 0, uptime: '5d 1h' },
    { id: '4', name: 'Vision-X', type: 'Image Generator', status: 'online', tasks: 8, uptime: '2d 18h' },
  ]);

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="logo-section">
          <div className="logo-icon">
            <Zap size={24} fill="var(--accent-primary)" stroke="var(--accent-primary)" />
          </div>
          <h1>Anti<span>Gravity</span></h1>
        </div>

        <nav className="nav-menu">
          <a href="#" className="nav-item active"><LayoutDashboard size={20} /> Dashboard</a>
          <a href="#" className="nav-item"><Bot size={20} /> Agents</a>
          <a href="#" className="nav-item"><Activity size={20} /> Analytics</a>
          <a href="#" className="nav-item"><Shield size={20} /> Security</a>
          <div className="nav-divider"></div>
          <a href="#" className="nav-item"><Settings size={20} /> Settings</a>
        </nav>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="avatar">JD</div>
            <div className="user-info">
              <span className="username">John Doe</span>
              <span className="user-role">System Admin</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-header">
          <div className="search-bar glass-panel">
            <Search size={18} className="search-icon" />
            <input type="text" placeholder="Search agents or tasks..." />
          </div>
          <div className="header-actions">
            <button className="icon-btn glass-panel"><Bell size={20} /><span className="badge"></span></button>
            <button className="btn btn-primary"><Plus size={18} /> Deploy Agent</button>
          </div>
        </header>

        <section className="dashboard-content">
          <div className="stats-grid">
            <div className="stat-card glass-panel">
              <div className="stat-icon cpu"><Cpu size={24} /></div>
              <div className="stat-info">
                <span className="stat-label">System Load</span>
                <span className="stat-value">24.8%</span>
              </div>
            </div>
            <div className="stat-card glass-panel">
              <div className="stat-icon zap"><Zap size={24} /></div>
              <div className="stat-info">
                <span className="stat-label">Active Tasks</span>
                <span className="stat-value">65</span>
              </div>
            </div>
            <div className="stat-card glass-panel">
              <div className="stat-icon activity"><Activity size={24} /></div>
              <div className="stat-info">
                <span className="stat-label">Uptime</span>
                <span className="stat-value">99.9%</span>
              </div>
            </div>
          </div>

          <div className="content-rows">
            <div className="agents-section glass-panel">
              <div className="section-header">
                <h2>Active Agents</h2>
                <button className="text-btn">View All <ChevronRight size={16} /></button>
              </div>
              <div className="agent-list">
                {agents.map(agent => (
                  <div key={agent.id} className="agent-item">
                    <div className="agent-info">
                      <div className={`agent-status-dot ${agent.status}`}></div>
                      <div>
                        <h3>{agent.name}</h3>
                        <p>{agent.type}</p>
                      </div>
                    </div>
                    <div className="agent-metrics">
                      <span className="metric">{agent.tasks} tasks</span>
                      <span className="metric">{agent.uptime}</span>
                    </div>
                    <span className={`status-badge status-${agent.status}`}>
                      {agent.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="activity-section glass-panel">
              <div className="section-header">
                <h2>Real-time Activity</h2>
              </div>
              <div className="activity-feed">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className="activity-item">
                    <div className="activity-dot"></div>
                    <div className="activity-details">
                      <p><strong>Agent-Alpha</strong> processed a new dataset in 450ms.</p>
                      <span className="time">Just now</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
