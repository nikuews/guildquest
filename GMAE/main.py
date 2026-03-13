"""CLI entry point for GuildQuest Mini-Adventure Environment."""

from __future__ import annotations

from GMAE.engine.gmae_facade import GmaeFacade


def main() -> None:
    GmaeFacade().run()


if __name__ == "__main__":
    main()
