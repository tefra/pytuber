import click
import click_completion


@click.command()
@click.argument(
    "shell_type",
    required=False,
    type=click_completion.DocumentedChoice(click_completion.core.shells),
)
def autocomplete(shell_type):
    """Enable the command auto completion."""

    shell, path = click_completion.core.install(
        shell=shell_type,
        append=True,
        extra_env={
            "_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"
        },
    )
    click.secho("%s completion installed in %s" % (shell, path))
