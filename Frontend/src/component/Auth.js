import React, { useState, useRef, useCallback, useEffect } from 'react';
import './Auth.css';

const API_URL = 'http://127.0.0.1:8001/api';

const Auth = ({ onLogin }) => {
  const [view, setView] = useState('login'); // 'login', 'register', 'verify', 'face_register', 'face_login'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [emotion, setEmotion] = useState(null);

  // Webcam refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const emotionIntervalRef = useRef(null);

  const formatError = (err) => {
    if (!err) return '';
    if (typeof err === 'string') return err;
    if (Array.isArray(err)) return err.map(e => e.msg || JSON.stringify(e)).join(', ');
    if (typeof err === 'object') return err.msg || JSON.stringify(err);
    return String(err);
  };

  // ── Start Webcam ──────────────────────────────────
  const startWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 320, height: 240, facingMode: 'user' } 
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError('Camera access denied. Please allow camera permissions.');
    }
  }, []);

  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    if (emotionIntervalRef.current) {
      clearInterval(emotionIntervalRef.current);
      emotionIntervalRef.current = null;
    }
  }, []);

  // Auto-start webcam when entering face views
  useEffect(() => {
    if (view === 'face_register' || view === 'face_login') {
      startWebcam();
      // Start emotion detection polling
      emotionIntervalRef.current = setInterval(async () => {
        const frame = captureFrame();
        if (frame) {
          try {
            const res = await fetch(`${API_URL}/emotion/detect`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ image: frame }),
            });
            const data = await res.json();
            setEmotion(data);
          } catch (_) {}
        }
      }, 3000); // Check emotion every 3 seconds
    } else {
      stopWebcam();
      setEmotion(null);
    }
    return () => stopWebcam();
  }, [view, startWebcam, stopWebcam]);

  // ── Capture Webcam Frame ──────────────────────────
  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth || 320;
    canvas.height = video.videoHeight || 240;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.8);
  };

  // ── Emotion Emoji ─────────────────────────────────
  const getEmotionEmoji = (em) => {
    const map = {
      happy: '😊', sad: '😢', angry: '😡', surprise: '😮',
      fear: '😨', disgust: '🤢', neutral: '😐', unknown: '❓'
    };
    return map[em] || '😐';
  };

  // ── Auth Handlers ─────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); setError(''); setMessage('');
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('david_token', data.token);
        localStorage.setItem('david_email', data.email);
        onLogin();
      } else {
        setError(formatError(data.detail) || 'Login failed');
      }
    } catch (_) { setError('Connection to backend failed'); }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true); setError(''); setMessage('');
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage('OTP sent! Please check your email.');
        setView('verify');
      } else {
        setError(formatError(data.detail) || 'Registration failed');
      }
    } catch (_) { setError('Connection to backend failed'); }
    setLoading(false);
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true); setError(''); setMessage('');
    try {
      const res = await fetch(`${API_URL}/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage('Account verified! You can now log in.');
        setView('login');
      } else {
        setError(formatError(data.detail) || 'Verification failed');
      }
    } catch (_) { setError('Connection to backend failed'); }
    setLoading(false);
  };

  // ── Face Login ────────────────────────────────────
  const handleFaceRegister = async () => {
    if (!email) { setError('Enter your email first'); return; }
    const frame = captureFrame();
    if (!frame) { setError('Camera not ready'); return; }
    setLoading(true); setError(''); setMessage('');
    try {
      const res = await fetch(`${API_URL}/face/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, image: frame }),
      });
      const data = await res.json();
      if (data.success) {
        setMessage('🔐 Face ID registered! You can now use Face Login.');
        setTimeout(() => setView('login'), 2000);
      } else {
        setError(data.error || 'Face registration failed');
      }
    } catch (_) { setError('Connection to backend failed'); }
    setLoading(false);
  };

  const handleFaceLogin = async () => {
    if (!email) { setError('Enter your email first'); return; }
    const frame = captureFrame();
    if (!frame) { setError('Camera not ready'); return; }
    setLoading(true); setError(''); setMessage('');
    try {
      const res = await fetch(`${API_URL}/face/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, image: frame }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('david_token', 'face_auth_' + Date.now());
        localStorage.setItem('david_email', email);
        setMessage(`✅ ${data.message}`);
        setTimeout(() => onLogin(), 1000);
      } else {
        setError(data.error || 'Face verification failed');
      }
    } catch (_) { setError('Connection to backend failed'); }
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1 className="auth-title">DAVID.AI</h1>
        <p className="auth-subtitle">CENTRAL INTELLIGENCE SYSTEM v2.0</p>

        {error && <div className="auth-alert error">{error}</div>}
        {message && <div className="auth-alert success">{message}</div>}

        {/* ── Emotion Display ────────────── */}
        {emotion && (view === 'face_register' || view === 'face_login') && (
          <div className="emotion-badge">
            <span className="emotion-emoji">{getEmotionEmoji(emotion.emotion)}</span>
            <span className="emotion-label">{emotion.emotion?.toUpperCase()} ({emotion.confidence}%)</span>
          </div>
        )}

        {/* ── Standard Login ────────────── */}
        {view === 'login' && (
          <form className="auth-form" onSubmit={handleLogin}>
            <div className="input-group">
              <label>SYSTEM IDENTIFIER (EMAIL)</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="operator@system.io" />
            </div>
            <div className="input-group">
              <label>ACCESS CODES (PASSWORD)</label>
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <button className="auth-button run-button" type="submit" disabled={loading}>
              {loading ? 'AUTHENTICATING...' : 'ESTABLISH UPLINK'}
            </button>
            
            <button type="button" className="auth-button face-btn" onClick={() => { setView('face_login'); setError(''); setMessage(''); }}>
              🔐 BIOMETRIC LOGIN (FACE ID)
            </button>

            <p className="auth-switch">
              Unregistered entity? <span onClick={() => { setView('register'); setError(''); setMessage(''); }}>Initialize new profile</span>
            </p>
          </form>
        )}

        {/* ── Register ────────────── */}
        {view === 'register' && (
          <form className="auth-form" onSubmit={handleRegister}>
            <div className="input-group">
              <label>EMAIL VERIFICATION</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="operator@system.io" />
            </div>
            <div className="input-group">
              <label>SET NEW PASSWORD</label>
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <button className="auth-button register-btn" type="submit" disabled={loading}>
              {loading ? 'GENERATING PROTOCOLS...' : 'REQUEST ACCESS'}
            </button>
            <p className="auth-switch">
              Already initialized? <span onClick={() => { setView('login'); setError(''); setMessage(''); }}>Return to Login</span>
            </p>
          </form>
        )}

        {/* ── OTP Verify ────────────── */}
        {view === 'verify' && (
          <form className="auth-form" onSubmit={handleVerify}>
            <div className="input-group">
              <label>INPUT OTP (SENT TO {email})</label>
              <input type="text" required value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="000000" maxLength={6} />
            </div>
            <button className="auth-button verify-btn" type="submit" disabled={loading}>
              {loading ? 'VALIDATING...' : 'VERIFY IDENTITY'}
            </button>
            <p className="auth-switch">
              Didn't receive it? <span onClick={() => { setView('register'); setError(''); setMessage(''); }}>Go back</span>
            </p>
          </form>
        )}

        {/* ── Face Login ────────────── */}
        {view === 'face_login' && (
          <div className="auth-form">
            <div className="input-group">
              <label>SYSTEM IDENTIFIER (EMAIL)</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="operator@system.io" />
            </div>
            
            <div className="webcam-container">
              <video ref={videoRef} autoPlay playsInline muted className="webcam-feed" />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              <div className="scan-overlay">
                <div className="scan-line"></div>
              </div>
            </div>
            
            <button className="auth-button face-btn" onClick={handleFaceLogin} disabled={loading}>
              {loading ? 'SCANNING BIOMETRICS...' : '🔐 VERIFY FACE ID'}
            </button>
            
            <div className="auth-switch-row">
              <span className="auth-link" onClick={() => { setView('face_register'); setError(''); setMessage(''); }}>Register Face ID</span>
              <span className="auth-link" onClick={() => { setView('login'); setError(''); setMessage(''); }}>Use Password</span>
            </div>
          </div>
        )}

        {/* ── Face Register ────────────── */}
        {view === 'face_register' && (
          <div className="auth-form">
            <div className="input-group">
              <label>EMAIL FOR FACE ID</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="operator@system.io" />
            </div>
            
            <div className="webcam-container">
              <video ref={videoRef} autoPlay playsInline muted className="webcam-feed" />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              <div className="scan-overlay">
                <div className="scan-line"></div>
              </div>
            </div>
            
            <button className="auth-button face-btn" onClick={handleFaceRegister} disabled={loading}>
              {loading ? 'ENCODING FACE DATA...' : '📸 REGISTER FACE ID'}
            </button>
            
            <p className="auth-switch">
              <span onClick={() => { setView('login'); setError(''); setMessage(''); }}>← Return to Login</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Auth;
