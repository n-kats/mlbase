from mlbase.utils.cli import Command


def estimate_command():
    cmd = Command("estimate", "見積もり計算をする")
    cmd_tpu = Command("tpu", "TPU見積もりを行う") << cmd
    cmd_tpu.option("--num_core", help="全コア数", required=True, type=float)
    cmd_tpu.option("--core_per_tpu", help="TPUあたりのコア数", default=8, type=float)
    cmd_tpu.option("--hours", help="何時間実行するか", type=float)
    cmd_tpu.option("--dollar_per_hour", help="コア数", default=5.22, type=float)
    cmd_tpu.option("--yen_per_dollar", help="1ドル何円か", default=110, type=float)

    @cmd_tpu
    def tpu_case(args, *others, **kwargs):
        num_tpu = args.num_core / args.core_per_tpu
        dollar_per_hour = args.dollar_per_hour * num_tpu
        yen_per_hour = dollar_per_hour * args.yen_per_dollar
        print(f"コア数: {args.num_core}")
        print(f"1TPUあたりコア数: {args.core_per_tpu}")
        print(f"TPU数: {num_tpu}")
        print(f"1TPU値段(ドル/h): {args.dollar_per_hour}")
        print(f"1ドル(円): {args.yen_per_dollar}")
        print(f"単位時間値段(ドル/h): {dollar_per_hour}")
        print(f"単位時間値段(円/h): {yen_per_hour}")

        if args.hours is not None:
            total_dollar = dollar_per_hour * args.hours
            total_yen = total_dollar * args.yen_per_dollar
            print(f"時間(h): {args.hours}")
            print(f"値段(ドル): {total_dollar}")
            print(f"値段(円): {total_yen}")

    return cmd
