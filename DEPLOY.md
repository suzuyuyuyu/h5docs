# 公開の設定

このリポジトリは GitHub Actions で GitHub Pages に公開する。
ワークフローは [`.github/workflows/pages.yml`](.github/workflows/pages.yml)。

## いつ公開されるか

| きっかけ | 動作 |
|---|---|
| `main` への push（PR のマージを含む） | リンク検査 → 公開 |
| `main` 向けの PR | リンク検査のみ。**公開しない** |
| 手動実行（Actions タブ） | リンク検査 → 公開 |

PR を開いた時点では公開しない。レビュー前の内容が公開サイトに出ないようにするため。

## 最初に一度だけ必要な設定（手動）

**Settings → Pages → Build and deployment → Source** を
**GitHub Actions** にする。

これは自動化できない。`configure-pages` の `enablement: true` で有効化を
試みると、Pages サイトの作成が `GITHUB_TOKEN` の権限を超えるため
`Resource not accessible by integration` で失敗する。`pages: write` は
デプロイを許すだけで、サイトの新規作成には足りない。

未設定のまま実行すると次で止まる。

```text
Get Pages site failed. Error: Not Found
```

設定後に Actions タブから再実行すれば通る。

## リファレンスの更新

`reference/` 配下は各リポジトリの `docs/*.md` から生成したもので、
生成結果をコミットしている。CI は生成せず、コミットされたものをそのまま公開する。

元の `docs/*.md` を変更したら、手元で作り直してコミットする。

```sh
uv run --with markdown scripts/build_reference.py
```

CI 側で生成しないのは、生成に4つの兄弟リポジトリが必要で、
それらを CI で取得すると公開が他リポジトリの状態に依存するため。
生成物をコミットしておけば、このリポジトリだけで公開が完結する。

代わりに、更新漏れは人が気づく必要がある。ライブラリ側の `docs/` を触ったら
このリポジトリでも生成し直すこと。

## サイトから他リポジトリへのリンク

`example/` のプログラムなどへのリンクは
`https://github.com/suzuyuyuyu/<repo>/blob/main/...` の形の絶対 URL を使う。
4つは独立したリポジトリなので、相対パスでは届かない。

リンク先は `main` を指す。ライブラリ側の変更が `main` にマージされるまで、
新しく追加したファイルへのリンクは解決しない。
