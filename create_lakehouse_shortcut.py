"""
Create OneLake shortcuts in a Fabric Lakehouse pointing to Iceberg tables
in Google Cloud Storage.

Prerequisites:
  - Azure CLI installed and signed in (`az login`)
  - A Fabric connection to GCS already configured (you need its GUID)

Usage:
  python create_lakehouse_shortcut.py \
    --workspace-id <WORKSPACE_GUID> \
    --lakehouse-id <LAKEHOUSE_GUID> \
    --connection-id <CONNECTION_GUID> \
    --location "https://storage.googleapis.com/<BUCKET_NAME>" \
    --table-path "consulting/engagement_roles"

The script creates a shortcut under Tables/ so Fabric recognizes it as a
queryable Iceberg table. The shortcut name is derived from the last segment
of --table-path (e.g. "engagement_roles").
"""

import argparse
import json
import subprocess
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def get_fabric_token() -> str:
    """Acquire a bearer token for the Fabric API using the Azure CLI."""
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Failed to get access token.\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    token_info = json.loads(result.stdout)
    return token_info["accessToken"]


def create_shortcut(
    workspace_id: str,
    lakehouse_id: str,
    connection_id: str,
    location: str,
    table_path: str,
) -> dict:
    """
    Create a GCS shortcut in the Lakehouse Tables section.

    Args:
        workspace_id: Fabric workspace GUID.
        lakehouse_id: Lakehouse item GUID.
        connection_id: Pre-configured Fabric connection GUID for GCS.
        location: GCS bucket URL, e.g. "https://storage.googleapis.com/my-bucket".
        table_path: Path within the bucket to the Iceberg table,
                    e.g. "consulting/engagement_roles".
    """
    token = get_fabric_token()

    # Derive shortcut name from the last path segment
    shortcut_name = table_path.rstrip("/").split("/")[-1]

    # Ensure subpath has a leading slash
    subpath = table_path.strip("/")
    subpath = f"/{subpath}"

    url = (
        f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}"
        f"/items/{lakehouse_id}/shortcuts"
    )

    body = {
        "path": "Tables",
        "name": shortcut_name,
        "target": {
            "googleCloudStorage": {
                "location": location,
                "subpath": subpath,
                "connectionId": connection_id,
            }
        },
    }

    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            status = resp.status
            response_body = json.loads(resp.read().decode("utf-8"))
            action = "Updated" if status == 200 else "Created"
            print(f"{action} shortcut '{shortcut_name}' successfully.")
            print(json.dumps(response_body, indent=2))
            return response_body
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(
            f"ERROR: HTTP {e.code} creating shortcut '{shortcut_name}'.\n{error_body}",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Create a OneLake shortcut to a GCS Iceberg table."
    )
    parser.add_argument("--workspace-id", required=True, help="Fabric workspace GUID")
    parser.add_argument("--lakehouse-id", required=True, help="Lakehouse item GUID")
    parser.add_argument("--connection-id", required=True, help="Fabric GCS connection GUID")
    parser.add_argument(
        "--location",
        required=True,
        help="GCS bucket URL, e.g. https://storage.googleapis.com/my-bucket",
    )
    parser.add_argument(
        "--table-path",
        required=True,
        help='Path to the Iceberg table in the bucket, e.g. "consulting/engagement_roles"',
    )

    args = parser.parse_args()

    create_shortcut(
        workspace_id=args.workspace_id,
        lakehouse_id=args.lakehouse_id,
        connection_id=args.connection_id,
        location=args.location,
        table_path=args.table_path,
    )


if __name__ == "__main__":
    main()
