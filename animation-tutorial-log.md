# Animation Tutorial — Interaction Log

A running log of prompt→edit interactions for building technical canvas animations via AI chat. This will become the basis for a tutorial website.

---

## Session: 2026-02-26 — Rug Pull Widget

### Context
- Widget: `~/sites/testmachine/rug-pull-widget.html` — HTML5 canvas animation showing Bayesian token risk scoring
- Served at: demos.lightscalar.net/rug-pull-widget.html
- Built over multiple sessions, iterated via Telegram prompts

### Interaction Log

#### 1. Icon Design: Arrow → Bicep → Spring
**Prompt:** "Can we update the MoonPump logo a little bit? The arrow up is not great — maybe something more closely resembling a pump? Maybe a flexed bicep?"
**Action:** Replaced the upward arrow in `drawCoinIcon()` with a flexed bicep (forearm, upper arm, bicep arc, fist).
**Follow-up prompt:** "Also that MOONPUMP logo is difficult to understand. Maybe a spring or something more easily parsed at that scale?"
**Action:** Replaced bicep with spring coil — 4 sinusoidal loops with flat endcaps.
**Lesson:** At small icon scale (<30px), geometric primitives (coils, arrows, circles) read better than figurative drawings (biceps, hands). When the first attempt is too complex, go simpler, not different-complex.

#### 2. Risk Score Display
**Prompt:** "Can we have the current risk score for the probability distribution displayed somewhere, so we can see how it evolves as the distribution shifts?"
**Action:** Added real-time percentage readout computed as weighted mean of distribution. Positioned top-right of chart area. Color-coded: gray <60%, teal 60-79%, red ≥80%.
**Follow-up prompt:** "Risk Score needs to be better placed wrt the chart. It is hitting text above."
**Action:** Moved to bottom-left, below x-axis. "RISK SCORE" label with percentage next to it.
**Lesson:** First placement is often wrong — expect a positioning iteration. Put dynamic overlays where they won't clash with any animation state.

#### 3. Distribution Normalization
**Prompt:** "I want the probability density to shift more dramatically with each piece of evidence. Also, I want it to be normalized. That is, whatever the area under that curve is at the beginning, it needs to remain constant."
**Action:** Three changes:
1. Normalized all distribution stages to integrate to 1 (trapezoidal integration)
2. Changed `drawDist()` from max-normalization to fixed-scale rendering — visual area stays constant as curve sharpens
3. Made stage shifts more dramatic: means 0.5→0.68→0.82→0.94 with tighter sigmas
**Matthew's response:** "It is a probability distribution after all."
**Lesson:** Domain experts will catch mathematical incorrectness. If you're visualizing a well-defined mathematical object, get the math right first — it's not just aesthetics.

---

## Patterns Emerging

### Effective Prompt Patterns
1. **"Can we [verb] the [element]?"** — Open-ended change request. Interpret broadly.
2. **"The [element] is [problem]. Maybe [suggestion]?"** — Problem statement with optional direction. Fix the problem; the suggestion is a hint, not a spec.
3. **"Also, [new requirement]"** — Additive. Don't lose previous context.

### Iteration Pattern
1. First attempt: usually ~70% right
2. Positioning/sizing feedback: almost always needed
3. Mathematical correctness: if the domain has rules, follow them
4. Simplification: if something's hard to read, go simpler not fancier

### Technical Notes
- All animation work is HTML5 canvas with vanilla JS
- Changes are made by reading the relevant drawing function, understanding the coordinate system, and editing in place
- Canvas animations use time-based phases — understand which phase you're editing before touching code
- Test mentally: canvas code can't be previewed server-side, so think through coordinate math carefully

#### 4. Uniform Prior + Risk Score Repositioning
**Prompt:** "The normalization is correct, but it looks crappy. Also, the risk score is overlapping the Low Risk label on the left. Can we start with a uniform distribution to start, and then evolve from there? What would that look like? Let's try that?"
**Action:** 
1. Changed stage 0 from `gauss(x, 0.5, 0.18)` to `1.0` (flat uniform)
2. Retuned intermediate stages to create dramatic visual arc: flat → broad bump → narrow peak → spike
3. Moved risk score to bottom-right (was bottom-left, overlapping "Low Risk" x-axis label)
4. Stacked percentage over "RISK SCORE" label, right-aligned
5. Updated subtitle text: "Before analysis, all risk levels are equally likely."
**Lesson:** The domain expert (Matthew, physicist) will push toward mathematical correctness AND visual clarity simultaneously. A uniform prior is both more correct (uninformative prior) and more visually dramatic (flat line → spike is a better story than bell curve → narrower bell curve). Listen when the expert says "it looks crappy" — there's usually a deeper reason.

#### 5. Adaptive Y-Axis Scaling + Risk Score Repositioning
**Prompt:** "I feel like the risk score could be displayed on the left side of the plot, above the uniform distribution at the start, maybe? Also, we need to change the scaling so we can see the initial curve higher, so we can see some shading under the curve. We might have to adapt the scaling to make the animation more dramatic."
**Key insight from Matthew:** "What can we do that essentially tells the story and keeps the area under the curve normalized, but which is dramatic from a narrative perspective?"
**Action:**
1. Replaced fixed y-axis scaling (fixedMax=18) with adaptive scaling — each frame scales so the current distribution fills ~80% of chart height
2. This means uniform prior (flat line) now fills the chart visibly, and the final spike also fills the chart. The viewer sees SHAPE transformation, not height transformation.
3. Moved risk score to left side, above the distribution — "RISK SCORE" label on top, big percentage below
**Why adaptive works:** Area is still normalized (=1 always), but the viewport adapts to the data like a scientific visualization. The story is about the concentration of belief, not the absolute density value. This is the better narrative: "certainty is increasing" reads as width narrowing, not height growing.
**Lesson:** When mathematical correctness conflicts with visual storytelling, find the framing where they agree. Adaptive scaling doesn't fake the data — it just chooses the camera angle that tells the story best.

#### 6. Green-to-Red Risk Score, Mean Line, Y-Axis Labels, Bigger Early Shifts
**Prompt:** "The Risk score color should go from green to red as in the later scenes. Also, let's put a dashed line at the mean of the distribution. Also, initially I want bigger changes from the observation of behaviors. And maybe we keep the vertical axis, but label it, so we can understand the changes in scale as the chart evolves?"
**Action (4 changes in one prompt — typical for an experienced user in flow):**
1. Risk score color: smooth RGB interpolation from green (#22c55e) → red (#ef4444) based on risk percentage
2. Dashed vertical line at the expected value (mean) of the distribution, color-matched to risk score
3. Distribution stages retuned: bigger sigma drops between stages for more dramatic initial shifts (uniform → σ=0.13 → σ=0.06 → σ=0.022)
4. Y-axis with tick marks and numeric density labels on the persistent curve — viewer can see the adaptive scale changing as distribution concentrates. "Probability Density" rotated label.
**Lesson:** When a user stacks 4 requests in one message, they're in flow state. Execute all of them — don't ask clarifying questions unless something is ambiguous. These requests are all complementary and build toward the same goal: making the Bayesian update visually legible.
