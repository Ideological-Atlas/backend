from ..base import DEBUG_SQL, ENVIRONMENT, PRODUCTION, PROJECT_NAME

IPYTHON_ARGUMENTS = ["--ext", "autoreload"]
SHELL_PLUS = "ipython"

if DEBUG_SQL:
    SHELL_PLUS_PRINT_SQL = True
    SHELL_PLUS_PRINT_SQL_TRUNCATE = None

SHELL_PLUS_IMPORTS = []
if not PRODUCTION:
    SHELL_PLUS_IMPORTS += [
        "from core.factories import *",
        "from ideology.factories import *",
    ]

try:
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    from IPython.terminal.prompts import Prompts, Token

    class BackendPrompt(Prompts):
        def in_prompt_tokens(self):
            project = PROJECT_NAME
            env_name = ENVIRONMENT

            return [
                (Token.Generic, f"({project}_{env_name}) "),
            ] + super().in_prompt_tokens()

        @staticmethod
        def get_style():
            env_name = ENVIRONMENT

            styles = {
                "production": "ansibrightred",
                "prod": "ansibrightred",
                "local": "ansibrightgreen",
                "dev": "ansibrightblue",
                "development": "ansibrightblue",
            }

            color = styles.get(env_name, "ansibrightmagenta")
            return {Token.Generic: f"bold {color}"}

    TerminalInteractiveShell.prompts_class = BackendPrompt
    TerminalInteractiveShell.highlighting_style_overrides = BackendPrompt.get_style()

except ImportError:
    pass
