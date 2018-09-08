# mlbase
機械学習をするためのツール(WIP)

## 主要サブコマンド
### tree  
サブコマンドの一覧を表示する

### config
設定を書く
```
$ mlbase config edit plugins
```

## 主要モジュール
### mlbase/utils/cli.py
コマンド構築を行う


### hyper_param
ハイパーパラメータを管理する

## 未実装
* report
  実験内容をまとめるもの
* schedule
  実験の手順を書くためのもの
* event
  実験の要素を書くためのもの
* logger
  実験の実行状態を記録するもの
* model_manager
  モデルの管理を行う
