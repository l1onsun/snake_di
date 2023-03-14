#!/usr/bin/env bash
python_versions=("${@}")

for version in ${python_versions[*]};
do
  pyenv local "$version"
  python_bin_path=$(pyenv which python)
  python_version_root=$(dirname "$(dirname "$python_bin_path")")
  echo "$python_version_root"
  rm -r "$python_version_root/lib/python$version/test"
  rm -r "$python_version_root/lib/python$version/config-$version-x86_64-linux-musl"
done