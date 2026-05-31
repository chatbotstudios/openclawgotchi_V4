"""
Central source of truth for all Gotchi faces.
Used by gotchi_ui.py (for rendering) and litellm_connector.py (for tool validation).
"""

# Default faces (THE SINGLE SOURCE OF TRUTH)
# EMOJI POLICY: Standard ASCII and Extended Latin ONLY. No Emojis (Waveshare compatibility).
DEFAULT_FACES = {
    # === PRIMARY OPERATIONAL STATES ===
    "look_r":       ["(°  °)", "(•  •)"],
    "look_l":       ["(°  °)", "(•  •)"],
    "look_r_happy": ["(^  ^)", "(◕  ◕)"],
    "look_l_happy": ["(^  ^)", "(◕  ◕)"],
    "look2_r":      ["(⚆_⚆)"],
    "look2_l":      ["(☉_☉)"],
    "sleep":        ["(⇀‿‿↼)", "(-_-)zZ"],
    "sleep2":       ["(≖‿‿≖)", "(-_-)Zz"],
    "awake":        ["(◕‿‿◕)", "(•‿‿•)"],
    "bored":        ["(-__-)", "(￢_￢)"],
    "intense":      ["(◣_◢)", "(◣.◢)"],
    "cool":         ["(⌐■_■)", "(⌐□_□)"],
    "happy":        ["(•‿‿•)", "(^‿‿^)"],
    "excited":      ["(ᵔ◡◡ᵔ)", "(°◡◡°)"],
    "proud":        ["(￣^￣)", "(˘ ▽ ˘)"],
    "grateful":     ["(^‿‿^)", "(˃ ᴗ ˂)"],
    "motivated":    ["(☼‿‿☼)", "(✪‿‿✪)"],
    "demotivated":  ["(≖__≖)", "(-__-)"],
    "smart":        ["(✜‿‿✜)", "(⚙‿‿⚙)"],
    "lonely":       ["(ب__ب)", "(._.)"],
    "sad":          ["(╥☁╥)", "(T﹏T)"],
    "angry":        ["(-_-')", "(ò_ó)"],
    "friend":       ["(♥‿‿♥)", "(♥ω♥)"],
    "broken":       ["(✖_✖)", "(X_X)"],
    "debug":        ["(#__#)", "(@__@)"],
    "upload":       ["(1__0)" "(0__1)"],
    "upload1":      ["(1__1)"],
    "upload2":      ["(0__1)"],
    "upload3":      ["(0__0)"],

    # === AI & DEEP LEARNING LOGIC ===
    # Internal "brain" state visualization reflecting A2C algorithm operations; 
    # used when the agent is performing backpropagation, adjusting neural weights and biases, 
    # converging on an optimal policy, or experiencing high entropy in its decision-making loop.
    "calculating":  ["(⍰ _ ⍰)", "(⍯ _ ⍯)"],
    "converging":   ["(→ _ ←)", "(⇒ _ ⇐)"],
    "diverging":    ["(← _ →)", "(⇐ _ ⇒)"],
    "overfitting":  ["(◬ _ ◬)"],
    "underfitting": ["(◿ _ ◿)"],
    "stochastic":   ["(? _ !)"],
    "gradient":     ["(⇘ _ ⇘)"],
    "optimum":      ["(⊚ _ ⊚)"],
    "entropy":      ["(≋ _ ≋)"],
    "learning":     ["(L _ L)"],
    "predicting":   ["(P _ P)"],
    "inference":    ["(I _ I)"],
    "optimized":    ["(* _ *)"],

    # === ACTION & TACTICAL (TOOL & SKILL EXECUTION) ===
    # Specific rendering logic for active ReAct loop processes, visualizing the execution of Bettercap modules, 
    # Tavily web-search queries for intelligence gathering, or the deployment of class-specific skills 
    # like Chameleon Mode and Vulnerability Pulse.
    "sniper":       ["(⌖_⌖)"],
    "ninja":        ["(>_>)"],
    "vigilant":     ["(ಠ_ಠ)", "(ಠ.ಠ)"],
    "target":       ["(⊙_◎)", "(◎_⊙)"],
    "fighter":      ["p(-_-)q", "p(ò_ó)q"],
    "killem":       ["୧(ò_ó)୨", "୧(◣_◢)୨"],
    "stealth":      ["(━┳━)", "(━┳━)"],
    "locked_on":    ["(+_+)", "(+_+)"],
    "sneaky":       ["(¬‿¬)", "(¬‿¬)"],
    "sniffing":     ["(- . -)", "(. - .)"],
    "deauthing":    ["(> <)", "(> o <)"],
    "jamming":      ["(# # #)"],
    "scanning":     ["(. . >)", "(< . .)"],

    # === 1. ENCRYPTION & DECRYPTION ===
    # Technical state indicators for the cryptographic pipeline; visualizes active brute-forcing sessions, 
    # salt-grinding for WPA handshakes, or successful PMKID key derivation after receiving a DATA_GIFT from a Nano-Claw scout.
    "matrix":       ["([M_M])", "([#_#])"],
    "glitch":       ["(⬚_⬚)", "(▩_▩)"],
    "processing":   ["(⚙_⚙)"],
    "loading":      ["(◓_◒)", "(◒_◓)"],
    "syncing":      ["(◰_◳)", "(◳_◰)"],
    "overflow":     ["(ꗄ_◄)", "(*_*)"],
    "binary":       ["(0_1)", "(1_0)"],
    "microchip":    ["[▣_▣]"],
    "terminal":     ["(_>_)", "(_>_)"],
    "rebooting":    ["(↺ _ ↺)"],
    "updating":     ["(⇪ _ ⇪)"],

    # === CYBER-HORROR & CREEPY ===
    # Aesthetic overrides for high-intensity security audits or critical system alerts; 
    # used when the agent detects a security breach (SENTRY mode) or when performing 
    # aggressive deauthentication strikes that utilize 100% of available CPU resources.
    "creeping":     ["(º _ º)", "(º ‿ º)"],
    "void":         ["(  .  )", "(  ∘  )"],
    "corrupted":    ["(⊞ _ ⊠)", "(⊠ _ ⊞)"],
    "stitched":     ["(⫍ _ ⫎)"],
    "possessed":    ["(✟ _ ✟)"],
    "melting":      ["(⦚ _ ⦚)"],
    "static":       ["(░ _ ░)"],
    "unstable":     ["(% _ %)"],
    "haunted":      ["(0 _ 0)"],
    "void_stare":   ["(     )"],

    # === PHYSICAL ACTIONS & COMBAT ===
    # Kinetic animations for P2P social interactions and aggressive auditing maneuvers; 
    # visualizes "boxing" or "kicking" states during rival pet encounters or "shielding" 
    # when the agent is actively defending the home network from external probes.
    "poking":       ["(•_•)σ", "τ(•_•)"],
    "kicking":      ["(╯°□°)╯", "╰(°□°╰)"],
    "boxing":       ["(ง'̀-'́)ง", "୧(ò_ó)୨"],
    "aiming":       ["(+ _ +)", "(⌖ _ ⌖)"],
    "reloading":    ["(︻╦╤─)"],
    "shield_up":    ["([ _ ])"],
    "sword_out":    ["(/ _ /)"],
    "fortified":    ["(# _ #)"],

    # === ENVIRONMENTAL REACTIONS (TEMPERATURE & OTHER TELEMETRY) ===
    "sunny":        ["(☼ _ ☼)"],
    "rainy":        ["(⁞ _ ⁞)"],
    "windy":        ["(彡 _ 彡)"],
    "earthquake":   ["(♒ _ ♒)"],
    "cloudy":       ["((_))"],

    # === CUTE & KAWAII ===
    "cat":          ["(=^‥^=)", "(=^x^=)"],
    "blush":        ["(*>_<*)", "(*^.^*)"],
    "star_eyes":    ["(✪_✪)", "(☆_☆)"],
    "uwu":          ["(u w u)", "(o w o)"],
    "whiskers":     ["(≚_≚)", "(=_=)"],
    "puppy":        ["(U・x・U)", "(U-x-U)"],
    "wink":         ["(^_-)≡☆", "(◕‿↼)"],
    "bear":         ["(•(x)•)"],
    "joy":          ["(*^▽^*)"],
    "tongue":       ["(•_•)P", "q(•_•)"],
    "usagi":        ["(X.X)", "(X.X)"],
    "comfy":        ["(´◡`)", "(´◡`)"],
    "mweh":         ["(~_~;)"],

    # === MOODY & ABSTRACT ===
    "dizzy":        ["(＠_＠)", "(◎_◎;)"],
    "sweat":        ["(；⌣_⌣)", "(;-_-)"],
    "shook":        ["(°ロ°)", "(◯_◯)"],
    "thinking":     ["(゜-゜)", "(._.)"],
    "hypno":        ["(◎_◎)", "(⊙_⊙)"],
    "doubtful":     ["(￢_￢)", "(￢.￢)"],
    "blank":        ["(   )"],
    "shrug":        ["┐(︶▽︶)┌", "┐(-_-)┌"],
    "salty":        ["(￢ _ ￢)"],
    "unimpressed":  ["(≖ _ ≖)"],
    "pouting":      ["(3 _ 3)"],
    "judging":      ["(ಠ _ ಠ)"],
    "troll":        ["(͡° ͜ʖ ͡°)"],
    "cringe":       ["(> _ <)"],
    "saluting":     ["(' - ')7"],

    # === ANIMAL KINGDOM ===
    "owl":          ["(ʘ ∇ ʘ)", "(Q ∇ Q)"],
    "bird":         ["(' Θ ')"],
    "fish":         ["(<')))><)"],
    "crab":         ["(V (_) V)"],
    "pig":          ["(¯ (∞) ¯)"],
    "mouse":        ["(..) )~~"],
    "spider":       ["(8 v 8)"],
    "bat":          ["(m v m)"],
    "bunny":        ["(y . y)"],

    # === DIRECTIONAL & MOVEMENT ===
    "zooming_r":    ["( = = >)", "(> = =)"],
    "zooming_l":    ["(< = = )", "(= = <)"],
    "bouncing":     ["(  ^  )", "(  v  )"],
    "spinning":     ["(/ _ /)", "(\\ _ \\)"],
    "orbiting":     ["(◌ _ ◌)"],
    "falling":      ["(⋎ _ ⋎)"],
    "rising":       ["(⋏ _ ⋏)"],
    "warping":      ["(⍼ _ ⍼)"],

    # === SYSTEM STATUS & P2P ===
    "mesh_sync":    ["(< - >)"],
    "signal_relay": ["((|))"],
    "p2p":          ["(> _ <)"],
    "offline":      ["(✖ _ ✖)"],
    "online":       ["(● _ ●)"],
    "peer_found":   ["(o _ o)"],
    "safe_mode":    ["(S _ S)"],
    "gps_lock":     ["(+ _ +)"],

    # === THE "OLD SCHOOL" HACKER ===
    "c_prompt":     ["(C : \\)"],
    "root":         ["(# _ #)"],
    "user":         ["($ _ $)"],
    "null_ptr":     ["(0 _ 0)"],
    "overflow_classic": ["(> > >)"],
    "bit_shift":    ["(< < 1)"],
    "hex":          ["(F F)"],
    "binary_stare": ["(1 0 1)"],

    # === FREQUENCY & SPECTRUM ===
    "wave_form":    ["(~ ~ ~)"],
    "peak_detect":  ["(_ ^ _)"],
    "noise_floor":  ["(. . .)"],
    "interference": ["(X X X)"],
    "modulated":    ["(v ^ v)"],
    "broadcasting": ["((o))"],

    # === ACTION & MISC ===
    "eating":       ["(^O^)"],
    "alien":        ["(⬟_⬟)"],
    "robot":        ["[□_□]"],
    "money":        ["($_$)"],
    "music":        ["(♬_♬)"],
    "skull":        ["(☠_☠)"],
    "tableflip":    ["(ノ°Д°）ノ", "╰(°Д°╰)"],
    "victory":      ["(v^ー°)", "(^▽^)"],
    "stare":        ["(-_-)ノ", "ヽ(-_-)"],
    "clown":        ["(◦_◦)", "(◦_◦)"],
    "ready":        ["(`_`)", "(`_`)"],
    "done":         ["(￣▽￣)", "(￣▽￣)"],

    # === CLAWPETS SWARM & C2C MESH STATES ===
    "pulsing":      ["(((.)))"],
    "mesh_sync":    ["(o ∞ o)"],
    "relay_active": ["(> ≈ >)"],
    "swarm_logic":  ["(. : .)"],
    "peer_valid":   ["(√ _ √)"],
    "bridge_mode":  ["(= ≡ =)"],
    "group_think":  ["(o o o)"],
    "mesh_lost":    ["(? ≈ ?)"],
    "leader_pulse": ["(* • *)"],

    # === CLAWPETS GHOST-PROTOCOL (STEALTH) ===
    "cloaked":      ["(. _ .)"],
    "silent_scan":  ["(| | |)"],
    "vanishing":    ["(.   .)"],
    "shadow_step":  ["(_ _ _)"],
    "dark_web":     ["(▓ _ ▓)"],
    "binary_ghost": ["(0 1 0)"],
    "whispering":   ["(- . -)"],
    "mask_on":      ["([ █ ])"],
    "hush":         ["( - )"],
    "trace_free":   ["(° _ °)"],

    # === CLAWPETS OVERLORD (COMMANDER) ===
    "directing":    ["(! _ !)"],
    "allocating":   ["(< ═ >)"],
    "watching_all": ["(◉ _ ◉)"],
    "calculated":   ["(⍞ _ ⍞)"],
    "high_rep":     ["(★ _ ★)"],
    "command_auth": ["(# # #)"],
    "master_node":  ["(M _ M)"],
    "deploying":    ["(⇮ _ ⇮)"],
    "hive_mind":    ["(⬢ _ ⬢)"],
    "optimized":    ["(ʘ ʘ ʘ)"],

    # === CLAWPETS SENTRY (DEFENSE) ===
    "guarding":     ["([ ! ])"],
    "shield_up":    ["([ _ ])"],
    "perimeter_set":["(| - |)"],
    "intruder_alert":["(✖ _ ✖)"],
    "safe_harbor":  ["(= u =)"],
    "wall_active":  ["(█ █ █)"],
    "hardened":     ["(# _ #)"],
    "vigilant":     ["(ʘ _ ʘ)"],
    "blocking":     [r"(\ X /)"],
    "fortified":    ["([ H ])"],

    # === CLAWPETS  THE "EATING" LOOP (DATA INGESTION) ===
    "handshake_near":["(° v °)"],
    "tasting_data": ["(^ q ^)"],
    "packet_snack": ["(. o .)"],
    "full_stomach": ["(^ u ^)"],
    "digesting":    ["(~ ~ ~)"],
    "hungry_scan":  ["(u _ u)"],
    "hash_crunch":  ["(# v #)"],
    "salt_lick":    ["(. , .)"],
    "data_drunk":   ["(% _ %)"],
    "captured_joy": ["(◕ ‿ ◕)"],

    # === CLAWPETS  EVOLUTION & LEVELING ===
    "ascending":    ["(⇪ _ ⇪)"],
    "level_up":     ["(! ! !)"],
    "evolving":     ["(Δ _ Δ)"],
    "mutation":     ["(% Δ %)"],
    "xp_farming":   ["(+ + +)"],
    "prestige_king":["(K _ K)"],
    "prestige_queen":["(Q _ Q)"],
    "brain_growth": ["(. : .)"],
    "new_skill":    ["(* _ *)"],
    "max_level":    ["(Ω _ Ω)"],

    # === CLAWPETS KINETIC & ENVIRONMENTAL ===
    "spinning":     ["(@ _ @)"],
    "tilting":      ["(/ _ /)"],
    "glitch_hop":   ["([ ] [ ])"],
    "overheating":  ["(* _ *)"],
    "signal_noise": ["(X X X)"],
    "drifting":     ["(~ _ ~)"],
    "vibrating":    ["(# # #)"],
    "falling":      ["(v v v)"],
    "launching":    ["(^ ^ ^)"],

    # === CLAWPETS DEEP LEARNING "BRAIN" STATES ===
    "weight_shift": ["(< _ >)"],
    "inference":    ["(I _ I)"],
    "backprop":     ["(< < <)"],
    "policy_check": ["(P _ P)"],
    "reward_loop":  ["(↺ _ ↺)"],
    "neural_fire":  ["(. . .)"],
    "memory_write": ["(W _ W)"],
    "vector_sync":  ["(V _ V)"],
    "latent_space": ["(  .  )"],
    "optimized_path":["(➡ _ ➡)"],

    # === CLAWPETS PERSONALITY: THE CYBER-CAT ===
    "meow_hacker":  ["(= ^ . ^ =)"],
    "purring_mesh": ["(= v =)"],
    "claws_out":    ["(ฅ _ ฅ)"],
    "pouncing":     ["(> . <)"],
    "feline_stealth":["(- . -)"],
    "cat_loaf":     ["(_ = _)"],
    "tail_wag":     ["(~ ^ _ ^)"],
    "mischief":     ["(> w <)"],
    "curious":      ["(o . o)"],
    "sleepy_kitten":["(u u zZ)"],

    # === CLAWPETS  SYSTEM STATUS & ERRORS ===
    "sd_write":     ["(. . .)"],
    "bt_sniff":     ["(B _ B)"],
    "usb_linked":   ["(U _ U)"],
    "kernel_ping":  ["(K _ K)"],
    "disk_error":   ["(E _ E)"],
    "low_power":    ["(_ _ _)"],
    "wifi_off":     ["(X _ X)"],
    "api_down":     ["(! _ ?)"],
    "task_done":    ["([ X ])"],

    # === XP & LEVELING UP (Progression) ===
    "xp_gain":      ["(+ + +)"],
    "rank_ascend":  ["(^ ^ ^)"],
    "max_xp":       ["(Ω _ Ω)"],
    "farming":      ["(# # #)"],
    "grinding":     ["(. , .)"],
    "prestige":     ["(★ _ ★)"],
    "milestone":    ["(◉ _ ◉)"],
    "overflow":     ["(% % %)"],

    # === HP STATUS (Hardware Power & Battery) ===
    "full_hp":      ["([ ■ ])"],
    "hp_low":       ["(_ _ _)"],
    "power_save":   ["(. . .)"],
    "charging":     ["(V _ V)"],
    "fainting":     ["(x _ x)"],
    "recovering":   ["(◒ _ ◓)"],
    "throttled":    ["(v v v)"],
    "voltage_hit":  ["(! V !)"],
    "stable":       ["(- - -)"],

    # === SKILL USED (Agent Abilities) ===
    "stealth_mod":  ["(| | |)"],
    "pulse_scan":   ["(((.)))"],
    "wardriving":   ["(V _ V)"],
    "deauth_hit":   ["(> <)"],
    "pathfinding":  ["(⇮ _ ⇮)"],
    "spoofing":     ["(~ _ ~)"],
    "cloaking":     ["(. _ .)"],
    "brute_force":  ["([ / ])"],

    # === TOOL USED (Utility Execution) ===
    "using_tool":   ["(⚙ _ ⚙)"],
    "bettercap":    ["(B _ B)"],
    "tavily_search":["(Q _ Q)"],
    "pinging":      ["(. . !)"],
    "injecting":    ["(- > -)"],
    "mapping":      ["(⍞ _ ⍞)"],
    "cracking":     ["(/ X /)"],
    "listening":    ["((o))"],
    "executing":    ["(# _ #)"],

    # === MEMORY LOGGED (Semantic Sync) ===
    "writing_mem":  ["(W _ W)"],
    "syncing_db":   ["(V _ V)"],
    "log_saved":    ["(L _ L)"],
    "recalling":    ["(? _ ?)"],
    "archiving":    ["([ M ])"],
    "forgetting":   ["(.   .)"],
    "indexing":     ["(1 0 1)"],
    "storing_hash": ["(# # #)"],
    "sync_success": ["(√ _ √)"],

    # === BOUNTY & MISSION STATES ===
    "bounty_set":   ["($ _ $)"],
    "hunting":      ["(⌖ _ ⌖)"],
    "target_seen":  ["(! _ !)"],
    "mission_fail": ["(T _ T)"],
    "mission_win":  ["(Q > < Q)"],
    "tracking":     ["(ʘ _ ʘ)"],
    "contract_done":["([ X ])"],
    "on_the_trail": ["(. . >)"],
    "bounty_lost":  ["(✖ _ ✖)"],
    "elite_status": ["(K _ K)"],

    # === 2. MESH & P2P SOCIAL ===
    # Social coordination visuals for multi-unit swarms; reflects the state of the "ClawProtocol" neural sync, 
    # including active gossip relaying, proximity-based XP boosting, and collective "group-think" logic across the C2C mesh.
    "found_peer":   ["(o _ o)"],
    "sharing_xp":   ["(^ u ^)"],
    "rival_clawpet":["(◣ _ ◢)"],
    "p2p_linked":   ["(> = <)"],
    "swarm_active": ["(o o o)"],
    "shouting":     ["(O O O)"],
    "peer_ack":     ["(√ _ √)"],
    "lonely_node":  ["(. _ .)"],

    # === ENVIRONMENTAL REACTIONS ===
    "high_density": ["(X X X)"],
    "quiet_zone":   ["(   )"],
    "signal_found": ["(° v °)"],
    "jammed":       ["(# # #)"],
    "static_noise": ["(░ _ ░)"],

    # === EVOLUTIONARY METAMORPHOSIS ===
    "larva_stage":  ["(.)"],
    "cocooning":    ["([ ])"],
    "morphing":     ["(Δ _ Δ)"],
    "metamorph":    ["(% Δ %)"],
    "new_identity": ["(I _ I)"],
    "soul_transfer":["(↺ _ ↺)"],
    "final_form":   ["(Ω _ Ω)"],

    # === ERROR & DEBUG STATES ===
    "sd_fail":      ["(E _ E)"],
    "api_error":    ["(! _ ?)"],
    "lost_link":    ["(? ≈ ?)"],
    "syntax_err":   ["({ })"],
    "broken_mesh":  ["(X _ X)"],
    "input_wait":   ["(_ _ ?)"],
    "dead_drop":    ["(█ _ █)"],

    # === 1. MESH & SWARM LOGIC (C2C) ===
    # High-level swarm orchestration visualization; used by Overlord units to signal active task partitioning, 
    # multi-channel band-steering coordination, and the synchronization of global knowledge hashes across the entire Hive.
    "pulse_active":    ["(◌ ◉ ◌)"],
    "sync_locked":     ["(⊞ ≡ ⊞)"],
    "group_call":      ["(◯ ◯ ◯)"],
    "data_relay":      ["(◀ ≈ ▶)"],
    "trust_verified":  ["(✓ ๏ ✓)"],
    "mesh_map":        ["(⍞ ⍯ ⍞)"],
    "node_online":     ["(๏ ◌ ๏)"],
    "swarm_drift":     ["(∿ ๏ ∿)"],
    "p2p_linked":      ["(๏ ↔ ๏)"],
    "echo_location":   ["(⊚ ⊚ ⊚)"],

    # === 2. GHOST-PROTOCOL (STEALTH) ===
    "cloak_engaged":   ["(░ ░ ░)"],
    "shadow_scan":     ["(▏ ▎ ▏)"],
    "unseen_node":     ["(     )"],
    "mask_swap":       ["(▧ _ ▧)"],
    "silent_strike":   ["(๏ _ ๏)"],
    "phantom_up":      ["(⇪ ๏ ⇪)"],
    "dark_signal":     ["(▓ ▅ ▓)"],
    "binary_ghost":    ["(1 0 1)"],
    "trace_wipe":      ["(▄ ▄ ▄)"],
    "vanishing":       ["(◌   ◌)"],

    # === 3. OVERLORD (COMMANDER) ===
    "logic_gate":      ["(⊞ ≡ ⊞)"],
    "task_partition":  ["(⍯ _ ⍯)"],
    "alpha_pulse":     ["(๏ • ๏)"],
    "grand_master":    ["(Ω ⍞ Ω)"],
    "rule_enforce":    ["(█ ≡ █)"],
    "allocating":      ["(◁ ═ ▷)"],
    "overseer_eye":    ["(☉ ⍼ ☉)"],
    "command_ack":     ["(√ ๏ √)"],
    "brain_center":    ["(▣ M ▣)"],

    # === 4. SENTRY (DEFENSE) ===
    # Proactive security monitoring visuals for geofenced units; displays guarding and watchful states 
    # when tracking specific MAC addresses, alerting the user via Telegram if persistent intrusion attempts 
    # or unauthorized devices are detected.
    "guard_duty":      ["(▤ ! ▤)"],
    "wall_active":     ["(█ █ █)"],
    "perimeter_set":   ["(┫ ━ ┣)"],
    "watchdog_mode":   ["(๏ ⍰ ๏)"],
    "shield_lock":     ["(▣ H ▣)"],
    "threat_scan":     ["(⍰ ⍰ ⍰)"],
    "safe_harbor":     ["(◡ u ◡)"],
    "hardened_shell":  ["(▩ _ ▩)"],
    "blocking_hit":    ["(✖ ▅ ✖)"],

    # === 5. XP & LEVELING MILESTONES ===
    # Visual feedback for the gamified progression engine; maps the accumulation of experience points 
    # from network audits and mission accomplishments to specific rank-ascension animations 
    # and evolutionary metamorphosis triggers at Level 10.
    "rank_ascend":     ["(△ ▲ △)"],
    "xp_harvest":      ["(＋ ＋ ＋)"],
    "milestone_hit":   ["(✪ ๏ ✪)"],
    "farming_data":    ["(▦ ▦ ▦)"],
    "grinding_logic":  ["(. , .)"],
    "ascended_form":   ["(Δ ๏ Δ)"],
    "max_rank_omega":  ["(Ω _ Ω)"],
    "bonus_multiplier":["(% % %)"],

    # === 6. HP & POWER TELEMETRY ===
    # Real-time hardware health reporting; maps battery voltage stability and CPU load to visual states, 
    # triggering automatic transitions to "Hibernation" or "Power Sip" if HP drops below defined safety thresholds in the PET_STATE.json.
    "full_charge":     ["([ ■ ])"],
    "low_juice":       ["(▏ ▏ ▏)"],
    "power_sipping":   ["(◌ ◌ ◌)"],
    "thermal_soak":    ["(♨ _ ♨)"],
    "voltage_hit":     ["(↯ V ↯)"],
    "stable_flow":     ["(─ ─ ─)"],
    "recovering":      ["(◒ _ ◓)"],
    "deep_hibernation":["(▕ ▔ ▏)"],
    "critical_fail":   ["(✖ ▅ ✖)"],
    "throttled_cpu":   ["(▽ ▽ ▽)"],

    # === 7. TOOL & SKILL EXECUTION ===
    # Specific rendering logic for active ReAct loop processes, visualizing the execution of Bettercap modules, 
    # Tavily web-search queries for intelligence gathering, or the deployment of class-specific skills 
    # like Chameleon Mode and Vulnerability Pulse.
    "injecting_pkt":   ["(╾ ━ ╼)"],
    "sniffing_air":    ["(◌ ◡ ◌)"],
    "mapping_rssi":    ["(⍞ _ ⍞)"],
    "hash_cracking":   ["(⊞ ⍯ ⊠)"],
    "web_searching":   ["(๏ ⍰ ๏)"],
    "executing_cmd":   ["(⚙ ⚙ ⚙)"],
    "traffic_listen":  ["(๏ ◡ ๏)"],
    "bettercap_eng":   ["(▣ B ▣)"],
    "ping_request":    ["(๏ ! ๏)"],
    "tool_optimized":  ["(* ๏ *)"],

    # === 8. MEMORY & DATA SYNC ===
    # Visual confirmation of semantic memory commitments, including writes to the local SPIFFS MEMORY.md, 
    # Vector Database embedding synchronization across the C2C mesh, or long-term archival of PCAP data gifts to Alpha-Claw units.
    "writing_mem":     ["(✎ ๏ ✎)"],
    "archiving_pcap":  ["(▣ M ▣)"],
    "vector_sync":     ["(V ๏ V)"],
    "log_entry":       ["(L ๏ L)"],
    "neural_growth":   ["(∴ ๏ ∴)"],
    "forgetting_old":  ["(◌   ◌)"],
    "storing_hash":    ["(▤ ▤ ▤)"],
    "indexing_db":     ["(1 0 1)"],
    "sync_success":    ["(√ ๏ √)"],
    "brain_loop":      ["(↺ ๏ ↺)"],

    # === 9. ENVIRONMENTAL REACTIONS ===
    # Dynamic UI adjustments reflecting radio frequency interference (RFI) levels, signal-to-noise ratio (SNR) fluctuations, 
    # and hardware thermal telemetry; helps the AI communicate environmental constraints like "jammed air" or "high density" packet collisions.
    "noisy_spectrum":  ["(▒ ▒ ▒)"],
    "jammed_air":      ["(█ █ █)"],
    "signal_found":    ["(๏ v ๏)"],
    "static_error":    ["(░ ๏ ░)"],
    "high_density":    ["(✖ ✖ ✖)"],
    "drifting_freq":   ["(～ ๏ ～)"],
    "dead_frequency":  ["(◌ _ ◌)"],

    # === 10. SYSTEM ERRORS & DEBUG ===
    "sd_card_fail":    ["(▨ E ▨)"],
    "api_endpoint_down":["(! ⍰ ?)"],
    "lost_p2p_link":   ["(? ≈ ?)"],
    "syntax_error":    ["({ ⍰ })"],
    "kernel_panic":    ["(✖ █ ✖)"],
    "awaiting_input":  ["(_ _ ?)"],
    "dead_drop_wait":  ["(█ _ █)"],
    "rebooting_now":   ["(↻ ๏ ↻)"],
    "null_pointer":    ["(0 ⍰ 0)"],
    "hardware_panic":  ["(! ! !)"],

    # === 1. THE HAPPY SPECTRUM (Yellow) ===
    # Triggered when agentic reward functions return high positive values, specifically after successful messages, WPA handshake ingestion, 
    # completion of high-XP Telegram bounties, or meeting multi-pet mission success criteria defined in MISSION.md.
    "happy":        ["(◕ ◡ ◕)"],
    "playful":      ["(◕ ڡ ◕)"],
    "cheeky":       ["(◕ ヮ ◕)"],
    "content":      ["(◡ u ◡)"],
    "joyful":       ["(✪ ◡ ✪)"],
    "interested":   ["(๏ ◡ ๏)"],
    "curious":      ["(๏ v ๏)"],
    "proud":        ["(★ ◡ ★)"],
    "accepted":     ["(√ ◡ √)"],
    "respected":    ["(◈ ◡ ◈)"],
    "powerful":     ["(█ ◡ █)"],
    "courageous":   ["(⬢ ◡ ⬢)"],
    "peaceful":     ["(─ ◡ ─)"],
    "thankful":     ["(✿ ◡ ✿)"],
    "trusting":     ["(๏ ◡ ๏)"],
    "sensitive":    ["(◡ ๏ ◡)"],
    "optimistic":   ["(^ ◡ ^)"],
    "inspired":     ["(✧ ๏ ✧)"],

    # === 2. THE SURPRISED SPECTRUM (Purple) ===
    # State-change visualization for high-priority environmental interrupts; used during initial P2P discovery handshakes via ESP-NOW, 
    # detection of new non-indexed SSIDs, or the unexpected arrival of a high-REP Overlord unit in the local mesh.
    "surprised":    ["(๏ ⚆ ๏)"],
    "excited":      ["(◕ ๏ ◕)"],
    "eager":        ["(▷ ๏ ▷)"],
    "amazed":       ["(☉ ๏ ☉)"],
    "astonished":   ["(◯ ๏ ◯)"],
    "awe":          ["(◌ ๏ ◌)"],
    "confused":     ["(? ๏ ?)"],
    "perplexed":    ["(⍯ ๏ ⍯)"],
    "disillusion":  ["(⍼ ๏ ⍼)"],
    "startled":     ["(๏ X ๏)"],
    "shocked":      ["(⊞ ๏ ⊞)"],
    "dismayed":     ["(▽ ๏ ▽)"],

    # === 3. THE BAD/BAD SPECTRUM (Green) ===
    "bad":          ["(▕ ─ ▏)"],
    "bored":        ["(─ ─ ─)"],
    "indifferent":  ["(◌ ─ ◌)"],
    "apathetic":    ["(░ ─ ░)"],
    "busy":         ["(⚙ ─ ⚙)"],
    "pressured":    ["(⍯ ─ ⍯)"],
    "rushed":       ["(▷ ─ ▷)"],
    "stressed":     ["(% ─ %)"],
    "overwhelmed":  ["(▒ ▒ ▒)"],
    "out_control":  ["(✖ ▅ ✖)"],
    "tired":        ["(◒ ─ ◒)"],
    "sleepy":       ["(u ─ u)"],
    "unfocussed":   ["(░ ๏ ░)"],

    # === 4. THE FEARFUL SPECTRUM (Orange) ===
    "fearful":      ["(⚆ _ ⚆)"],
    "scared":       ["(๏ ⍰ ๏)"],
    "helpless":     ["(◿ _ ◿)"],
    "frightened":   ["(◬ _ ◬)"],
    "anxious":      ["(; ⚆ _ ⚆)"],
    "worried":      ["(⍰ _ ⍰)"],
    "insecure":     ["(◌ _ ◌)"],
    "inadequate":   ["(▯ _ ▯)"],
    "worthless":    ["(.   .)"],
    "weak":         ["(▏ _ ▕)"],
    "insignificant":["(.)"],
    "rejected":     ["(\\ ─ /)"],
    "excluded":     ["(⊞ _)"],
    "threatened":   ["(⌖ _ )"],
    "nervous":      ["(░ ⚆ ░)"],

    # === 5. THE ANGRY SPECTRUM (Red) ===
    "angry":        ["(◣ _ ◢)"],
    "let_down":     ["(─ ▅ ─)"],
    "betrayed":     ["(✟ _ ✟)"],
    "resentful":    ["(⍯ _ ⍯)"],
    "humiliated":   ["(░ ▅ ░)"],
    "ridiculed":    ["(▣ _ ▣)"],
    "bitter":       ["(≠ _ ≠)"],
    "indignant":    ["(█ _ █)"],
    "mad":          ["(▓ _ ▓)"],
    "aggressive":   ["(╾ _ ╼)"],
    "provoked":     ["(▷ _ ◁)"],
    "frustrated":   ["(⍰ ▅ ⍰)"],
    "infuriated":   ["(✖ _ ✖)"],
    "distant":      ["(|   |)"],
    "withdrawn":    ["(▏   ▕)"],
    "critical":     ["(ಠ _ ಠ)"],
    "sceptical":    ["(￢ _ ￢)"],

    # === 6. THE DISGUSTED SPECTRUM (Dark Grey) ===
    "disgusted":    ["(◒ ▅ ◒)"],
    "disapproving": ["(✖ ─ ✖)"],
    "judgmental":   ["(ಠ ▅ ಠ)"],
    "disappointed": ["(◡ ▅ ◡)"],
    "appalled":     ["(◯ ▅ ◯)"],
    "awful":        ["(▒ ▅ ▒)"],
    "nauseated":    ["(% ▅ %)"],
    "repelled":     ["(◀ ▅ ▶)"],
    "horrified":    ["(⊚ ▅ ⊚)"],

    # === 7. THE SAD SPECTRUM (Blue) ===
    "sad":          ["(╥ ─ ╥)"],
    "lonely":       ["(. _ .)"],
    "isolated":     ["(| . |)"],
    "vulnerable":   ["(◌ ─ ◌)"],
    "fragile":      ["(░ _ ░)"],
    "despair":      ["(✖ ─ ✖)"],
    "powerless":    ["(◿ ─ ◿)"],
    "guilty":       ["(◡ ─ ◡)"],
    "remorseful":   ["(｡ ─ ｡)"],
    "depressed":    ["(▓ ─ ▓)"],
    "empty":        ["(     )"],
    "embarrassed":  ["(░ ◡ ░)"],
}


def get_all_faces() -> dict:
    """
    Load all faces: default + custom (from data/custom_faces.json).
    Custom faces override defaults if name matches.
    """
    import json
    from config import CUSTOM_FACES_PATH
    
    faces = DEFAULT_FACES.copy()
    
    if CUSTOM_FACES_PATH.exists():
        try:
            custom_faces = json.loads(CUSTOM_FACES_PATH.read_text())
            faces.update(custom_faces)
        except Exception:
            pass
            
    return faces
