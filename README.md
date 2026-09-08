# h5docs

`h5fortran` / `h5c` / `h5cpp` / `h5xdmf` の利用者向けサイト。
GitHub Pages で公開する。

対応バージョンは **2.0.0**。4 つのライブラリと揃えている。

## 構成

| パス | 内容 |
|---|---|
| `index.html` | HDF5 と XDMF の説明、どのライブラリを使うか |
| `install/` | 4 つのインストール手順 |
| `usage/` | 書く・読む・並列・可視化用出力。Fortran / C / C++ をタブで切り替え |
| `visualization/` | HDF5 を出してから ParaView で開くまで |
| `reference/` | 各リポジトリの `docs/*.md` を変換したもの |

手書きは `index.html` と `install/` `usage/` `visualization/` の 4 ページ。
`reference/` は生成物で、直接編集しない。

## リファレンスの再生成

各リポジトリの `docs/*.md` を変更したら作り直す。

```sh
uv run scripts/build_reference.py
```

必要な Python と依存はスクリプト自身が宣言しているので、引数は要らない。
兄弟ディレクトリに 4 つのリポジトリが並んでいる前提で読み取る。

生成結果はコミットする。CI では生成せず、コミットされたものを公開する。

## デザイン

`assets/style.css` 1 枚。色・フォント・余白・行長はすべて `:root` の
カスタムプロパティで、見た目を変えるときはそこを差し替える。
コンポーネント側に色のリテラルを書かない。

## 公開

`main` への push で自動デプロイされる。設定と注意点は [DEPLOY.md](DEPLOY.md)。
