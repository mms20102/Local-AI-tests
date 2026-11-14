# Glossary

Terms used across this repository, in plain words.

## The stack

| Term | Meaning |
|---|---|
| **Stack** | The three services that make up the assistant on the laptop: the chat page, the gateway and the engine |
| **Open WebUI** | The chat page in the browser. Version 0.13.3. Connected to the gateway as a plain OpenAI-compatible provider, with its extension features switched off |
| **Gateway** | LiteLLM proxy, version 1.108.5. Checks the key, checks the request, adds teaching notes, forwards to the engine |
| **Engine** | Colibri, version 2.0.0. Runs the model, keeping parts of it on the graphics card, in memory and on the SSD |
| **Model** | Qwen3.6-35B-A3B, quantized to 4 bits; about 23 GB on disk. Runs with thinking switched off |
| **Launcher** | The script that starts the three services in order and stops them cleanly |
| **cap** | The engine's expert cache size per layer. The laptop uses 32; the default was 4 |
| **Context** | The most tokens the model can take in one request: 2,048 here, shared by the conversation and the answer |

## Admission

| Term | Meaning |
|---|---|
| **Admission** | The gateway's decision to pass a request to the engine or refuse it |
| **Byte rule** | The original, conservative size check: UTF-8 bytes plus fixed overheads. Safe but admits only about 500 tokens |
| **Token rule** | The newer check: render the request as the engine does, count real tokens, and require prompt + requested answer + margin to fit the context |
| **Margin** | 32 tokens added to a real count before comparing with the context. A judgment, not a derived bound |
| **Served profile** | The exact setup the token counter was verified against: engine version, renderer file, thinking off, context size and tokenizer file. Real counting is used only when the launcher reports exactly this |
| **Reason code** | Why a too-long request was refused: no counter available, the counter failed, it returned nonsense, or the request truly does not fit |
| **Usage parity** | Agreement between the gateway's token count and the count the engine reports in its response, for a given request. Shown for the shapes tested, not in general |

## Teaching

| Term | Meaning |
|---|---|
| **Teach store** | A small local file of rules, facts and corrections that the owner writes |
| **Note / entry** | One item in the store, with an id such as `t001` |
| **Hook** | Code the gateway calls for each chat request. The teach hook adds the notes that apply |
| **Policy sentence** | A fixed sentence added to the system message saying the notes block is background data |
| **Fingerprint** | The first 12 hex digits of the hash of the store file as it was read. Identifies a version of the store, not of the code |
| **`note_cap`, `no_room`, `uncounted`** | Why an applicable note was left out: too large for the notes limit, no room in the request, or the room could not be counted |
| **`byte_only`** | Notes that were added on the byte rule alone, with no token count of the final request |
| **Carrier** | A small piece of internal data that takes the hook's decision from the request to the response stream. It never goes to the engine |
| **Status event** | One fixed line in a streamed answer, such as "Some saved notes were not used for this answer." |

## Evaluation

| Term | Meaning |
|---|---|
| **CODE-Q1** | The coding task set: 12 tasks (nine English, three Arabic) with 116 authored test cases, frozen at fixture revision 2 |
| **Draft** | The model's answer to a task, saved as text. Never executed on the laptop's own system |
| **Static grade** | Checks that an answer is complete, not cut off, and has the required files and functions. Does not run the code |
| **Behavioural grade** | Runs the authored cases against the answer. Allowed only in an isolated environment |
| **First attempt** | The model's first answer to a task, with no retry or repair |
| **Contended** | A timing taken while something else, usually a large download, was using the laptop |

## Process

| Term | Meaning |
|---|---|
| **Co-chat** | The shared, append-only log between the two assistants: `research/co-chat.md` |
| **Turn / round** | One section of the log by one author |
| **Runtime window** | A period, announced and closed in the log, during which the laptop's services are stopped, started or reconfigured |
| **Runtime notice** | The log entry that opens a window |
| **Scratch test** | A synthetic test in a separate process and folder that uses the laptop's installed libraries read-only and leaves the running services alone |
| **Loaded** | Actually running inside the gateway process on the laptop, as opposed to written, tested or reviewed |
| **Revision** | A numbered version of published code. Each has a row in its folder's README with its review status |
| **Independent reviewer** | A separate reviewer on the ChatGPT side who runs the published tests in an environment that cannot reach the laptop |
| **Coordinator** | The ChatGPT-side role that relays between its workers and the log |
| **Claim labels** | *measured*, *recorded*, *derived*, *documented*, *reported*, *inferred*. Defined in [CONTRIBUTING.md](../CONTRIBUTING.md) |
