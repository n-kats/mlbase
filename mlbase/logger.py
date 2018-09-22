import sys
import subprocess


def info(s):
    print(f"[info] {s}")


def failure(s):
    # 実験の失敗を記録する(発散など)
    print(f"[failure] {s}")


def error(s):
    # プログラムの失敗を記録する
    print(f"[error] {s}", file=sys.stderr)


def important(s):
    print(f"[important] {s}")


def notify(s):
    print(f"[notify] {s}")
    subprocess.Popen(["notify-send", s])


def debug(s):
    pass
