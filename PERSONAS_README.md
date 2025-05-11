# Personas Small Repos

In this branch we propose several possible code libraries, then implement several implementations of each library according to different possible personas that would use it. 
We then implement an agentic approach to refactoring the different implementations into one compressed shared repository, that retains functionality of the original but is ideally more compressed and re-usable.

Some libraries and personas have already been implemented:
```

```

## Setup
Setup your `.env` with `TOGETHER_API_KEY`, `OPENAI_API_KEY`, and `ANTHROPIC_API_KEY`

To do the refactoring, make sure to have OpenAI `codex` and Anthropic's `claude-code` harnesses setup.


## Generate more
To generate more libraries and persona implementations to setup for refactoring:
```
./generate_repos_for_refactor.sh
```

To refactor a library implementation of choice `LIBRARY_IMPL_PATH`:
```
bash scripts/refactor_claude_codex.sh $LIBRARY_IMPL_PATH
```