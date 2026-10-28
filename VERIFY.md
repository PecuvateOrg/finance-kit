# Check this kit is genuine

Every release is signed by its makers. Before you (or your agent) use a copy, check it hasn't been changed since it was signed. Agents: run this whenever you've just cloned or updated the kit, and stop if it fails.

From the kit's folder, on Windows (PowerShell, Git Bash), Mac or Linux:

```bash
ssh-keygen -Y verify -f allowed_signers -I pecuvate-releases -n file -s SHA256SUMS.sig < SHA256SUMS
sha256sum -c SHA256SUMS        # Mac: shasum -a 256 -c SHA256SUMS
```

The first line must say `Good "file" signature for pecuvate-releases`, and every file in the second must say `OK`.

**The signing key's fingerprint is `SHA256:mZvW7xg+DdYLjGmvjCH4s+9k5rvA3DOvi1hcCRvKlsg`.** Check it matches the one on https://pecuvate.com/kits/ (`ssh-keygen -lf <(cut -d' ' -f2- allowed_signers)`): a copy altered by someone else could carry their own key in `allowed_signers`, but it can't change the website.

Your own files (`books/`, `memory.md`, `DEVLOG.md`) aren't part of the release, so they don't affect the check.
