# Server Deploy Resources

These files were exported from the working server `192.168.1.100` for installation on a new server.

Use the root guide:

```text
../NEW_SERVER_DEPLOYMENT_GUIDE.md
```

Important:

- `opt-data/` files are copied into Hermes agent containers under `/opt/data`.
- `hermes/plugins/camofox-extra` is copied onto the host under `/home/ubuntu/.hermes/plugins/camofox-extra`.
- `hermes/config/hermes-config-required-snippets.yaml` is a redacted reference. Merge it manually into `/home/ubuntu/.hermes/config.yaml`.
- `opt-data/.config/hq-browser/cdp-url.example` is a template. Replace the token before creating `/opt/data/.config/hq-browser/cdp-url` inside the target container.
