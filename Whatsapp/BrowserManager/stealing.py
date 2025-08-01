from playwright.sync_api import Page
from playwright_stealth import Stealth


def stealth(page: Page) -> None:
    """
    Applies stealth techniques and JS spoofing to the given page.
    :return: Page itself
    """
    s = Stealth()
    s.apply_stealth_sync(page)
    page.add_init_script(_custom_js_spoof_payload())
    page.add_init_script(Mouse_UI)
    print("[[Stealth scripts and Mouse UI injected]]")
    print("----------------------------------------------------------")


Mouse_UI = """
window.addEventListener('DOMContentLoaded', () => {
  const dot = document.createElement('div');
  dot.id = '__mouse_dot__';
  Object.assign(dot.style, {
    position: 'fixed',
    width: '10px',
    height: '10px',
    borderRadius: '65%',
    backgroundColor: 'black',
    zIndex: '2147483647',  // Max z-index
    pointerEvents: 'none',
    top: '0px',
    left: '0px',
    transform: 'translate(-50%, -50%)',
    transition: 'top 0.03s linear, left 0.03s linear'
  });
  document.body.appendChild(dot);
  window.addEventListener('mousemove', e => {
    dot.style.left = `${e.clientX}px`;
    dot.style.top = `${e.clientY}px`;
  });
});
"""

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
        // Object.defineProperty(navigator, 'doNotTrack', { get: () => '1' });

        // 🪟 Screen and Window
        Object.defineProperty(window, 'innerWidth', { get: () => 1301 });
        Object.defineProperty(window, 'innerHeight', { get: () => 724});
        Object.defineProperty(window, 'outerWidth', { get: () => 1301 });
        Object.defineProperty(window, 'outerHeight', { get: () => 724 });
        
        Object.defineProperty(window.screen, 'width', { get: () => 1301 });
        Object.defineProperty(window.screen, 'height', { get: () => 724 });
        Object.defineProperty(window.screen, 'availWidth', { get: () => 1301 });
        Object.defineProperty(window.screen, 'availHeight', { get: () => 724 });
        //Object.defineProperty(window.screen, 'colorDepth', { get: () => 24 });
        //Object.defineProperty(window.screen, 'pixelDepth', { get: () => 24 });

        //  Fake Chrome object to prevent runtime errors
        window.chrome = {
            runtime: {},
            webstore: {}
        };

        // 🔍 matchMedia override (updated logic)
        const originalMatchMedia = window.matchMedia;
        window.matchMedia = function(query) {
            const forcedMatch = /1301|724|max\-width|min\-width|max\-height|min\-height/.test(query);
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


headers = {

    "Origin": "https://web.whatsapp.com",
    "Referer": "https://web.whatsapp.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/138.0.0.0 Safari/537.36",
}
# ---- This is for the network calls
# "Content-Type": "application/json",
# "Origin": "https://www.example.com",
# "Referer": "https://www.example.com/home",

# "Sec-Ch-Ua": '"Chromium";v="120", "Google Chrome";v="120", "Not-A.Brand";v="99"',
# "Sec-Ch-Ua-Mobile": "?0", # 0, 1
# "Sec-Ch-Ua-Platform": "Windows", #Windows, macOS, Android
# "Viewport-Width": "1920", # Optional, but can help match screen

# "Accept": "text/html,application/xhtml+xml, application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
# "Accept-Encoding": "gzip, deflate, br",
# "Accept-Language": "en-US, en;q=0.9",
# "Cache-Control": "no-cache",
# "Upgrade-Insecure-Requests": "1",
# "DNT": "1",  # Do Not Track enabled
# "Sec-Fetch-Dest": "document",
# "Sec-Fetch-Mode": "navigate",
# "Sec-Fetch-Site": "none",
# "Sec-Fetch-User": "?1",



