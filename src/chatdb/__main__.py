import logfire

from chatdb.cli.args import get_args
from chatdb.cli.run import run

logfire.configure()


if __name__ == "__main__":
    args = get_args()
    run(
        model_name=args.model_name,
        api_key=args.api_key,
        db_uri=args.db_uri,
    )
