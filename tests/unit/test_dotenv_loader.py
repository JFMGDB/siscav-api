"""Tests for automatic .env loading in config."""

import os
from unittest.mock import patch

from apps.api.src.api.v1.core import config


class TestLoadDotenvFiles:
    def test_skip_in_production(self):
        with (
            patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=False),
            patch.object(config, "load_dotenv") as mock_load,
        ):
            config._load_dotenv_files()
            mock_load.assert_not_called()

    def test_loads_existing_files_in_order(self, tmp_path):
        (tmp_path / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")
        (tmp_path / ".env").write_text("FOO=from_env\n", encoding="utf-8")
        (tmp_path / ".env.local").write_text("FOO=from_local\nBAR=local_only\n", encoding="utf-8")

        with (
            patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=False),
            patch.object(config, "_find_repo_root", return_value=tmp_path),
            patch.object(config, "load_dotenv") as mock_load,
        ):
            config._load_dotenv_files()
            assert mock_load.call_count == 2
            first_path, first_kw = mock_load.call_args_list[0][0][0], mock_load.call_args_list[0][1]
            second_path, second_kw = (
                mock_load.call_args_list[1][0][0],
                mock_load.call_args_list[1][1],
            )
            assert first_path == tmp_path / ".env"
            assert first_kw["override"] is False
            assert second_path == tmp_path / ".env.local"
            assert second_kw["override"] is True

    def test_skips_missing_files(self, tmp_path):
        (tmp_path / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")

        with (
            patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=False),
            patch.object(config, "_find_repo_root", return_value=tmp_path),
            patch.object(config, "load_dotenv") as mock_load,
        ):
            config._load_dotenv_files()
            mock_load.assert_not_called()

    def test_find_repo_root_finds_alembic_ini(self):
        root = config._find_repo_root()
        assert (root / "alembic.ini").is_file()
