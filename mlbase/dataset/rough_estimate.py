from mlbase.utils.cli import Command


def rough_estimate_command() -> Command:
    cmd = Command("rough_estimate", "概算する")
    data_size_cmd = Command("datasize", "データサイズを概算") << cmd
    data_size_cmd.option("--width", type=int, required=True)
    data_size_cmd.option("--height", type=int, required=True)
    data_size_cmd.option("--channel", type=int, required=True)
    data_size_cmd.option("--count", type=int, required=True)

    @data_size_cmd
    def _(args, *_, **__):
        print(args.width * args.height * args.channel * args.count // 1000000000, "[GB]")

    return cmd
