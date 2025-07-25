from playwright.sync_api import Page
from playwright_stealth import Stealth


def stealth(page: Page) -> Page:
    """
    Applies stealth techniques and JS spoofing to the given page.
    :return: Page itself
    """
    s = Stealth()
    s.apply_stealth_sync(page)
    page.add_init_script(_custom_js_spoof_payload())
    print("🕵️ Stealth and spoof scripts injected.")
    return page


def _custom_js_spoof_payload():
    """
    Custom js Spoof -------
    :return: payload as String to run as a script.
    """
    return r"""
    (() => {
        // Removing webdriver 
        try {
            delete Object.getPrototypeOf(navigator).webdriver;
        } catch (e) {}

        // 🖼 Canvas Spoofing
        const toDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(...args) {
            const ctx = this.getContext('2d');
            const shift = 2;
            ctx.globalAlpha = 0.9;
            ctx.fillStyle = 'rgba(100,100,100,0.1)';
            ctx.fillRect(shift, shift, this.width - shift*2, this.height - shift*2);
            return toDataURL.apply(this, args);
        };

        // 📐 ClientRects Spoofing
        const origGetClientRects = Element.prototype.getClientRects;
        Element.prototype.getClientRects = function() {
            const rects = origGetClientRects.apply(this);
            for (const r of rects) {
                r.x += 0.1; r.y += 0.1;
                r.width += 0.1; r.height += 0.1;
            }
            return rects;
        };

        // 🎧 AudioContext Spoofing
        const origGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function() {
            const data = origGetChannelData.apply(this, arguments);
            for (let i = 0; i < data.length; i += 100) {
                data[i] += Math.random() * 1e-7;
            }
            return data;
        };

        // 🌐 WebRTC Leak Prevention
        function RTCPeerConnectionStub() {
            return {
                createOffer: async () => ({}),
                setLocalDescription: async () => {},
                addIceCandidate: async () => {},
                close: () => {},
                addEventListener: () => {},
                removeEventListener: () => {}
            };
        }
        Object.defineProperty(window, 'RTCPeerConnection', { value: RTCPeerConnectionStub });
        Object.defineProperty(window, 'webkitRTCPeerConnection', { value: RTCPeerConnectionStub });

        // 📱 mediaDevices spoof
        Object.defineProperty(navigator, 'mediaDevices', {
            value: {
                enumerateDevices: async () => [
                    { kind: 'audioinput',  label: 'Microphone', deviceId: 'mic1' },
                    { kind: 'videoinput', label: 'Webcam',    deviceId: 'cam1' },
                    { kind: 'audiooutput', label: 'Speaker',   deviceId: 'spk1' }
                ]
            }
        });

        // 🧠 Hardware Properties
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 16 });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });

        // 💻 Platform spoof (Match with UA)
        Object.defineProperty(navigator, 'platform', { get: () => 'Linux x86_64' });

        // 🌐 Do Not Track
        Object.defineProperty(navigator, 'doNotTrack', { get: () => '1' });

        // 🪟 Screen and Window
        Object.defineProperty(window, 'innerWidth', { get: () => 1920 });
        Object.defineProperty(window, 'innerHeight', { get: () => 1080 });
        Object.defineProperty(window, 'outerWidth', { get: () => 1920 });
        Object.defineProperty(window, 'outerHeight', { get: () => 1080 });

        Object.defineProperty(window.screen, 'width', { get: () => 1920 });
        Object.defineProperty(window.screen, 'height', { get: () => 1080 });
        Object.defineProperty(window.screen, 'availWidth', { get: () => 1920 });
        Object.defineProperty(window.screen, 'availHeight', { get: () => 1040 });
        Object.defineProperty(window.screen, 'colorDepth', { get: () => 24 });
        Object.defineProperty(window.screen, 'pixelDepth', { get: () => 24 });

        //  Fake Chrome object to prevent runtime errors
        window.chrome = {
            runtime: {},
            webstore: {}
        };

        // 🔍 matchMedia override (updated logic)
        const originalMatchMedia = window.matchMedia;
        window.matchMedia = function(query) {
            const forcedMatch = /1920|1080|max\-width|min\-width|max\-height|min\-height/.test(query);
            return {
                matches: forcedMatch,
                media: query,
                onchange: null,
                addListener: () => {},
                removeListener: () => {},
                addEventListener: () => {},
                removeEventListener: () => {},
                dispatchEvent: () => false
            };
        };
    })();
    """


def _get_plugins_spoof_script() -> str:
    return r"""
        (() => {
            const fakePlugins = [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
            ];
            Object.defineProperty(navigator, 'plugins', {
                get: () => fakePlugins,
                configurable: true
            });
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => fakePlugins.map(p => ({
                    type: p.name.toLowerCase().split(' ').join('/'),
                    suffixes: '',
                    description: p.description,
                    enabledPlugin: p
                })),
                configurable: true
            });
        })();
        """


def _get_webgl_spoof_script() -> str:
    return r"""
        (() => {
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(param) {
                if (param === 37445) return 'Intel Inc.';       // UNMASKED_VENDOR_WEBGL
                if (param === 37446) {                         // UNMASKED_RENDERER_WEBGL
                    const choices = [
                      'Intel Iris OpenGL Engine',
                      'NVIDIA GeForce GTX 1060',
                      'AMD Radeon Pro 560X OpenGL Engine'
                    ];
                    return choices[Math.floor(Math.random()*choices.length)];
                }
                return originalGetParameter.apply(this, arguments);
            };
        })();
        """


# WhatsApp specific for stopping the update writing and making it a persistent version.
"""
Object.defineProperty(navigator.serviceWorker, 'register', {
    value: () => Promise.resolve(),
    writable: false,
    configurable: true,
});

Object.defineProperty(Notification, 'permission', {
                get: () => 'granted'
            });
"""
