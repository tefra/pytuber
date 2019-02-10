from pytuber.storage import Registry


def init_registry(path: str, version: str):
    Registry.from_file(path)

    current_version = Registry.get("version", default="0")
    if current_version == "0":
        if Registry.exists("configuration", "youtube", "data"):
            Registry.set(
                "configuration", "youtube", "data", "quota_limit", 1000000
            )

    Registry.set("version", version)
