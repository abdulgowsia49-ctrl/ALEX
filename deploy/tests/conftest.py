"""Skip, rather than error, tests that need regenerated data products that are not committed."""
import pytest
from pyroharmonize import config as _cfg

_PAIRS = _cfg.PROCESSED_DIR / "pairs_aqua_snpp.parquet"


def pytest_collection_modifyitems(config, items):
    if _PAIRS.is_file():
        return
    skip = pytest.mark.skip(reason="processed pair table not committed (data/processed/pairs_aqua_snpp.parquet); "
                                   "regenerate with scripts/02 + 03 on the source machine")
    for item in items:
        if "pairs" in getattr(item, "fixturenames", ()):
            item.add_marker(skip)
