---
name: ui-ux-pro-max
description: Anti-slop frontend design system combining UI/UX Pro Max design intelligence with Linear/Vercel precision B2B craft. Use for all UI components, layouts, typography, spacing, color tokens, and micro-interactions.
---

# UI/UX Pro Max + Linear Craft (Anti-Slop B2B Design Intelligence)

This skill provides a battle-tested, anti-AI-slop frontend design and UX framework designed specifically for high-converting B2B applications, directories, lead generation engines, and sales pipelines.

It enforces strict aesthetic standards, functional precision, and micro-interactions that mirror \$50M+ modern SaaS platforms (Linear, Supabase, Vercel, Stripe, Raycast).

---

## 🚫 1. Anti-AI-Slop Directives (Strict Rules)

AI-generated interfaces often look cheap, cookie-cutter, or chaotic ("AI Slop"). This skill strictly forbids the following anti-patterns:

| Priority | Anti-Pattern (AI Slop) | Required Standard (Linear / Pro Max Craft) |
| :--- | :--- | :--- |
| **P0** | **Emoji as UI Icons in Buttons/Tabs** (e.g. `[🚀 Başlat]`, `[💬 Sohbet]`) | **Pure SVG Icons (Lucide):** Emojis are strictly banned in UI buttons, tabs, chips, and badges. Use `<i data-lucide="..."></i>` with consistent stroke width (`1.5px` or `2px`). Emojis are only allowed in customer-facing message body text (WhatsApp pitches). |
| **P0** | **Purple/Violet Gradient Soup** | **Monochromatic Slate Base + Intentional Accents:** Backgrounds must be deep `slate-950` / `slate-900` in dark mode, and clean `slate-50` / `slate-100` in light mode. Accents must have clear semantic meaning (Emerald for money/WhatsApp, Indigo for software, Amber for stars/opportunity, Rose for security bugs). |
| **P0** | **Low Contrast & Illegible Text** | **WCAG 4.5:1 Strict Contrast:** Text must never be light grey on white or dark grey on black. Subtitles use `text-slate-600 dark:text-slate-400`. High-importance text uses `text-slate-900 dark:text-white`. |
| **P1** | **Floaty Bubble Corners (`rounded-3xl` everywhere)** | **Hierarchical Radius System:** Outer containers: `rounded-2xl` or `rounded-3xl`. Inner cards: `rounded-xl`. Buttons and inputs: `rounded-xl`. Tags and badges: `rounded-lg` or `rounded-full`. |
| **P1** | **Missing States (No Hover / Focus / Disabled)** | **Complete Micro-States:** Every interactive element must define: `hover:bg-...`, `active:scale-95 transition-all duration-200`, `focus-visible:ring-2 focus:ring-brand-500/30`, and `disabled:opacity-50 disabled:cursor-not-allowed`. |
| **P1** | **Cluttered Marketing Fluff & Centered Walls of Text** | **High Data Density Bento Grids:** Left-aligned, scannable cards with clear label-value pairings, monospace numbers for currency/phones, and tight visual groupings. |
| **P2** | **Tiny Inaccessible Touch Targets** | **44×44px Minimum (`touch-target`):** All clickable items on mobile and desktop must have at least 44px height/width or padding to prevent accidental misclicks. |

---

## 🎨 2. Color Palette & Semantic Tokens

### Neutral Foundation (Zero Dark-Mode Collision)
```css
/* Dark Mode */
--bg-page:        #020617; /* slate-950 */
--bg-surface:     #0f172a; /* slate-900 */
--bg-elevated:    #1e293b; /* slate-800 */
--border-subtle:  rgba(255, 255, 255, 0.08); /* 1px border */
--border-default: #334155; /* slate-700 */
--text-primary:   #f8fafc; /* slate-50 */
--text-secondary: #94a3b8; /* slate-400 */
--text-tertiary:  #64748b; /* slate-500 */

/* Light Mode */
--bg-page:        #f8fafc; /* slate-50 */
--bg-surface:     #ffffff; /* white */
--bg-elevated:    #f1f5f9; /* slate-100 */
--border-subtle:  #e2e8f0; /* slate-200 */
--border-default: #cbd5e1; /* slate-300 */
--text-primary:   #0f172a; /* slate-900 */
--text-secondary: #475569; /* slate-600 */
--text-tertiary:  #94a3b8; /* slate-400 */
```

### Semantic Accent Palettes
- **Brand / Primary:** Deep Indigo & Violet Tint (`#4f46e5` to `#6366f1`).
- **Revenue & Conversion:** Emerald (`#059669` / `#10b981`) for WhatsApp, closing deals, export.
- **Urgency & Opportunity:** Amber (`#d97706` / `#f59e0b`) for opportunity score, stars, warm leads.
- **Risk & Digital Gaps:** Rose (`#e11d48` / `#f43f5e`) for missing website, insecure SSL, critical vulnerabilities.

---

## 📐 3. Industry-Specific B2B Design Profiles

### A. Software & Tech Sales (KOBİ, Clinics, Agencies)
- **Vibe:** Sleek, engineered, modern B2B SaaS.
- **Key Elements:** Code brackets (`code-2`), live interactive demos, workflow automation diagrams, API health badges.
- **Palette Accent:** Indigo/Sky blue `#3b82f6`.

### B. Hair Dye & Salon Supply (Kuaför & Güzellik Salonları)
- **Vibe:** Clean, premium aesthetic, boutique wholesale.
- **Key Elements:** Palette swatches, wholesale box tiers, free sample trial kit badges, before/after shade references.
- **Palette Accent:** Rose/Pink `#ec4899` & Warm Slate.

### C. Industrial Steam Irons & Central Silter Boilers (Tekstil & Terziler)
- **Vibe:** Industrial reliability, workshop durability, engineering precision.
- **Key Elements:** Bar pressure indicators (`bar`), boiler capacity (`LT`), pipeline maintenance specs, spare parts stock badges.
- **Palette Accent:** Steel Blue `#2563eb` & Amber `#f59e0b`.

### D. Custom Products & Commerce
- **Vibe:** Flexible corporate procurement, distributor discounts, invoice terms.
- **Key Elements:** MOQ (Minimum Order Quantity), unit margins, lead times.

---

## ⚡ 4. Keyboard-First Interaction & Micro-UX

1. **Command Palette (`Cmd+K` / `Ctrl+K`):** Instant search across all campaigns, filters, tools, and actions without touching the mouse.
2. **Sequential Flow Hotkeys:** In rapid outreach and queue review, support `[` (Previous), `]` (Next), and `Esc` (Close/Cancel).
3. **Optimistic Feedback:** When clicking a 1-click action (e.g. WhatsApp / Copy / Advance), immediately update UI state and trigger audio/haptic feedback before waiting for background requests.
4. **Toast Feedback:** Never use browser `alert()`. Use auto-dismissing glass toasts with icon and status color.

---

## 🏗️ 5. Component Checklist (Before Shipping Any UI)

- [ ] Does every button use a Lucide SVG icon instead of an emoji?
- [ ] Are all touch targets at least 44×44px?
- [ ] Does the screen look balanced in both Dark Mode (`slate-950`) and Light Mode (`slate-50`)?
- [ ] Is there clear visual hierarchy between headers, data labels, and values?
- [ ] Are all interactive elements equipped with `active:scale-95` and focus rings?
- [ ] Are loading states (spinners/skeletons) and empty states clearly designed?
