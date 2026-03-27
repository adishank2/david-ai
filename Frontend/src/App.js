import React, { useState, useEffect } from 'react';
import './App.css';
import AudioReactivePlasmaBlob from './component/blob';
import SpeechTerminal from './component/SpeechTerminal';
import Auth from './component/Auth';
import useDavidAI from './hooks/useDavidAI';

function App() {
    const [isMicActive, setIsMicActive] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const { isConnected, davidResponse, status, ragStatus, sendCommand, triggerScan } = useDavidAI();

    useEffect(() => {
        if (localStorage.getItem('david_token')) {
            setIsAuthenticated(true);
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('david_token');
        localStorage.removeItem('david_email');
        setIsAuthenticated(false);
        setIsMicActive(false);
    };

    const toggleMicrophone = () => setIsMicActive(prev => !prev);

    if (!isAuthenticated) {
        return <Auth onLogin={() => setIsAuthenticated(true)} />;
    }

    return (
        <div className="App">
            {/* Dark cyberpunk radial background with grid */}
            <div className="App-background"></div>

            <div className="hud-container">
                {/* JARVIS Header */}
                <div className="hud-header">
                    <h1 className="hud-title">DAVID</h1>
                    <div className="hud-subtitle">Digitally Advanced Virtual Intelligent Device</div>
                </div>

                {/* 3D Visualization & Input */}
                <div className="hud-center">
                    <div style={{ width: '360px', height: '360px', position: 'relative' }}>
                        <AudioReactivePlasmaBlob isListeningExternally={isMicActive} />
                    </div>

                    <div style={{ marginTop: '20px', width: '100%', display: 'flex', justifyContent: 'center' }}>
                         <SpeechTerminal
                            isActive={isMicActive}
                            onSpeechResult={sendCommand}
                            davidResponse={davidResponse}
                        />
                    </div>
                </div>

                {/* Controls and Footer metrics */}
                <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div className="hud-buttons">
                        <button className={`hud-btn ${isMicActive ? 'active' : ''}`} onClick={toggleMicrophone}>
                            {isMicActive ? 'SYSTEM LISTENING' : 'ACTIVATE COMMS'}
                        </button>
                        <button className="hud-btn" onClick={() => sendCommand("show diagnostics")}>DIAGNOSTICS</button>
                        <button className="hud-btn" onClick={triggerScan} disabled={ragStatus.is_indexing}>
                            {ragStatus.is_indexing ? 'INDEXING...' : 'SYNC KNOWLEDGE'}
                        </button>
                        <button className="hud-btn" onClick={() => sendCommand("system status")}>ANALYTICS</button>
                        <button className="hud-btn" onClick={handleLogout}>DISCONNECT</button>
                    </div>

                    <div className="hud-footer">
                        <div className="hud-stat-box">
                            <span className="hud-stat-label">STATUS:</span>
                            <span className="hud-stat-value">{isConnected ? 'ONLINE' : 'OFFLINE'}</span>
                        </div>
                        <div className="hud-stat-box">
                            <span className="hud-stat-label">CORE:</span>
                            <span className="hud-stat-value">{String(status || 'AWAITING LINK...')}</span>
                        </div>
                        <div className="hud-stat-box">
                            <span className="hud-stat-label">KNOWLEDGE:</span>
                            <span className="hud-stat-value">
                                {ragStatus.is_indexing ? 'INDEXING...' : `${ragStatus.count} FILES`}
                            </span>
                        </div>
                        <div className="hud-stat-box">
                            <span className="hud-stat-label">LATENCY:</span>
                            <span className="hud-stat-value">22ms</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
