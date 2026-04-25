# Sync catalog files with S3

`catalog/files/` is gitignored, so the only durable backup of the
underlying media is an S3 bucket. `sync.sh` is a thin wrapper around
`aws s3 sync` that handles direction (push or pull) and the bucket and
profile defaults baked into the script.

Requires the AWS CLI and a configured AWS profile that can reach the
bucket. The bucket and profile are set at the top of `sync.sh`; change
them there if the destination moves.

## Procedure

To back up local files to S3:

    ./sync.sh push

To restore files from S3 onto a fresh checkout:

    ./sync.sh pull

Extra arguments are forwarded to `aws s3 sync`. For example, dry-run a
push without uploading anything:

    ./sync.sh push --dryrun

## Re-running

`aws s3 sync` skips files whose size and mtime match the destination,
so re-running is cheap. Deleting a file locally and pushing does not
remove it from the bucket unless you pass `--delete`. Same in the
opposite direction. Use `--delete` deliberately.

## Files

- `sync.sh` — wrapper. Bucket and profile live at the top of the file.
- `catalog/files/` — source on push, destination on pull.
