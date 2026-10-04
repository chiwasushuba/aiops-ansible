"""Offline checks with synthetic secrets; never connects to Docker or EC2."""

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import tempfile

from jinja2 import Environment, StrictUndefined
import yaml


ROOT = Path(__file__).resolve().parents[1]


def render_and_check(output: Path) -> None:
    variables = yaml.safe_load((ROOT / "roles/aiops/defaults/main.yml").read_text())
    password = "synthetic-$value#'\"-password-only-for-offline-tests"
    owner_hash = "$2b$12$" + "a" * 53
    variables.update(
        aiops_api_domain="api.test.invalid",
        aiops_frontend_origin="https://app.test.invalid",
        aiops_backend_image="aiops-backend:offline-test",
        aiops_backend_image_archive="/tmp/synthetic-image.tar",
        aiops_postgres_password=password,
        aiops_owner_password_hash=owner_hash,
        aiops_openai_api_key="synthetic-model-key",
    )
    environment = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    environment.filters.update(to_json=json.dumps, quote=shlex.quote)
    output.mkdir(parents=True, exist_ok=True)
    for source in (ROOT / "roles/aiops/templates").glob("*.j2"):
        rendered = environment.from_string(source.read_text()).render(**variables)
        (output / source.name.removesuffix(".j2")).write_text(rendered)

    def env_values(filename: str) -> dict[str, str]:
        return dict(
            line.split("=", 1)
            for line in (output / filename).read_text().splitlines()
            if line.strip()
        )

    backend = env_values("runtime.env")
    database = env_values("database.env")
    assert backend["AIOPS_OWNER_PASSWORD_HASH"] == owner_hash
    assert backend["DB_PASSWORD"] == database["POSTGRES_PASSWORD"] == password
    assert set(database) == {"POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"}
    assert "synthetic-model-key" not in (output / "database.env").read_text()
    compose = yaml.safe_load((output / "compose.yml").read_text())
    services = compose["services"]
    assert "ports" not in services["db"]
    assert services["db"]["networks"] == ["database"]
    assert compose["networks"]["database"]["internal"] is True
    assert services["backend"]["ports"] == ["127.0.0.1:8080:8080"]
    assert services["proxy"]["ports"] == ["80:80", "443:443"]
    assert services["backend"]["environment"]["SERVER_SERVLET_SESSION_COOKIE_SECURE"] == "true"
    for service in services.values():
        assert "build" not in service
        assert service["restart"] == "unless-stopped"
        assert service["logging"]["options"]["max-size"] == "10m"
    for service in ("backend", "db"):
        assert services[service]["env_file"][0]["format"] == "raw"
    assert services["backend"]["pull_policy"] == "never"
    assert compose["volumes"]["postgres-data"] == {}

    # Also render the registry delivery branch.
    variables["aiops_backend_image_archive"] = ""
    variables["aiops_backend_image"] = "registry.test.invalid/backend@sha256:" + "a" * 64
    registry = environment.from_string(
        (ROOT / "roles/aiops/templates/compose.yml.j2").read_text()
    ).render(**variables)
    assert yaml.safe_load(registry)["services"]["backend"]["pull_policy"] == "missing"
    backup = (output / "backup.sh").read_text()
    assert password not in backup and owner_hash not in backup
    assert "{{.ID}}" in backup
    subprocess.run(["bash", "-n", str(output / "backup.sh")], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="Keep synthetic rendered fixtures")
    args = parser.parse_args()
    if args.output_dir:
        render_and_check(args.output_dir)
    else:
        with tempfile.TemporaryDirectory(prefix="aiops-offline-") as directory:
            render_and_check(Path(directory))
    print("Template checks passed: secret preservation, private DB, delivery branches, backup shell syntax.")


if __name__ == "__main__":
    main()
