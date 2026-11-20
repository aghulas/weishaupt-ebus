#!/usr/bin/env python3
"""Validates a generated metadata or fixtures JSON file against its JSON Schema under schemas/.

  scripts/validate-schema.py <schema.json> <data.json> [--require-jsonschema]

Uses the `jsonschema` package (Draft 2020-12) when installed. Without it, checks JSON syntax
and schema version only, unless --require-jsonschema is passed.
"""
import argparse
import json
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("schema", help="Path to JSON Schema file")
    p.add_argument("data", help="Path to JSON document to validate")
    p.add_argument("--require-jsonschema", action="store_true",
                   help="Fail if the jsonschema package is not installed")
    args = p.parse_args()

    with open(args.schema, encoding="utf-8") as f:
        schema = json.load(f)
    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    try:
        import jsonschema
    except ImportError:
        if args.require_jsonschema:
            sys.exit("FAIL: jsonschema package is not installed (pip install jsonschema)")
        want = schema.get("properties", {}).get("schema", {}).get("const")
        have = data.get("schema")
        if want is not None and have != want:
            sys.exit(f"FAIL: {args.data}: schema is {have}, expected {want}")
        print(f"schema: ok (basic check only, install jsonschema for full Draft 2020-12 validation)")
        return

    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        for err in errors[:20]:
            loc = "/".join(str(x) for x in err.absolute_path) or "<root>"
            print(f"  {loc}: {err.message}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... ({len(errors) - 20} more)", file=sys.stderr)
        sys.exit(f"FAIL: {args.data} has {len(errors)} schema error(s)")
    print(f"schema: ok ({args.data} matches {args.schema})")


if __name__ == "__main__":
    main()
