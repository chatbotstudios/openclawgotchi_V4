        // Parse the dynamic custom states dictionary compiled on python backend
        const statesData = {states_json};
        
        // Static fallbacks for state colors if mappings are incomplete
        const stateColorMap = {
            'connecting': '#FF9F1C',
            'thinking': '#2EC4B6',
            'tool loop': '#9B5DE5',
            'success': '#4CAF50',
            'error': '#E63946',
            'idle': '#00f0ff',
            'sleeping': '#4A5568'
        };

        // Static fallbacks for specialized thought processes
        const thinkingVerbs = [
            "backpropagating", "gradient descending", "optimizing policy",
            "brute forcing", "deauthing", "jamming", "decrypting", "encrypting",
            "vectorizing", "inferencing", "packet sniffing", "wardriving", 
            "port scanning", "synthesizing", "conceptualizing", "compiling payload",
            "deploying firewalls", "wiping traces", "accessing hive mind"
        ];
        const thinkingKaomojis = ["(◉_◉)", "(ಠ_ಠ)", "(⚙_⚙)", "(⬚_⬚)", "[▣_▣]"];

        let currentGotchiState = 'idle';
        let currentGotchiSpecial = '';
        let frameIndex = 0;
        let animationInterval = null;
        let mockMode = false;
        let mockState = 'idle';
        
        // Energy HP & RPG Level metrics
        let hpValue = 100;
        let xpValue = 0;
        let levelValue = 2;
        let previousLevel = null;
        let isNapping = false;

        // Auto-detect low-power devices (Pi Zero, mobile). Disable expensive effects.
        const _isLowPower = navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2;
        let _effectsEnabled = !_isLowPower;

        // Diagnostics window controls state
        let consoleMaximized = false;
        let consoleMinimized = false;

        // Generate the physical 5x8 circular LED grid screen
        function initLedMatrix() {
            const matrixGrid = document.getElementById('led-matrix-grid');
            matrixGrid.innerHTML = '';
            for (let r = 0; r < 5; r++) {
                for (let c = 0; c < 8; c++) {
                    const dot = document.createElement('div');
                    dot.className = 'led-dot';
                    dot.dataset.row = r;
                    dot.dataset.col = c;
                    matrixGrid.appendChild(dot);
                }
            }
        }

        // Custom real-time 60fps physical LED matrix render loop
        function startBrailleRenderLoop() {
            if (animationInterval) clearInterval(animationInterval);
            
            animationInterval = setInterval(() => {
                frameIndex++;
                const activeState = mockMode ? mockState : currentGotchiState;
                const mode = getAnimationMode(activeState);
                const color = getStateColor(activeState, currentGotchiSpecial);
                
                // Set EPD display boundary glow dynamically
                document.documentElement.style.setProperty('--state-color', color);
                document.documentElement.style.setProperty('--state-glow', hexToRgbGlow(color, 0.28));

                // Also calculate mode-specific colors for the physical LED matrix
                let dotColor = '#00F0FF';
                if (mode === 'wave') dotColor = '#FF7700'; // Orange
                else if (mode === 'random') dotColor = '#3B82F6'; // Deep Blue
                else if (mode === 'spiral') dotColor = '#9B51E0'; // Violet
                else if (mode === 'cascade') dotColor = '#00FF87'; // Emerald
                else if (mode === 'rain') dotColor = '#FF3366'; // Crimson
                else if (mode === 'breathe') dotColor = '#4A5568'; // Slate Grey

                const matrixGrid = document.getElementById('led-matrix-grid');
                matrixGrid.style.setProperty('--dot-color', dotColor);
                matrixGrid.style.setProperty('--dot-glow', hexToRgbGlow(dotColor, 0.6));

                const dots = document.querySelectorAll('.led-dot');
                
                dots.forEach(dot => {
                    const r = parseInt(dot.dataset.row);
                    const c = parseInt(dot.dataset.col);
                    let intensity = 0;
                    
                    if (mode === 'random') {
                        intensity = Math.random() > 0.45 ? 1.0 : 0.08;
                    } else if (mode === 'wave') {
                        const phase = (frameIndex * 0.15) + (r * 0.8) + (c * 0.5);
                        intensity = Math.sin(phase) * 0.45 + 0.55;
                    } else if (mode === 'cascade') {
                        const progress = ((frameIndex + (4 - r) * 3) % 20) / 20;
                        const fillThreshold = progress * 8 + Math.sin(c + frameIndex * 0.3) * 2;
                        intensity = ( (4 - r) < fillThreshold || Math.random() > 0.88 ) ? 1.0 : 0.08;
                    } else if (mode === 'spiral') {
                        const angle = (frameIndex * 0.12) + r * 1.2;
                        const cx = c - 3.5, cy = r - 2;
                        const dist = Math.sqrt(cx * cx + cy * cy);
                        const localAngle = Math.atan2(cy, cx) + angle;
                        intensity = Math.sin(localAngle * 3 - dist) * 0.45 + 0.55;
                    } else if (mode === 'rain') {
                        const drop = ((frameIndex * 2 + c * 7) % 30);
                        const isActive = drop > (r * 5) && drop < (r * 5 + 12);
                        intensity = isActive ? (Math.random() > 0.3 ? 1.0 : 0.25) : (Math.random() > 0.94 ? 0.6 : 0.08);
                    } else if (mode === 'breathe') {
                        intensity = Math.sin(frameIndex * 0.05) * 0.4 + 0.6;
                    } else {
                        // static
                        intensity = Math.sin(frameIndex * 0.02 + r * 0.5 + c * 0.3) * 0.15 + 0.25;
                    }
                    
                    dot.style.opacity = intensity;
                });
            }, 60);
        }

        function getAnimationMode(state) {
            switch(state.toLowerCase()) {
                case 'connecting': return 'wave';
                case 'thinking': return 'random';
                case 'tool loop': return 'spiral';
                case 'success': return 'cascade';
                case 'error': return 'rain';
                case 'sleeping': return 'breathe';
                default: return 'static';
            }
        }

        function getStateColor(state, specialState) {
            state = state.toLowerCase();
            
            // Check if special state has color override in gotchi_states.json
            if (specialState && statesData && statesData.SPECIAL_STATES) {
                const specDef = statesData.SPECIAL_STATES.find(s => s.state.toLowerCase() === specialState.toLowerCase());
                if (specDef && specDef.color) {
                    return extractHex(specDef.color);
                }
            }
            
            // Check if main state has color override
            if (statesData && statesData.MAIN_STATES) {
                const mainDef = statesData.MAIN_STATES.find(s => s.state.toLowerCase() === state);
                if (mainDef && mainDef.color) {
                    return extractHex(mainDef.color);
                }
            }
            
            return stateColorMap[state] || '#00f0ff';
        }

        function extractHex(val) {
            if (val.includes(" ")) {
                return val.split(" ")[1].trim();
            }
            return val.trim();
        }

        function hexToRgbGlow(hex, alpha) {
            hex = hex.replace('#', '');
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }

        // Sound synthesizer for tactical retro cyber effects
        const audioSynth = {
            ctx: null,
            init() {
                if (!this.ctx) {
                    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
                }
            },
            playBeep() {
                if (!_effectsEnabled) return;
                try {
                    this.init();
                    if (this.ctx.state === 'suspended') this.ctx.resume();
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(880, this.ctx.currentTime); // A5
                    gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
                    osc.start();
                    osc.stop(this.ctx.currentTime + 0.08);
                } catch (e) { console.warn("Audio Context blocked:", e); }
            },
            playSuccessArpeggio() {
                if (!_effectsEnabled) return;
                try {
                    this.init();
                    if (this.ctx.state === 'suspended') this.ctx.resume();
                    const now = this.ctx.currentTime;
                    const playNote = (freq, delay, duration) => {
                        const osc = this.ctx.createOscillator();
                        const gain = this.ctx.createGain();
                        osc.connect(gain);
                        gain.connect(this.ctx.destination);
                        osc.type = 'triangle';
                        osc.frequency.setValueAtTime(freq, now + delay);
                        gain.gain.setValueAtTime(0.04, now + delay);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + delay + duration);
                        osc.start(now + delay);
                        osc.stop(now + delay + duration);
                    };
                    playNote(523.25, 0.0, 0.12); // C5
                    playNote(659.25, 0.06, 0.12); // E5
                    playNote(783.99, 0.12, 0.12); // G5
                    playNote(1046.50, 0.18, 0.22); // C6
                } catch (e) { }
            }
        };

        // DOM Particle Emitter Explosion (Emits glowing particles from click location)
        function createParticleExplosion(e) {
            if (!_effectsEnabled) return;
            if (!e) return;
            const rect = e.target.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            
            const count = 12;
            const colors = ['var(--magenta)', 'var(--cyan)', '#FFB703', '#00FF87'];
            
            for (let i = 0; i < count; i++) {
                const p = document.createElement('div');
                p.className = 'hud-particle';
                p.style.left = `${x}px`;
                p.style.top = `${y}px`;
                p.style.background = colors[Math.floor(Math.random() * colors.length)];
                p.style.boxShadow = `0 0 8px ${p.style.background}`;
                
                const angle = Math.random() * Math.PI * 2;
                const velocity = 25 + Math.random() * 65;
                const tx = Math.cos(angle) * velocity;
                const ty = Math.sin(angle) * velocity;
                
                p.style.setProperty('--tx', `${tx}px`);
                p.style.setProperty('--ty', `${ty}px`);
                
                document.body.appendChild(p);
                
                setTimeout(() => p.classList.add('explode'), 10);
                setTimeout(() => p.remove(), 700);
            }
        }

        // Mock State Controller implementation
        function setMockState(state) {
            mockMode = true;
            mockState = state.toLowerCase();
            
            // UI interaction
            audioSynth.playBeep();
            
            // Remove active style from all mock buttons
            document.querySelectorAll('.mock-btn').forEach(btn => btn.classList.remove('active'));
            
            let btnId = 'mock-btn-idle';
            if (mockState === 'connecting') btnId = 'mock-btn-connecting';
            else if (mockState === 'thinking') btnId = 'mock-btn-thinking';
            else if (mockState === 'tool loop') btnId = 'mock-btn-tool';
            else if (mockState === 'success') btnId = 'mock-btn-success';
            else if (mockState === 'error') btnId = 'mock-btn-error';
            else if (mockState === 'sleeping') btnId = 'mock-btn-sleeping';
            document.getElementById(btnId).classList.add('active');

            // Force override metrics and texts based on mock state
            const badge = document.getElementById('state-badge-val');
            badge.textContent = mockState.toUpperCase();
            
            const specBadge = document.getElementById('special-badge-val');
            const thoughtTicker = document.getElementById('thought-ticker-val');
            const toolsList = document.getElementById('tools-list-val');
            const kaomojiFace = document.getElementById('kaomoji-val');

            // Dynamic states mock attributes
            if (mockState === 'error') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Failsafe triggered. Core energy state depleted!";
                toolsList.textContent = "battery_hibernation, low_power_sleep, error_dump";
                kaomojiFace.textContent = '(✖ █ ✖)';
                hpValue = 0;
            } else if (mockState === 'success') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Uplink handshake established. Success cascade completed!";
                toolsList.textContent = "telemetry_synced, consensus_achieved";
                kaomojiFace.textContent = '(★ ‿ ★)';
                hpValue = 100;
                audioSynth.playSuccessArpeggio();
            } else if (mockState === 'thinking') {
                specBadge.textContent = 'pondering';
                specBadge.style.display = 'inline-block';
                thoughtTicker.textContent = "[◉_◉] ┊ wardriving c2c routing table...";
                toolsList.textContent = "packet_sniffing, compute_xp_gain, network_scan";
                kaomojiFace.textContent = '(ಠ_ಠ)';
                hpValue = 68;
            } else if (mockState === 'connecting') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Handshaking visual HUD telemetry channel...";
                toolsList.textContent = "wifi_scan, espnow_broadcast, peer_auth";
                kaomojiFace.textContent = '(◕ ‿ ◕)';
                hpValue = 45;
            } else if (mockState === 'tool loop') {
                specBadge.textContent = 'processing';
                specBadge.style.display = 'inline-block';
                thoughtTicker.textContent = "(⚙_⚙) ┊ inferencing synaptic coefficients...";
                toolsList.textContent = "load_nvs, fetch_api_proxy, write_buffer";
                kaomojiFace.textContent = '(◕ ‿ ◕)';
                hpValue = 82;
            } else if (mockState === 'sleeping') {
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Core sleeping gesture activated. HP regeneration loop enabled.";
                toolsList.textContent = "idle_listener, voltage_regulator";
                kaomojiFace.textContent = '(─ ‿ ─) zZ';
                hpValue = 95;
            } else {
                // idle
                specBadge.style.display = 'none';
                thoughtTicker.textContent = "Passively sniffing ambient cyberspace beacons...";
                toolsList.textContent = "boot_sequence, load_nvs, idle_listener";
                kaomojiFace.textContent = '(◕ ‿ ◕)';
                hpValue = 100;
            }

            // Sync indicators
            const spinnerIds = ['active-pulse-spinner', 'thought-spinner'];
            const showSpinners = (mockState === 'thinking' || mockState === 'connecting' || mockState === 'tool loop');
            spinnerIds.forEach(id => {
                document.getElementById(id).style.display = showSpinners ? 'inline-block' : 'none';
            });

            updateMetricsUI();
            addMockLog(mockState);
        }

        function exitMockMode() {
            mockMode = false;
            document.querySelectorAll('.mock-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('mock-btn-resume').classList.add('active');
            audioSynth.playBeep();
            fetchStats();
        }

        // Live HP decay & nap regeneration loop - ticks every 5 seconds
        setInterval(() => {
            const activeState = mockMode ? mockState : currentGotchiState;
            if (activeState === 'sleeping' || isNapping) {
                hpValue = Math.min(100, hpValue + 4);
            } else if (activeState === 'error') {
                hpValue = 0;
            } else {
                hpValue = Math.max(0, hpValue - 1);
            }
            updateMetricsUI();
        }, 5000);

        function updateMetricsUI() {
            // XP progress
            const xpHeader = document.getElementById('xp-header-text');
            const xpBar = document.getElementById('xp-progress');
            if (xpHeader && xpBar) {
                const inLevel = Math.round(xpValue);
                xpHeader.textContent = `XP PROGRESS ${inLevel}%`;
                xpBar.style.width = `${Math.min(100, inLevel)}%`;
            }

            // HP progress
            const hpHeader = document.getElementById('hp-header-text');
            const hpBar = document.getElementById('hp-progress');
            const hpText = document.getElementById('energy-hp-text');
            if (hpHeader && hpBar && hpText) {
                hpHeader.textContent = `ENERGY HP ${hpValue}%`;
                hpBar.style.width = `${hpValue}%`;
                hpText.textContent = hpValue === 0 ? "Status: Depleted" : "Status: Active";
                
                // Color coding HP empty/low/high states
                if (hpValue === 0) {
                    hpBar.style.width = '0%';
                } else if (hpValue < 20) {
                    hpBar.style.background = 'var(--red)';
                    hpBar.style.boxShadow = '0 0 10px var(--red-glow)';
                } else if (hpValue < 50) {
                    hpBar.style.background = 'var(--yellow)';
                    hpBar.style.boxShadow = '0 0 10px var(--yellow-glow)';
                } else {
                    hpBar.style.background = 'var(--magenta)';
                    hpBar.style.boxShadow = '0 0 10px var(--magenta-glow)';
                }
            }

            // Trust Rep progress gauge
            const trustHeader = document.getElementById('trust-header-text');
            const trustBar = document.getElementById('trust-progress');
            const trustSub = document.getElementById('trust-subtext');
            if (trustHeader && trustBar && trustSub) {
                let messages = xpValue * 2; // Simulated relative mapping
                if (messages > 80) {
                    trustHeader.textContent = "TRUST REP 1.000";
                    trustBar.style.width = "100%";
                    trustSub.textContent = "Rating: Trusted";
                    trustSub.style.color = "var(--cyan)";
                } else if (messages > 30) {
                    trustHeader.textContent = "TRUST REP 0.850";
                    trustBar.style.width = "85%";
                    trustSub.textContent = "Rating: Friendly";
                    trustSub.style.color = "var(--green)";
                } else {
                    trustHeader.textContent = "TRUST REP 0.500";
                    trustBar.style.width = "50%";
                    trustSub.textContent = "Rating: Neutral";
                    trustSub.style.color = "var(--text-secondary)";
                }
            }
        }

        // Ticker task polling hook - every 1.0s
        setInterval(() => {
            const activeState = mockMode ? mockState : currentGotchiState;
            if (activeState === 'thinking' || activeState === 'connecting' || activeState === 'tool loop') {
                const verb = thinkingVerbs[Math.floor(Math.random() * thinkingVerbs.length)];
                const kaomoji = thinkingKaomojis[Math.floor(Math.random() * thinkingKaomojis.length)];
                const target = ["internal core arrays", "c2c routing table", "network packets", "promiscuous adapters"][Math.floor(Math.random() * 4)];
                document.getElementById('thought-ticker-val').textContent = `${kaomoji} ┊ ${verb} ${target}...`;
            }
        }, 1000);

        // Terminal text highlight formatter
        function formatConsoleLine(line) {
            // Escape HTML tags to protect log flow
            let escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            // 1. Timestamps in dark gray (e.g. "[12:34:56]")
            escaped = escaped.replace(/^(\\[\\d{2}:\\d{2}:\\d{2}\\])/, '<span style="color: #656d8a;">$1</span>');
            
            // 2. Success tags [XP Gain] in emerald green
            escaped = escaped.replace(/(\\[XP Gain\\]|\\[XP \\+\\d+\\])/gi, '<span style="color: var(--green); font-weight: bold; text-shadow: 0 0 5px rgba(0, 255, 135, 0.2);">$1</span>');
            
            // 3. Uplink actions [Uplink] in gold/yellow
            escaped = escaped.replace(/(\\[Uplink\\])/gi, '<span style="color: var(--yellow); font-weight: bold; text-shadow: 0 0 5px rgba(255, 184, 0, 0.2);">$1</span>');
            
            // 4. Network mesh telemetry [Telemetry Mesh] / [System] in cyber cyan
            escaped = escaped.replace(/(\\[Telemetry Mesh\\]|\\[System\\]|\\[System Init\\]|\\[Cyberspace\\]|\\[Synapse\\])/gi, '<span style="color: var(--cyan); font-weight: bold; text-shadow: 0 0 5px rgba(0, 240, 255, 0.2);">$1</span>');
            
            return escaped;
        }

        // Add visual mock log line
        function addMockLog(state) {
            const feed = document.getElementById('log-feed');
            const timestamp = new Date().toTimeString().split(' ')[0];
            let logMsg = "";
            if (state === 'error') {
                logMsg = `[${timestamp}] [System] Critical failsafe alert! [Telemetry Mesh] offline. Core energy state depleted.`;
            } else if (state === 'success') {
                logMsg = `[${timestamp}] [XP Gain] Handshake complete! Captured 1 AP credential. +40 XP granted!`;
            } else if (state === 'thinking') {
                logMsg = `[${timestamp}] [System] Initializing neural reasoning pipeline. Deployed LLM search hooks.`;
            } else if (state === 'connecting') {
                logMsg = `[${timestamp}] [Uplink] Pinging swarm telemetry channels. AP index scan initiated.`;
            } else if (state === 'tool loop') {
                logMsg = `[${timestamp}] [System] Invoking local system calls. [Telemetry Mesh] synchronizing socket bounds.`;
            } else {
                logMsg = `[${timestamp}] [System Init] Normal execution loops idling. Telemetry channels stable.`;
            }
            
            const div = document.createElement('div');
            div.className = 'console-line sys';
            div.innerHTML = formatConsoleLine(logMsg);
            div.onclick = () => copyLogToClipboard(logMsg);
            
            feed.insertBefore(div, feed.firstChild);
        }

        // Real-time telemetry fetch — used for initial load and SSE fallback
        async function fetchStats() {
            if (mockMode) return; // Freeze API polling if in mock data mode
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                updateDashboard(data);
            } catch (err) {
                console.error("Stats fetch error:", err);
            }
        }

        // Shared DOM update — called by both fetchStats() and SSE stream
        function updateDashboard(data) {
            // Update System
                document.getElementById('cpu-usage').textContent = data.system.cpu_load || '-';
                document.getElementById('ram-usage').textContent = data.system.memory || '-';
                document.getElementById('cpu-temp').textContent = data.system.temp || '-';
                document.getElementById('uptime').textContent = data.system.uptime || '-';

                // Update Gotchi RPG
                document.getElementById('rpg-class').textContent = data.gotchi.title || '-';
                document.getElementById('rpg-level').textContent = data.gotchi.level || '-';
                
                // Parse XP progression (real level data from backend)
                xpValue = 0;
                if (data.gotchi.xp_in_level !== undefined && data.gotchi.xp_needed_this_level > 0) {
                    xpValue = (data.gotchi.xp_in_level / data.gotchi.xp_needed_this_level) * 100;
                }

                // Sync HP from Backend State Manager
                if (data.gotchi.hp !== undefined && data.gotchi.hp !== "?") {
                    hpValue = parseFloat(data.gotchi.hp);
                }
                
                // Track RPG Level Up arpeggio sound!
                const currentLevel = parseInt(data.gotchi.level) || 2;
                levelValue = currentLevel;
                if (previousLevel !== null && currentLevel > previousLevel) {
                    audioSynth.playSuccessArpeggio();
                    showToastNotification(`LEVEL UP! Evolved to Tier ${currentLevel} // ${data.gotchi.title}`);
                }
                previousLevel = currentLevel;

                // Update API Badge Status
                const apiBadge = document.getElementById('api-status-badge');
                if (apiBadge) {
                    if (data.api_ready) {
                        apiBadge.textContent = 'READY';
                        apiBadge.style.background = '#4CAF50';
                        apiBadge.style.boxShadow = '0 0 10px rgba(76,175,80,0.4)';
                    } else {
                        apiBadge.textContent = 'UNKEY';
                        apiBadge.style.background = '#E63946';
                        apiBadge.style.boxShadow = '0 0 10px rgba(230,57,70,0.4)';
                    }
                }

                // Update Gotchi display states
                const mood = (data.gotchi.mood || 'idle').toLowerCase();
                const kaomoji = data.gotchi.kaomoji || '(◕ ‿ ◕)';
                const text = data.gotchi.text || '';
                
                // Map system state badge
                let mainState = 'idle';
                let specialState = '';
                
                if (mood === 'thinking') {
                    mainState = 'thinking';
                } else if (mood === 'connecting' || mood === 'boot') {
                    mainState = 'connecting';
                } else if (mood === 'errored' || mood === 'confused' || mood === 'sad') {
                    mainState = 'error';
                } else if (mood === 'success' || mood === 'celebrate') {
                    mainState = 'success';
                } else if (mood === 'sleeping') {
                    mainState = 'sleeping';
                }
                
                if (text && text.toLowerCase().includes('say:')) {
                    const cleanText = text.replace(/say:/i, '');
                    document.getElementById('thought-ticker-val').textContent = cleanText;
                } else if (text) {
                    document.getElementById('thought-ticker-val').textContent = text;
                }
                
                // Determine if special state matches any entries in gotchi_states.json
                if (text && statesData && statesData.SPECIAL_STATES) {
                    const match = statesData.SPECIAL_STATES.find(s => text.toLowerCase().includes(s.state.toLowerCase()));
                    if (match) {
                        specialState = match.state;
                        mainState = 'tool loop'; // set main state as tool loop
                    }
                }
                
                currentGotchiState = mainState;
                currentGotchiSpecial = specialState;
                
                // Update Badge UI
                const badge = document.getElementById('state-badge-val');
                badge.textContent = mainState.toUpperCase();
                
                const specBadge = document.getElementById('special-badge-val');
                if (specialState) {
                    specBadge.textContent = specialState;
                    specBadge.style.display = 'inline-block';
                } else {
                    specBadge.style.display = 'none';
                }

                // Show active spinners if active
                const spinnerIds = ['active-pulse-spinner', 'thought-spinner'];
                const showSpinners = (mainState === 'thinking' || mainState === 'connecting' || mainState === 'tool loop');
                spinnerIds.forEach(id => {
                    document.getElementById(id).style.display = showSpinners ? 'inline-block' : 'none';
                });

                // Update face (override if napping)
                if (isNapping) {
                    document.getElementById('kaomoji-val').textContent = '(─ ‿ ─) zZ';
                } else {
                    document.getElementById('kaomoji-val').textContent = kaomoji;
                }

                // Update active tools
                if (text && text.includes('| STATUS:')) {
                    const parts = text.split('| STATUS:');
                    document.getElementById('tools-list-val').textContent = parts[1].trim();
                } else if (mainState === 'thinking') {
                    document.getElementById('tools-list-val').textContent = "packet_sniffing, compute_xp_gain, network_scan";
                } else if (mainState === 'connecting') {
                    document.getElementById('tools-list-val').textContent = "wifi_scan, espnow_broadcast, peer_auth";
                } else if (mainState === 'tool loop') {
                    document.getElementById('tools-list-val').textContent = "load_nvs, fetch_api_proxy, write_buffer";
                } else {
                    document.getElementById('tools-list-val').textContent = "boot_sequence, load_nvs, idle_listener";
                }

                // Update Radio & Pwn
                document.getElementById('pwn-status').textContent = data.pwn.status || 'OFFLINE';
                document.getElementById('pwn-status').style.color = data.pwn.status === 'ONLINE' ? 'var(--cyan)' : 'var(--text-secondary)';
                document.getElementById('discovered-aps').textContent = data.pwn.aps || '0';
                document.getElementById('discovered-ble').textContent = data.pwn.ble || '0';
                document.getElementById('captured-handshakes').textContent = data.pwn.handshakes || '0';

                // Update Vitals Progress Bars
                updateMetricsUI();

                // Update Monospace Terminal Logs (Most recent log on top, with sub-string color parser)
                const logFeed = document.getElementById('log-feed');
                logFeed.innerHTML = '';
                if (data.logs && data.logs.length > 0) {
                    const reversedLogs = [...data.logs].reverse();
                    reversedLogs.forEach(line => {
                        const div = document.createElement('div');
                        div.className = 'console-line';
                        
                        if (line.includes('[USER]') || line.includes('[CHAT:USER]')) {
                            div.className += ' user';
                        } else if (line.includes('[ASSISTANT]') || line.includes('[BOT]') || line.includes('[CHAT:BOT]')) {
                            div.className += ' bot';
                        } else {
                            div.className += ' sys';
                        }
                        
                        div.innerHTML = formatConsoleLine(line);
                        div.onclick = () => copyLogToClipboard(line);
                        logFeed.appendChild(div);
                    });
                } else {
                    logFeed.innerHTML = '<div class="console-line sys">[Idle] Waiting for dialog chat events...</div>';
                }

                // Refresh E-Paper waveshare thumbnail
                document.getElementById('epd-image').src = '/simulator.png?t=' + new Date().getTime();
        }

        // Action dispatcher
        async function executeAction(event, actionName) {
            if (typeof event === 'string') {
                actionName = event;
                event = null;
            }
            if (event) {
                audioSynth.playBeep();
                createParticleExplosion(event);
            }
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=${actionName}`
                });
                const result = await res.json();
                showToastNotification(result.message || 'Action executed successfully.');
                if (event && result.success) {
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Action error:", err);
            }
        }

        // Swarm action uplinks verified XP dispatcher
        async function triggerUplink(e, actionName) {
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=${actionName}`
                });
                const result = await res.json();
                showToastNotification(result.message || 'Uplink synchronization complete.');
                if (result.success) {
                    updateMetricsUI();
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Uplink error:", err);
            }
        }

        // Cyberspace Brave Search query dispatcher
        async function triggerCyberSearch(e) {
            const query = prompt("ENTER SYSTEM CYBERSPACE SEARCH QUERY:");
            if (!query) return;
            
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=brave_search&query=${encodeURIComponent(query)}`
                });
                const result = await res.json();
                showToastNotification(result.message || 'Brave search complete.');
                if (result.success) {
                    updateMetricsUI();
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Search error:", err);
            }
        }

        // Sleeping Nap Mode toggle
        async function toggleNapMode(e) {
            isNapping = !isNapping;
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            const btn = document.getElementById('nap-btn');
            if (isNapping) {
                btn.classList.add('napping');
                btn.textContent = '🛌 Sleeping...';
            } else {
                btn.classList.remove('napping');
                btn.textContent = '🛌 Gesture: Nap';
            }
            
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `action=toggle_nap&is_napping=${isNapping}`
                });
                const result = await res.json();
                showToastNotification(result.message);
                if (result.success) {
                    setTimeout(() => audioSynth.playSuccessArpeggio(), 200);
                }
                setTimeout(fetchStats, 200);
            } catch (err) {
                console.error("Nap error:", err);
            }
        }

        // Neural Core Direct Synapse dispatch
        async function transmitSynapseCommand(e) {
            const promptInput = document.getElementById('synapse-prompt-val');
            const prompt = promptInput.value.trim();
            if (!prompt) return;
            
            audioSynth.playBeep();
            createParticleExplosion(e);
            
            promptInput.value = "";
            promptInput.placeholder = "TRANSMITTING COMMAND PATHWAY...";
            promptInput.disabled = true;
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `prompt=${encodeURIComponent(prompt)}`
                });
                const result = await res.json();
                if (result.success) {
                    audioSynth.playSuccessArpeggio();
                    showToastNotification("Direct synapse pathway synchronized.");
                    updateMetricsUI();
                } else {
                    showToastNotification("Core error: " + result.message);
                }
            } catch (err) {
                console.error("Transmission error:", err);
                showToastNotification("Connection gateway disrupted.");
            } finally {
                promptInput.placeholder = "TRANSMIT SYNAPSE COMMAND...";
                promptInput.disabled = false;
                setTimeout(fetchStats, 200);
            }
        }

        // Clipboard copy log handler
        function copyLogToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToastNotification("Copied raw log to clipboard!");
            }).catch(err => {
                console.error("Clipboard copy failed:", err);
            });
        }

        function showToastNotification(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'show';
            setTimeout(() => { toast.className = ''; }, 2500);
        }

        function clearConsoleLog() {
            executeAction('clear_history');
        }

        // Sliding overlay panel configuration editor
        async function toggleConfigPanel(show) {
            const panel = document.getElementById('config-panel');
            const editor = document.getElementById('env-editor-area');
            
            if (show) {
                editor.value = "Loading environment configurations...";
                panel.classList.add('active');
                audioSynth.playBeep();
                
                try {
                    const res = await fetch('/api/config');
                    const text = await res.text();
                    editor.value = text;
                } catch (err) {
                    editor.value = "Error loading config: " + err;
                }
            } else {
                panel.classList.remove('active');
            }
        }

        async function saveSettingsConfig() {
            const content = document.getElementById('env-editor-area').value;
            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: content
                });
                const result = await res.json();
                showToastNotification(result.message || 'Config saved.');
                if (result.success) toggleConfigPanel(false);
            } catch (err) {
                showToastNotification("Failed to save config: " + err);
            }
        }

        // Diagnostics terminal controls
        function toggleConsoleMinimize() {
            const screen = document.getElementById('log-feed');
            consoleMinimized = !consoleMinimized;
            audioSynth.playBeep();
            if (consoleMinimized) {
                screen.style.height = '0px';
                screen.style.padding = '0px';
                consoleMaximized = false;
                const card = document.querySelector('.console-card');
                card.style.position = 'static';
                card.style.width = 'auto';
                card.style.height = 'auto';
            } else {
                screen.style.height = '250px';
                screen.style.padding = '10px';
            }
        }

        function toggleConsoleMaximize() {
            const card = document.querySelector('.console-card');
            const screen = document.getElementById('log-feed');
            consoleMaximized = !consoleMaximized;
            audioSynth.playBeep();
            
            if (consoleMaximized) {
                card.style.position = 'fixed';
                card.style.top = '5vh';
                card.style.left = '5vw';
                card.style.width = '90vw';
                card.style.height = '90vh';
                card.style.zIndex = '999';
                screen.style.height = 'calc(90vh - 100px)';
                consoleMinimized = false;
                screen.style.padding = '10px';
            } else {
                card.style.position = 'static';
                card.style.width = 'auto';
                card.style.height = 'auto';
                screen.style.height = '250px';
            }
        }

        // Initialize HUD
        initLedMatrix();
        fetchStats();  // Initial fetch
        startBrailleRenderLoop();

        // Real-time SSE stream — replaces 1s polling
        const eventSource = new EventSource('/api/events');
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                // Call the same update function that fetchStats uses
                if (typeof updateDashboard === 'function') {
                    updateDashboard(data);
                }
            } catch (e) {
                console.error("SSE parse error:", e);
            }
        };
        eventSource.onerror = function() {
            // SSE connection dropped — fall back to polling
            console.warn("SSE disconnected, falling back to polling...");
            if (window._sseFallback) return;
            window._sseFallback = setInterval(fetchStats, 2000);
        };
