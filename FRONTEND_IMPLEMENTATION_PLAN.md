# TRINETRA AI Frontend Implementation Plan

This plan details the audit results, proposed architectural improvements, design enhancements, and implementation details for the TRINETRA AI frontend dashboard.

---

## 1. Audit & Architectural Review

During the audit of the frontend repository, we identified several critical issues and enhancement opportunities:

*   **Missing QueryClientProvider**: The application imports `@tanstack/react-query` but does not instantiate or wrap the routing tree with `QueryClientProvider`. This would cause the app to crash on any page utilizing React Query hooks.
*   **Import Bug in Live.jsx**: `Live.jsx` imports `useStats` from `../hooks/useViolations`, but `useStats` is actually defined in `../hooks/useAnalytics`.
*   **Placeholder Image Uri in Evidence.jsx**: The evidence page displays `Image: {violation.evidence_uri}` as a text string instead of loading the actual annotated JPEG served from the backend's `/evidence` static files mount.
*   **Missing Pages**: The frontend lacks dedicated views for:
    *   Consolidated Overview Dashboard (KPI cards + Recent Activity Feed).
    *   Image-based Detection Upload (`POST /detect` integration).
    *   Video-based Detection Upload (`POST /detect-video` integration).
    *   Visual Analytics & Hotspot plotting.
*   **Aesthetics**: The current design uses default browser layouts and generic gray panels. To make this suitable for Flipkart GRID judging, we will implement a premium **Dark-Tech Cybernetic Command Center** UI with vibrant neon warning highlights, smooth micro-animations, glassmorphic card overlays, and clean typographic scaling.

---

## 2. Design System & Aesthetics (Flipkart GRID Focus)

To ensure the interface feels state-of-the-art and visually premium:
*   **Background**: Deep workspace theme (`bg-slate-950` / `bg-zinc-950`).
*   **Cards & Glassmorphism**: Translucent cards using `bg-slate-900/60 backdrop-blur-md border border-slate-800`.
*   **Neon Color Accents**:
    *   `CRITICAL / DANGER` -> Violet-Red / Magenta (`text-rose-500`, border/glow matching).
    *   `HIGH RISK / WARNING` -> Vivid Orange (`text-amber-500`).
    *   `LOW RISK / SUCCESS` -> Emerald Green (`text-emerald-400`).
    *   `PROCESSING / SYSTEMS` -> Electric Cyan (`text-cyan-400`).
*   **Typography**: High-tech display fonts (loaded via Google Fonts) like **Outfit** or **Inter**, with clean monospaced font family for License Plates (`font-mono tracking-wider`).
*   **Transitions**: Smooth hover states, glowing border triggers, and fade-in animations.

---

## 3. Detailed Component & Page Specifications

