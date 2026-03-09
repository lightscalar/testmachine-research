# Best Practices for AI-Assisted Visualization Development

Distilled from real interaction logs building the TestMachine rug pull widget (Bayesian token risk animation) — a multi-session, iterative build via Telegram between a domain expert (physicist) and an AI assistant.

---

## 1. Respect the Domain

**The single most important rule.** If you're visualizing something with mathematical or scientific meaning, get the math right before worrying about aesthetics.

- A probability distribution must integrate to 1. Always.
- A Bayesian prior should start uninformative (uniform) unless there's reason otherwise.
- Axis labels, units, and scales should be meaningful, not decorative.

When the domain expert says "it looks crappy," there's often a deeper correctness issue underneath. The uniform prior wasn't just more correct — it was also more dramatic. Correctness and good storytelling usually point the same direction.

**Rule: Math first, then make it pretty.**

## 2. Simplify at Small Scale

Icons, logos, and detail elements at small canvas sizes (<30px) need to be geometric primitives: circles, lines, coils, arrows. Figurative drawings (a flexed bicep, a hand, a face) become unreadable mud at icon scale.

The progression Arrow → Bicep → Spring Coil followed a universal pattern: the first attempt was wrong, the second was too ambitious, the third was simple enough to actually work.

**Rule: When something's hard to read, go simpler — not different-complex.**

## 3. Expect Positioning Iterations

First placement of any dynamic element (score readout, label, overlay) is almost always wrong. It'll overlap something, or be in the wrong visual hierarchy, or compete with another element that only appears in certain animation states.

This happened three times with the risk score alone: top-right → bottom-left → bottom-right → left-above-distribution. Each move was triggered by a collision with something that wasn't visible in the default state.

**Rule: Plan for 2-3 positioning iterations. Put dynamic overlays where they can't clash with ANY animation state, not just the current one.**

## 4. Adaptive Framing > Fixed Framing

When visualizing data that changes dramatically in magnitude (like a probability distribution going from flat to a narrow spike), fixed-scale rendering hides the story. The early stages look flat and boring, the late stages dominate.

Adaptive scaling — where the viewport adjusts so the current data fills ~80% of the chart height — solves this without faking the data. The viewer sees shape transformation instead of height growth. The story shifts from "the number got bigger" to "certainty is concentrating."

This is the same principle as a camera operator choosing an angle. You're not manipulating the data; you're choosing the framing that tells the story best.

**Rule: When mathematical correctness conflicts with visual storytelling, find the framing where they agree.**

## 5. Read the Prompt Structure

Domain experts develop consistent prompt patterns. Recognizing them saves iterations:

| Pattern | Example | What it means |
|---------|---------|---------------|
| "Can we [verb] the [element]?" | "Can we update the MoonPump logo?" | Open-ended. Interpret broadly. |
| "The [element] is [problem]. Maybe [suggestion]?" | "The logo is difficult to understand. Maybe a spring?" | The problem is the spec; the suggestion is a hint, not a requirement. |
| "Also, [new thing]" | "Also, let's put a dashed line at the mean" | Additive. Don't lose previous context. |
| "It looks crappy" | — | There's a deeper issue. Probe or think harder. |
| Multiple requests in one message | "Color should change AND add mean line AND bigger shifts AND label the axis" | User is in flow. Execute all of them. Don't interrupt with clarifying questions unless something is genuinely ambiguous. |

**Rule: Match the user's tempo. When they're in flow, ship fast. When they flag something vague ("looks crappy"), slow down and think.**

## 6. The 70% Rule

First attempts are typically ~70% right. The iteration pattern is predictable:

1. **V1:** Core concept lands, positioning/sizing wrong
2. **V2:** Layout fixes, reveals new conflicts
3. **V3:** Mathematical or domain corrections
4. **V4:** Polish — color interpolation, labels, supplementary indicators

Knowing this means: don't over-polish V1. Ship it fast, get feedback, iterate. The feedback will teach you things you couldn't have anticipated.

**Rule: Show early, show ugly, show often.**

## 7. Color Carries Meaning

Color isn't decoration — it's a data channel. In the rug pull widget:
- Risk score interpolates green → red (semantic: safe → dangerous)
- The mean line color-matches the risk score (visual binding)
- Distribution fill uses the same color scheme (consistency)

Every color choice should answer: "What does this color MEAN?" If the answer is "it looks nice," you probably haven't thought hard enough.

**Rule: Color is data. Every hue should encode something.**

## 8. Stack Changes, Don't Sequence Them

When an experienced user sends 4 requests in one message, they're telling you these changes are complementary and should ship together. Asking "which one first?" breaks their flow.

The exception: if two requests genuinely conflict (e.g., "make the text bigger" and "fit more items in the same space"), flag the conflict and propose a resolution. But if they're additive, execute all of them in one pass.

**Rule: Batch complementary changes. Only break flow for genuine conflicts.**

## 9. The Expert Sees What You Don't

The domain expert is viewing the animation on their phone, in context, with knowledge of the audience. They see problems invisible from the code:

- "The risk score is overlapping the Low Risk label" — layout collision only visible at runtime
- "I want bigger changes from the observation of behaviors" — narrative pacing issue
- "It looks crappy" — holistic assessment that combines correctness, aesthetics, and storytelling

Trust the feedback, even when (especially when) it's vague. Your job is to translate vague dissatisfaction into specific code changes.

**Rule: Vague feedback from a domain expert contains more information than precise feedback from a non-expert.**

## 10. Capture Everything

Every interaction — prompt, response, what worked, what didn't — is training data for getting better at this. The patterns above only emerged because the interactions were logged. Without the log, each session starts from zero.

**Rule: Log the interaction, not just the code.**

---

## The Meta-Pattern

Building visualizations with AI is a conversation, not a specification. The human brings domain knowledge, narrative intuition, and aesthetic judgment. The AI brings rapid execution, coordinate math, and the ability to try 10 things in the time it takes to describe one.

The sweet spot is: **human steers, AI rows.** Short prompts, fast iterations, progressive refinement. The worst workflow is a long spec upfront — it will be wrong in ways neither party can anticipate. The best workflow is: show something fast, get a reaction, adjust, repeat.

This is fundamentally different from traditional development where you spec→build→review. It's closer to pair programming, or better yet, pair sketching — two people at a whiteboard, one drawing and one directing.
