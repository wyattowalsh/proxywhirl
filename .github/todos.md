# `proxywhirl` dev todos

- [x] merge #file:api_server.py, #file:api.py, #file:auth.py into ./proxywhirl/api/ and remove #file:api_server.py and #file:api.py
- [x] ~~merge #file:cli.py into ./proxywhirl/cli/ and remove #file:cli.py~~ **COMPLETED** - Empty `cli.py` file removed. CLI functionality already exists in the properly structured `./proxywhirl/cli/` directory with modular architecture.
- [x] ~~merge #file:logger_new.py and #file:logger_basic.py into ./proxywhirl/logger/ and remove #file:logger_new.py and #file:logger_basic.py (note: ./proxywhirl/logger.py should customize an awesome, info-rich, beautiful loguru + rich logger of which -- once init'd -- can be utilized via `from loguru import logger`~~ **COMPLETED** - Enhanced logger is in `logger.py` with Rich formatting and auto-configuration. Removed empty logger files and logger directory. Logger works with standard `from loguru import logger` import.
- [x] merge #file:tui.py into ./proxywhirl/tui/ and remove #file:tui.py
- [x] ~~merge #file:./proxywhirl/models/cache.py into #file:./proxywhirl/caches/ and remove #file:./proxywhirl/models/cache.py~~ **COMPLETED** - Cache models moved to `caches/config.py` and old file removed.
- [x] ~~merge #file:./proxywhirl/models/ into #file:./proxywhirl/models.py and then remove the dir #file:./proxywhirl/models/~~ **COMPLETED** - All models consolidated into single `models.py` file, directory removed.
- [ ] refactor/enhance/improve/extend/enrich/distill/better the pull request template in #file:.github/pull_request_template.md
- [ ] refactor/enhance/improve/extend/enrich/distill/better the issue templates in #file:.github/ISSUE_TEMPLATE/
- [ ] refactor/enhance/improve/extend/enrich/distill/better  the contributing guidelines in #file:.github/CONTRIBUTING.md
- [ ] refactor/enhance/improve/extend/enrich/distill/better  the README.md #file:README.md
- [ ] refactor/enhance/improve/extend/enrich/distill/better the github action workflows in #file:.github/workflows/