import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';

const AudioReactivePlasmaBlob = ({ isListeningExternally }) => {
    // Audio Refs
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const dataArrayRef = useRef(null);
    const streamRef = useRef(null);
    const [isListening, setIsListening] = useState(false);

    // Three.js Refs
    const mountRef = useRef(null);
    const sceneRef = useRef(null);
    const cameraRef = useRef(null);
    const rendererRef = useRef(null);
    const particlesRef = useRef(null);
    const animationIdRef = useRef(null);

    const audioParams = useRef({
        smoothedVolume: 0,
        targetVolume: 0,
        smoothingFactor: 0.15,
    });

    // 1. Initialize Three.js Scene
    useEffect(() => {
        if (!mountRef.current) return;

        const width = 360;
        const height = 360;

        // Scene
        const scene = new THREE.Scene();
        sceneRef.current = scene;

        // Camera
        const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.z = 15;
        cameraRef.current = camera;

        // Renderer
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        // Clear children to prevent double-render in StrictMode
        while (mountRef.current.firstChild) {
            mountRef.current.removeChild(mountRef.current.firstChild);
        }
        
        mountRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Particles Geometry (Create a sphere of glowing dots)
        const geometry = new THREE.BufferGeometry();
        const particleCount = 1500;
        const positions = new Float32Array(particleCount * 3);
        const radius = 8; // base radius

        for (let i = 0; i < particleCount; i++) {
            // Random point on a sphere surface (using math for even distribution or just random cube constrained)
            const u = Math.random();
            const v = Math.random();
            const theta = 2 * Math.PI * u;
            const phi = Math.acos(2 * v - 1);
            
            const x = radius * Math.sin(phi) * Math.cos(theta);
            const y = radius * Math.sin(phi) * Math.sin(theta);
            const z = radius * Math.cos(phi);

            positions[i * 3] = x;
            positions[i * 3 + 1] = y;
            positions[i * 3 + 2] = z;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        // Particle Material (Glowing cyan dots)
        const material = new THREE.PointsMaterial({
            color: 0x00ffe1,
            size: 0.15,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });

        const particles = new THREE.Points(geometry, material);
        scene.add(particles);
        particlesRef.current = particles;

        // 2. Render Loop
        const animate = () => {
            animationIdRef.current = requestAnimationFrame(animate);

            // Audio reaction logic
            let vol = 0;
            if (analyserRef.current && dataArrayRef.current) {
                analyserRef.current.getByteFrequencyData(dataArrayRef.current);
                let sum = 0;
                for (let i = 0; i < dataArrayRef.current.length; i++) {
                    sum += (dataArrayRef.current[i] / 255) ** 2;
                }
                const rms = Math.sqrt(sum / dataArrayRef.current.length);
                audioParams.current.targetVolume = rms;
                audioParams.current.smoothedVolume += 
                    (audioParams.current.targetVolume - audioParams.current.smoothedVolume) * audioParams.current.smoothingFactor;
                
                vol = audioParams.current.smoothedVolume;
            }

            // Animate Particles
            if (particlesRef.current) {
                // Base rotation
                particlesRef.current.rotation.y += 0.005;
                particlesRef.current.rotation.x += 0.002;

                // Scale based on audio volume
                const scale = 1.0 + (vol * 0.4); 
                particlesRef.current.scale.set(scale, scale, scale);
                
                // Color intensity shift based on volume
                particlesRef.current.material.opacity = 0.5 + (vol * 0.5);
                particlesRef.current.material.size = 0.15 + (vol * 0.2);
            }

            renderer.render(scene, camera);
        };

        animate();

        // Cleanup Three.js
        return () => {
            if (animationIdRef.current) {
                cancelAnimationFrame(animationIdRef.current);
            }
            if (mountRef.current && renderer.domElement) {
                mountRef.current.removeChild(renderer.domElement);
            }
            geometry.dispose();
            material.dispose();
            renderer.dispose();
        };
    }, []);

    // 3. Audio Handlers
    const initAudio = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            audioContextRef.current = audioCtx;
            
            const analyser = audioCtx.createAnalyser();
            analyserRef.current = analyser;
            analyser.fftSize = 256;
            analyser.smoothingTimeConstant = 0.8;

            const bufferLength = analyser.frequencyBinCount;
            dataArrayRef.current = new Uint8Array(bufferLength);

            const source = audioCtx.createMediaStreamSource(stream);
            source.connect(analyser);

            setIsListening(true);
        } catch (error) {
            console.error('Error accessing microphone:', error);
        }
    };

    const stopAudio = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
            audioContextRef.current.close().catch(console.error);
        }
        setIsListening(false);
        audioParams.current.smoothedVolume = 0; // reset
    };

    // Prop synchronization
    useEffect(() => {
        if (isListeningExternally && !isListening) {
            initAudio();
        } else if (!isListeningExternally && isListening) {
            stopAudio();
        }
    }, [isListeningExternally, isListening]);

    // Cleanup audio on unmount
    useEffect(() => {
        return () => {
            stopAudio();
        };
    }, []);

    const containerStyle = {
        position: 'relative', 
        width: '360px', 
        height: '360px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        // Outer glowing aura to sell the JARVIS effect
        background: 'radial-gradient(circle, rgba(0,255,225,0.08) 0%, transparent 60%)',
        borderRadius: '50%'
    };

    return (
        <div style={containerStyle}>
             {/* The container for Three.js canvas */}
            <div ref={mountRef} style={{ width: '360px', height: '360px' }} />
        </div>
    );
};

export default AudioReactivePlasmaBlob;