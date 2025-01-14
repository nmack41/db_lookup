import logfire

from chatdb.cli.args import get_cli_args
from chatdb.cli.run import run

args = get_cli_args()

# Configure logging

logfire.configure(send_to_logfire="if-token-present", console=None if args.debug else False)

run(
    model_name=args.model,
    api_key=args.api_key,
    db_uri=args.db_uri,
    max_return_values=args.max_return_values,
)
