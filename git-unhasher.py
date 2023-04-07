import re
import shutil
import pathlib
import argparse
import subprocess


dir_names = ["gitlab-data", "repositories", "@hashed"]


def main(path: pathlib.Path, output: pathlib.Path):
    for idx, name in enumerate(dir_names):
        if path.name == name:
            path = path.joinpath(*dir_names[idx+1:])
            break

    for repo_config in path.glob("**/config"):
        with open(repo_config) as file:
            config = file.read()

        match = re.search(r"fullpath = ([\w\.@\:/\-~]+)", config)
        if not match:
            continue

        repo_path = match.group(1)
        print(f"[+] copying {repo_path}")

        dotgit_path = output / repo_path / ".git"
        shutil.copytree(repo_config.parent, dotgit_path)

        with open(dotgit_path / "config", "w") as file:
            file.write(config.replace("bare = true", "bare = false"))

        subprocess.run(["git", "checkout", "HEAD"], cwd=dotgit_path.parent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="git unhasher")

    parser.add_argument(
        "-o", "--output",
        default=".", type=pathlib.Path, help="output path"
    )

    parser.add_argument(
        "path", metavar="PATH",
        type=pathlib.Path, help="path to hashed directory"
    )

    args = parser.parse_args()
    main(args.path, args.output)
