import React, { useEffect, useRef, useState } from 'react';
import './SpeechTerminal.css';

const SpeechTerminal = ({ isActive, onSpeechResult, davidResponse }) => {
    const [userText, setUserText]     = useState('');
    const [interimText, setInterimText] = useState('');
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef(null);

    // Speech recognition
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;

        if (isActive) {
            const recognition = new SpeechRecognition();
            recognition.lang            = 'en-IN';  // English (India) — understands English + picks up Hindi words
            recognition.continuous      = true;
            recognition.interimResults  = true;

            recognition.onstart = () => setIsListening(true);

            recognition.onresult = (event) => {
                let interim = '';
                let final   = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const t = event.results[i][0].transcript.trim();
                    if (event.results[i].isFinal) final = t;
                    else interim = t;
                }
                if (final) {
                    setUserText(final);
                    setInterimText('');
                    onSpeechResult && onSpeechResult(final);   // send to backend
                } else {
                    setInterimText(interim);
                }
            };

            recognition.onerror = () => {};
            recognition.onend   = () => {
                if (recognitionRef.current) {
                    try { recognition.start(); } catch (_) {}
                }
            };

            recognitionRef.current = recognition;
            recognition.start();
        } else {
            if (recognitionRef.current) {
                recognitionRef.current.onend = null;
                recognitionRef.current.stop();
                recognitionRef.current = null;
            }
            setIsListening(false);
            setUserText('');
            setInterimText('');
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.onend = null;
                recognitionRef.current.stop();
                recognitionRef.current = null;
            }
        };
    }, [isActive]);

    // Decide what to show:
    // 1. David's latest response (cyan)
    // 2. User's final spoken text (white)
    // 3. Interim / listening dots
    const showDavid   = davidResponse && !interimText;
    const showUser    = userText && !interimText && !davidResponse;
    const showInterim = !!interimText;

    return (
        <div className="speech-terminal">
            <div className="terminal-label">DAVID.AI</div>
            <div className="terminal-divider" />
            <div className="terminal-content">
                {isListening && !userText && !interimText && !davidResponse && (
                    <span className="terminal-placeholder">
                        ENTER COMMAND<span className="cursor-blink">_</span>
                    </span>
                )}
                {showInterim && (
                    <span className="terminal-text terminal-interim">{interimText}</span>
                )}
                {showUser && (
                    <span className="terminal-text terminal-user">{userText}</span>
                )}
                {showDavid && (
                    <span className="terminal-text terminal-david">{davidResponse}</span>
                )}
            </div>
        </div>
    );
};

export default SpeechTerminal;
