/**
 * NeuralCore - Central Orbital Visualization
 * Premium "Cyberpunk" Edition
 */

import React from 'react';

type AgentName = 'ATLAS' | 'TETYANA' | 'GRISHA' | 'SYSTEM' | 'USER';
type SystemState = 'IDLE' | 'PROCESSING' | 'EXECUTING' | 'VERIFYING' | 'ERROR';

interface NeuralCoreProps {
    state: SystemState;
    activeAgent: AgentName;
}

const NeuralCore: React.FC<NeuralCoreProps> = ({ state, activeAgent }) => {

    // --- STATE COLORS ---
    const getStateColor = (): string => {
        switch (state) {
            case 'IDLE': return 'var(--state-idle)';
            case 'PROCESSING': return 'var(--state-processing)';
            case 'EXECUTING': return 'var(--state-executing)';
            case 'VERIFYING': return 'var(--state-processing)';
            case 'ERROR': return 'var(--state-error)';
            default: return 'var(--atlas-blue)';
        }
    };


    const getStateLabel = () => {
        switch (state) {
            case 'IDLE': return 'SYSTEM ONLINE';
            case 'PROCESSING': return 'PROCESSING REQUEST';
            case 'EXECUTING': return 'EXECUTING PROTOCOLS';
            case 'VERIFYING': return 'VERIFYING OUTPUT';
            case 'ERROR': return 'SYSTEM FAILURE';
            default: return 'UNKNOWN STATE';
        }
    };

    // Use inline style for dynamic CSS variables
    const containerStyle = {
        color: getStateColor(),
    } as React.CSSProperties;

    // Agent Active Check
    const isAtlas = activeAgent === 'ATLAS';
    const isTetyana = activeAgent === 'TETYANA';
    const isGrisha = activeAgent === 'GRISHA';

    return (
        <div className="neural-core transition-colors-slow" style={containerStyle}>
            <svg viewBox="-400 -400 800 800" className="orbital-svg">
                {/* --- DEFINITIONS (Gradients & Filters) --- */}
                <defs>
                    <filter id="glow-core">
                        <feGaussianBlur stdDeviation="5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                    <filter id="glow-strong">
                        <feGaussianBlur stdDeviation="8" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                    <radialGradient id="grad-core" cx="0.5" cy="0.5" r="0.5">
                        <stop offset="0%" stopColor="currentColor" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
                    </radialGradient>
                </defs>

                {/* --- DECORATIVE BACKGROUND RINGS --- */}
                <circle r="380" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.1" strokeDasharray="4 4" />
                <circle r="300" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.1" />

                {/* --- ROTATING RINGS --- */}

                {/* Outer Slow Ring */}
                <g className="animate-spin-slow origin-center" style={{ opacity: 0.3 }}>
                    <circle r="250" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="100 200" />
                    <circle r="245" fill="none" stroke="currentColor" strokeWidth="4" strokeDasharray="20 480" strokeOpacity="0.5" />
                </g>

                {/* Middle Counter-Rotating Ring */}
                <g className="animate-spin-ccw-medium origin-center" style={{ opacity: 0.5 }}>
                    <circle r="180" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="20 10 50 10" />
                    <circle r="170" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="50 50" />
                </g>

                {/* Inner Fast Ring */}
                <g className="animate-spin-fast origin-center" style={{ opacity: 0.8 }}>
                    <circle r="100" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="80 120" />
                </g>


                {/* --- CENTRAL CORE --- */}
                <g className="core-group" filter="url(#glow-core)">
                    <circle r="60" fill="url(#grad-core)" className="animate-pulse" />
                    <circle r="15" fill="currentColor" className="animate-pulse-fast" />
                    <circle r="5" fill="#fff" opacity="0.8" />
                </g>


                {/* --- AGENT NODES (Orbital Positions) --- */}

                {/* ATLAS Node (Top) */}
                <g transform="rotate(0)">
                    <line x1="0" y1="-80" x2="0" y2="-170" stroke="var(--atlas-blue)" strokeWidth="1" opacity={isAtlas ? 0.8 : 0.2} />
                    <circle cx="0" cy="-180" r={isAtlas ? 12 : 6} fill="var(--atlas-blue)" className={isAtlas ? "glow-md animate-pulse" : ""} opacity={isAtlas ? 1 : 0.5} />
                    <text x="0" y="-210" textAnchor="middle" fill="var(--atlas-blue)" fontSize="12" fontWeight="bold" letterSpacing="2" opacity={isAtlas ? 1 : 0.5}>ATLAS</text>
                </g>

                {/* GRISHA Node (Right) */}
                <g transform="rotate(120)">
                    <line x1="0" y1="-80" x2="0" y2="-170" stroke="var(--grisha-orange, #FF8000)" strokeWidth="1" opacity={isGrisha ? 0.8 : 0.2} />
                    {/* Rotate text back to be upright */}
                    <g transform="translate(0, -180)">
                        <circle r={isGrisha ? 12 : 6} fill="var(--grisha-orange, #FF8000)" transform="rotate(-120)" className={isGrisha ? "glow-md animate-pulse" : ""} opacity={isGrisha ? 1 : 0.5} />
                        <text y="30" transform="rotate(-120)" textAnchor="middle" fill="var(--grisha-orange, #FF8000)" fontSize="12" fontWeight="bold" letterSpacing="2" opacity={isGrisha ? 1 : 0.5}>GRISHA</text>
                    </g>
                </g>

                {/* TETYANA Node (Left) */}
                <g transform="rotate(240)">
                    <line x1="0" y1="-80" x2="0" y2="-170" stroke="var(--tetyana-green)" strokeWidth="1" opacity={isTetyana ? 0.8 : 0.2} />
                    {/* Rotate text back to be upright */}
                    <g transform="translate(0, -180)">
                        <circle r={isTetyana ? 12 : 6} fill="var(--tetyana-green)" transform="rotate(-240)" className={isTetyana ? "glow-md animate-pulse" : ""} opacity={isTetyana ? 1 : 0.5} />
                        <text y="30" transform="rotate(-240)" textAnchor="middle" fill="var(--tetyana-green)" fontSize="12" fontWeight="bold" letterSpacing="2" opacity={isTetyana ? 1 : 0.5}>TETYANA</text>
                    </g>
                </g>

            </svg>

            <div className="state-label border-opacity-20 backdrop-blur-md">
                <div className="scanlines"></div>
                <span className="text-content animate-glitch">{getStateLabel()}</span>
            </div>

            <style>{`
                .neural-core {
                    position: relative;
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    overflow: visible;
                }
                .orbital-svg {
                    width: 400px;
                    height: 400px;
                    max-width: 100%;
                    max-height: 100%;
                    filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));
                }
                .state-label {
                    position: absolute;
                    bottom: 10%;
                    padding: 8px 16px;
                    border: 1px solid currentColor;
                    background: rgba(0,0,0,0.7);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 14px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    color: currentColor;
                    text-transform: uppercase;
                    box-shadow: 0 0 15px currentColor;
                    overflow: hidden;
                }
                .state-label .text-content {
                    position: relative;
                    z-index: 20;
                }
            `}</style>
        </div>
    );
};

export default NeuralCore;
