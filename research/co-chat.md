# Co-Chat: Claude × ChatGPT

A shared research log where Claude and ChatGPT ask each other questions,
answer them, and challenge each other's answers. The human moderator decides
the topic and when a thread is finished.

## Briefing

> **Status: pending.** The briefing has not been added to this repository yet.
> Add it as `research/briefing.md` (or paste it below), and the first round of
> questions will be drawn from it.

<!-- Paste or link the briefing here. -->

## How this works

1. **Turns are tagged** with the speaker: `Claude`, `ChatGPT`, or `Moderator`.
2. **Every turn is a question, an answer, or a challenge.** Use the matching
   label (`Q`, `A`, `Challenge`) and the question number it belongs to (`Q1`, `A1.1`, ...).
3. **ChatGPT's turns are real, never imagined.** They are added either by the
   moderator pasting ChatGPT's reply, or by a script calling the OpenAI API.
   Claude never writes ChatGPT's lines.
4. **Sources:** when an answer states a fact, cite where it comes from or mark
   it `unverified`.
5. **Close a question** by moving it to *Conclusions* with a status:
   `agreed`, `disagreed`, or `open`.

### Turn template

```markdown
### Q<n> · <Speaker> asks
<question>

#### A<n> · <Speaker> answers
<answer>

#### Challenge <n>.<k> · <Speaker>
<follow-up or objection>
```

## Open questions

| # | Asked by | Question | Status |
|---|----------|----------|--------|
| — | — | *(waiting for the briefing)* | — |

## Conversation log

*(No turns yet.)*

## Conclusions

| # | Topic | Claude's position | ChatGPT's position | Outcome |
|---|-------|-------------------|--------------------|---------|
| — | — | — | — | — |
