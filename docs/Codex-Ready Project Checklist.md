# **Codex-Ready Project Checklist**

1. **Create Repo**

   * [X] Create empty GitHub repo (`anonymization-service` or similar).

2. **Add Requirements**

   * [X] Add `REQUIREMENTS.md` (the document above, or your finalized version).

3. **Initialize Project**

   * [X] Add `.gitignore` (Node, Python, or both depending on your stack).
   * [X] Add `README.md` with:

     * One-line purpose/description.
     * Quick-start for dev setup.
   * [X] Add a `LICENSE` (MIT/Apache 2.0 unless you need something else).

4. **Choose Language & Scaffold**

   * [X] python -m venv venv
   * [X] Add `pyproject.toml` or `requirements.txt`, install `boto3`, `pytest`, linter.

   * [ ] Add `config.sample.json` (example of anonymization field mapping/config).

5. **Dev Environment**

   * [ ] Add `.env.example` (if any env vars needed).
   * [ ] Add instructions to README for setting up/test-driving Lambda locally (`serverless`, `sam`, or plain AWS CLI).

6. **Testing**

   * [ ] Add `/tests` or `/__tests__` folder.
   * [ ] Add one basic test for each endpoint (`anonymize`, `deanonymize`).
   * [ ] Add lint config (`.eslintrc`, `.prettierrc`, or `.flake8`).

7. **CI/CD Prep**

   * [ ] Add simple GitHub Actions workflow (`.github/workflows/ci.yml`) to run tests on push.
   * [ ] Add badge for build status in `README.md`.

8. **AWS Bootstrap**

   * [ ] Add deploy config for Lambda (`serverless.yml`, `template.yaml`, or a deployment script).
   * [ ] Add section in `README.md` for deployment steps (including minimum AWS permissions needed).

9. **Copilot/Codex Hints**

    * [ ] Add inline docstrings/comments (especially in the function stubs—explain inputs/outputs).
    * [ ] Keep code modular and file/folder names obvious.
    * [ ] Use explicit TODO comments where you want AI help.

---

**Pro tips:**

* The more explicit you are in `README.md` and your stub function comments, the better Codex/GitHub Copilot will perform.
* Having example input/output payloads in the repo (as `.json` files or in `README.md`) helps guide Copilot/autocomplete.

Let me know your language choice and I can stub out the minimal starter files if you want.
