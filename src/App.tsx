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
  Plus,
  Upload,
  BarChart3,
  Terminal,
  BrainCircuit,
  Database,
  Workflow
} from 'lucide-react';
import './App.css';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'busy' | 'offline';
  tasks: number;
  uptime: string;
  load: number;
}

const App: React.FC = () => {
  const [agents] = useState<Agent[]>([
    { id: '1', name: 'Supervisor-1', type: 'Orchestrator', status: 'online', tasks: 4, uptime: '24d 12h', load: 15 },
    { id: '2', name: 'Analyst-Prime', type: 'Statistical Engine', status: 'busy', tasks: 12, uptime: '12d 4h', load: 88 },
    { id: '3', name: 'Viz-Core', type: 'UI Generation', status: 'online', tasks: 2, uptime: '5d 1h', load: 12 },
    { id: '4', name: 'RCA-Delta', type: 'Root Cause Engine', status: 'offline', tasks: 0, uptime: '2d 18h', load: 0 },
  ]);

  const [activeTab, setActiveTab] = useState('dashboard');

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
          <a href="#" onClick={() => setActiveTab('dashboard')} className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}><LayoutDashboard size={20} /> Dashboard</a>
          <a href="#" onClick={() => setActiveTab('agents')} className={`nav-item ${activeTab === 'agents' ? 'active' : ''}`}><Bot size={20} /> Agent Swarm</a>
          <a href="#" onClick={() => setActiveTab('analytics')} className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}><BarChart3 size={20} /> Analytics</a>
          <a href="#" onClick={() => setActiveTab('philosophy')} className={`nav-item ${activeTab === 'philosophy' ? 'active' : ''}`}><BrainCircuit size={20} /> Philosophy</a>
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
            <input type="text" placeholder="Search insights or telemetry..." />
          </div>
          <div className="header-actions">
            <button className="icon-btn glass-panel"><Bell size={20} /><span className="badge"></span></button>
            <button className="btn btn-primary"><Workflow size={18} /> Initialize Swarm</button>
          </div>
        </header>

        {activeTab === 'dashboard' && (
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
                  <span className="stat-label">Pending Inferences</span>
                  <span className="stat-value">65</span>
                </div>
              </div>
              <div className="stat-card glass-panel">
                <div className="stat-icon activity"><Activity size={24} /></div>
                <div className="stat-info">
                  <span className="stat-label">Uptime Accuracy</span>
                  <span className="stat-value">99.9%</span>
                </div>
              </div>
            </div>

            <div className="upload-section glass-panel">
              <div className="upload-placeholder">
                <div className="upload-icon-circle">
                  <Upload size={32} className="text-accent" />
                </div>
                <h3>Ingest Raw Data</h3>
                <p>Drag and drop your CSV dataset here to begin agentic profiling.</p>
                <div className="upload-actions">
                  <button className="btn btn-ghost">Browse Files</button>
                  <label className="btn btn-primary cursor-pointer">
                    <Plus size={18} /> Select CSV
                  </label>
                </div>
              </div>
            </div>

            <div className="content-rows">
              <div className="agents-section glass-panel">
                <div className="section-header">
                  <h2>Active Agent Nodes</h2>
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
                        <div className="mini-chart">
                          <div className="chart-bar" style={{ height: `${agent.load}%` }}></div>
                        </div>
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
                  <h2>Swarm Telemetry</h2>
                  <Terminal size={18} className="text-secondary" />
                </div>
                <div className="activity-feed">
                  {[
                    { agent: 'Supervisor', msg: 'Delegated ingestion task to Analyst-Prime', time: 'Just now' },
                    { agent: 'Analyst-Prime', msg: 'Inferred schema for sales_data.csv', time: '2m ago' },
                    { agent: 'Planner', msg: 'Generated 5-step execution plan for YoY growth', time: '5m ago' },
                    { agent: 'Viz-Core', msg: 'Rendered Multi-Series Line Chart for Trend Analysis', time: '12m ago' },
                    { agent: 'RCA-Delta', msg: 'Identified Outlier in Region: North (Impact: +12%)', time: '15m ago' }
                  ].map((item, i) => (
                    <div key={i} className="activity-item">
                      <div className="activity-dot"></div>
                      <div className="activity-details">
                        <p><strong>{item.agent}</strong> {item.msg}</p>
                        <span className="time">{item.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'philosophy' && (
          <section className="philosophy-content glass-panel">
            <div className="philosophy-header">
              <h2>Engineering <span className="text-gradient">Philosophy</span></h2>
              <p>Building data systems that are resilient, observable, and autonomous.</p>
            </div>
            <div className="philosophy-grid">
              <div className="philosophy-card">
                <Database className="text-accent" size={32} />
                <h3>Scale-First Mindset</h3>
                <p>Designed to handle 10x today's volume with zero manual intervention.</p>
              </div>
              <div className="philosophy-card">
                <Workflow className="text-secondary" size={32} />
                <h3>Agentic Autonomy</h3>
                <p>Multi-agent swarms that decompose complex queries into executable logic.</p>
              </div>
              <div className="philosophy-card">
                <Shield className="text-success" size={32} />
                <h3>Observability by Default</h3>
                <p>Logging, monitoring, and tracing integrated from the start.</p>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

export default App;

