# TRINETRA AI Frontend Redesign Preview

This document previews the visual redesign of TRINETRA AI into a premium **cyber-dark command center** tailored for judges. The new theme transitions the UI from excessive red/rose branding to a balanced, high-contrast, security-focused palette using cyber navy, neon cyan/blue accents, and color-coded status elements.

---

## 🎨 Theme & Color Palette Changes

| Styling Category | Current Theme (Slate + Rose/Red) | Redesigned Theme (Cyber Navy + Cyan) |
| :--- | :--- | :--- |
| **Global Background** | Deep Slate (`bg-slate-950`) with red radial glow | Dark Navy (`bg-[#050b18]`) with deep blue/cyan radial backdrop glows |
| **Primary Accents** | Rose/Red (`#ef4444`, `text-rose-500`, `from-red-600`) | Cyan/Blue (`#00f0ff`, `#0077ff`, `text-cyan-400`, `from-cyan-500 to-blue-600`) |
| **Healthy / Cleared Status** | Emerald Green/Slate | Neon Green (`#10b981`, `text-emerald-400`) |
| **Warnings / Medium Risk** | Amber (`#f59e0b`, `text-amber-500`) | Neon Amber (`#ff9f00`, `text-amber-400`) |
| **Critical Violations Only** | Red (`#ef4444`, `text-rose-500`) | Critical Threat Red (`#ff003c`, `text-red-500`) |
| **Glassmorphic Cards** | Standard border, slate card | High-transparency navy card (`bg-[#0b1329]/65 backdrop-blur-lg border-[#1e293b]/40`) |

---

## 🛠️ Key UI Modifications

### 1. Global Custom Variables & Buttons (`index.css` & `tailwind.config.js`)
* Update theme root values to map primary branding to cyan (`#00f0ff`) and warning/danger states to specific values.
* Convert the `.btn-primary` class to use a gradients of `from-cyan-600 to-blue-600` with cyan glows, replacing red gradients.
* Update global background linear gradients to reference deep indigo and dark navy (`bg-[#050b18]`).

### 2. Header Redesign (`Header.jsx`)
* Remove the red gradient inside the logo box and replace it with a glowing cyan neon border.
* Change "TRINETRA AI" logo styling: the AI text will be styled with text-cyan-400 instead of rose-500.
* Re-style active navigation items: change rose background highlight to cyan highlight (`bg-cyan-950/40 text-cyan-400 border-cyan-800/30`).

### 3. Dashboard Analytics & KPIs (`Dashboard.jsx`)
* Change the total violation count tile from a rose theme to a professional cyber-blue theme.
* Keep **Critical Violations** highlighted in deep red as they represent high risk.
* Change "ALL RUNTIME ENGINES ONLINE" to a neon-green pulse indicator.
* Update shortcut banners (Image Detect, Video Surveillance, Analytics) to showcase cyan icons and borders on hover.

### 4. Interactive Detection Portals (`Detection.jsx` & `VideoDetection.jsx`)
* Modify full-screen overlay colors: change rose spinner animations and step checks to neon cyan.
* Style detection result lists with cyan accents. Safe/Cleared vehicles receive neon green check indicators, while vehicles with violations receive red indicators.

### 5. Analytics Charts (`Analytics.jsx`)
* Recharts bar graphs will use a custom gradient filled with cyan/blue instead of red/rose.
* Pie charts will map risk levels precisely: Green (Low), Amber (Medium), Yellow-Orange (High), Red (Critical).
* Line graphs for violation trends will display a cyan-accent line.

### 6. Evidence Audit Chamber (`Evidence.jsx`)
* Replace red shield logos and focal points with cyan enforcement styling.
