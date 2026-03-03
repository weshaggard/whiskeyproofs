# Task Report

## Task
Set up an agentic workflow that runs weekly to find new bourbon/rye releases from official updates, update the whiskey index with correct fields/URLs/labels, and extend release-year ranges instead of duplicating unchanged entries.

## Result
✅ Success

## Summary
- Items processed: 2
- Succeeded: 2
- Failed: 0
- Skipped: 0

## Completed
- Added `.github/workflows/find-new-releases.yml`:
  - Weekly schedule configured (`0 9 * * 1`) plus manual trigger.
  - Runs Copilot CLI against `.github/prompts/find-new-releases.prompt.md`.
  - Runs `validate_whiskey_data.py`, `validate_urls.py`, and `validate_ttb_urls.py`.
  - Creates automated PRs using GitHub App token (`actions/create-github-app-token` + `peter-evans/create-pull-request`).
- Added `.github/prompts/find-new-releases.prompt.md`:
  - Encodes Task → Requirements → Retry → Report framework.
  - Prioritizes official press releases/websites and bourbon/rye-only scope.
  - Requires full field correctness and TTB lookup process (repo labels first, then public registry).
  - Instructs extending `ReleaseYear` ranges for unchanged recurring releases instead of adding duplicates.
- Validation run after edits:
  - `python3 .github/scripts/validate_whiskey_data.py` passed.
  - Full validation chain (`validate_whiskey_data.py`, `validate_urls.py`, `validate_ttb_urls.py`) passed.
- Security scanning:
  - `codeql_checker` reported 0 alerts.

## Errors
- Baseline local build attempt with `bundle exec jekyll build` initially failed because `bundle` was missing.
- Installing bundler globally failed with permission errors writing to `/var/lib/gems/3.2.0`.
- Resolved by installing user-scoped bundler and setting local bundle path (`bundle config set --local path vendor/bundle`), then `bundle install && bundle exec jekyll build` succeeded.

## Remaining Work
None.

## State
- New workflow is committed and pushed on branch `copilot/setup-weekly-agentic-workflow`.
- New prompt path used by workflow: `.github/prompts/find-new-releases.prompt.md`.
