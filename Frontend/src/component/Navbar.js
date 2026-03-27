import React, { useState } from 'react';
import './Navbar.css';
const Navbar = ({ onInitialize, isMicActive, isConnected, onLogout }) => {
  const [showSettings, setShowSettings] = useState(false);
  const [activeModalTab, setActiveModalTab] = useState(null);

  const handleOpenTab = (tabName) => {
    setActiveModalTab(tabName);
    setShowSettings(false);
  };

  return (
    <>
      <nav className="futuristic-navbar">
        <div className="navbar-container">
        <div className="navbar-logo">
          <span className="logo-text">DAVID.AI</span>
        </div>

        <ul className="navbar-links">
          {/* Empty now, links moved to settings dropdown */}
        </ul>

        <div className="navbar-actions">
          {/* Backend connection indicator */}
          <span
            title={isConnected ? 'Backend connected' : 'Backend offline'}
            style={{
              display: 'inline-block',
              width: 10,
              height: 10,
              borderRadius: '50%',
              marginRight: 10,
              backgroundColor: isConnected ? '#00ff88' : '#ff4444',
              boxShadow: isConnected
                ? '0 0 8px #00ff88, 0 0 16px rgba(0,255,136,0.4)'
                : '0 0 8px #ff4444',
              transition: 'all 0.4s ease',
            }}
          />
          <button
            className="glow-on-hover"
            type="button"
            onClick={onInitialize}
            style={{
              backgroundColor: isMicActive
                ? 'rgba(255, 68, 68, 0.4)'
                : 'rgba(0, 255, 255, 0.1)'
            }}
          >
            {isMicActive ? 'DEACTIVATE' : 'INITIALIZE'}
          </button>
          
          {onLogout && (
            <button
              className="glow-on-hover"
              type="button"
              onClick={onLogout}
              style={{ marginLeft: 10, backgroundColor: 'rgba(255, 68, 68, 0.1)', borderColor: 'rgba(255, 68, 68, 0.5)', color: '#ffaaaa' }}
            >
              LOGOUT
            </button>
          )}
        </div>
      </div>
    </nav>

    {/* Floating Settings Button in Bottom Left */}
    <div className="floating-settings-container">
      <button 
        className="settings-icon-btn floating-cog" 
        onClick={() => setShowSettings(!showSettings)}
        title="Settings"
      >
        ⚙
      </button>
      
      {showSettings && (
        <div className="settings-dropdown floating-dropdown">
          <div className="dropdown-item" onClick={() => handleOpenTab('ACCOUNT')}>
            <span>ACCOUNT</span>
            <span className="dropdown-desc">User Details & Security</span>
          </div>
          <div className="dropdown-item" onClick={() => handleOpenTab('GENERAL')}>
            <span>GENERAL SETTINGS</span>
            <span className="dropdown-desc">App Version: v2.0 David AI</span>
          </div>
          <div className="dropdown-item" onClick={() => handleOpenTab('PERSONALISE')}>
            <span>PERSONALISE</span>
            <span className="dropdown-desc">Theme, UI & Voice Options</span>
          </div>
        </div>
      )}
    </div>

    {/* Settings Modal Overlay */}
    {activeModalTab && (
      <div className="settings-modal-overlay" onClick={() => setActiveModalTab(null)}>
        <div className="settings-modal" onClick={e => e.stopPropagation()}>
            <div className="settings-modal-header">
              <h2>{activeModalTab === 'GENERAL' ? 'GENERAL SETTINGS' : activeModalTab}</h2>
              <button className="close-modal-btn" onClick={() => setActiveModalTab(null)}>✕</button>
            </div>
            
            <div className="settings-modal-body">
              {activeModalTab === 'ACCOUNT' && (
                <>
                  <div className="setting-row">
                    <div className="setting-info">
                      <h3>Local User Account</h3>
                      <p>Email: admin@david.ai</p>
                    </div>
                  </div>
                  <div className="setting-row">
                    <div className="setting-info">
                      <h3>Security</h3>
                      <p>End-to-End Encryption: Active</p>
                    </div>
                    <div className="setting-control">
                      <button className="auth-button" style={{ padding: '8px 15px', marginTop: 0 }}>Change Password</button>
                    </div>
                  </div>
                </>
              )}

              {activeModalTab === 'GENERAL' && (
                <>
                  <div className="setting-row">
                    <div className="setting-info">
                      <h3>Application Version</h3>
                      <p>v2.0 (Cyberpunk Edition)</p>
                    </div>
                  </div>
                  <div className="setting-row">
                    <div className="setting-info">
                      <h3>Language Model</h3>
                      <p>Backend Base: LLaMA 3.2</p>
                    </div>
                    <div className="setting-control">
                      <select defaultValue="llama">
                        <option value="llama">Ollama (Local)</option>
                        <option value="openai">OpenAI (Cloud)</option>
                      </select>
                    </div>
                  </div>
                </>
              )}

              {activeModalTab === 'PERSONALISE' && (
                <>
                  <div className="setting-row">
                    <div className="setting-info">
                      <h3>UI Theme</h3>
                      <p>Core Visual Identity</p>
                    </div>
                    <div className="setting-control">
                      <select defaultValue="cyberpunk">
                        <option value="cyberpunk">Cyberpunk Neon</option>
                        <option value="dark">Deep Space</option>
                        <option value="glass">Glassmorphism</option>
                      </select>
                    </div>
                  </div>
                  <div className="setting-row">
                    <div className="setting-info">
                      <h3>Voice Voice (Cloud TTS)</h3>
                      <p>AI Audio Avatar</p>
                    </div>
                    <div className="setting-control">
                      <select defaultValue="male">
                        <option value="male">Christopher (Male)</option>
                        <option value="female">Aria (Female)</option>
                      </select>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
