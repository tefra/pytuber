import click


class ConfigMissing(click.UsageError):
    pass


class RecordExists(click.UsageError):
    pass


class NotFound(click.UsageError):
    pass