### A. App Setup & Navigation
*   Initialize `QueryClient` and wrap the router in `<QueryClientProvider client={queryClient}>` inside [App.jsx](file:///d:/GRIDLOCK/frontend/src/App.jsx).
*   Add a Google Fonts import in [index.html](file:///d:/GRIDLOCK/frontend/public/index.html) to load **Outfit** and **JetBrains Mono**.
*   Revamp [Header.jsx](file:///d:/GRIDLOCK/frontend/src/components/Header.jsx) to support the new page routes:
    *   `Dashboard` (`/`)
    *   `Image Detect` (`/detect`)
    *   `Video Detect` (`/video-detection`)
    *   `Live Stream` (`/live-feed`)
    *   `Analytics` (`/analytics`)

---

### B. Dashboard Page (`Dashboard.jsx` at `/`)
*   **KPI Panel**: Four large glowing metric cards:
    *   **Total Violations**: `stats.total_violations`.
    *   **Critical Violations**: `stats.risk_distribution.CRITICAL` (score >= 80).
    *   **Today's Violations**: `stats.today_violations`.
    *   **Total Vehicles Processed**: Estimated dynamically as `stats.total_violations * 1.5` plus active session processing counts, since SQLite only stores violations.
*   **Recent Violations Feed**: Auto-polling recent violations stream with quick action buttons. Clicking on any entry redirects to the `/evidence/:id` page.
*   **Quick Execution Panel**: Diagnostic grid to jump straight into image or video analysis.

---

### C. Image Detection Page (`Detection.jsx` at `/detect`)
*   **Interactive Upload**: Drag-and-drop or select box with support for image formats.
*   **Dual-Pane View**:
    *   *Left Pane*: Interactive preview of uploaded image / annotated result.
    *   *Right Pane*: Interactive analysis table listing all vehicles found in the frame.
*   **Detection Results**:
    *   Overall risk score gauge (circle diagram with neon rings).
    *   List of detected vehicles. For each vehicle:
        *   Plate OCR (with details: original vs. enhanced OCR confidence from hybrid strategy).
        *   Vehicle crop if generated.
        *   Associated violations (No Helmet, Triple Riding) shown as badges.
        *   Associated risk score.

---

### D. Video Detection Page (`VideoDetection.jsx` at `/video-detection`)
*   **Drag-and-Drop Video Area**: Supports `.mp4`, `.avi`, `.mov`.
*   **Upload & Process States**: Shows processing feedback with execution messages.
*   **Process Report**:
    *   Total frames processed & violations detected.
    *   Scrollable grid of detected violating frames.
    *   Table listing plate numbers, violation categories, timestamps, and confidence values.

---

### E. Analytics Page (`Analytics.jsx` at `/analytics`)
*   **Violation Type Distribution**: Recharts `BarChart` / `AreaChart` plotting violation counts.
*   **Risk Profile Breakdown**: Recharts radial/pie diagram displaying `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` risk distributions.
*   **Hotspot Maps**: Integrated Leaflet map rendering location-based hotspots parsed from GeoJSON coordinates returned by `GET /api/v1/analytics/heatmap`.
*   **Manpower Forecasting**: Line chart displaying predictive manpower officer requirements.

---

### F. Evidence Viewer Page (`Evidence.jsx` at `/evidence/:id`)
*   **Annotated Frame Viewer**: Loads the actual JPG file directly from `http://localhost:8000/` + `violation.evidence_uri`.
*   **Detailed Analytics Summary**:
    *   License Plate with confidence metrics.
    *   Speed, density, and local safety zone variables.
    *   Generated enforcement report text.
*   **Tamper-Evident Security Badge**: Renders the SHA-256 cryptographic hash of the image and the chain pointer, proving the digital evidence has not been modified.
*   **Verification Workflow**: Live `Verify` and `Reject` buttons that update SQLite statuses.

---

## 4. Proposed File Changes

```markdown
- [MODIFY] frontend/public/index.html (Load fonts: Outfit, JetBrains Mono)
- [MODIFY] frontend/src/App.jsx (Wrap in QueryClientProvider, update routes)
- [MODIFY] frontend/src/components/Header.jsx (Modern cyber-navbar, update routes)
- [MODIFY] frontend/src/pages/Live.jsx (Fix useStats import, change styling)
- [MODIFY] frontend/src/pages/Evidence.jsx (Display image, details, verify buttons, SHA hash)
- [NEW] frontend/src/pages/Dashboard.jsx (Consolidated KPI cards & Activity feed)
- [NEW] frontend/src/pages/Detection.jsx (Dual-pane image upload & result analyzer)
- [NEW] frontend/src/pages/VideoDetection.jsx (Video processor interface)
- [NEW] frontend/src/pages/Analytics.jsx (Recharts, Leaflet hotspot map, predictions)
```

---

## 5. Verification Plan

### Automated Build Checks
1. Compile and build the production bundle to verify zero compiler errors:
   `npm run build` in the `frontend` folder.

### Manual End-to-End Walkthrough
1. **Login Flow**: Log in using the default credentials (`demo` / `demo123`).
2. **Dashboard Verification**: Check statistics cards and ensure recent violations poll successfully.
3. **Image Detection**: Upload a test traffic image, wait for inference, and verify OCR output, annotated image mapping, and risk indicators.
4. **Video Detection**: Upload a traffic video, process it, and verify that the summary outputs frames processed and violation details.
5. **Analytics**: Verify Recharts visual renders, Leaflet maps, and risk profile counts.
6. **Evidence Page**: Click a violation to verify the evidence image, tamper hash, and action buttons.
