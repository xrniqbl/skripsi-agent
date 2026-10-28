#!/usr/bin/env bash
# Push repo skripsi-agent ke GitHub.
#
# Dua jalur kredensial, pilih salah satu:
#
#   A. SSH (disarankan — tidak ada secret yang lewat chat)
#      1. Tambahkan public key ke GitHub:
#         https://github.com/settings/keys  →  New SSH key
#         (atau sebagai Deploy key dengan "Allow write access" di
#          https://github.com/xrniqbl/skripsi-agent/settings/keys)
#      2. bash scripts/push-github.sh --ssh
#
#   B. Personal Access Token (classic, scope `repo`)
#      Simpan ke berkas, JANGAN ke chat:
#         printf '%s' 'ghp_xxx' > ~/.github_token && chmod 600 ~/.github_token
#      lalu:
#         bash scripts/push-github.sh
#
# Tanpa argumen: coba SSH dulu, lalu token dari ~/.github_token.
set -uo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="${GITHUB_TOKEN_FILE:-$HOME/.github_token}"
OWNER_REPO="xrniqbl/skripsi-agent"
MODE="${1:-auto}"

cd "$REPO_DIR" || exit 2

echo "== repo: $REPO_DIR"
echo "== commit lokal: $(git rev-parse --short HEAD) $(git log -1 --pretty=%s | cut -c1-60)"
echo "== commit remote: $(git ls-remote origin refs/heads/main 2>/dev/null | cut -c1-7 || echo '?')"

coba_ssh() {
    echo "-- uji SSH ke github.com…"
    if timeout 20 ssh -T -o BatchMode=yes git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "   SSH OK"
        return 0
    fi
    echo "   SSH belum terdaftar di GitHub (public key di bawah)"
    echo
    cat "$HOME/.ssh/id_ed25519_github.pub" 2>/dev/null || echo "   (public key belum dibuat)"
    echo
    return 1
}

push_ssh() {
    git remote set-url origin "git@github.com:$OWNER_REPO.git"
    git push -u origin main
}

push_token() {
    local tok
    tok="$(tr -d '\r\n' < "$TOKEN_FILE")"
    if [ -z "$tok" ]; then
        echo "GAGAL: $TOKEN_FILE kosong"; return 2
    fi
    # kredensial hanya hidup selama perintah ini, tidak ditulis ke config
    git -c "credential.helper=" \
        -c "http.https://github.com/.extraheader=Authorization: Basic $(printf 'x-access-token:%s' "$tok" | base64 -w0)" \
        push -u origin main
}

verifikasi() {
    local lokal remote
    lokal="$(git rev-parse HEAD)"
    remote="$(git ls-remote origin refs/heads/main 2>/dev/null | cut -f1)"
    echo
    echo "== verifikasi"
    echo "   lokal : ${lokal:0:7}"
    echo "   remote: ${remote:0:7}"
    if [ "$lokal" = "$remote" ] && [ -n "$remote" ]; then
        echo "   STATUS: SAMA — push berhasil dan terverifikasi"
        git remote set-url origin "https://github.com/$OWNER_REPO.git"
        return 0
    fi
    echo "   STATUS: BEDA — push belum landing"
    return 1
}

case "$MODE" in
    --ssh)
        push_ssh && verifikasi
        ;;
    --token)
        [ -f "$TOKEN_FILE" ] || { echo "GAGAL: $TOKEN_FILE tidak ada"; exit 2; }
        push_token && verifikasi
        ;;
    *)
        if coba_ssh; then
            push_ssh && verifikasi
        elif [ -f "$TOKEN_FILE" ] && [ -s "$TOKEN_FILE" ]; then
            echo "-- jatuh ke token dari $TOKEN_FILE"
            push_token && verifikasi
        else
            echo "Tidak ada kredensial. Ikuti salah satu jalur di header skrip ini."
            exit 1
        fi
        ;;
esac
