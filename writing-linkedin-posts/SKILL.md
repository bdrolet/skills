---
name: writing-linkedin-posts
description: Use when Ben wants a LinkedIn post written or reworked — sharing a blog post, announcing something, or turning an idea or anecdote into a post — or asks what to post, when to post it, or why a post underperformed. Output is paste-ready post text.
metadata:
  research: research.md
---

# Writing LinkedIn Posts

A LinkedIn post is a **doorway, not a copy of the room**: one idea from
direct experience, one concrete proof, a reason to click or comment.
Everything else stays in the article.

**REQUIRED SUB-SKILL:** apply `matching-writing-style` to the final text.
Ben's voice: plain words, short declaratives, no corporate polish.

## The post is these five parts, in this order

1. **Hook (first line, ≤140 characters).** The audience's situation and the
   stakes. It's all a phone shows before "…see more", so it stands alone.
   Write it last.
2. **One insight** — a single claim from Ben's own work: a decision and its
   reasoning, a pattern across clients, a result. If the article has five
   sections, the post has one.
3. **One proof** — a concrete detail only someone who did the work would
   know: a number, a timeline, a thing that happened.
4. **The link, in the body**, near the end, introduced by what the reader
   gets ("what we built and what it bought us", not "read more").
5. **A question only a practitioner can answer** — their experience, not
   yes/no, not "agree?". That is what draws multi-sentence comments.

Shape: 120–220 words, one idea per paragraph, 1–2 sentences each; one short
`–` list at most.

If the article names the **Battened Down** framework, the post names it too,
in one line, the way the article does ("battened-down AI", the harbor image).
It is the consulting signature; a share that drops it loses the brand. Past
work reads as consulting work ("a platform I built for a healthcare team"),
never as a previous job.

## Delivery

Put the text on the clipboard in one Bash call, quoted heredoc so nothing
expands (`pbcopy <<'EOF_MSG' … EOF_MSG`), then show it so Ben reads it before
he posts. **Never post it, never type it into LinkedIn.** Ben posts.

## Delivery line (always include after the text)

One line: **when** (Tue–Thu, 7–9 am in the audience's time zone; never
12–2 pm) and that Ben must be free for the **next 60–90 minutes to reply
substantively to every comment** — early replies decide distribution. Skip
the slot rather than post and walk away.

## Fixed choices (don't relitigate)

| Choice | Setting | Why (see research.md) |
|---|---|---|
| Hashtags | none | 5–10% better without; stacks read as template |
| Image | none with a link | the OG card renders; images cut reach ~30% |
| Link | in the body | first-comment costs clicks; personal profiles barely pay a link penalty |
| Opener | the hook | not "Excited to share" / "I wanted to" / "Thrilled to" |
| Topic | the consulting subject | the feed scores topic consistency |
| Profile | personal | ≈5× a company page's engagement |

## Quick check before returning

- First line stands alone at 140 characters?
- Reader still needs to click? If the post *is* the article, cut.
- Proof detail is something a stranger couldn't have written?
- Closing question needs experience to answer?
- Anything personal, or a named employer, that Ben didn't supply? Flag it
  in one line; don't decide for him.

## Example of the shape (the ship post, 2026-10-14)

Hook: *Most healthcare AI pilots I've seen are held together with duct tape.
That's why "production" feels scary.* (112 chars: audience, situation,
stakes.) Insight: one hull instead of a raft of inner tubes. Proof: a PM's
morning ask was live by lunch because the ship existed. Link: "what we built
and what it bought us". Question: "If you've shipped an AI feature into a
clinical workflow, what did you end up having to build underneath it?"

That is the shape to reproduce; each new post gets its own hook, proof and
question from its own material.
